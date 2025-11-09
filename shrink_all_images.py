#!/usr/bin/env python3
"""
AGGRESSIVE image optimization for ALL images
Shrinks everything to max 800px width, 70% quality for fast loading
"""

import os
from PIL import Image
import glob

def optimize_image(filepath, max_width=800, quality=70):
    """Aggressively shrink an image"""
    try:
        original_size = os.path.getsize(filepath)
        
        # Skip if already small enough
        if original_size < 100 * 1024:  # Skip if < 100KB
            return None
        
        img = Image.open(filepath)
        print(f"\n{os.path.basename(filepath)}")
        print(f"  Before: {img.width}x{img.height}, {original_size/1024:.0f}KB")
        
        # Resize if too wide
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to RGB
        if img.mode == 'RGBA':
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Backup original
        backup = filepath + '.backup'
        if not os.path.exists(backup):
            os.rename(filepath, backup)
        
        # Save optimized
        new_path = os.path.splitext(filepath)[0] + '.jpg'
        img.save(new_path, 'JPEG', quality=quality, optimize=True)
        
        new_size = os.path.getsize(new_path)
        reduction = ((original_size - new_size) / original_size) * 100
        
        print(f"  After: {img.width}x{img.height}, {new_size/1024:.0f}KB")
        print(f"  ✓ Reduced by {reduction:.0f}%")
        
        # Delete backup
        if os.path.exists(backup):
            os.remove(backup)
        
        return (original_size, new_size)
    except Exception as e:
        print(f"  ERROR: {e}")
        backup = filepath + '.backup'
        if os.path.exists(backup):
            os.rename(backup, filepath)
        return None

print("=" * 70)
print("SHRINKING ALL IMAGES - PLEASE WAIT")
print("=" * 70)

# Find all images
all_images = []
for folder in ['static/uploads', 'static/images']:
    all_images += glob.glob(f'{folder}/*.jpg')
    all_images += glob.glob(f'{folder}/*.jpeg')
    all_images += glob.glob(f'{folder}/*.png')
    all_images += glob.glob(f'{folder}/*.gif')

print(f"\nFound {len(all_images)} images to check")

total_before = 0
total_after = 0
optimized = 0

for img_path in all_images:
    result = optimize_image(img_path)
    if result:
        total_before += result[0]
        total_after += result[1]
        optimized += 1

print("\n" + "=" * 70)
print(f"DONE! Optimized {optimized} images")
if total_before > 0:
    total_reduction = ((total_before - total_after) / total_before) * 100
    print(f"Total: {total_before/1024/1024:.1f}MB → {total_after/1024/1024:.1f}MB")
    print(f"Saved: {(total_before - total_after)/1024/1024:.1f}MB ({total_reduction:.0f}% reduction)")
print("=" * 70)
