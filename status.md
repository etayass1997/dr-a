# ד"ר א. — סטטוס פרויקט

## סטטוס כללי: ✅ פעיל ומוכן לדפלוי

## מה הושלם
- [x] Flask backend (`app.py`)
- [x] Frontend קובץ יחיד (`index.html`) — RTL מלא
- [x] העלאת קבצים (PDF/DOCX/XLSX/TXT/תמונות)
- [x] צ'אט עם Claude + web_search
- [x] ייצוא תשובות ל-DOCX
- [x] ייצוא תשובות ל-PDF (עם fallback לArial ב-Windows)
- [x] PWA (manifest + service worker)
- [x] `render.yaml` + `Procfile` לדפלוי
- [x] אין login — localStorage בלבד

## שינויים אחרונים
| תאריך | שינוי |
|--------|-------|
| 18/06/2026 | תיקון `.gitignore` ו-`index.html` |
| 17/06/2026 | הקמת כל הפרויקט (app.py, index.html, PWA, README) |

## עתידי / פתוח
- [ ] הוספת פונט עברית ל-`static/fonts/` לדפלוי Render
- [ ] בדיקת דפלוי בפועל על Render
- [ ] תמיכה בהיסטוריית שיחות בין session
