# Menu Dish Image Processing Guide

## Standard Processing Pipeline

Every menu dish image must go through this automated pipeline to ensure consistent, beautiful display on the website.

## Quick Start

When you have a new dish photo to add to the menu:

```bash
python process_new_menu_image.py static/uploads/your_new_dish.jpg
```

This will create: `static/uploads/your_new_dish_processed.png`

## What Happens Automatically

### Step 1: AI Background Removal
- Uses advanced U2-Net model to remove backgrounds
- Creates clean transparent PNG
- Preserves all dish details perfectly

### Step 2: Crop to Dish Only
- Removes all extra transparent space
- Crops tightly to just the dish object
- Adds small 10px margin for breathing room

### Step 3: Optimize & Format
- Square format with dish centered
- PNG with RGBA transparency
- Optimized compression (~80-110KB per image)
- Result: Dish fills 85-98% of frame

## Display Specifications

### Desktop
- Container: 450px height with black gradient background
- Padding: 0.5rem (minimal)
- Image: Fills almost entire container

### Mobile
- Container: 350px height with black gradient background
- Padding: 0.5rem (minimal)
- Image: Fills almost entire container

### Background
- Elegant black gradient: `linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #2a2a2a 100%)`
- Makes dishes pop with vibrant colors

## Examples

### Process single image:
```bash
python process_new_menu_image.py static/uploads/sushi_roll.jpg
# Creates: static/uploads/sushi_roll_processed.png
```

### Process with custom output name:
```bash
python process_new_menu_image.py static/uploads/ramen.jpg static/uploads/menu_ramen_final.png
# Creates: static/uploads/menu_ramen_final.png
```

## Requirements

- Python 3.11+
- rembg library (AI background removal)
- PIL/Pillow (image processing)
- numpy (image manipulation)

All requirements are already installed in this project.

## Tips for Best Results

1. **Good Input Photos:**
   - High resolution (min 800px)
   - Well-lit dish
   - Clean background
   - Dish centered in frame

2. **After Processing:**
   - Upload the `_processed.png` file to the menu in admin
   - Original dish will be large and clear for customers
   - Transparent background shows elegant gradient

3. **File Naming:**
   - Use descriptive names (e.g., `teriyaki_chicken.jpg`)
   - Output will be `teriyaki_chicken_processed.png`
   - Keep organized in `static/uploads/`

## Support

For issues or questions about the image processing pipeline, check:
- `process_new_menu_image.py` - Main processing script
- `replit.md` - Full technical documentation
- CSS: `static/css/public.css` - Display specifications (line ~3403)
