# ד"ר א. — עוזר אקדמי אישי

PWA לסטודנטים: פרופיל אישי, העלאת חומרי קורס (PDF/DOCX/XLSX/TXT/תמונות — קובץ בודד, תיקייה שלמה, או קליטה מסקריפט טרמינל בכמות גדולה), צ'אט עם Claude (כולל חיפוש באינטרנט והודעות קוליות), ואפשרות להוריד כל תשובה כ-DOCX או PDF.

## סטאק
- **Frontend**: `index.html` — קובץ יחיד (HTML+CSS+JS), RTL מלא, PWA (manifest + service worker)
- **Backend**: `app.py` — Flask
- **AI**: Anthropic Claude (`claude-sonnet-5`) עם כלי `web_search`
- **קול**: תמלול הודעות קוליות דרך Groq Whisper (`whisper-large-v3`, עברית)
- **שמירת מצב**: פרופיל הסטודנט, ההיסטוריה וחומרי הקורס נשמרים בצד השרת (`data/state.json`, `data/materials.json` + `data/files/`) — אין login, אין משתמשים מרובים, אבל המצב משותף בין דפדפנים/מכשירים ובין קליטה דרך הדפדפן לקליטה דרך `ingest_cli.py`

## הרצה מקומית

```bash
pip install -r requirements.txt
set ANTHROPIC_API_KEY=sk-ant-...   # PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."
python app.py
```
האפליקציה תרוץ על http://localhost:5005

## משתני סביבה
- `ANTHROPIC_API_KEY` — מפתח Claude (חובה)
- `GROQ_API_KEY` — מפתח לתמלול קול דרך Whisper (אופציונלי; בלעדיו כפתור ההקלטה יחזיר שגיאה ברורה)
- `DRA_API_KEY` — סוד משותף לאימות בקשות דרך header `X-API-Key` (אופציונלי, מומלץ כשהשרת חשוף מעבר ל-localhost)
- `PORT` — פורט האזנה (ברירת מחדל 5005)

## קליטת קבצים בכמות גדולה מהטרמינל

כשיש הרבה חומרי קורס (עשרות/מאות קבצים) עדיף לקלוט אותם ישירות מהטרמינל במקום דרך הדפדפן:

```bash
python ingest_cli.py --folder "C:\path\to\course-materials"
```

הסקריפט סורק את התיקייה רקורסיבית, מחלץ טקסט/תמונות מכל קובץ נתמך (PDF/DOCX/XLSX/TXT/PNG/JPG), וכותב ישירות ל-`data/materials.json` (בלי HTTP ובלי מגבלת גודל בקשה) — הקבצים יופיעו אוטומטית בצ'אט של הדפדפן בהעלאה הבאה.

## הערה חשובה: ייצוא PDF בעברית

ייצוא תשובה ל-**PDF** דורש קובץ פונט שתומך בעברית בנתיב `static/fonts/Hebrew-Regular.ttf` (לא כלול בריפו מטעמי רישוי). בפיתוח מקומי על Windows האפליקציה תיפול בחזרה אוטומטית לפונט המערכת (Arial). לפריסה על שרת לינוקס יש להוסיף פונט עברית, לדוגמה [Noto Sans Hebrew](https://fonts.google.com/noto/specimen/Noto+Sans+Hebrew) (רישיון OFL, חינמי) — מורידים את `NotoSansHebrew-Regular.ttf`, שומרים בנתיב `static/fonts/Hebrew-Regular.ttf`.

ייצוא **DOCX** עובד בלי תלות בפונט (Word מצייר עברית בעצמו), כולל פיצול נכון של כיוון טקסט בשורות עם עברית ואנגלית מעורבות (ראו `static/fonts` להערת הפונט של ה-PDF בלבד — ה-DOCX לא צריך פונט).

## פריסה כשירות systemd (שרת ביתי)

האפליקציה רצה על שרת ביתי (SSH `malloy@192.168.0.199`), תחת `~/agents/dr-a`, כשירות systemd בשם `dr-a.service`, פורט 5005 — באותו דפוס כמו שאר הסוכנים (`tishi-server` וכו').

1. **הכנת השרת**
   ```bash
   cd ~/agents/dr-a
   python3 -m venv venv
   venv/bin/pip install -r requirements.txt
   ```
2. **קובץ `.env`** ב-`~/agents/dr-a/.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   GROQ_API_KEY=gsk_...
   DRA_API_KEY=...
   ```
3. **התקנת השירות** — ראו `dr-a.service` לדוגמת unit file:
   ```bash
   sudo cp dr-a.service /etc/systemd/system/dr-a.service
   sudo systemctl daemon-reload
   sudo systemctl enable --now dr-a.service
   ```
4. בדיקה: `curl http://localhost:5005/` או `sudo systemctl status dr-a`.

## מבנה הפרויקט

```
dr-a/
├── app.py                   # Flask backend
├── materials_store.py       # אחסון חומרי קורס בצד שרת (data/materials.json + data/files/)
├── ingest_cli.py             # קליטת קבצים בכמות גדולה מהטרמינל
├── index.html                # כל ה-Frontend (HTML+CSS+JS)
├── config.js                 # API_URL
├── manifest.json              # PWA manifest
├── service-worker.js          # PWA service worker
├── generate_icons.py          # סקריפט ליצירת אייקוני PWA (הורץ פעם אחת)
├── static/
│   ├── icon.svg
│   ├── icon-192.png
│   ├── icon-512.png
│   └── fonts/Hebrew-Regular.ttf   # להוסיף בעצמכם (ראו לעיל)
├── data/                      # נוצר אוטומטית — state.json, materials.json, files/
├── requirements.txt
├── dr-a.service                # unit file ל-systemd
└── .gitignore
```
