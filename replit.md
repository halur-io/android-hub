# Restaurant Website Project

## Overview
This project delivers a comprehensive, fully functional restaurant website designed to enhance customer engagement and streamline operations. It features a public-facing site for menu display, contact forms, and an advanced online ordering system. Key capabilities include multi-branch support, a deals and coupon system, and upsell functionalities to maximize revenue. The administrative backend provides robust content management, user and role management (RBAC), and a specialized iPad Operations Dashboard for efficient in-house staff management. The overarching goal is to provide a scalable and user-friendly platform for restaurant businesses, supporting efficient online presence, order processing, and operational control.

## User Preferences
I prefer clear, concise language in all communications. For coding, I favor an iterative development approach, focusing on delivering functional increments. I expect detailed explanations for complex architectural decisions or significant code changes. Please ask for my approval before implementing any major changes or refactoring large sections of the codebase. I want all action buttons (edit, delete, view, etc.) to be placed under a 3-dot dropdown menu (`<i class="fas fa-ellipsis-v"></i>`) for a cleaner and consistent UI across all admin pages. I also prefer that the user's view state preferences (e.g., cards vs. list view) are persisted using `localStorage` and restored on page load.

## System Architecture

### UI/UX Decisions
- **Admin Panel UI:** Clean, intuitive interface with consistent design patterns.
- **Action Buttons:** All action buttons (edit, delete, view) are consolidated under a 3-dot dropdown menu (`<i class="fas fa-ellipsis-v"></i>`) for a cleaner UI.
- **View State Persistence:** User preferences for views (e.g., cards vs. list) are saved in `localStorage` and restored on page load.
- **iPad Operations Dashboard (Ops):** Tabit-style, dark-themed, touch-optimized for tablets, featuring a bottom tab navigation.
- **Popup Designer:** Split-screen interface with a live preview panel and collapsible form controls. Supports drag-and-drop element reordering and responsive previews.

### Technical Implementations
- **Core Website:** Built with Python/Flask, serving static content and dynamic pages.
- **Contact Forms:** Submissions are saved to the database.
- **Online Ordering System:** Integrated from a `standalone_order_service` package, supporting menu display, cart management, multi-branch operations, and real-time KDS.
- **Popup System:** Comprehensive system for announcements with full design controls, timing options, multiple triggers (time delay, scroll, exit intent), device targeting, and display frequency settings.
- **Deals, Coupons & Upsells:**
    - **Deals:** Bundled menu items at special prices, configured via admin and validated server-side.
    - **Coupons:** Discount codes with server-side validation and usage limits.
    - **Upsells:** Suggested items at checkout based on cart contents, with discounted prices validated server-side.
- **Role-Based Access Control (RBAC):** Granular permission system for admin panel access, dynamically adjusting sidebar visibility and enforcing route-level permissions via `before_request` hooks. Roles include superadmin, admin, manager, kitchen, cashier, delivery, and viewer.
- **Google Tag Manager (GTM):** Integration for tracking page views, menu interactions (`dish_view`, `menu_category_view`, `add_to_cart`).
- **XSS Protection:** Implemented safer DOM manipulation (`textContent` instead of `innerHTML`) to prevent XSS vulnerabilities.

### Feature Specifications
- **Multi-branch Support:** Branch-specific menus, prices, delivery zones, and payment gateways.
- **KDS (Kitchen Display System):** Real-time order management dashboard with branch filtering, staff PIN login, and order activity logging.
- **SMS Notifications:** Utilizes SMS4Free for order and activity notifications, with detailed logging (`SMSLog`).
- **iPad Operations Dashboard:**
    - Device enrollment with one-time codes and persistent tokens.
    - PIN-based authentication (`ManagerPIN` model) with role-based permissions (`ops_permissions`).
    - Modules: Home (KPIs), Menu management, Stock management, Deals & Coupons, Branch settings, Orders module (Kanban-style board with status progression).
    - Orders module features: Kanban board with status filters, detailed order view, one-tap status progression, branch-scoped order display, auto-refresh.

### Auto-Print System (Print Agent v4.0 - Multi-Printer)
- **Architecture:** Cloud server cannot reach restaurant LAN printers directly. Solution: a local print agent (`print_agent.py`) runs on a Mac at the restaurant (one per branch), fetches printer config from the server, polls for new orders, and routes each bon to the correct printer by station.
- **Multi-Printer Management:** Admin panel (`/admin/printers`) allows CRUD of printers per branch. Each printer has IP, port, encoding, codepage, stations, and copy settings. One printer per branch is marked as default (receives checker + payment bons).
- **DB Models:** `Printer` (per-branch printer config), `PrinterStation` (maps station names to printers). `MenuItem.print_station` links dishes to stations. `MenuItem.print_name` (optional custom name for bon printing).
- **Print Settings Tab:** Dedicated tab in menu item edit form (`enhanced_menu_item.html`) with print station dropdown and custom print name field. Print name is used on bons when set; falls back to `name_he`.
- **API Endpoints:**
    - `GET /ops/api/orders/unprinted?branch_id=X` (returns unprinted orders, optionally filtered by branch)
    - `POST /ops/api/orders/mark-printed` (marks orders as printed)
    - `GET /ops/api/branch/<id>/printers` (returns printer config for print agent: default printer, station map, all printers)
