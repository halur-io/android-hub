#!/usr/bin/env python3
"""
Optimize ONLY menu pictures - nothing else!
Aggressive compression for fast loading menu images
"""

import os
from PIL import Image
import glob

def optimize_menu_picture(filepath):
    """Shrink menu picture to 500px, 60% quality"""
    try:
        original_size = os.path.getsize(filepath)
        
        img = Image.open(filepath)
        filename = os.path.basename(filepath)
        print(f"\n{filename}")
        print(f"  Before: {img.width}x{img.height}, {original_size/1024:.0f}KB")
        
        # Resize to max 500px width for menu items
        if img.width > 500:
            ratio = 500 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((500, new_height), Image.Resampling.LANCZOS)
        
        # Convert to RGB
        if img.mode == 'RGBA':
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Backup
        backup = filepath + '.backup'
        if not os.path.exists(backup):
            os.rename(filepath, backup)
        
        # Save with 60% quality for menu images
        new_path = os.path.splitext(filepath)[0] + '.jpg'
        img.save(new_path, 'JPEG', quality=60, optimize=True)
        
        new_size = os.path.getsize(new_path)
        reduction = ((original_size - new_size) / original_size) * 100
        
        print(f"  After: {img.width}x{img.height}, {new_size/1024:.0f}KB")
        print(f"  ✓ {reduction:.0f}% smaller")
        
        # Remove backup
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
print("OPTIMIZING MENU PICTURES ONLY")
print("=" * 70)

# Find ONLY menu images
menu_images = glob.glob('static/uploads/menu_*.jpg')
menu_images += glob.glob('static/uploads/menu_*.jpeg')
menu_images += glob.glob('static/uploads/menu_*.png')
menu_images += glob.glob('static/uploads/menu_*.gif')

if not menu_images:
    print("\nNo menu images found!")
    print("Menu images should be named: menu_*.jpg/png/gif")
else:
    print(f"\nFound {len(menu_images)} menu pictures")
    
    total_before = 0
    total_after = 0
    
    for img_path in menu_images:
        result = optimize_menu_picture(img_path)
        if result:
            total_before += result[0]
            total_after += result[1]
    
    if total_before > 0:
        print("\n" + "=" * 70)
        print(f"Before: {total_before/1024:.0f}KB")
        print(f"After: {total_after/1024:.0f}KB")
        print(f"Saved: {(total_before - total_after)/1024:.0f}KB")
        print("=" * 70)
