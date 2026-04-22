#!/usr/bin/env python3
"""
Resize all existing gallery images for better performance
This script will resize images to max 1920px width and 85% quality
"""

import os
from PIL import Image
import glob

UPLOAD_FOLDER = 'static/uploads'

def resize_image(filepath):
    """Resize a single image"""
    try:
        print(f"Processing: {os.path.basename(filepath)}")
        
        # Get original file size
        original_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
        
        # Open image
        img = Image.open(filepath)
        original_width = img.width
        
        # Convert RGBA to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Resize if too large
        max_width = 1920
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Save with optimization
        img.save(filepath, 'JPEG', quality=85, optimize=True)
        
        # Get new file size
        new_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
        savings = ((original_size - new_size) / original_size) * 100
        
        print(f"  ✓ {original_width}px → {img.width}px | {original_size:.1f}MB → {new_size:.1f}MB ({savings:.0f}% smaller)")
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False

def main():
    # Find all gallery images
    patterns = [
        os.path.join(UPLOAD_FOLDER, 'gallery_*.jpg'),
        os.path.join(UPLOAD_FOLDER, 'gallery_*.jpeg'),
        os.path.join(UPLOAD_FOLDER, 'gallery_*.png')
    ]
    
    images = []
    for pattern in patterns:
        images.extend(glob.glob(pattern))
    
    if not images:
        print("No gallery images found!")
        return
    
    print(f"\nFound {len(images)} gallery images to resize\n")
    print("=" * 60)
    
    success = 0
    failed = 0
    
    for filepath in sorted(images):
        if resize_image(filepath):
            success += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"\n✓ Successfully resized: {success}")
    if failed > 0:
        print(f"✗ Failed: {failed}")
    print("\nYour gallery is now optimized for fast loading! 🚀")

if __name__ == '__main__':
    main()
