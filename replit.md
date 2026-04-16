# Restaurant Website Project

## Overview
This project delivers a comprehensive, fully functional restaurant website designed to enhance customer engagement and streamline operations. It features a public-facing site for menu display, contact forms, and an advanced online ordering system with multi-branch support, deals/coupons, and upsell functionalities. The administrative backend offers content management, user/role management, and a specialized iPad Operations Dashboard for efficient in-house staff management. The goal is to provide a scalable, user-friendly platform supporting online presence, order processing, and operational control, with a focus on business growth and market competitiveness.

## User Preferences
I prefer clear, concise language in all communications. For coding, I favor an iterative development approach, focusing on delivering functional increments. I expect detailed explanations for complex architectural decisions or significant code changes. Please ask for my approval before implementing any major changes or refactoring large sections of the codebase. I want all action buttons (edit, delete, view, etc.) to be placed under a 3-dot dropdown menu (`<i class="fas fa-ellipsis-v"></i>`) for a cleaner and consistent UI across all admin pages. I also prefer that the user's view state preferences (e.g., cards vs. list view) are persisted using `localStorage` and restored on page load.

## System Architecture

### UI/UX Decisions
- **Admin Panel UI:** Clean, intuitive interface with consistent design patterns, including consolidated action buttons under a 3-dot dropdown menu and persistence of user view state preferences via `localStorage`.
- **iPad Operations Dashboard (Ops):** Tabit-style, dark-themed, touch-optimized for tablets, featuring bottom tab navigation. Includes modules for device enrollment, PIN-based authentication, Menu, Stock, Deals & Coupons, Branch settings, Orders (Kanban-style), Worker Time Tracking, Delivery Zones, Employee & PIN Management, and a Table Floor Layout Designer.
- **Popup Designer:** Split-screen interface with live preview, collapsible controls, drag-and-drop element reordering, and responsive previews.

### Technical Implementations
- **Core Website:** Built with Python/Flask, supporting static content and dynamic pages.
- **Online Ordering System:** Integrated for menu display, cart management, multi-branch operations, and real-time KDS.
- **Timezone Handling:** All datetimes stored as naive UTC in the database. Display uses Jinja2 filters for conversion to `Asia/Jerusalem`.
- **Popup System:** Comprehensive announcement system with design controls, multiple triggers, device targeting, and display frequency.
- **Deals, Coupons & Upsells:** Server-side validated systems for bundled deals, discount coupons, and checkout upsell suggestions, supporting "customer picks" deals with flexible category assignments.
- **Role-Based Access Control (RBAC):** Granular permission system for admin panel UI and route-level enforcement.
- **XSS Protection:** Safer DOM manipulation using `textContent`.
- **SMS Notification Center:** Full SMS management system with bilingual templates, auto-triggers, and message log viewer.
- **Auto-Print System (Print Agent v4.0):** Local print agent for fetching configurations, polling for new orders, and routing bons to specific printers by station, supporting multi-printer management.
- **Android Print Hub API:** Server-side API layer for Android tablet print apps, including SSE real-time order streaming, device registration/heartbeat, order acknowledgment, and remote device configuration. Uses `PrintDevice` model.
- **Dish Photo Processing System:** Automated pipeline for image processing including background removal, auto-cropping, and optimization.
- **Cash Order Management & Hidden Archive:** Allows superadmins to hard-delete cash orders by archiving a snapshot to a separate table, releasing order numbers for recycling.
- **Order Deletion Secret Gesture:** Hidden UI deletion mechanism requiring specific taps and long press.
- **Ops Manual Order Creation:** Allows staff to create phone/walk-in orders from the Ops dashboard with customer lookup, full menu access, item options, discounts, notes, and payment processing (cash/HYP payment link).
- **Dine-In Table Service (ישיבה):** Full Tabit-style table service module in Ops dashboard, tracking tables and multi-order sessions. Features include real-time table status, session ordering UI with item modification, kitchen sending, cash/HYP payment options (including split payment), session cancellation with reasons, and void logging for items.
- **Real-Time Order Alerts (Ops):** Hybrid SSE + polling for live notifications (sound, visual, browser push, slide-down banner) on the Ops orders page.
- **Table Floor Layout Designer:** Visual drag-and-drop designer for positioning tables on a canvas, updating `DineInTable` with layout properties.
- **Ops PWA (Standalone Installable App):** Ops Dashboard is a full PWA installable to home screen. Web App Manifest at `/ops/manifest.json` (scope/start_url `/ops/`, standalone, theme `#1a1a2e`). Service Worker at `/ops/sw.js` (cache-first for static assets, network-first for `/ops/` navigations with `/ops/offline` fallback, API/SSE bypassed). Install prompt banner with 7-day dismissal persistence. Update flow: new SW detected → user-controlled toast → SKIP_WAITING + reload (no auto-takeover). Web Push notifications for new orders via VAPID (auto-generated keypair persisted in `OpsPushVAPID`), with `OpsPushSubscription` storing per-device subscriptions. Push send is fired in a background thread from the SSE new-order broadcast. Subscribe/unsubscribe endpoints require enrolled device + authenticated PIN; endpoints are CSRF-protected via Origin/Referer checks. Generated icons (72→512, plus maskable + Apple touch) at `static/ops/icons/`. PWA tags + SW registration are present on entry pages (`not_enrolled`, `login`) so installation works from first visit.

### Project Structure (Layered Architecture)
- **`models/`**: Domain model package with 18 modules covering user, site, menu, branch, order, stock, receipt, print, ops, dine-in, marketing, sms, catering, checklist, content, payment, audit, and push.
- **`utils/`**: Utility package for permissions, HTML sanitization, and audit logging.
- **`api/v1/`**: Versioned REST API blueprint for menu, branches, and order tracking.
- **`database.py`**: Central SQLAlchemy instance.

### System Design Choices
- **Modularity:** Achieved through separation of concerns.
- **Print Stations as Entities:** `PrintStation` is a first-class entity for flexible print routing.
- **Database Schema:** Includes models for `FoodOrder` (with `source` field), `MenuItem`, `ManagerPIN`, `Deal`, `Coupon`, `Printer`, `PrintDevice`, `TimeLog`, `DeliveryZone`, `ArchivedOrder`, `ReleasedOrderNumber`, `DineInTable`, `DineInSession`, `PendingPrintJob`.
- **Print Job Queue (DB-backed):** `PendingPrintJob` table for reliable print job storage and processing across workers.
- **Print Sync (Atomic ACK+Poll):** `POST /ops/api/print-sync` combines acknowledgment and polling for efficient and reliable print synchronization.
- **API Endpoints:** Dedicated APIs for order validation, coupon validation, upsell suggestions, and print agent polling.
- **Swagger API Documentation:** Interactive OpenAPI 3.0 docs at `/api/docs` for Print Hub endpoints.
- **Per-Device API Keys:** `ApiKey` model for managing unique API keys with usage tracking.

## External Dependencies
- **Payment Gateways:** HYP, MAX Pay.
- **SMS Provider:** SMS4Free.
- **Analytics:** Google Tag Manager.
- **UI Libraries:** SortableJS.
- **Messaging:** Telegram.
- **Image Processing:** rembg, Pillow.