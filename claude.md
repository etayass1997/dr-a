# ד"ר א. — עוזר אקדמי אישי

## תיאור
PWA לסטודנטים: פרופיל אישי, העלאת חומרי קורס (PDF/DOCX/XLSX/TXT/תמונות), צ'אט עם Claude (כולל חיפוש אינטרנט), ואפשרות להוריד כל תשובה כ-DOCX או PDF. אין login ואין DB — הכל ב-localStorage.

## סטאק
- **Frontend**: `index.html` — קובץ יחיד (HTML+CSS+JS), RTL מלא, PWA
- **Backend**: `app.py` — Flask
- **AI**: Claude `claude-sonnet-5` עם כלי `web_search`
- **שמירה**: localStorage בלבד (פרופיל, קורסים, חומרים, היסטוריה)
- **דפלוי**: Render (port 5005)

## קבצים מרכזיים
| קובץ | תפקיד |
|------|--------|
| `app.py` | Flask backend |
| `index.html` | כל ה-Frontend |
| `config.js` | `API_URL` (ריק = אותו דומיין) |
| `manifest.json` | PWA manifest |
| `service-worker.js` | PWA offline |

## הערה: PDF עברית
ייצוא PDF דורש `static/fonts/Hebrew-Regular.ttf` (לא בgit מטעמי רישיון).  
בפיתוח מקומי fallback לArial. לדפלוי Render — יש להוסיף Noto Sans Hebrew.

## הרצה מקומית
```bash
pip install -r requirements.txt
set ANTHROPIC_API_KEY=sk-ant-...
python app.py   # http://localhost:5005
```
