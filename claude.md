# ד"ר א. — עוזר אקדמי אישי

## תיאור
PWA לסטודנטים: פרופיל אישי, העלאת חומרי קורס (PDF/DOCX/XLSX/TXT/תמונות — קובץ בודד, תיקייה שלמה מהדפדפן, או קליטה בכמות גדולה דרך `ingest_cli.py` בטרמינל), צ'אט עם Claude (כולל חיפוש אינטרנט והודעות קוליות), ואפשרות להוריד כל תשובה כ-DOCX או PDF. אין login ואין משתמשים מרובים — הכל נשמר בצד השרת (`data/`) כמצב יחיד ומשותף.

## סטאק
- **Frontend**: `index.html` — קובץ יחיד (HTML+CSS+JS), RTL מלא, PWA
- **Backend**: `app.py` — Flask
- **AI**: Claude `claude-sonnet-5` עם כלי `web_search`
- **קול**: Groq Whisper (`whisper-large-v3`, עברית) — הקלטה בדפדפן + `/transcribe`
- **שמירה**: צד שרת — `materials_store.py` (`data/materials.json` + `data/files/` לתמונות) ו-`data/state.json` (פרופיל + היסטוריה)
- **דפלוי**: שרת ביתי (SSH `malloy@192.168.0.199`), systemd service `dr-a.service`, פורט 5005 (לא Render יותר)

## קבצים מרכזיים
| קובץ | תפקיד |
|------|--------|
| `app.py` | Flask backend — chat/upload/transcribe/downloads/state |
| `materials_store.py` | אחסון חומרי קורס בצד שרת |
| `ingest_cli.py` | קליטת קבצים בכמות גדולה מהטרמינל (סורק תיקייה, קורא ל-`materials_store` ישירות) |
| `index.html` | כל ה-Frontend |
| `config.js` | `API_URL` (ריק = אותו דומיין) |
| `manifest.json` | PWA manifest |
| `service-worker.js` | PWA offline |
| `dr-a.service` | unit file ל-systemd |

## הערה: PDF עברית
ייצוא PDF דורש `static/fonts/Hebrew-Regular.ttf` (לא בgit מטעמי רישיון). בפיתוח מקומי fallback ל-Arial. לפריסה על שרת לינוקס — יש להוסיף Noto Sans Hebrew.
ייצוא DOCX משתמש בלוגיקת פיצול-כיוון per-run (מבוססת על `bidi_fixer/fix_bidi.py`) כדי לתמוך נכון בטקסט עברית-אנגלית מעורב.

## הרצה מקומית
```bash
pip install -r requirements.txt
set ANTHROPIC_API_KEY=sk-ant-...
python app.py   # http://localhost:5005
```

## אימות בקשות
אופציונלי, דרך `DRA_API_KEY` + header `X-API-Key` (אותו דפוס כמו `tishi-server`), מומלץ כשהשרת חשוף מעבר ל-localhost.
