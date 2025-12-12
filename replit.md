# Restaurant Website Project

## Overview
A fully functional restaurant website with contact forms, menu display, and admin panel.

## Current Status
- ✅ Website is fully functional
- ✅ Contact forms save to database
- ✅ Admin panel for managing content
- ✅ XSS vulnerability fixed in form submission buttons
- ✅ Google Tag Manager integration for tracking
- ✅ SEO: robots.txt, sitemap.xml, Google verification file
- ⏸️ Email notifications: Not configured yet (optional)

## Google Tag Manager Setup
GTM tracks page views and menu dish interactions automatically.

**To enable:**
1. Create a GTM container at https://tagmanager.google.com
2. Copy your Container ID (GTM-XXXXXXX)
3. Go to Admin → Site Settings → Advanced → Analytics & Tracking
4. Paste your GTM ID and save

**Events tracked:**
- `dish_view` - When a menu dish is clicked (includes dish name, category, price)
- `menu_category_view` - When switching menu categories
- `add_to_cart` - When adding items to cart

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

## Role-Based Access Control (RBAC)
The admin panel uses a comprehensive RBAC system:

**How it works:**
- Roles (admin, manager, kitchen, cashier, delivery, viewer) contain sets of permissions
- Users are assigned roles via Admin → User Management → Edit User
- Superadmins (is_superadmin=true) bypass all permission checks
- The sidebar dynamically shows/hides menu items based on user permissions

**Permission enforcement:**
- `admin_routes.py` has a `ROUTE_PERMISSIONS` mapping that defines required permissions for each route
- The `before_request` hook checks permissions before allowing access
- Routes without explicit mapping in `ROUTE_PERMISSIONS` only require login

**Available roles:**
- `superadmin` - Full system access
- `admin` - Administrative functions
- `manager` - Operations management
- `kitchen` - Kitchen operations and stock
- `cashier` - Payment and orders
- `delivery` - Delivery management
- `viewer` - Read-only access

**Files:**
- `permissions.py` - Permission decorators and utilities
- `admin_routes.py` - ROUTE_PERMISSIONS mapping and before_request hook
- `models.py` - Role, Permission, AdminUser models
- `templates/admin/base.html` - Sidebar with permission checks

## Recent Security Fixes
- Fixed XSS vulnerability in form submission button handling (static/js/main.js, line 484)
- Changed from innerHTML to textContent for safer DOM manipulation
- Implemented centralized RBAC enforcement via before_request hook in admin routes
- Added users.* and roles.* permissions to ROUTE_PERMISSIONS for complete coverage
- Sidebar and dashboard correctly hide unauthorized links based on user permissions

## RBAC Permission Categories
- `users.view/create/edit/delete` - User management
- `roles.view/create/edit/delete` - Role management  
- `settings.view/edit` - Site settings, gallery, messages, newsletter, reservations
- `menu.view/edit` - Menu management
- `branches.view/edit` - Branch management
- `stock.view/manage/suppliers/transactions/alerts/analytics/shopping_lists/settings` - Stock operations
- `checklists.view/edit` - Task checklists
- `kitchen.view/manage` - Kitchen operations
- `reports.view` - Reports access
- `system.admin` - System configuration