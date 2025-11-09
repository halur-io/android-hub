#!/usr/bin/env python3
"""
Script to aggressively optimize all existing menu images
Resizes to max 500px width, 65% quality for fast loading (target: 20-50KB per image)
Updates database references when changing file extensions
"""

import os
from PIL import Image
import glob
from database import db
from models import MenuItem
from app import app

UPLOAD_FOLDER = 'static/uploads'

def optimize_menu_image(filepath):
    """Aggressively optimize a menu image to reduce file size and update database references"""
    try:
        # Get original file size
        original_size = os.path.getsize(filepath)
        original_filename = os.path.basename(filepath)
        
        # Open image
        img = Image.open(filepath)
        print(f"\nProcessing: {original_filename}")
        print(f"  Original: {img.width}x{img.height}, {original_size/1024:.1f}KB")
        
        # Resize to max 500px width
        if img.width > 500:
            ratio = 500 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((500, new_height), Image.Resampling.LANCZOS)
            print(f"  Resized to: {img.width}x{img.height}")
        
        # Convert to RGB (remove transparency)
        if img.mode == 'RGBA':
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img
            print(f"  Converted RGBA to RGB")
        elif img.mode != 'RGB':
            img = img.convert('RGB')
            print(f"  Converted {img.mode} to RGB")
        
        # Change extension to .jpg since we're saving as JPEG
        filepath_base = os.path.splitext(filepath)[0]
        new_filepath = filepath_base + '.jpg'
        new_filename = os.path.basename(new_filepath)
        
        # Check if extension changed
        extension_changed = (filepath != new_filepath)
        
        # Create backup of original first
        backup_path = filepath + '.backup'
        if not os.path.exists(backup_path):
            os.rename(filepath, backup_path)
        
        # Save as JPEG with correct .jpg extension
        img.save(new_filepath, 'JPEG', quality=65, optimize=True)
        
        # Get new file size
        new_size = os.path.getsize(new_filepath)
        reduction = ((original_size - new_size) / original_size) * 100
        
        print(f"  Optimized: {new_size/1024:.1f}KB (reduced by {reduction:.1f}%)")
        print(f"  Saved as: {new_filename}")
        
        # Update database if extension changed
        if extension_changed:
            old_path = f'/static/uploads/{original_filename}'
            new_path = f'/static/uploads/{new_filename}'
            
            with app.app_context():
                items = MenuItem.query.filter_by(image_path=old_path).all()
                if items:
                    for item in items:
                        item.image_path = new_path
                    db.session.commit()
                    print(f"  Updated {len(items)} database record(s)")
        
        # Remove backup if successful
        if os.path.exists(backup_path):
            os.remove(backup_path)
        
        return (original_filename, new_filename, extension_changed)
    except Exception as e:
        print(f"  ERROR: {e}")
        # Restore from backup if it exists
        backup_path = filepath + '.backup'
        if os.path.exists(backup_path):
            os.rename(backup_path, filepath)
        return None

def main():
    print("=" * 70)
    print("AGGRESSIVE MENU IMAGE OPTIMIZATION")
    print("Target: 500px max width, 65% quality, ~20-50KB per image")
    print("=" * 70)
    
    # Find all menu images
    menu_images = glob.glob(os.path.join(UPLOAD_FOLDER, 'menu_*.jpg'))
    menu_images += glob.glob(os.path.join(UPLOAD_FOLDER, 'menu_*.jpeg'))
    menu_images += glob.glob(os.path.join(UPLOAD_FOLDER, 'menu_*.png'))
    menu_images += glob.glob(os.path.join(UPLOAD_FOLDER, 'menu_*.gif'))
    
    if not menu_images:
        print("\nNo menu images found in static/uploads/")
        return
    
    print(f"\nFound {len(menu_images)} menu images to optimize\n")
    
    successful = 0
    failed = 0
    renamed_files = []
    
    for image_path in menu_images:
        result = optimize_menu_image(image_path)
        if result:
            successful += 1
            if result[2]:  # extension_changed
                renamed_files.append(result)
        else:
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"COMPLETE: {successful} optimized, {failed} failed")
    if renamed_files:
        print(f"\nRenamed files (old → new):")
        for old, new, _ in renamed_files:
            print(f"  {old} → {new}")
    print("=" * 70)

if __name__ == '__main__':
    main()
