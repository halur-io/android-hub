#!/usr/bin/env python3
"""
Optimize menu PNG images to ideal dimensions
Square format 660x660px for perfect retina display
"""

from PIL import Image
import os
from database import db
from models import MenuItem
from app import app

TARGET_SIZE = 660  # 660x660 for retina displays (3x the 220px display height)

def resize_png_optimal(input_path, output_path):
    """
    Resize PNG to optimal square dimensions while preserving transparency
    """
    try:
        img = Image.open(input_path)
        
        # Ensure RGBA mode for transparency
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Create square canvas
        canvas = Image.new('RGBA', (TARGET_SIZE, TARGET_SIZE), (0, 0, 0, 0))
        
        # Calculate scaling to fit the dish centered
        img.thumbnail((TARGET_SIZE, TARGET_SIZE), Image.Resampling.LANCZOS)
        
        # Center the image on the canvas
        x = (TARGET_SIZE - img.width) // 2
        y = (TARGET_SIZE - img.height) // 2
        canvas.paste(img, (x, y), img)
        
        # Save optimized PNG
        canvas.save(output_path, 'PNG', optimize=True, compression_level=6)
        
        original_size = os.path.getsize(input_path)
        new_size = os.path.getsize(output_path)
        
        print(f"  ✓ Optimized to {TARGET_SIZE}x{TARGET_SIZE}px")
        print(f"  Size: {original_size/1024:.1f}KB → {new_size/1024:.1f}KB")
        
        return output_path
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

def optimize_all_menu_pngs():
    """Optimize all menu PNG images to ideal dimensions"""
    print("=" * 70)
    print(f"OPTIMIZING MENU PNGs TO {TARGET_SIZE}x{TARGET_SIZE}px")
    print("Perfect for Retina Displays!")
    print("=" * 70)
    
    with app.app_context():
        menu_items = MenuItem.query.filter(
            MenuItem.image_path.isnot(None), 
            MenuItem.image_path != ''
        ).all()
        
        if not menu_items:
            print("\nNo menu items found!")
            return
        
        print(f"\nProcessing {len(menu_items)} menu items\n")
        
        processed = 0
        
        for item in menu_items:
            image_path = item.image_path.lstrip('/')
            
            if not os.path.exists(image_path):
                print(f"File not found: {image_path}")
                continue
            
            # Only process PNG files
            if not image_path.endswith('.png'):
                print(f"Skipping non-PNG: {os.path.basename(image_path)}")
                continue
            
            filename = os.path.basename(image_path)
            print(f"\n{filename}")
            
            # Create optimized version
            base_name = os.path.splitext(image_path)[0]
            # Remove _nobg suffix if present, add _optimized
            if '_nobg' in base_name:
                base_name = base_name.replace('_nobg', '')
            output_path = base_name + '_optimized.png'
            
            # Resize and optimize
            result = resize_png_optimal(image_path, output_path)
            
            if result:
                # Update database
                item.image_path = '/' + output_path
                processed += 1
                print(f"  Database updated: {os.path.basename(output_path)}")
        
        if processed > 0:
            db.session.commit()
        
        print("\n" + "=" * 70)
        print(f"COMPLETE: {processed} images optimized to {TARGET_SIZE}x{TARGET_SIZE}px")
        print("=" * 70)

if __name__ == '__main__':
    optimize_all_menu_pngs()
