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

### System Design Choices
- **Modularity:** Separation of concerns (e.g., `standalone_order_service` for ordering).
- **Database Schema:** Includes models for `FoodOrder`, `FoodOrderItem`, `MenuItemOptionGroup`, `MenuItemOptionChoice`, `ManagerPIN`, `Deal`, `Coupon`, `UpsellRule`, `OrderActivityLog`, `SMSLog`, `EnrolledDevice`, `Branch`, `Role`, `Permission`, `AdminUser`.
- **API Endpoints:** Dedicated endpoints for order validation, coupon validation, and upsell suggestions.

## External Dependencies
- **Payment Gateways:** HYP, MAX Pay (with branch-specific configurations).
- **SMS Provider:** SMS4Free.
- **Analytics:** Google Tag Manager.
- **UI Libraries:** SortableJS (for drag-and-drop in Popup Designer).
- **Messaging:** Telegram (for order notifications).