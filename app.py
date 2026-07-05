# -*- coding: utf-8 -*-
import base64
import io
import os

import openpyxl
import PyPDF2
import anthropic
from bidi.algorithm import get_display
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
from fpdf import FPDF

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder='static')
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024  # 30MB

MODEL = 'claude-sonnet-5'

IMAGE_EXT = {'png', 'jpg', 'jpeg'}
TEXT_EXT = {'pdf', 'docx', 'xlsx', 'txt'}

SYSTEM_TEMPLATE = """אתה ד"ר א., עוזר אקדמי אישי. הסטודנט {name} לומד {degree} ב{institution}, שנה {year}. הקורסים שלו: {courses}. החומרים שהועלו: {materials}

ענה תמיד בעברית, בצורה מקצועית אך ידידותית. הסבר מושגים בצורה בהירה, תן דוגמאות כשמועיל, והתייחס לחומרי הקורס וההקשר האקדמי של הסטודנט כשרלוונטי. אתה יכול להשתמש בחיפוש באינטרנט כדי להביא מידע עדכני, הפניות למקורות, או הבהרות שאינן בחומרים שהועלו."""


def _load_api_key():
    key = os.environ.get('ANTHROPIC_API_KEY', '')
    if key:
        return key
    raise RuntimeError('ANTHROPIC_API_KEY not found - set it as an environment variable')


client = anthropic.Anthropic(api_key=_load_api_key())


# ─── Text extraction ────────────────────────────────────────────────────────

def extract_pdf_text(stream):
    reader = PyPDF2.PdfReader(stream)
    parts = []
    for page in reader.pages:
        text = page.extract_text() or ''
        if text.strip():
            parts.append(text)
    return '\n'.join(parts)


def extract_docx_text(stream):
    doc = Document(stream)
    return '\n'.join(p.text for p in doc.paragraphs if p.text.strip())


def extract_xlsx_text(stream):
    wb = openpyxl.load_workbook(stream, data_only=True)
    lines = []
    for sheet in wb.worksheets:
        lines.append(f'== גיליון: {sheet.title} ==')
        for row in sheet.iter_rows(values_only=True):
            cells = [str(c) for c in row if c is not None]
            if cells:
                lines.append(' | '.join(cells))
    return '\n'.join(lines)


def extract_txt_text(stream):
    raw = stream.read()
    for encoding in ('utf-8', 'cp1255', 'latin-1'):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode('utf-8', errors='ignore')


EXTRACTORS = {
    'pdf': extract_pdf_text,
    'docx': extract_docx_text,
    'xlsx': extract_xlsx_text,
    'txt': extract_txt_text,
}


# ─── DOCX export (RTL) ───────────────────────────────────────────────────────

def set_rtl(paragraph):
    p_pr = paragraph._p.get_or_add_pPr()
    bidi = OxmlElement('w:bidi')
    p_pr.append(bidi)
    for run in paragraph.runs:
        r_pr = run._element.get_or_add_rPr()
        rtl = OxmlElement('w:rtl')
        r_pr.append(rtl)


def build_docx(text, title=None):
    doc = Document()
    if title:
        heading = doc.add_heading(title, level=1)
        heading.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        set_rtl(heading)
    for line in text.split('\n'):
        paragraph = doc.add_paragraph(line)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        set_rtl(paragraph)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf


# ─── PDF export (RTL) ────────────────────────────────────────────────────────

FONT_CANDIDATES = [
    os.path.join(BASE_DIR, 'static', 'fonts', 'Hebrew-Regular.ttf'),
    'C:/Windows/Fonts/arial.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    '/usr/share/fonts/truetype/noto/NotoSansHebrew-Regular.ttf',
    '/usr/share/fonts/truetype/noto/NotoSansHebrew[wdth,wght].ttf',
]


def find_hebrew_font():
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


