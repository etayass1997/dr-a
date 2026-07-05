# ד"ר א. — עוזר אקדמי אישי

PWA לסטודנטים: פרופיל אישי, העלאת חומרי קורס (PDF/DOCX/XLSX/TXT/תמונות), וצ'אט עם Claude (כולל חיפוש באינטרנט), עם אפשרות להוריד כל תשובה כ-DOCX או PDF.

## סטאק
- **Frontend**: `index.html` — קובץ יחיד (HTML+CSS+JS), RTL מלא, PWA (manifest + service worker)
- **Backend**: `app.py` — Flask
- **AI**: Anthropic Claude (`claude-sonnet-5`) עם כלי `web_search`
- **שמירת מצב**: פרופיל הסטודנט, רשימת הקורסים, חומרי הקורס וההיסטוריה נשמרים ב-`localStorage` בדפדפן — אין login ואין בסיס נתונים

## הרצה מקומית

```bash
pip install -r requirements.txt
set ANTHROPIC_API_KEY=sk-ant-...   # PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."
python app.py
```
האפליקציה תרוץ על http://localhost:5005

## הערה חשובה: ייצוא PDF בעברית

ייצוא תשובה ל-**PDF** דורש קובץ פונט שתומך בעברית בנתיב `static/fonts/Hebrew-Regular.ttf` (לא כלול בריפו מטעמי רישוי). בפיתוח מקומי על Windows האפליקציה תיפול בחזרה אוטומטית לפונט המערכת (Arial), כך שזה יעבוד בלי הגדרה נוספת. **לדפלוי בענן (Render)** יש צורך להוסיף פונט עברית בקוד הפתוח, לדוגמה [Noto Sans Hebrew](https://fonts.google.com/noto/specimen/Noto+Sans+Hebrew) (רישיון OFL, חינמי) — מורידים את `NotoSansHebrew-Regular.ttf`, שומרים בנתיב `static/fonts/Hebrew-Regular.ttf` ומוסיפים ל-git לפני הדפלוי.

ייצוא **DOCX** עובד בלי תלות בפונט (Word מצייר עברית בעצמו).

## דפלוי ל-Render

1. **העלאה ל-GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/USERNAME/REPO.git
   git push -u origin main
   ```
   (זכרו להוסיף את פונט העברית ל-`static/fonts/Hebrew-Regular.ttf` לפני ה-commit, כמתואר לעיל)

2. **חיבור ל-Render**
   - נכנסים ל-[Render Dashboard](https://dashboard.render.com)
   - **New +** → **Web Service** → מחברים את ה-repo מ-GitHub
   - Render יזהה את `render.yaml` אוטומטית (Build: `pip install -r requirements.txt`, Start: `gunicorn app:app`)

3. **הוספת מפתח API**
   - בלשונית **Environment** של השירות ב-Render מוסיפים משתנה סביבה:
     - `ANTHROPIC_API_KEY` = המפתח שלכם מ-console.anthropic.com

4. **עדכון API_URL**
   - אם ה-Frontend וה-Backend רצים מאותו שירות (המצב הסטנדרטי כאן) — אין צורך לשנות כלום, `config.js` משאיר `API_URL = ""` (כתובת יחסית).
   - אם בעתיד תפצלו לשני שירותים נפרדים — עדכנו את `const API_URL` בקובץ `config.js` לכתובת ה-backend המלאה (לדוגמה `https://dr-a-api.onrender.com`).

5. לאחר הדפלוי, האפליקציה תהיה זמינה בכתובת שש Render ייתן (`https://dr-a-XXXX.onrender.com`), כולל אפשרות "התקנה" כ-PWA במובייל.

## מבנה הפרויקט

```
dr-a/
├── app.py                 # Flask backend
├── index.html              # כל ה-Frontend (HTML+CSS+JS)
├── config.js               # API_URL
├── manifest.json            # PWA manifest
├── service-worker.js        # PWA service worker
├── generate_icons.py        # סקריפט ליצירת אייקוני PWA (הורץ פעם אחת)
├── static/
│   ├── icon.svg
│   ├── icon-192.png
│   ├── icon-512.png
│   └── fonts/Hebrew-Regular.ttf   # להוסיף בעצמכם (ראו לעיל)
├── requirements.txt
├── render.yaml
├── Procfile
└── .gitignore
```
