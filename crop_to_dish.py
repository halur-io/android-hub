#!/usr/bin/env python3
"""
Crop menu images to just the dish object
Removes all transparent padding to make dishes fill the frame
"""

from PIL import Image
import numpy as np
import os
from database import db
from models import MenuItem
from app import app

def crop_to_object(input_path, output_path, margin=20):
    """
    Crop image to just the visible object (dish)
    Removes all transparent areas
    """
    try:
        img = Image.open(input_path)
        
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Convert to numpy array
        data = np.array(img)
        
        # Get alpha channel
        alpha = data[:, :, 3]
        
        # Find non-transparent pixels
        rows = np.any(alpha > 10, axis=1)
        cols = np.any(alpha > 10, axis=0)
        
        # Get bounding box
        row_min, row_max = np.where(rows)[0][[0, -1]]
        col_min, col_max = np.where(cols)[0][[0, -1]]
        
        # Add margin
        row_min = max(0, row_min - margin)
        row_max = min(data.shape[0], row_max + margin)
        col_min = max(0, col_min - margin)
        col_max = min(data.shape[1], col_max + margin)
        
        # Crop to bounding box
        cropped = img.crop((col_min, row_min, col_max, row_max))
        
        # Get dimensions
        width, height = cropped.size
        
        # Make square by adding transparent padding to shorter side
        max_dim = max(width, height)
        square = Image.new('RGBA', (max_dim, max_dim), (0, 0, 0, 0))
        
        # Center the cropped dish
        x = (max_dim - width) // 2
        y = (max_dim - height) // 2
        square.paste(cropped, (x, y), cropped)
        
        # Save
        square.save(output_path, 'PNG', optimize=True)
        
        original_size = os.path.getsize(input_path)
        new_size = os.path.getsize(output_path)
        
        print(f"  ✓ Cropped from {img.size[0]}x{img.size[1]} to {max_dim}x{max_dim}")
        print(f"  Dish now fills {((width*height)/(max_dim*max_dim)*100):.0f}% of image")
        print(f"  Size: {original_size/1024:.1f}KB → {new_size/1024:.1f}KB")
        
        return output_path
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

def process_all_images():
    """Crop all menu images to just the dish"""
    print("=" * 70)
    print("CROPPING IMAGES TO DISH ONLY (REMOVING TRANSPARENT SPACE)")
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
            
            if not image_path.endswith('.png'):
                print(f"Skipping non-PNG: {os.path.basename(image_path)}")
                continue
            
            filename = os.path.basename(image_path)
            print(f"\n{filename}")
            
            # Create cropped version
            base_name = os.path.splitext(image_path)[0]
            # Remove _optimized if present
            if '_optimized' in base_name:
                base_name = base_name.replace('_optimized', '')
            output_path = base_name + '_cropped.png'
            
            # Crop to dish
            result = crop_to_object(image_path, output_path, margin=10)
            
            if result:
                # Update database
                item.image_path = '/' + output_path
                processed += 1
                print(f"  Database updated: {os.path.basename(output_path)}")
        
        if processed > 0:
            db.session.commit()
        
        print("\n" + "=" * 70)
        print(f"COMPLETE: {processed} images cropped to dish only")
        print("Dishes now fill the frame!")
        print("=" * 70)

if __name__ == '__main__':
    process_all_images()
