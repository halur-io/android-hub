# Restaurant Website Project

## Version
**Current Version: 1.0.3**

See `VERSION` file for the current deployment version.

### Version History
- **1.0.3** - View state persistence, 3-dot action menus, RBAC improvements
- **1.0.2** - Previous deployment
- **1.0.1** - Previous deployment

## Overview
A fully functional restaurant website with contact forms, menu display, and admin panel.

## Current Status
- ✅ Website is fully functional
- ✅ Contact forms save to database
- ✅ Admin panel for managing content
- ✅ XSS vulnerability fixed in form submission buttons
- ✅ Google Tag Manager integration for tracking
- ✅ SEO: robots.txt, sitemap.xml, Google verification file
- ✅ Popup system for announcements and promotions
- ⏸️ Email notifications: Not configured yet (optional)

## Popup System
The website includes a comprehensive popup system for displaying announcements, promotions, or special messages to visitors.

**Features:**
- Full design controls (colors, fonts, border radius, shadows)
- Timing controls (start/end dates, display delay)
- Multiple trigger options (time delay, scroll percentage, exit intent)
- Device targeting (desktop, mobile, tablet)
- Display frequency (once per session, once ever, every X days)
- Analytics tracking (impressions, clicks, closes)
- Rate limiting to prevent analytics manipulation

**Popup Designer (New):**
The popup editor features a modern split-screen design interface:
- **Live Preview Panel** - Real-time preview on the left with device switching (desktop/tablet/mobile)
- **Form Controls Panel** - Collapsible sections on the right for organized editing
- **Drag-and-Drop** - Reorder popup elements (title, content, button, image) with SortableJS
- **Element Position Storage** - Saved element order persists in `element_positions` JSONB column
- **Responsive Preview** - Preview how popups look on different devices
- **Live Updates** - "מתעדכן בזמן אמת" indicator shows changes update instantly

**Admin Management:**
Access at Admin → פופאפים (Popups) to:
- Create and edit popups with live preview
- Set targeting and timing options
- View analytics statistics
- Activate/deactivate popups
- Duplicate existing popups

**Files:**
- `models.py` - Popup model (line 1849+)
- `admin_routes.py` - Admin CRUD routes (line 7861+)
- `routes.py` - Public API endpoints (line 817+)
- `templates/admin/popups.html` - Popup list page
- `templates/admin/popup_form.html` - Popup editor
- `static/js/popup-system.js` - Frontend display logic

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

## UI/UX Design Preferences

**Action Buttons Pattern:**
- ALL action buttons (edit, delete, view, etc.) MUST be placed under a 3-dot dropdown menu
- Use `<i class="fas fa-ellipsis-v"></i>` for the 3-dot icon
- This creates a cleaner UI and is consistent across all admin pages
- Example pattern:
```html
<div class="action-menu">
  <button class="btn-dots" onclick="toggleActionMenu(event, this)">
    <i class="fas fa-ellipsis-v"></i>
  </button>
  <div class="action-dropdown">
    <a href="edit_url"><i class="fas fa-edit"></i> עריכה</a>
    <button class="delete-action"><i class="fas fa-trash"></i> מחיקה</button>
  </div>
</div>
```

**View State Persistence:**
- Use localStorage to save user's view preferences (cards vs list view)
- Restore preference on page load