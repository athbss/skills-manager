# Skills Manager

ממשק ניהול מקומי לסקילים של Claude AI — עורך מלא עם סנכרון אוטומטי לכלים מרובים.

**→ http://localhost:7337**

---

## דרישות

- Python 3 (stdlib בלבד, אין תלויות חיצוניות)

---

## הפעלה

```bash
python3 ~/.claude/skills-manager.py
```

הדפדפן נפתח אוטומטית. לביטול פתיחת הדפדפן:

```bash
python3 ~/.claude/skills-manager.py --no-browser
```

---

## ארכיטקטורה

### Backend — `skills-manager.py`

שרת `BaseHTTPRequestHandler` טהור עם REST API:

| Method | Path | תיאור |
|--------|------|--------|
| `GET` | `/` | הגשת ממשק ה-HTML |
| `GET` | `/api/skills` | רשימת כל הסקילים |
| `GET` | `/api/skills/{name}` | קבלת סקיל (מטא + תוכן) |
| `POST` | `/api/skills/{name}` | יצירה / עדכון סקיל |
| `DELETE` | `/api/skills/{name}` | מחיקת סקיל |
| `POST` | `/api/sync` | הפעלת סקריפט הסנכרון לCursor |
| `GET` | `/api/sync-targets` | זיהוי כלים מסונכרנים במחשב |

### Frontend — `skills-manager.html`

SPA בקובץ HTML יחיד. Vanilla JS, עיצוב RTL עברי, Toast UI Editor.

### פורמט קובץ Skill

כל סקיל יושב בתיקייה נפרדת תחת `~/.claude/skills/{name}/`:

```
~/.claude/skills/
└── my-skill/
    ├── SKILL.md       ← תוכן הסקיל (Markdown)
    └── skill.json     ← מטאדאטה {"description", "version", "tags"}
```

---

## סנכרון לכלים

| כלי | שיטה |
|-----|------|
| **Claude Code** | מקור — קורא ישירות מ-`~/.claude/skills/` |
| **Codex** | Symlink: `~/.codex/skills/ → ~/.claude/skills/` |
| **Cursor** | LaunchAgent + `~/.claude/sync-skills-to-cursor.py` |

הממשק מזהה אוטומטית אילו כלים מותקנים ומציג אותם בתפריט "מסנכרן ל".

### יצירת Symlink לCodex

```bash
mkdir -p ~/.codex
ln -s ~/.claude/skills ~/.codex/skills
```

---

## ניהול גרסאות

- **גרסת פרוייקט** — נשמרת בקובץ `VERSION`, נעלה אוטומטית ב-patch בכל push ל-`main` (GitHub Actions)
- **גרסת סקיל** — נשמרת ב-`skill.json`, נעלה אוטומטית ב-patch בכל שמירה

---

## פיתוח

```bash
# שכפול הריפו
git clone https://github.com/athbss/skills-manager.git
cd skills-manager

# פריסה לוקלית (דורס את הקבצים ב-~/.claude/)
cp skills-manager.py ~/.claude/skills-manager.py
cp skills-manager.html ~/.claude/skills-manager.html

# הפעלה
python3 ~/.claude/skills-manager.py
```
