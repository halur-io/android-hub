import os
import math
from PIL import Image, ImageDraw, ImageFilter, ExifTags
import numpy as np

UPLOAD_FOLDER = 'static/uploads'
CARD_SIZE = 500
HERO_MAX = 1200
TARGET_MARGIN_RATIO = 0.08


def create_dark_glaze_background(size):
    w, h = size, size
    img = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    cx, cy = w * 0.45, h * 0.35
    max_radius = int(math.sqrt(w**2 + h**2) * 0.7)

    for r in range(max_radius, 0, -1):
        t = r / max_radius
        base_r = int(10 + 22 * (1 - t))
        base_g = int(10 + 18 * (1 - t))
        base_b = int(12 + 20 * (1 - t))
        gloss = max(0, 1 - t * 1.8)
        base_r = min(255, int(base_r + 40 * gloss))
        base_g = min(255, int(base_g + 35 * gloss))
        base_b = min(255, int(base_b + 38 * gloss))
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=(base_r, base_g, base_b, 255)
        )

    edge_overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    edge_draw = ImageDraw.Draw(edge_overlay)
    for i in range(int(w * 0.15)):
        alpha = int(60 * (1 - i / (w * 0.15)))
        edge_draw.rectangle([i, 0, i, h], fill=(0, 0, 0, alpha))
        edge_draw.rectangle([w - 1 - i, 0, w - 1 - i, h], fill=(0, 0, 0, alpha))
        edge_draw.rectangle([0, i, w, i], fill=(0, 0, 0, alpha))
        edge_draw.rectangle([0, h - 1 - i, w, h - 1 - i], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img, edge_overlay)

    return img


def fix_exif_orientation(img):
    try:
        if hasattr(img, '_getexif') and img._getexif():
            exif = img._getexif()
            if exif:
                orientation_key = None
                for key in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[key] == 'Orientation':
                        orientation_key = key
                        break
                if orientation_key and orientation_key in exif:
                    orientation = exif[orientation_key]
                    if orientation == 3:
                        img = img.rotate(180, expand=True)
                    elif orientation == 6:
                        img = img.rotate(270, expand=True)
                    elif orientation == 8:
                        img = img.rotate(90, expand=True)
    except Exception:
        pass
    return img


def remove_background(img):
    from rembg import remove
    import io
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    output_data = remove(buf.read())
    return Image.open(io.BytesIO(output_data)).convert('RGBA')


def auto_crop_and_center(img, target_size):
    data = np.array(img)
    alpha = data[:, :, 3]
    rows = np.any(alpha > 10, axis=1)
    cols = np.any(alpha > 10, axis=0)

    if not rows.any() or not cols.any():
        return img.resize((target_size, target_size), Image.Resampling.LANCZOS)

    row_min, row_max = np.where(rows)[0][[0, -1]]
    col_min, col_max = np.where(cols)[0][[0, -1]]

    cropped = img.crop((col_min, row_min, col_max + 1, row_max + 1))

    margin = int(target_size * TARGET_MARGIN_RATIO)
    available = target_size - 2 * margin
    cw, ch = cropped.size
    scale = min(available / cw, available / ch)
    new_w = int(cw * scale)
    new_h = int(ch * scale)
    cropped = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)

    square = Image.new('RGBA', (target_size, target_size), (0, 0, 0, 0))
    x = (target_size - new_w) // 2
    y = (target_size - new_h) // 2
    square.paste(cropped, (x, y), cropped)

    return square


def composite_on_glaze(dish_rgba, target_size):
    bg = create_dark_glaze_background(target_size)
    bg.paste(dish_rgba, (0, 0), dish_rgba)
    return bg.convert('RGB')


def process_dish_image(input_path, output_dir=None, base_name=None, progress_callback=None):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    if output_dir is None:
        output_dir = os.path.dirname(input_path) or UPLOAD_FOLDER
    os.makedirs(output_dir, exist_ok=True)

    if base_name is None:
        base_name = os.path.splitext(os.path.basename(input_path))[0]

    def report(step, pct):
        if progress_callback:
            progress_callback(step, pct)

    report('opening', 5)
    img = Image.open(input_path)
    img = fix_exif_orientation(img)

    if max(img.size) > 2000:
        ratio = 2000 / max(img.size)
        img = img.resize((int(img.size[0] * ratio), int(img.size[1] * ratio)), Image.Resampling.LANCZOS)

    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGB')

    report('removing_bg', 20)
    dish_rgba = remove_background(img)

    report('cropping', 60)
    card_dish = auto_crop_and_center(dish_rgba, CARD_SIZE)
    hero_dish = auto_crop_and_center(dish_rgba, HERO_MAX)

    report('compositing', 75)
    card_final = composite_on_glaze(card_dish, CARD_SIZE)
    hero_final = composite_on_glaze(hero_dish, HERO_MAX)

    report('saving', 90)
    card_path = os.path.join(output_dir, f"{base_name}_card.jpg")
    hero_path = os.path.join(output_dir, f"{base_name}_hero.jpg")

    card_final.save(card_path, 'JPEG', quality=82, optimize=True)
    hero_final.save(hero_path, 'JPEG', quality=85, optimize=True)

    card_kb = os.path.getsize(card_path) / 1024
    hero_kb = os.path.getsize(hero_path) / 1024

    report('done', 100)

    return {
        'card_path': card_path,
        'hero_path': hero_path,
        'card_size_kb': round(card_kb, 1),
        'hero_size_kb': round(hero_kb, 1),
    }
