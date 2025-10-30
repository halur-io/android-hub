# Restaurant Platform - Microservices Architecture

## Overview

This project is a comprehensive restaurant management platform built with a microservices architecture. Its purpose is to provide a scalable and configurable solution for restaurant operations. Key capabilities include:

-   **Public Website**: Modern, mobile-responsive customer-facing website with hero video, menu display, online ordering, gallery, and contact forms.
-   **Ordering System**: Full online ordering with cart management, branch selection, and payment integration.
-   **Payment Gateway**: Supports multiple payment providers (MAX, Bit, Cash, Apple Pay, Google Pay) - configurable via admin.
-   **Admin Dashboard**: Comprehensive control panel for all restaurant operations.
-   **Menu Management**: Dynamic menu system with dietary properties, Excel import, and print capabilities.

The platform prioritizes scalability and flexibility, with all business logic configurable via admin settings to avoid hardcoding.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### UI/UX Decisions
-   **Frontend Framework**: Flask-rendered Jinja2 templates (replaced React SPA for better SEO and simplicity).
-   **Styling**: Bootstrap 5 RTL + custom CSS, Google Fonts (Playfair Display + Inter + Rubik), Font Awesome 6.4.0 for icons.
-   **Color Scheme**: Navy Blue (#1a3a6e) and Red (#dc3545) from restaurant logo, replacing previous gold theme.
-   **Responsive Design**: Mobile-first approach with 100% mobile optimization.
-   **Language Support**: Session-based language switching with full Right-to-Left (RTL) support for Hebrew and English.

### Technical Implementations
-   **Backend Framework**: Flask, modular structure.
-   **Form Handling**: Flask-WTF with WTForms for validation and CSRF protection.
-   **Email System**: Flask-Mail for notifications.
-   **Security**: CSRF protection, environment-based configuration.
-   **Logging**: Python logging for debugging.
-   **Microservices Architecture**:
    -   **Core Services**: Auth, Order, Payment, Delivery, Kitchen, Notification, and Configuration services.
    -   **Communication**: Internal RESTful APIs, WebSockets for real-time updates, Message Queue for inter-service communication, and shared PostgreSQL database with service-specific schemas.

### Feature Specifications
-   **Public Website Pages**:
    -   **Homepage**: Hero video section (looping background video), featured menu items, gallery preview, call-to-action buttons.
    -   **Menu Page**: Full menu display organized by categories with dietary icons, prices in ₪ (NIS), and item descriptions.
    -   **Order Page**: Online ordering with live cart, quantity management, branch selection, subtotal/tax calculation, and checkout flow.
    -   **Gallery**: Admin-managed photo gallery with responsive grid layout.
    -   **Contact**: Contact form with branch information, maps integration (Waze/Google Maps), and email submission.
-   **Site Settings & Feature Toggles** (Admin-controlled):
    -   Enable/disable online ordering, English language, delivery, and pickup options.
    -   Configurable minimum order amount and tax rate.
    -   Hero section text (title, subtitle, description) in Hebrew and English.
-   **Menu Management**: Customizable dietary properties with icons (hot, gluten-free, vegan, etc.), drag-and-drop reordering, CSV/Excel import functionality, and comprehensive menu wizard with page grouping and 2-column print layout.
-   **Media Management**: Admin upload interface for hero videos and gallery images with section-based organization.
-   **Payment Configuration**: Admin panel for managing multiple payment providers with API credentials and settings.
-   **Admin Panel**: Mobile-responsive design with comprehensive Role-Based Access Control (RBAC) and granular permissions.

### System Design Choices
-   **Configuration**: Environment variable-based for production, configurable email settings, debug mode, and secret key management.
-   **Data Models**: SQLAlchemy models for ContactMessage and Reservation, with timestamp tracking.
-   **Database Architecture**: Robust models with proper relationships (e.g., many-to-many for roles and permissions), default data seeding, and safe migration practices.

## External Dependencies

-   **SMTP Integration**: Configurable SMTP server (default: Gmail) for email services.
-   **Bootstrap 5 RTL**: Frontend CSS framework for responsive design.
-   **Font Awesome 6.4.0**: Icon library for UI elements and dietary properties.
-   **Google Fonts API**: Playfair Display (headings), Inter (body text), Rubik (Hebrew text).
-   **Python Packages**: Flask, Flask-Mail, Flask-WTF, WTForms, SQLAlchemy, Gunicorn.

## Recent Changes (October 30, 2025)

### Brand Color Update & UX Improvements
-   **Color Scheme Refresh**: Updated entire site from gold/yellow theme to match restaurant logo colors:
    -   Primary: Navy Blue (#1a3a6e, #2d5492) - used for backgrounds, accordions, navigation
    -   Accent: Red (#dc3545, #c82333) - used for CTAs, highlights, mobile nav accents
    -   Replaced all instances of gold (#d4af37, #c49933) throughout the UI
-   **UX Enhancements**:
    -   Hero buttons: Red gradient primary button with improved hover states and glassmorphism effect on outline button
    -   Mobile bottom nav: Navy blue background with red accent border, enhanced tactile feedback
    -   Branch accordion: Navy blue expanded state with red icon accents
    -   Social icons: Navy blue hover states with glow effects
    -   Navigation links: Red hover color with text glow
    -   Improved shadows, transitions, and focus states throughout for better accessibility
    -   Better visual hierarchy and contrast for improved readability



### Initial Frontend Redesign
-   **Complete Frontend Redesign**: Replaced React SPA with Flask-rendered templates for better SEO, simpler maintenance, and tighter integration with admin panel.
-   **Database Enhancements**:
    -   Extended `SiteSettings` model with feature toggles (`enable_online_ordering`, `enable_english_language`, `enable_delivery`, `enable_pickup`).
    -   Added `PaymentConfiguration` model for managing multiple payment providers.
    -   Leveraged existing `Order` and `OrderItem` models from `services/order/order_service.py`.
-   **Public Website Structure**: Created 5 main pages (Home, Menu, Order, Gallery, Contact) all controlled via admin panel settings.
-   **Cart System**: Client-side cart management using localStorage with server-side order processing ready for integration.

### Latest Updates (October 30, 2025 - Night)
-   **Gallery Image Optimization**: Implemented automatic image resizing on upload
    -   All images compressed to max 1920px width with 85% JPEG quality
    -   Batch resize script converted 17 existing images: 2.2MB-9MB → 0.2MB-0.8MB (85-94% size reduction)
    -   Sequential single-file upload system for reliability (prevents gunicorn worker timeouts)
    -   Automatic PNG→JPEG conversion with white background for transparency handling
-   **Admin Feature Toggles Expansion**: Added comprehensive on/off controls in SiteSettings:
    -   `enable_menu_display` - Show/hide entire menu section
    -   `enable_gallery` - Show/hide gallery page
    -   `enable_contact_form` - Show/hide contact page
    -   `enable_table_reservations` - Show/hide table reservation features
    -   All toggles integrated into footer sitemap and navigation
-   **Hero Video Desktop Fix**: Changed `object-fit` from `contain` to `cover` with 1.1x scale transform
    -   Desktop: Full-screen video coverage with slight zoom for cinematic effect
    -   Mobile: Maintains `contain` view for portrait video compatibility
-   **Branch Accordion UX**: All branches now collapsed by default (removed auto-expand on first item)
-   **Footer Sitemap Redesign**: Replaced compact footer with comprehensive 4-column sitemap:
    -   Column 1: About (logo, tagline, social icons with navy/red hover effects)
    -   Column 2: Quick Links (all pages with feature toggle respect)
    -   Column 3: Information (Terms of Use, About, Locations, language toggle)
    -   Column 4: Contact (phone, address, WhatsApp with icon accents)
    -   Fully responsive with centered mobile layout
-   **Terms of Use Page**: Created complete legal page system:
    -   New `TermsOfUse` model with Hebrew/English bilingual content
    -   Pre-populated with comprehensive Israeli restaurant ToU template
    -   Accessible at `/terms` route with elegant card-based layout
    -   Fully integrated into footer sitemap

### Previous Updates (October 30, 2025 - Evening)
-   **Hero Video**: Integrated user-uploaded restaurant video with balanced performance optimization:
    -   Original: 55MB (1440x2560 portrait) → Mobile: 7.4MB (720x1280, CRF 23) | Desktop: 23MB (1080x1920, CRF 20)
    -   Poster image: 144KB for instant display while video loads
    -   Smart responsive loading: JavaScript-driven source selection based on viewport
    -   Connection-aware: Disables autoplay on 2G/slow connections and data saver mode
    -   Accessibility: Respects prefers-reduced-motion settings
    -   Admin uploads take priority over optimized defaults
    -   CSS uses `object-fit: contain` to prevent zoom/crop issues with portrait video
    -   Higher quality compression settings (CRF 20-23) for better visual quality
-   **Logo Integration**: Added restaurant logo (`sumo-logo.png`) to navbar with responsive sizing (50px on mobile).
-   **Dynamic Sections System**:
    -   Created `CustomSection` model for admin-controlled homepage sections.
    -   Supports three content types: plain text, HTML, and embedded content (iframes).
    -   Sections can be reordered via `display_order` field.
-   **Table Reservation Integration**:
    -   Created `ReservationSettings` model with external system integration.
    -   Connected to external reservation system: `https://tbit.be/BHWCPU`.
    -   Admin can enable/disable, customize button text, and control visibility.
-   **Branch Enhancements**:
    -   Converted branch display to **Bootstrap Accordion** (collapsible sections) with elegant gold-accented design.
    -   Integrated existing `WorkingHours` model display on homepage.
    -   Updated Waze navigation link to user-specific URL: `https://waze.com/ul/hsvc5ksnm1`.
    -   Branch sections show: name, address, phone, working hours, and navigation buttons.
-   **Footer Redesign**:
    -   Simplified footer to **single-row compact design** containing only logo, social icons, and copyright.
    -   Removed excessive multi-column content for cleaner appearance.
-   **Menu Images System**:
    -   Added ability to display uploaded menu images instead of text-based menu items.
    -   Uses existing `MediaFile` model with `section='menu'`.
    -   Full-screen **lightbox modal** functionality for zooming in on menu images.
    -   Falls back to traditional category-based menu items when no images are uploaded.
-   **Mobile Bottom Navigation**:
    -   Fixed persistent bottom navigation bar (visible on screens <768px).
    -   Contains 3 prominent action buttons: Table Reservation, Call, and Order.
    -   Gold gradient styling matching the site's premium design.
-   **Interactive Backgrounds & Dividers**:
    -   **Wave Dividers**: SVG wave transitions between major sections for smooth visual flow.
    -   **Floating Shapes**: Animated geometric shapes in background (20s animation cycle) on About section.
    -   **Gradient Overlays**: Subtle radial gradients on Featured Menu section.
    -   **Animated Center Divider**: Rotating gold icon divider with horizontal lines between sections.
    -   **Pattern Background**: Geometric pattern overlay on Branches section.
    -   **Gold Gradient Effect**: Rotating radial gradient on Table Reservation section.
    -   **Curved Dividers**: SVG curved transitions for elegant section separations.
    -   All effects are CSS-only for optimal performance and fully mobile responsive.
-   **Mobile Optimization**:
    -   100% mobile-responsive design across all breakpoints (768px, 576px).
    -   Responsive hero buttons, navigation menu, and section layouts.
    -   Optimized font sizes, spacing, and button widths for mobile devices.
    -   Full-width buttons on mobile with centered layouts.
    -   Interactive backgrounds automatically scale and reduce opacity on mobile devices.