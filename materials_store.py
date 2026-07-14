# -*- coding: utf-8 -*-
"""Server-side storage for uploaded course materials.

Text content lives inline in data/materials.json; image bytes are kept as
separate files under data/files/ so the JSON file stays small even with a
large number of uploaded images. Both the Flask app (/upload, browser) and
ingest_cli.py (terminal bulk ingestion) write through this module, so
materials from either source show up in the chat the same way.
"""
import base64
import json
import os
import uuid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
FILES_DIR = os.path.join(DATA_DIR, 'files')
MATERIALS_PATH = os.path.join(DATA_DIR, 'materials.json')


def _ensure_dirs():
    os.makedirs(FILES_DIR, exist_ok=True)


def load_materials():
    """Lean list for the UI: no image bytes, just metadata."""
    _ensure_dirs()
    if not os.path.exists(MATERIALS_PATH):
        return []
    with open(MATERIALS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def _save_materials(materials):
    _ensure_dirs()
    with open(MATERIALS_PATH, 'w', encoding='utf-8') as f:
        json.dump(materials, f, ensure_ascii=False, indent=2)


def add_material(filename, mtype, content=None, media_type=None, image_bytes=None, error=None):
    """Extracts+stores one material and persists it. Returns the stored record."""
    materials = load_materials()
    record = {'id': uuid.uuid4().hex, 'filename': filename, 'type': mtype}

    if mtype == 'text':
        record['content'] = content or ''
    elif mtype == 'image':
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'png'
        file_name = f"{record['id']}.{ext}"
        _ensure_dirs()
        with open(os.path.join(FILES_DIR, file_name), 'wb') as f:
            f.write(image_bytes or b'')
        record['media_type'] = media_type or 'image/png'
        record['file'] = file_name
    elif mtype == 'error':
        record['error'] = error or 'שגיאה'

    materials.append(record)
    _save_materials(materials)
    return record


def delete_material(material_id):
    materials = load_materials()
    remaining = [m for m in materials if m.get('id') != material_id]
    if len(remaining) == len(materials):
        return False
    removed = next(m for m in materials if m.get('id') == material_id)
    if removed.get('type') == 'image' and removed.get('file'):
        path = os.path.join(FILES_DIR, removed['file'])
        if os.path.exists(path):
            os.remove(path)
    _save_materials(remaining)
    return True


def load_materials_with_data():
    """Hydrated list for chat requests: images get their base64 data loaded from disk."""
    result = []
    for m in load_materials():
        if m.get('type') == 'image' and m.get('file'):
            path = os.path.join(FILES_DIR, m['file'])
            try:
                with open(path, 'rb') as f:
                    data = base64.b64encode(f.read()).decode('ascii')
            except FileNotFoundError:
                continue
            hydrated = dict(m)
            hydrated['data'] = data
            result.append(hydrated)
        else:
            result.append(m)
    return result
