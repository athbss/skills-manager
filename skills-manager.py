#!/usr/bin/env python3
"""
Claude Skills Manager - Local Web Interface
http://localhost:7337

Serves a management UI for ~/.claude/skills/ with full CRUD + Cursor sync.
"""

import json
import os
import shutil
import subprocess
import sys
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional, List, Dict
from urllib.parse import urlparse, unquote

SKILLS_DIR  = Path.home() / ".claude" / "skills"
SYNC_SCRIPT = Path.home() / ".claude" / "sync-skills-to-cursor.py"
HTML_FILE   = Path.home() / ".claude" / "skills-manager.html"
PORT        = 7337
PYTHON      = sys.executable


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def find_skill_md(skill_dir: Path) -> Optional[Path]:
    for name in ("SKILL.md", "skill.md"):
        p = skill_dir / name
        if p.exists():
            return p
    return None


def skill_modified(skill_dir: Path) -> str:
    """Return ISO datetime string of most recent file modification in skill dir."""
    candidates = [skill_dir / "SKILL.md", skill_dir / "skill.md", skill_dir / "skill.json"]
    mtimes = [p.stat().st_mtime for p in candidates if p.exists()]
    if not mtimes:
        mtimes = [skill_dir.stat().st_mtime]
    return datetime.fromtimestamp(max(mtimes)).strftime("%Y-%m-%dT%H:%M:%S")


def get_sync_targets() -> List[Dict]:
    """Return list of detected sync targets on this machine."""
    targets = [{"name": "Claude Code", "active": True}]
    codex_skills = Path.home() / ".codex" / "skills"
    if codex_skills.exists() or codex_skills.is_symlink():
        targets.append({"name": "Codex", "active": True})
    cursor_dir = Path.home() / ".cursor"
    if cursor_dir.exists():
        targets.append({"name": "Cursor", "active": SYNC_SCRIPT.exists()})
    return targets


def bump_patch(version: str) -> str:
    """Bump the patch (rightmost) component of a semver string."""
    if not version:
        return "1.0.0"
    parts = version.split(".")
    try:
        parts[-1] = str(int(parts[-1]) + 1)
    except ValueError:
        parts.append("1")
    return ".".join(parts)


def list_skills() -> List[Dict]:
    if not SKILLS_DIR.exists():
        return []
    skills = []
    for d in sorted(SKILLS_DIR.iterdir()):
        if not d.is_dir():
            continue
        meta: dict = {}
        jp = d / "skill.json"
        if jp.exists():
            try:
                meta = json.loads(jp.read_text(encoding="utf-8"))
            except Exception:
                pass
        skills.append({
            "name":        d.name,
            "description": meta.get("description", ""),
            "version":     meta.get("version", "") or "1.0.0",
            "tags":        meta.get("tags", []),
            "modified":    skill_modified(d),
        })
    return skills


def get_skill(name: str) -> Optional[Dict]:
    d = SKILLS_DIR / name
    if not d.is_dir():
        return None
    meta: dict = {}
    jp = d / "skill.json"
    if jp.exists():
        try:
            meta = json.loads(jp.read_text(encoding="utf-8"))
        except Exception:
            pass
    md_path = find_skill_md(d)
    content = md_path.read_text(encoding="utf-8") if md_path else ""
    files = [f.name for f in sorted(d.iterdir()) if f.is_file() and not f.name.startswith(".")]
    return {"name": name, "meta": meta, "content": content, "files": files}


def save_skill(name: str, meta: Dict, content: str) -> Dict:
    d = SKILLS_DIR / name
    d.mkdir(parents=True, exist_ok=True)
    # Auto-version: bump patch on every save
    current = meta.get("version", "") or ""
    if not current:
        # First save — check if existing skill.json already has a version
        jp = d / "skill.json"
        if jp.exists():
            try:
                existing = json.loads(jp.read_text(encoding="utf-8"))
                current = existing.get("version", "") or ""
            except Exception:
                pass
    new_version = bump_patch(current)
    meta["version"] = new_version
    (d / "skill.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    md_path = find_skill_md(d) or (d / "SKILL.md")
    md_path.write_text(content, encoding="utf-8")
    return {"version": new_version, "modified": skill_modified(d)}


def delete_skill(name: str) -> None:
    d = SKILLS_DIR / name
    if d.is_dir():
        shutil.rmtree(d)


def run_sync() -> str:
    if not SYNC_SCRIPT.exists():
        return "Sync script not found"
    try:
        r = subprocess.run(
            [PYTHON, str(SYNC_SCRIPT)],
            capture_output=True, text=True, timeout=30
        )
        return (r.stdout + r.stderr).strip()
    except Exception as e:
        return str(e)


# ---------------------------------------------------------------------------
# HTTP Handler
# ---------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # quiet

    # ---- helpers -----------------------------------------------------------

    def _send_json(self, data, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    def _skill_name(self) -> str:
        path = urlparse(self.path).path
        return unquote(path[len("/api/skills/"):])

    # ---- OPTIONS -----------------------------------------------------------

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    # ---- GET ---------------------------------------------------------------

    def do_GET(self):
        path = urlparse(self.path).path

        # Serve HTML app
        if path in ("/", "/index.html"):
            if HTML_FILE.exists():
                body = HTML_FILE.read_bytes()
            else:
                body = b"<h1>skills-manager.html not found</h1>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # API: sync targets
        if path == "/api/sync-targets":
            self._send_json(get_sync_targets())
            return

        # API: list skills
        if path == "/api/skills":
            self._send_json(list_skills())
            return

        # API: get single skill
        if path.startswith("/api/skills/"):
            name = self._skill_name()
            skill = get_skill(name)
            if skill:
                self._send_json(skill)
            else:
                self._send_json({"error": "not found"}, 404)
            return

        self._send_json({"error": "not found"}, 404)

    # ---- POST --------------------------------------------------------------

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._read_json()

        if path == "/api/sync":
            result = run_sync()
            self._send_json({"result": result})
            return

        if path.startswith("/api/skills/"):
            name = self._skill_name()
            result = save_skill(name, body.get("meta", {}), body.get("content", ""))
            self._send_json({"ok": True, **result})
            return

        self._send_json({"error": "not found"}, 404)

    # ---- DELETE ------------------------------------------------------------

    def do_DELETE(self):
        path = urlparse(self.path).path
        if path.startswith("/api/skills/"):
            delete_skill(self._skill_name())
            self._send_json({"ok": True})
            return
        self._send_json({"error": "not found"}, 404)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"✅ Claude Skills Manager → http://localhost:{PORT}")
    if "--no-browser" not in sys.argv:
        webbrowser.open(f"http://localhost:{PORT}")
    server.serve_forever()
