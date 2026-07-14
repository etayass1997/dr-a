# -*- coding: utf-8 -*-
"""ingest_cli.py — קליטת קבצים בכמות גדולה מהטרמינל ישירות ל-materials_store,
בלי HTTP ובלי תלות ב-ANTHROPIC_API_KEY (ראו extractors.py).

שימוש:
    python ingest_cli.py --folder "C:\\path\\to\\course-materials"
    python ingest_cli.py --file "C:\\path\\to\\syllabus.pdf"
"""
import argparse
import sys
from pathlib import Path

from extractors import EXTRACTORS, IMAGE_EXT, ingest_file

# מסוף Windows יכול לרוץ בקידוד cp1255 שלא תומך ב-✓/✗ — כופים UTF-8 על הפלט.
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SUPPORTED_EXT = set(EXTRACTORS) | IMAGE_EXT


def ingest_path(path):
    with open(path, 'rb') as f:
        record = ingest_file(path.name, f)
    if record.get('type') == 'error':
        print(f'  ✗ {path.name}: {record.get("error")}')
        return False
    print(f'  ✓ {path.name}')
    return True


def ingest_folder(folder):
    files = sorted(
        p for p in folder.rglob('*')
        if p.is_file() and p.suffix.lower().lstrip('.') in SUPPORTED_EXT
    )
    if not files:
        print(f'לא נמצאו קבצים נתמכים בתיקייה {folder} (נתמך: {", ".join(sorted(SUPPORTED_EXT))})')
        return
    print(f'נמצאו {len(files)} קבצים נתמכים. קולט...')
    ok = sum(ingest_path(p) for p in files)
    print(f'\nסיכום: {ok}/{len(files)} קבצים נקלטו בהצלחה.')


def main():
    parser = argparse.ArgumentParser(description='קליטת חומרי קורס ל-ד"ר א׳ ישירות מהטרמינל')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--folder', type=str, help='תיקייה לסריקה רקורסיבית')
    group.add_argument('--file', type=str, help='קובץ בודד')
    args = parser.parse_args()

    if args.folder:
        folder = Path(args.folder)
        if not folder.is_dir():
            parser.error(f'התיקייה לא נמצאה: {folder}')
        ingest_folder(folder)
    else:
        path = Path(args.file)
        if not path.is_file():
            parser.error(f'הקובץ לא נמצא: {path}')
        ingest_path(path)


if __name__ == '__main__':
    main()
