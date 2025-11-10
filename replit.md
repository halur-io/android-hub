# Restaurant Platform - Microservices Architecture

## Overview

This project is a scalable and configurable restaurant management platform built with a microservices architecture. It provides a comprehensive solution for restaurant operations, including a modern, mobile-responsive public website for online ordering, menu display, and customer interaction. A robust admin dashboard allows for dynamic menu management, payment gateway configuration, and overall operational control. The platform's core vision is to offer a highly flexible solution where business logic is configurable via admin settings, avoiding hardcoded dependencies and ensuring adaptability.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### UI/UX Decisions
-   **Frontend Framework**: Flask-rendered Jinja2 templates (chosen for SEO and simplicity).
-   **Styling**: Bootstrap 5 RTL with custom CSS, Google Fonts (Playfair Display, Inter, Rubik), and Font Awesome 6.4.0.
-   **Color Scheme**: Navy Blue (#1a3a6e) and Red (#dc3545), derived from the restaurant's logo.
-   **Example2 Theme**: Black/dramatic/elegant alternative theme available at `/example2/` with deep blacks (#0a0a0a, #1a1a1a), gold accents (#d4af37, #c9a961), and burgundy highlights (#8b0000) - a parallel version of the entire site showcasing an upscale, luxurious aesthetic
-   **Responsive Design**: Mobile-first approach with 100% mobile optimization.
-   **Language Support**: Session-based language switching with full Right-to-Left (RTL) support for Hebrew and English.
-   **Dynamic Visuals**: Incorporates hero videos/images with parallax, animated elements (light rays, particles), gradient overlays, SVG wave/curved dividers, and rotating icon dividers for an engaging user experience.
-   **Admin Dashboard UI**: Modern horizontal tabs layout that fits perfectly within the main admin content area, featuring:
    -   Professional SaaS-style design with clean visual hierarchy
    -   Modern horizontal tabs with icons and descriptions (no sidebar overlap)
    -   Modern form components: toggle switches, file upload areas, color pickers
    -   Responsive two-column grid layouts
    -   Sticky action bar for Save/Cancel buttons
    -   Dedicated admin.css design system with design tokens
    -   Smooth tab transitions without page reload
    -   **Mobile-Optimized Pages**: Stock Management, Menu Management (with quick availability toggle), and Orders pages feature touch-friendly controls, horizontal-scroll tabs, and optimized layouts for kitchen/service staff mobile use

### Technical Implementations
-   **Backend Framework**: Flask with a modular structure.
-   **Form Handling**: Flask-WTF with WTForms for validation and CSRF protection.
-   **Email System**: Flask-Mail for notifications.
-   **Security**: CSRF protection and environment-based configuration.
-   **Logging**: Python logging for debugging.
-   **Theme System**: Conditional CSS loading via context variable enables parallel design versions (example2.css overrides public.css when theme='example2'). All example2 routes set theme flag and use example2-prefixed route names for isolated navigation.
-   **Microservices Architecture**:
    -   **Core Services**: Auth, Order, Payment, Delivery, Kitchen, Notification, and Configuration services.
    -   **Communication**: Internal RESTful APIs, WebSockets for real-time updates, Message Queue for inter-service communication, and a shared PostgreSQL database with service-specific schemas.
-   **Image Optimization**: Automatic image resizing and compression on upload (e.g., hero images, gallery images) to optimize performance, with PNG to JPEG conversion for transparency handling.
-   **Menu Dish Image Processing Pipeline** (Standard for all menu images):
    1. AI background removal using rembg library (U2-Net model)
    2. Automatic crop to dish only (removes transparent space)
    3. Square format with dish centered
    4. PNG format with RGBA transparency
    5. Optimized compression (target: 80-110KB per image)
    6. Result: Dish fills 85-98% of frame, transparent background
    7. Display: 450px height (desktop) / 350px (mobile) with minimal padding (0.5rem)
    8. Background: Black gradient (135deg, #0a0a0a → #1a1a1a → #2a2a2a)
    9. Script: `process_new_menu_image.py` for automated processing
-   **Video Optimization**: Responsive video loading based on viewport and connection speed, with poster images for quick display.

### Feature Specifications
-   **Public Website**:
    -   **Homepage**: Hero section (video/image), combined About Us & Table Reservation section, gallery preview. Clean flowing design with no boxed sections.
    -   **Menu Page**: Dynamic menu display by categories, dietary icons, prices, and descriptions. Menu item images are mobile-optimized (140px height on mobile vs 220px desktop) with click-to-enlarge lightbox functionality for better UX.
    -   **Order Page**: When online ordering is disabled, redirects users to app download with clear message "Orders & Delivery Available via App Only" and download buttons for both app stores. Includes alternative actions to view menu or contact restaurant.
    -   **Gallery**: Admin-managed photo gallery.
    -   **Contact**: Modern two-column layout with gradient hero, contact form in elevated card, quick contact methods (phone, email, WhatsApp, social), and branch location cards with Waze/Google Maps navigation buttons. Fully responsive.
    -   **App Download Section**: Simple, clean section on homepage emphasizing app-only ordering:
        -   Minimalist card design with mobile icon
        -   Clear heading: "Orders & Delivery via App Only"
        -   App Store and Google Play download buttons
        -   Optional promotional discount text
        -   Only displays when app store URLs are configured
    -   **Smart App Banner**: Mobile-only dismissible banner that:
        -   Appears at top of page on mobile devices (viewport ≤767px)
        -   Simple message: "Order via App - Download Now"
        -   Remembers dismissal preference via cookie (7 days)
        -   Shows after 1.5 second delay to avoid disrupting initial page load
    -   **Legal & Compliance Pages**:
        -   **Terms of Use**: Dynamic bilingual content
        -   **Accessibility Statement**: Comprehensive IS 5568 / WCAG 2.1 Level AA compliance page with accessibility features list, coordinator contact information, and compliance dates
    -   **Newsletter Subscription**: Footer-integrated newsletter signup with email validation, duplicate checking, resubscription support, and database persistence. Tracks subscription source for analytics.
    -   **Cookie Consent Banner**: GDPR/Israeli-compliant cookie consent banner with LocalStorage persistence, Accept/Decline options, bilingual messaging, and link to privacy policy.
-   **Admin Dashboard**:
    -   **Site Settings**: Modern horizontal tabs interface with 5 tabs at the top:
        -   General: Hero section, about content, site info, social media links, catering homepage section, and full catering page control (hero, gallery, CTA sections)
        -   Branding: Hero images, logo, favicon, brand colors with live preview
        -   Features: Toggle switches for all major features (ordering, delivery, menu, gallery, etc.)
        -   Delivery: Costs, free delivery threshold, estimated times, zones info
        -   Advanced: Analytics IDs, announcement banners, maintenance mode
    -   **General Settings Organization**: All sections in General tab use collapsible Bootstrap accordions for better organization:
        -   Hero Section (open by default)
        -   About Section
        -   Catering - Homepage Section
        -   Catering Page - Full Control (hero, gallery, CTA text)
        -   Careers Page - Full Control (hero, gallery, CTA text)
        -   Site Info & Social Media
    -   **Menu Management**: Modern tabbed interface with:
        -   Categories Tab: Full category management with icons, colors, display order
        -   Items Tab: Quick availability toggle for mobile updates
        -   Import Tab: Excel/Word menu import functionality
        -   Mobile-responsive with touch-friendly availability toggles
    -   **Stock Management**: Advanced inventory management system with horizontal tabs:
        -   Inventory Tab: Full stock item management with categories, units, suppliers
        -   Suppliers Tab: Supplier management with delivery schedules, terms
        -   Orders Tab: Shopping lists and supplier orders
        -   Transactions Tab: Stock movement tracking (in/out, usage, waste)
        -   Reports Tab: Analytics and cost tracking
        -   Mobile-optimized for kitchen staff updates
    -   **Media Management**: Admin upload for hero videos/images and gallery images.
    -   **Catering Gallery Management**: Dedicated admin interface (/admin/catering-gallery) for managing catering page images with upload, delete, and active/inactive toggle controls.
    -   **Careers Management**: Dedicated admin interface (/admin/careers) for managing job positions with add/edit/delete operations, bilingual content support, and display order control.
    -   **Payment Configuration**: Admin panel for managing multiple payment providers and API credentials.
    -   **User Management**: Role-Based Access Control (RBAC) with granular permissions.
    -   **Custom Sections**: Admin-controlled homepage sections supporting text, HTML, and embedded content.
-   **Core Functionality**:
    -   **Online Ordering**: App-only ordering system. When web ordering is disabled (or when delivery is disabled), the order page redirects users to download the mobile app with clear messaging that orders and delivery are exclusively through the app.
    -   **Catering Page**: Minimal, clean catering page (/catering) with:
        -   Hero section with customizable title/subtitle
        -   Gallery section displaying images from dedicated catering gallery (managed separately in admin via direct link in settings)
        -   Dedicated contact form with event-specific fields (event date, event type, guest count)
        -   Form submissions saved to separate CateringContact database table
        -   All text content controlled via admin settings
    -   **Careers Page**: Clean careers page (/careers) mirroring catering page structure with:
        -   Hero section with customizable title/subtitle
        -   Job listings section displaying active positions
        -   Application form with specific fields (name, email, phone, position applied, message)
        -   Form submissions saved to separate CareerContact database table
        -   All text content controlled via admin settings
        -   Admin interface for managing job positions (add/edit/delete)
    -   **Table Reservations**: Integration with external reservation systems.
    -   **Branch Management**: Display with working hours, navigation links, and dynamic branch information.
    -   **Cart System**: Client-side cart management with server-side order processing.

### System Design Choices
-   **Configuration**: Environment variable-based for production settings.
-   **Data Models**: SQLAlchemy models for various entities including:
    -   Core: ContactMessage, Reservation, SiteSettings, CustomSection, TermsOfUse
    -   Menu: MenuCategory (with footer_text, show_in_menu, show_in_order, featured, image_path), MenuItem, MenuSettings
    -   Media: MediaFile, GalleryPhoto
    -   Catering: CateringGalleryImage (dedicated gallery for catering page with caption_he/en, alt_text_he/en, is_active, display_order), CateringContact (name, email, phone, event_date, event_type, guest_count, message, is_read, created_at)
    -   Careers: CareerPosition (title_he/en, description_he/en, requirements_he/en, location_he/en, employment_type_he/en, is_active, display_order), CareerContact (name, email, phone, position_applied, message, is_read, created_at)
    -   Branch: Branch, WorkingHours
    -   Compliance: NewsletterSubscriber (email, name, is_active, subscribed_at, unsubscribed_at, source tracking)
    -   Stock Management: StockCategory, StockItem, StockLevel, StockTransaction, StockAlert, Supplier, ShoppingList, ShoppingListItem, StockSettings, Receipt, ReceiptItem
-   **Database Architecture**: Robust models, default data seeding, and safe migration practices.
-   **Accessibility Compliance**: IS 5568 (Israeli Standard) and WCAG 2.1 Level AA implementation with:
    -   Comprehensive accessibility statement page
    -   ARIA labels throughout forms and interactive elements
    -   Semantic HTML with proper heading hierarchy
    -   Keyboard navigation support with visible focus indicators
    -   Color contrast compliance (4.5:1 minimum ratio)
    -   Screen reader compatibility (JAWS, NVDA)
    -   Full RTL support for Hebrew
    -   Text resizing up to 200% without content loss
-   **Privacy & Consent**: Cookie consent management with LocalStorage persistence, following GDPR and Israeli privacy standards.

## External Dependencies

-   **SMTP Integration**: Configurable SMTP server (e.g., Gmail) for email services.
-   **Bootstrap 5 RTL**: Frontend CSS framework.
-   **Font Awesome 6.4.0**: Icon library.
-   **Google Fonts API**: Playfair Display, Inter, Rubik.
-   **Python Packages**: Flask, Flask-Mail, Flask-WTF, WTForms, SQLAlchemy, Gunicorn.
-   **External Reservation System**: Integration with platforms like `tbit.be`.
-   **Mapping Services**: Waze, Google Maps.