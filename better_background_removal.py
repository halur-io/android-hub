#!/usr/bin/env python3
"""
Better background removal for menu dish images
Uses smarter color-based detection and edge smoothing
"""

from PIL import Image, ImageFilter
import numpy as np
import os
from database import db
from models import MenuItem
from app import app

def smart_background_removal(input_path, output_path):
    """
    Smart background removal with edge smoothing
    Removes black/dark backgrounds while preserving dish details
    """
    try:
        # Open image
        img = Image.open(input_path).convert('RGBA')
        data = np.array(img)
        
        # Separate channels
        r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]
        
        # Calculate luminosity (brightness)
        luminosity = 0.299 * r + 0.587 * g + 0.114 * b
        
        # Find very dark pixels (true black background)
        very_dark = luminosity < 30
        
        # Find dark pixels (shadow/background)
        dark = luminosity < 60
        
        # Find the edges of the main subject
        # Pixels that are dark but have bright neighbors are likely edges
        from scipy import ndimage
        
        # Apply edge detection
        edges = ndimage.sobel(luminosity)
        edge_mask = edges > 20
        
        # Create alpha channel
        new_alpha = np.ones_like(a, dtype=np.uint8) * 255
        
        # Make very dark areas completely transparent
        new_alpha[very_dark] = 0
        
        # Make dark areas partially transparent, but preserve edges
        dark_but_not_edge = dark & ~edge_mask
        new_alpha[dark_but_not_edge] = np.minimum(new_alpha[dark_but_not_edge], 50)
        
        # Apply the new alpha channel
        data[:, :, 3] = new_alpha
        
        # Convert back to image
        result = Image.fromarray(data, 'RGBA')
        
        # Apply slight blur to alpha channel to smooth edges
        # Split channels
        r_ch, g_ch, b_ch, a_ch = result.split()
        
        # Blur alpha for smooth edges
        a_ch = a_ch.filter(ImageFilter.GaussianBlur(radius=1))
        
        # Merge back
        result = Image.merge('RGBA', (r_ch, g_ch, b_ch, a_ch))
        
        # Save as PNG
        result.save(output_path, 'PNG', optimize=True)
        
        original_size = os.path.getsize(input_path)
        new_size = os.path.getsize(output_path)
        
        print(f"  ✓ Smart background removed")
        print(f"  Size: {original_size/1024:.0f}KB → {new_size/1024:.0f}KB")
        
        return output_path
    except ImportError:
        # If scipy not available, use simpler method
        print("  Using basic method (scipy not available)")
        return simple_background_removal(input_path, output_path)
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

def simple_background_removal(input_path, output_path):
    """
    Simpler background removal without scipy
    Just removes very dark pixels
    """
    try:
        img = Image.open(input_path).convert('RGBA')
        data = np.array(img)
        
        r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]
        
        # Only remove truly black pixels
        black_mask = (r < 40) & (g < 40) & (b < 40)
        
        # Set to transparent
        data[:, :, 3][black_mask] = 0
        
        result = Image.fromarray(data, 'RGBA')
        result.save(output_path, 'PNG', optimize=True)
        
        print(f"  ✓ Basic background removed")
        return output_path
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

def process_all_menu_images():
    """Process all menu images with better background removal"""
    print("=" * 70)
    print("BETTER BACKGROUND REMOVAL FOR MENU IMAGES")
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
        
        for item in menu_items:
            image_path = item.image_path.lstrip('/')
            
            # Check for file with extensions
            if not os.path.exists(image_path):
                for ext in ['.jpg', '.JPG', '.jpeg', '.png', '.PNG']:
                    test_path = image_path + ext if not image_path.endswith(ext) else image_path.replace(ext, '') + ext
                    if os.path.exists(test_path):
                        image_path = test_path
                        break
            
            # Try original file before transparent version
            if '_transparent' in image_path:
                original_path = image_path.replace('_transparent', '')
                if os.path.exists(original_path):
                    image_path = original_path
            
            if not os.path.exists(image_path):
                print(f"File not found: {image_path}")
                continue
            
            filename = os.path.basename(image_path)
            print(f"\n{filename}")
            
            # Output as new transparent version
            base_name = os.path.splitext(image_path)[0]
            if '_transparent' in base_name:
                output_path = base_name + '.png'
            else:
                output_path = base_name + '_clean.png'
            
            # Process
            result = smart_background_removal(image_path, output_path)
            
            if result:
                # Update database
                item.image_path = '/' + output_path
                print(f"  Updated: {os.path.basename(output_path)}")
        
        db.session.commit()
        print("\n" + "=" * 70)
        print("COMPLETE!")
        print("=" * 70)

if __name__ == '__main__':
    process_all_menu_images()
