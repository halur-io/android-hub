# How to Upload Dish Images - Simple Guide

## The Upload Interface is Now Fixed! ✓

You'll now see a **clear upload box** with:
- Large cloud upload icon
- Text: "לחץ לבחירת תמונה" (Click to select image)
- File confirmation when selected
- No more timeout errors!

## How to Upload a Dish Image

### Quick Steps:
1. Go to Admin → Menu Management → Edit a dish
2. Click the **upload box** (big blue cloud icon)
3. Choose your dish image
4. Click "עדכן מנה" (Update Dish)
5. Done! Image is uploaded

### Best Results - Two Options:

#### Option 1: Upload Already-Processed Images (Recommended)
If you have processed images ready:
1. Upload the `_processed.png` file directly
2. Image will display perfectly right away

#### Option 2: Process Images After Upload
If you upload raw photos:
1. Upload your original photo first
2. Note the filename (shown after upload)
3. Run processing script:
   ```bash
   python process_new_menu_image.py static/uploads/YOUR_IMAGE.jpg
   ```
4. Edit the dish again and upload the `_processed.png` file

## What's Different Now?

### Before (Problems):
- ❌ No clear upload button
- ❌ Confusing file input
- ❌ 500 timeout errors
- ❌ Long wait times

### Now (Fixed):
- ✓ Clear upload box with icon
- ✓ File name confirmation
- ✓ Fast uploads (no timeout)
- ✓ Simple and clean

## File Types Accepted:
- PNG (best for processed images)
- JPG/JPEG (good for originals)

## Processing Script Reference:
```bash
# Process a single dish image
python process_new_menu_image.py static/uploads/raw_photo.jpg

# Creates: static/uploads/raw_photo_processed.png
```

See `MENU_IMAGE_GUIDE.md` for full processing details.

## Troubleshooting:

**Q: Upload button still not showing?**
- Refresh the page (Ctrl+F5)

**Q: Image looks small or weird?**
- Use the processing script to prepare it correctly
- Upload the `_processed.png` version

**Q: Still getting errors?**
- Check file size (keep under 5MB for originals)
- Make sure it's a PNG or JPG file

That's it! The interface is now simple and fast.
