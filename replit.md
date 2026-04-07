# Restaurant Website Project

## Overview
This project delivers a comprehensive, fully functional restaurant website designed to enhance customer engagement and streamline operations. It features a public-facing site for menu display, contact forms, and an advanced online ordering system with multi-branch support, deals/coupons, and upsell functionalities. The administrative backend offers content management, user/role management, and a specialized iPad Operations Dashboard for efficient in-house staff management. The goal is to provide a scalable, user-friendly platform supporting online presence, order processing, and operational control.

## User Preferences
I prefer clear, concise language in all communications. For coding, I favor an iterative development approach, focusing on delivering functional increments. I expect detailed explanations for complex architectural decisions or significant code changes. Please ask for my approval before implementing any major changes or refactoring large sections of the codebase. I want all action buttons (edit, delete, view, etc.) to be placed under a 3-dot dropdown menu (`<i class="fas fa-ellipsis-v"></i>`) for a cleaner and consistent UI across all admin pages. I also prefer that the user's view state preferences (e.g., cards vs. list view) are persisted using `localStorage` and restored on page load.

## System Architecture

### UI/UX Decisions
- **Admin Panel UI:** Clean, intuitive interface with consistent design patterns, including consolidated action buttons under a 3-dot dropdown menu and persistence of user view state preferences via `localStorage`.
- **iPad Operations Dashboard (Ops):** Tabit-style, dark-themed, touch-optimized for tablets, featuring bottom tab navigation.
- **Popup Designer:** Split-screen interface with live preview, collapsible controls, drag-and-drop element reordering, and responsive previews.

### Technical Implementations
- **Timezone Handling:** All datetimes stored as naive UTC in the database (`datetime.utcnow`). Display uses Jinja2 filters (`|il_time`, `|il_time_short`, `|il_hour`) that convert UTC to `Asia/Jerusalem` via `zoneinfo.ZoneInfo`. Server-side "today" queries convert Israel midnight to UTC before filtering. Helper: `_israel_today_start_utc()` in `ops_routes.py`, `_to_il_hour()` in order/KDS routes.
- **Core Website:** Built with Python/Flask, supporting static content and dynamic pages.
- **Online Ordering System:** Integrated from a `standalone_order_service` for menu display, cart management, multi-branch operations, and real-time KDS.
- **Popup System:** Comprehensive announcement system with design controls, multiple triggers (time delay, scroll, exit intent), device targeting, and display frequency.
- **Deals, Coupons & Upsells:** Server-side validated systems for bundled deals, discount coupons, and checkout upsell suggestions.
- **Role-Based Access Control (RBAC):** Granular permission system for the admin panel, dynamically adjusting UI and enforcing route-level permissions.
- **XSS Protection:** Implemented safer DOM manipulation using `textContent`.

### Feature Specifications
- **Multi-branch Support:** Branch-specific menus, pricing, delivery zones, and payment gateways.
- **KDS (Kitchen Display System):** Real-time order management dashboard with branch filtering and staff PIN login.
- **SMS Notification Center:** Full SMS management system with bilingual templates, auto-triggers based on order status, and a message log viewer.
- **iPad Operations Dashboard Modules:** Includes device enrollment, PIN-based authentication, Menu, Stock, Deals & Coupons, Branch settings, and a Kanban-style Orders module.
- **Auto-Print System (Print Agent v4.0):** Local print agent runs at each branch to fetch printer configurations, poll for new orders, and route bons to specific printers by station. Supports multi-printer management and branch-specific printer settings.
- **Android Print Hub API:** Server-side API layer for Android tablet print apps. Includes SSE real-time order streaming (`/ops/api/orders/stream`), device registration/heartbeat (`/ops/api/devices/*`), order acknowledgment (`/ops/api/orders/<id>/ack`), and remote device configuration. Uses `PrintDevice` model for device tracking. Comprehensive API documentation at `docs/android-app-api-spec.md`.
- **Dish Photo Processing System:** Automated pipeline for image processing including background removal, auto-cropping, gradient compositing, and optimization for web display.
- **Worker Time Tracking:** Standalone shift clock module within the Ops dashboard, allowing PIN-based clock-in/out and providing administrative oversight.
- **Delivery Zones Management:** Admin and Ops modules for managing delivery zones with branch filtering and city autocomplete.
- **Branch-Specific Print Routing:** Allows per-branch override of menu item print station assignments.
- **Employee & PIN Management (Ops):** Module for managing employee PINs with branch isolation and superadmin safeguards.
- **Branch & Settings Isolation (Ops):** Enforces branch-level isolation for settings, allowing non-superadmin users to manage only their assigned branch's details.
- **Cash Order Management & Hidden Archive:** Allows superadmins to hard-delete cash orders (credit card orders cannot be deleted) by archiving a snapshot to a separate table. Deleted order numbers are released and recycled for the next new order via `ReleasedOrderNumber` model. A hidden dashboard provides access to archived orders, financial summaries, and restore capabilities.
- **Order Deletion Secret Gesture:** Delete is hidden from UI — requires 5 taps on order title followed by a long press (~800ms) on the receipt button to trigger the deletion modal/prompt. Applied consistently across admin order detail, Ops orders modal, and Ops order history.
- **Ops Order History Module:** Provides search, filter, re-order, and send receipt functionalities for past orders, with branch-scoped access.

### System Design Choices
- **Modularity:** Achieved through separation of concerns, e.g., `standalone_order_service`.
- **Print Stations as Entities:** `PrintStation` is a first-class entity for flexible print routing.
- **Database Schema:** Includes models for `FoodOrder`, `MenuItem`, `ManagerPIN`, `Deal`, `Coupon`, `Printer`, `PrintDevice`, `TimeLog`, `DeliveryZone`, `ArchivedOrder`, `ReleasedOrderNumber`, among others.
- **API Endpoints:** Dedicated APIs for order validation, coupon validation, upsell suggestions, and print agent polling.

## External Dependencies
- **Payment Gateways:** HYP, MAX Pay.
- **SMS Provider:** SMS4Free.
- **Analytics:** Google Tag Manager.
- **UI Libraries:** SortableJS.
- **Messaging:** Telegram.
- **Image Processing:** rembg, Pillow.