# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Skills Manager is a local web-based CRUD interface for managing Claude AI skills stored in `~/.claude/skills/`. It consists of a Python HTTP server + single-page HTML app. No build tools or external dependencies required — just Python 3 stdlib.

## Running the Server

```bash
# Run server (serves on http://localhost:7337)
python3 skills-manager.py

# Run the updated server (falls back to new HTML if available)
python3 skills-manager-updated.py

# Skip auto-opening the browser
python3 skills-manager.py --no-browser
```

## Deployment

```bash
# Deploy new HTML + restart server (comprehensive)
bash deploy-and-start.sh

# Deploy HTML only
python3 quick-deploy.py
# Or with explicit source path:
python3 quick-deploy.py /path/to/skills-manager-new.html
```

**Deployment target paths:**
- Server: `~/.claude/skills-manager.py`
- HTML: `~/.claude/skills-manager.html`
- Skills data: `~/.claude/skills/{skill-name}/`
- Cursor sync script: `~/.claude/sync-skills-to-cursor.py`

## Architecture

### Backend (`skills-manager.py` / `skills-manager-updated.py`)

Pure Python 3 `BaseHTTPRequestHandler` server. Key functions:

- `list_skills()` — reads all skill directories from `~/.claude/skills/`
- `get_skill(name)` — returns metadata (`skill.json`) + content (`SKILL.md` or `skill.md`)
- `save_skill(name, meta, content)` — writes files to disk
- `delete_skill(name)` — removes skill directory
- `run_sync()` — invokes the Cursor sync script via subprocess

**REST API:**
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Serve HTML |
| GET | `/api/skills` | List all skills |
| GET | `/api/skills/{name}` | Get skill (metadata + content) |
| POST | `/api/skills/{name}` | Create/update skill `{meta, content}` |
| DELETE | `/api/skills/{name}` | Delete skill |
| POST | `/api/sync` | Trigger Cursor sync |

### Frontend (`skills-manager.html` / `skills-manager-new.html`)

Vanilla JS SPA embedded in a single HTML file. All state is in-memory; all persistence goes through the REST API above.

- **`skills-manager.html`** — English, Tailwind CSS via CDN
- **`skills-manager-new.html`** — Hebrew/RTL (`lang="he" dir="rtl"`), custom CSS design system (primary `#002D23`, bold `#64C3BE`, accent `#D0EDEB`), Google Fonts (Noto Sans Hebrew)

Both HTML files share the same JavaScript API contract and are interchangeable from the server's perspective.

### Skill File Format

Each skill lives in `~/.claude/skills/{name}/`:
```
skill.json    ← {"description": "...", "version": "...", "tags": [...]}
SKILL.md      ← markdown content (also accepted as skill.md)
```
