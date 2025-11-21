# Restaurant Website Project

## Overview
A fully functional restaurant website with contact forms, menu display, and admin panel.

## Current Status
- ✅ Website is fully functional
- ✅ Contact forms save to database
- ✅ Admin panel for managing content
- ✅ XSS vulnerability fixed in form submission buttons
- ⏸️ Email notifications: Not configured yet (optional)

## Email Configuration (Optional - For Future Setup)
The website works perfectly without email notifications. All messages are saved to the database and can be viewed in the admin panel at `/admin`.

If you want to enable email notifications later:
1. Enable 2-Step Verification on your Google account
2. Generate an App Password from Google Account settings
3. Set these environment variables:
   - `MAIL_USERNAME`: Your Gmail address
   - `MAIL_PASSWORD`: Your Google App Password (not regular password)

## Admin Access
Access the admin panel at `/admin` to:
- View all contact form submissions
- Manage menu items
- Update site content
- Check messages from visitors

## Recent Security Fix
- Fixed XSS vulnerability in form submission button handling (static/js/main.js, line 484)
- Changed from innerHTML to textContent for safer DOM manipulation