def build_pdf(text, title=None):
    font_path = find_hebrew_font()
    if not font_path:
        raise RuntimeError(
            'לא נמצא פונט התומך בעברית בשרת. הוסיפו קובץ פונט (לדוגמה Noto Sans Hebrew) '
            'בנתיב static/fonts/Hebrew-Regular.ttf ונסו שוב.'
        )
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('Hebrew', '', font_path)
    if title:
        pdf.set_font('Hebrew', size=16)
        pdf.multi_cell(0, 10, get_display(title), align='R', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(2)
    pdf.set_font('Hebrew', size=12)
    for line in text.split('\n'):
        if line.strip():
            pdf.multi_cell(0, 8, get_display(line), align='R', new_x='LMARGIN', new_y='NEXT')
        else:
            pdf.ln(8)
    buf = io.BytesIO(bytes(pdf.output()))
    buf.seek(0)
    return buf


# ─── Static file routes ──────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')


@app.route('/config.js')
def config_js():
    return send_from_directory(BASE_DIR, 'config.js', mimetype='application/javascript')


@app.route('/manifest.json')
def manifest():
    return send_from_directory(BASE_DIR, 'manifest.json', mimetype='application/manifest+json')


@app.route('/service-worker.js')
def service_worker():
    return send_from_directory(BASE_DIR, 'service-worker.js', mimetype='application/javascript')


# ─── API: upload ──────────────────────────────────────────────────────────────

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'לא נבחרו קבצים'}), 400

    materials = []
    for f in files:
        filename = f.filename or 'קובץ'
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

        if ext in IMAGE_EXT:
            try:
                data = base64.b64encode(f.read()).decode('ascii')
                media_type = 'image/jpeg' if ext in ('jpg', 'jpeg') else 'image/png'
                materials.append({
                    'filename': filename,
                    'type': 'image',
                    'media_type': media_type,
                    'data': data,
                })
            except Exception as e:
                materials.append({'filename': filename, 'type': 'error', 'error': str(e)})
            continue

        extractor = EXTRACTORS.get(ext)
        if not extractor:
            materials.append({
                'filename': filename,
                'type': 'error',
                'error': 'סוג קובץ לא נתמך',
            })
            continue

        try:
            text = extractor(io.BytesIO(f.read()))
            materials.append({
                'filename': filename,
                'type': 'text',
                'content': text,
            })
        except Exception as e:
            materials.append({'filename': filename, 'type': 'error', 'error': str(e)})

    return jsonify({'materials': materials})


# ─── API: chat ────────────────────────────────────────────────────────────────

def materials_summary(materials):
    if not materials:
        return 'לא הועלו חומרים.'
    lines = []
    for m in materials:
        if m.get('type') == 'text':
            content = m.get('content', '').strip()
            if content:
                lines.append(f"--- קובץ: {m.get('filename')} ---\n{content}")
        elif m.get('type') == 'image':
            lines.append(f"--- קובץ: {m.get('filename')} (תמונה, מצורפת להודעה) ---")
    return '\n\n'.join(lines) if lines else 'לא הועלו חומרים.'


def build_user_content(message_text, materials, inline_image):
    image_blocks = []
    for m in materials or []:
        if m.get('type') == 'image' and m.get('data'):
            image_blocks.append({
                'type': 'image',
                'source': {
                    'type': 'base64',
                    'media_type': m.get('media_type', 'image/png'),
                    'data': m['data'],
                },
            })
    if inline_image and inline_image.get('data'):
        image_blocks.append({
            'type': 'image',
            'source': {
                'type': 'base64',
                'media_type': inline_image.get('media_type', 'image/png'),
                'data': inline_image['data'],
            },
        })
    if not image_blocks:
        return message_text
    return image_blocks + [{'type': 'text', 'text': message_text}]


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json or {}
    message = data.get('message', '').strip()
    history = data.get('history', [])
    profile = data.get('profile') or {}
    materials = data.get('materials') or []
    inline_image = data.get('image')

    if not message and not inline_image:
        return jsonify({'error': 'אין הודעה'}), 400

    system = SYSTEM_TEMPLATE.format(
        name=profile.get('name', 'הסטודנט'),
        degree=profile.get('degree', 'לא צוין'),
        institution=profile.get('institution', 'לא צוין'),
        year=profile.get('year', 'לא צוין'),
        courses=profile.get('courses', 'לא צוין'),
        materials=materials_summary(materials),
    )

    messages = [{'role': h.get('role'), 'content': h.get('content')} for h in history]
    messages.append({
        'role': 'user',
        'content': build_user_content(message, materials, inline_image),
    })

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=6000,
            system=system,
            tools=[{'type': 'web_search_20260209', 'name': 'web_search'}],
            messages=messages,
        )
        reply = '\n\n'.join(
            block.text for block in response.content if block.type == 'text'
        ).strip()
        if not reply:
            reply = 'מצטער, לא הצלחתי לייצר תשובה. ננסה שוב?'
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─── API: downloads ─────────────────────────────────────────────────────────

@app.route('/download/docx', methods=['POST'])
def download_docx():
    data = request.json or {}
    content = data.get('content', '')
    title = data.get('title', 'תשובת ד"ר א.')
    buf = build_docx(content, title)
    return send_file(
        buf,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        as_attachment=True,
        download_name='dr-a-answer.docx',
    )


@app.route('/download/pdf', methods=['POST'])
def download_pdf():
    data = request.json or {}
    content = data.get('content', '')
    title = data.get('title', 'תשובת ד"ר א.')
    try:
        buf = build_pdf(content, title)
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500
    return send_file(
        buf,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='dr-a-answer.pdf',
    )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5005))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
