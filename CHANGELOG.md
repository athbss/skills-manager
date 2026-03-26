# Changelog

כל השינויים המשמעותיים בפרוייקט מתועדים כאן.

פורמט מבוסס על [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), גרסאות לפי [Semantic Versioning](https://semver.org/).

---

## [2.0.2] — טרם שוחרר

---

## [2.0.1] — 2026-03-26

### תוקן
- תפריט "מסנכרן ל" לא הציג תוכן — נדרש restart לשרת לאחר הוספת endpoint חדש

---

## [2.0.0] — 2026-03-26

### נוסף
- **עורך Toast UI** — תמיכה במצב Markdown ומצב WYSIWYG (ויזואלי)
- **ניהול גרסאות אוטומטי לסקילים** — patch bump בכל שמירה, תצוגת גרסה ותאריך בסייד-בר
- **סנכרון לכלים מרובים** — Codex (symlink), Cursor (LaunchAgent), Claude Code (מקור)
- **תפריט "מסנכרן ל"** — זיהוי אוטומטי של כלים מותקנים ומצב הסנכרון
- **פילטר תגיות** — פאנל מתקפל עם ספירת סקילים לכל תגית
- **תאריך ושעה** בסייד-בר לפי הגדרות locale של המשתמש
- **גרסת פרוייקט** (v2.0.0) בתפריט העליון + קרדיט לחיץ
- **GitHub Actions** — bump אוטומטי של גרסת הפרוייקט בכל push ל-`main`

### שונה
- `skill_modified()` מחזיר datetime מלא (כולל שעה) במקום תאריך בלבד
- `/api/sync-targets` — endpoint חדש לזיהוי כלים מסונכרנים
- כפתורי "תוכן" / "מטא" ו-"Markdown" / "ויזואלי" עוצבו מחדש (underline tabs + mode toggle)
- `[hidden] { display: none !important }` — תיקון CSS שמנע לחיצה על סקילים

### תוקן
- לחיצה על סקיל לא עשתה כלום (`.empty-state { display: flex }` דרס `[hidden]`)
- Toast UI Editor נכשל באתחול כשה-container היה hidden — עבר ל-lazy init
- תוכן עורך יושר לימין (RTL) — תוקן עם `direction: ltr !important`

---

## [1.0.0] — 2026-01-01

### נוסף
- ממשק CRUD בסיסי לניהול סקילים
- שרת Python עם `BaseHTTPRequestHandler`
- SPA ב-HTML יחיד, עיצוב RTL עברי
- חיפוש בזמן אמת
- מודאל יצירה / מחיקה
- כפתור סנכרון לCursor
