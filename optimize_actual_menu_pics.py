#!/usr/bin/env python3
"""
Optimize the actual menu pictures from database
"""

import os
from PIL import Image
from database import db
from models import MenuItem
from app import app

def optimize_menu_image(filepath):
    """Shrink menu image to 400px width, 55% quality for super fast loading"""
    try:
        # Handle files without extension
        if not os.path.exists(filepath):
            # Try adding common extensions
            for ext in ['.JPG', '.jpg', '.jpeg', '.png', '.PNG']:
                test_path = filepath + ext
                if os.path.exists(test_path):
                    filepath = test_path
                    break
        
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return None
        
        original_size = os.path.getsize(filepath)
        img = Image.open(filepath)
        filename = os.path.basename(filepath)
        
        print(f"\n{filename}")
        print(f"  Before: {img.width}x{img.height}, {original_size/1024:.0f}KB")
        
        # Super aggressive resize for menu: 400px max width
        if img.width > 400:
            ratio = 400 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((400, new_height), Image.Resampling.LANCZOS)
        
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
        
        # Always save as .jpg
        new_path = os.path.splitext(filepath)[0] + '.jpg'
        
        # Super aggressive compression: 55% quality
        img.save(new_path, 'JPEG', quality=55, optimize=True)
        
        new_size = os.path.getsize(new_path)
        
        print(f"  After: {img.width}x{img.height}, {new_size/1024:.0f}KB")
        print(f"  ✓ {((original_size - new_size) / original_size * 100):.0f}% smaller!")
        
        # Update database if path changed
        old_db_path = filepath.replace('static', '/static')
        new_db_path = new_path.replace('static', '/static')
        
        if old_db_path != new_db_path:
            with app.app_context():
                items = MenuItem.query.filter_by(image_path=old_db_path).all()
                if items:
                    for item in items:
                        item.image_path = new_db_path
                    db.session.commit()
                    print(f"  Database updated: {len(items)} menu item(s)")
        
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
print("OPTIMIZING MENU PICTURES FOR FAST LOADING")
print("=" * 70)

# Get menu images from database
with app.app_context():
    menu_items = MenuItem.query.filter(MenuItem.image_path.isnot(None), MenuItem.image_path != '').all()
    
    if not menu_items:
        print("\nNo menu items with images found!")
    else:
        print(f"\nFound {len(menu_items)} menu items with images")
        
        total_before = 0
        total_after = 0
        optimized = 0
        
        for item in menu_items:
            # Convert /static/uploads/... to static/uploads/...
            filepath = item.image_path.lstrip('/')
            
            result = optimize_menu_image(filepath)
            if result:
                total_before += result[0]
                total_after += result[1]
                optimized += 1
        
        if optimized > 0:
            print("\n" + "=" * 70)
            print(f"Optimized: {optimized} menu pictures")
            print(f"Before: {total_before/1024:.0f}KB")
            print(f"After: {total_after/1024:.0f}KB")
            print(f"SAVED: {(total_before - total_after)/1024:.0f}KB ({((total_before - total_after) / total_before * 100):.0f}% reduction)")
            print("=" * 70)