- Auth via `X-Print-Key` header matching `PRINT_AGENT_KEY` env var.
- **DB Fields:** `FoodOrder.bon_printed` (Boolean), `FoodOrder.bon_printed_at` (DateTime) track print status.
- **Printer:** SNBC BTP-R880NPV 80mm thermal (ESC/POS, ISO-8859-8, Hebrew1 codepage 36, IP 10.100.10.234:9100).
- **Printer Model Field:** `Printer.printer_type` stores the hardware model (default: `snbc-btp-r880npv`).
- **Connection Test:** Admin tab at `/admin/printers` (בדיקת חיבור) tests TCP connectivity to all configured printers.
- **Bon Types:** Checker bon (configurable copies), Payment bon (configurable copies), Station bons (routed to correct printer by dish station).
- **Print Agent Usage:** `python3 print_agent.py --branch <BRANCH_ID>` (env vars: `PRINT_AGENT_SERVER`, `PRINT_AGENT_KEY`)
- **Print Modes:** Browser (hidden iframe + print dialog) or Server (direct TCP via print agent).

### Dish Photo Processing System
- **Pipeline:** `image_processing.py` — EXIF fix → rembg AI background removal → auto-crop → dark glaze radial gradient compositing → 500x500 card + 1200px hero output.
- **Admin Upload:** AJAX endpoint `POST /admin/menu/item/<id>/upload-image` with 4-step progress bar (upload → AI removal → glaze compositing → optimize). Fallback to basic resize on processing failure. Permission-protected via `menu.edit` RBAC.
- **Form Submit:** New items (id=0) use form-submit path with same processing pipeline.
- **DB Fields:** `MenuItem.image_path` (card image), `MenuItem.image_hero_path` (hero image for detail view).
- **Order Display:** Dish card backgrounds use `#1a1a1a` dark to complement processed images. Item detail sheet uses hero image when available.
- **Batch CLI:** `python3 process_dish_photo.py --batch [--update-db]` processes all unprocessed menu images. Single file: `python3 process_dish_photo.py <image_path>`.
- **File Validation:** Uses `allowed_image_file()` (jpg/jpeg/png/gif/webp only) for dish uploads. Filenames include microseconds to prevent collisions.

### System Design Choices
- **Modularity:** Separation of concerns (e.g., `standalone_order_service` for ordering).
- **Print Stations as Entities:** `PrintStation` model is a standalone first-class entity (name + display_name). Managed via admin tab at `/admin/printers` (עמדות הדפסה). `PrinterStation` remains as a join table linking printers to stations. Menu item edit form shows real stations with their linked printer info (name + IP). No hardcoded station fallbacks.
- **Worker Time Tracking:** Standalone shift clock module in Ops dashboard (not tied to system login/logout). `TimeLog` model (worker_id FK→ManagerPIN, branch_id, clock_in, clock_out, source). Ops module at `/ops/shifts` — workers select their name, enter PIN to clock in/out independently. Active shifts shown with elapsed timers; today's shift log displayed below. APIs: `POST /ops/shifts/clock-in`, `POST /ops/shifts/clock-out` (JSON: worker_id + pin). Admin page at `/admin/time-logs` with filters (worker, branch, date range), daily/weekly totals per worker, open shifts display, manual clock-out, and auto-close stale shifts. Auto-close threshold configurable via `SHIFT_AUTO_CLOSE_HOURS` env var (default 12). Automatic stale-shift closure runs via `before_request` hook (throttled to every 5 minutes). `shifts` added to `ManagerPIN.OPS_MODULES`. RBAC: `system.admin` for admin page.
- **Delivery Zones Management:** Admin CRUD at `/admin/delivery-zones` with branch filter, city autocomplete from data.gov.il settlements API (`/admin/api/cities`). Ops module at `/ops/delivery` with modal-based add/edit, toggle, delete. Branch-scoped access control in Ops (non-superadmin users can only modify zones in their branch). `delivery` added to `ManagerPIN.OPS_MODULES`. RBAC: `branches.view` for list, `branches.edit` for mutations. City autocomplete also available at `/ops/api/cities`.
- **Branch-Specific Print Routing:** `BranchMenuItem.print_station` field allows per-branch override of dish print station assignment. Ops menu module (`/ops/menu`) shows print station dropdown per item alongside price and availability. Print routing in bons/orders checks branch override → global fallback. API: `POST /ops/api/menu/station` (JSON: item_id, station). Creating new `BranchMenuItem` records preserves the item's current `is_available` state. Print station changes require explicit confirm button click.
- **Employee & PIN Management (Ops):** Superadmin-only module at `/ops/employees` for managing employee PINs directly from the iPad dashboard. Supports add, edit, and activate/deactivate employees with name, PIN, branch assignment, and granular module permissions. Server-side validation includes branch existence check, permissions whitelist against `OPS_MODULES`, last-superadmin protection (cannot remove or deactivate the last superadmin), and self-toggle prevention. `employees` added to `ManagerPIN.OPS_MODULES`.
- **Database Schema:** Includes models for `FoodOrder`, `FoodOrderItem`, `MenuItemOptionGroup`, `MenuItemOptionChoice`, `ManagerPIN`, `Deal`, `Coupon`, `UpsellRule`, `OrderActivityLog`, `SMSLog`, `EnrolledDevice`, `Branch`, `Role`, `Permission`, `AdminUser`, `Printer`, `PrinterStation`, `PrintStation`, `TimeLog`, `DeliveryZone`, `BranchMenuItem`.
- **API Endpoints:** Dedicated endpoints for order validation, coupon validation, upsell suggestions, and print agent polling.

## External Dependencies
- **Payment Gateways:** HYP, MAX Pay (with branch-specific configurations).
- **SMS Provider:** SMS4Free.
- **Analytics:** Google Tag Manager.
- **UI Libraries:** SortableJS (for drag-and-drop in Popup Designer).
- **Messaging:** Telegram (for order notifications).
- **Image Processing:** rembg (AI background removal), Pillow (image manipulation).