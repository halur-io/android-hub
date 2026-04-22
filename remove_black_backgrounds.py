#!/usr/bin/env python3
"""
Remove black/dark backgrounds from menu dish images
Makes dark backgrounds transparent for a clean look
"""

from PIL import Image
import numpy as np
import os
from database import db
from models import MenuItem
from app import app

def remove_black_background(input_path, output_path):
    """Remove black/dark background and make transparent"""
    try:
        # Open image
        img = Image.open(input_path)
        
        # Convert to RGBA for transparency
        img = img.convert('RGBA')
        
        # Convert to numpy array
        data = np.array(img)
        
        # Get RGB channels
        r, g, b, a = data.T
        
        # Find dark areas (black/very dark backgrounds)
        # Pixels where all RGB values are below threshold (e.g., 50)
        dark_threshold = 50
        dark_areas = (r < dark_threshold) & (g < dark_threshold) & (b < dark_threshold)
        
        # Also find near-black areas (slightly lighter)
        medium_dark_threshold = 80
        medium_dark_areas = (r < medium_dark_threshold) & (g < medium_dark_threshold) & (b < medium_dark_threshold)
        
        # Set alpha to 0 (transparent) for dark areas
        data[..., 3][dark_areas.T] = 0
        
        # Set partial transparency for medium dark areas
        data[..., 3][medium_dark_areas.T] = np.minimum(data[..., 3][medium_dark_areas.T], 100)
        
        # Convert back to image
        result = Image.fromarray(data)
        
        # Save as PNG to preserve transparency
        result.save(output_path, 'PNG', optimize=True)
        
        original_size = os.path.getsize(input_path)
        new_size = os.path.getsize(output_path)
        
        print(f"  ✓ Background removed")
        print(f"  Size: {original_size/1024:.0f}KB → {new_size/1024:.0f}KB")
        
        return output_path
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

def process_menu_images():
    """Process all menu images to remove black backgrounds"""
    print("=" * 70)
    print("REMOVING BLACK BACKGROUNDS FROM MENU DISH IMAGES")
    print("=" * 70)
    
    with app.app_context():
        # Get all menu items with images
        menu_items = MenuItem.query.filter(
            MenuItem.image_path.isnot(None), 
            MenuItem.image_path != ''
        ).all()
        
        if not menu_items:
            print("\nNo menu items with images found!")
            return
        
        print(f"\nFound {len(menu_items)} menu items with images\n")
        
        processed = 0
        failed = 0
        
        for item in menu_items:
            # Convert /static/uploads/... to static/uploads/...
            image_path = item.image_path.lstrip('/')
            
            # Handle files without extension
            if not os.path.exists(image_path):
                for ext in ['.jpg', '.JPG', '.jpeg', '.png', '.PNG']:
                    test_path = image_path + ext
                    if os.path.exists(test_path):
                        image_path = test_path
                        break
            
            if not os.path.exists(image_path):
                print(f"File not found: {image_path}")
                failed += 1
                continue
            
            filename = os.path.basename(image_path)
            print(f"\n{filename}")
            
            # Create output path as PNG
            output_path = os.path.splitext(image_path)[0] + '_transparent.png'
            
            # Process image
            result = remove_black_background(image_path, output_path)
            
            if result:
                # Update database to point to new transparent image
                old_db_path = item.image_path
                new_db_path = '/' + output_path
                
                item.image_path = new_db_path
                processed += 1
                
                print(f"  Database updated: {os.path.basename(new_db_path)}")
            else:
                failed += 1
        
        # Commit all changes
        if processed > 0:
            db.session.commit()
        
        print("\n" + "=" * 70)
        print(f"COMPLETE: {processed} images processed, {failed} failed")
        print("=" * 70)

if __name__ == '__main__':
    process_menu_images()
