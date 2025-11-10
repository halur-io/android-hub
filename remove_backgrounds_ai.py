#!/usr/bin/env python3
"""
AI-powered background removal for menu dish images
Uses rembg library with U2-Net model
"""

from rembg import remove
from PIL import Image
import os
from database import db
from models import MenuItem
from app import app

def remove_background_ai(input_path, output_path):
    """
    Remove background using AI (rembg)
    Much better than simple color-based removal
    """
    try:
        print(f"  Processing with AI...")
        
        # Open input image
        with open(input_path, 'rb') as input_file:
            input_data = input_file.read()
        
        # Remove background using AI
        output_data = remove(input_data)
        
        # Save as PNG (supports transparency)
        with open(output_path, 'wb') as output_file:
            output_file.write(output_data)
        
        original_size = os.path.getsize(input_path)
        new_size = os.path.getsize(output_path)
        
        print(f"  ✓ Background removed with AI")
        print(f"  Size: {original_size/1024:.0f}KB → {new_size/1024:.0f}KB")
        
        return output_path
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

def process_menu_images():
    """Process all menu images with AI background removal"""
    print("=" * 70)
    print("AI-POWERED BACKGROUND REMOVAL FOR MENU DISHES")
    print("=" * 70)
    
    with app.app_context():
        menu_items = MenuItem.query.filter(
            MenuItem.image_path.isnot(None), 
            MenuItem.image_path != ''
        ).all()
        
        if not menu_items:
            print("\nNo menu items with images found!")
            return
        
        print(f"\nFound {len(menu_items)} menu items with images")
        print("Using AI model (this may take a moment)...\n")
        
        processed = 0
        failed = 0
        
        for item in menu_items:
            # Convert /static/uploads/... to static/uploads/...
            image_path = item.image_path.lstrip('/')
            
            if not os.path.exists(image_path):
                print(f"File not found: {image_path}")
                failed += 1
                continue
            
            filename = os.path.basename(image_path)
            print(f"\n{filename}")
            
            # Create output path as PNG
            base_name = os.path.splitext(image_path)[0]
            output_path = base_name + '_nobg.png'
            
            # Process image with AI
            result = remove_background_ai(image_path, output_path)
            
            if result:
                # Update database to point to new background-free image
                item.image_path = '/' + output_path
                processed += 1
                print(f"  Database updated: {os.path.basename(output_path)}")
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
