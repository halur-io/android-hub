#!/usr/bin/env python3
"""
STANDARD MENU IMAGE PROCESSOR
================================
Automated pipeline for all new menu dish images.
Run this script whenever you upload a new menu image.

Process:
1. AI background removal (rembg)
2. Crop to dish only (remove transparent space)
3. Optimize for web display

Result: Dish fills frame, transparent background, ready for black gradient display
"""

from rembg import remove
from PIL import Image
import numpy as np
import os
import sys

TARGET_MARGIN = 10  # Small margin around dish

def process_menu_image(input_path, output_path=None):
    """
    Complete processing pipeline for menu dish images
    """
    if not os.path.exists(input_path):
        print(f"ERROR: File not found: {input_path}")
        return None
    
    if output_path is None:
        base_name = os.path.splitext(input_path)[0]
        output_path = base_name + '_processed.png'
    
    print(f"Processing: {os.path.basename(input_path)}")
    print("=" * 60)
    
    # Step 1: Remove background with AI
    print("\n[1/3] Removing background with AI...")
    try:
        with open(input_path, 'rb') as f:
            input_data = f.read()
        
        output_data = remove(input_data)
        
        # Save to temp file
        temp_path = input_path + '.temp.png'
        with open(temp_path, 'wb') as f:
            f.write(output_data)
        
        print("  ✓ Background removed")
    except Exception as e:
        print(f"  ERROR: {e}")
        return None
    
    # Step 2: Crop to dish only
    print("\n[2/3] Cropping to dish only...")
    try:
        img = Image.open(temp_path)
        
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        data = np.array(img)
        alpha = data[:, :, 3]
        
        # Find non-transparent pixels
        rows = np.any(alpha > 10, axis=1)
        cols = np.any(alpha > 10, axis=0)
        
        # Get bounding box
        row_min, row_max = np.where(rows)[0][[0, -1]]
        col_min, col_max = np.where(cols)[0][[0, -1]]
        
        # Add margin
        row_min = max(0, row_min - TARGET_MARGIN)
        row_max = min(data.shape[0], row_max + TARGET_MARGIN)
        col_min = max(0, col_min - TARGET_MARGIN)
        col_max = min(data.shape[1], col_max + TARGET_MARGIN)
        
        # Crop to bounding box
        cropped = img.crop((col_min, row_min, col_max, row_max))
        
        width, height = cropped.size
        
        # Make square
        max_dim = max(width, height)
        square = Image.new('RGBA', (max_dim, max_dim), (0, 0, 0, 0))
        
        # Center the dish
        x = (max_dim - width) // 2
        y = (max_dim - height) // 2
        square.paste(cropped, (x, y), cropped)
        
        print(f"  ✓ Cropped to {max_dim}x{max_dim}px")
        print(f"  Dish fills {((width*height)/(max_dim*max_dim)*100):.0f}% of frame")
        
    except Exception as e:
        print(f"  ERROR: {e}")
        os.remove(temp_path)
        return None
    
    # Step 3: Optimize and save
    print("\n[3/3] Optimizing and saving...")
    try:
        square.save(output_path, 'PNG', optimize=True, compression_level=6)
        
        # Clean up temp file
        os.remove(temp_path)
        
        file_size = os.path.getsize(output_path) / 1024
        
        print(f"  ✓ Saved as: {os.path.basename(output_path)}")
        print(f"  File size: {file_size:.1f}KB")
        
    except Exception as e:
        print(f"  ERROR: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return None
    
    print("\n" + "=" * 60)
    print("✓ PROCESSING COMPLETE")
    print(f"Ready to upload: {output_path}")
    print("=" * 60)
    
    return output_path

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python process_new_menu_image.py <image_path> [output_path]")
        print("\nExample:")
        print("  python process_new_menu_image.py static/uploads/new_dish.jpg")
        print("  Output: static/uploads/new_dish_processed.png")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = process_menu_image(input_path, output_path)
    
    if result:
        print(f"\n✓ Success! Use this file for the menu: {result}")
    else:
        print("\n✗ Processing failed")
        sys.exit(1)
