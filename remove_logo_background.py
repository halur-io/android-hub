#!/usr/bin/env python3
"""
Remove white/light background from logo and make it transparent
"""

from PIL import Image
import numpy as np

def remove_background(input_path, output_path):
    """Remove white/light background from image"""
    try:
        # Open image
        img = Image.open(input_path)
        
        # Convert to RGBA if not already
        img = img.convert('RGBA')
        
        # Convert to numpy array for easier manipulation
        data = np.array(img)
        
        # Get RGB channels
        r, g, b, a = data.T
        
        # Find white/light areas (adjust threshold as needed)
        # This looks for pixels that are mostly white (RGB > 200)
        white_areas = (r > 200) & (g > 200) & (b > 200)
        
        # Set alpha to 0 (transparent) for white areas
        data[..., 3][white_areas.T] = 0
        
        # Convert back to image
        result = Image.fromarray(data)
        
        # Save as PNG with transparency
        result.save(output_path, 'PNG')
        
        print(f"✓ Background removed!")
        print(f"  Input: {input_path}")
        print(f"  Output: {output_path}")
        
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

# Process the logo
print("Removing logo background...")
print("=" * 50)

# Remove background from the database logo
success1 = remove_background(
    'static/uploads/sumo_logo_transparent.png',
    'static/uploads/sumo_logo_transparent.png'
)

# Also update the public logo if it exists
try:
    success2 = remove_background(
        'static/images/sumo-logo.png',
        'static/images/sumo-logo.png'
    )
except:
    success2 = False

print("=" * 50)
if success1 or success2:
    print("Logo background removed - now transparent!")
