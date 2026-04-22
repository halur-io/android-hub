#!/usr/bin/env python3
"""
DISH PHOTO PROCESSOR CLI
=========================
Process dish photos: remove background + dark glaze compositing.

Usage:
  Single:  python3 process_dish_photo.py <image_path> [output_dir]
  Batch:   python3 process_dish_photo.py --batch [--update-db]

The --batch flag processes all menu_*.jpg/png in static/uploads/ that
don't already have a _card.jpg counterpart.

The --update-db flag also updates MenuItem.image_path in the database.
"""

import os
import sys
import glob
import time

def process_single(input_path, output_dir=None):
    from image_processing import process_dish_image

    if not os.path.exists(input_path):
        print(f"ERROR: File not found: {input_path}")
        return None

    base = os.path.splitext(os.path.basename(input_path))[0]
    if base.endswith('_raw'):
        base = base[:-4]
    if base.endswith('_card') or base.endswith('_hero'):
        print(f"SKIP: {input_path} is already a processed file")
        return None

    if output_dir is None:
        output_dir = os.path.dirname(input_path) or 'static/uploads'

    def progress(step, pct):
        labels = {
            'opening': 'Opening image',
            'removing_bg': 'Removing background (AI)',
            'cropping': 'Cropping & centering',
            'compositing': 'Adding dark glaze background',
            'saving': 'Optimizing & saving',
            'done': 'Complete',
        }
        print(f'  [{pct:3d}%] {labels.get(step, step)}')

    print(f'\nProcessing: {os.path.basename(input_path)}')
    print('=' * 50)

    t = time.time()
    result = process_dish_image(input_path, output_dir=output_dir, base_name=base, progress_callback=progress)
    elapsed = time.time() - t

    print(f'  Card: {result["card_path"]} ({result["card_size_kb"]}KB)')
    print(f'  Hero: {result["hero_path"]} ({result["hero_size_kb"]}KB)')
    print(f'  Time: {elapsed:.1f}s')
    print('=' * 50)
    return result


def batch_process(update_db=False):
    upload_dir = 'static/uploads'
    patterns = [
        os.path.join(upload_dir, 'menu_*.jpg'),
        os.path.join(upload_dir, 'menu_*.jpeg'),
        os.path.join(upload_dir, 'menu_*.png'),
        os.path.join(upload_dir, 'menu_*.JPG'),
    ]

    all_files = []
    for p in patterns:
        all_files.extend(glob.glob(p))

    to_process = []
    for f in all_files:
        base = os.path.splitext(os.path.basename(f))[0]
        if base.endswith(('_card', '_hero', '_raw', '_nobg', '_cropped', '_optimized', '_processed')):
            continue
        card_path = os.path.join(upload_dir, base + '_card.jpg')
        if os.path.exists(card_path):
            continue
        to_process.append(f)

    if not to_process:
        print('No unprocessed menu images found.')
        return

    print(f'Found {len(to_process)} images to process\n')

    success = 0
    failed = 0
    results = []

    for i, filepath in enumerate(to_process, 1):
        print(f'\n[{i}/{len(to_process)}]')
        try:
            result = process_single(filepath)
            if result:
                success += 1
                results.append((filepath, result))
            else:
                failed += 1
        except Exception as e:
            print(f'  ERROR: {e}')
            failed += 1

    print(f'\n{"=" * 50}')
    print(f'BATCH COMPLETE: {success} processed, {failed} failed')

    if update_db and results:
        print('\nUpdating database...')
        try:
            from app import app
            from database import db
            from models import MenuItem
            with app.app_context():
                updated = 0
                for filepath, result in results:
                    old_path = f'/static/uploads/{os.path.basename(filepath)}'
                    card_rel = f'/static/uploads/{os.path.basename(result["card_path"])}'
                    hero_rel = f'/static/uploads/{os.path.basename(result["hero_path"])}'
                    items = MenuItem.query.filter_by(image_path=old_path).all()
                    for item in items:
                        item.image_path = card_rel
                        item.image_hero_path = hero_rel
                        updated += 1
                db.session.commit()
                print(f'Updated {updated} menu item(s) in database')
        except Exception as e:
            print(f'Database update failed: {e}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == '--batch':
        update_db = '--update-db' in sys.argv
        batch_process(update_db=update_db)
    else:
        input_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        result = process_single(input_path, output_dir)
        if result:
            print(f'\nSuccess!')
        else:
            print('\nFailed')
            sys.exit(1)
