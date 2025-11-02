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
-   **Microservices Architecture**:
    -   **Core Services**: Auth, Order, Payment, Delivery, Kitchen, Notification, and Configuration services.
    -   **Communication**: Internal RESTful APIs, WebSockets for real-time updates, Message Queue for inter-service communication, and a shared PostgreSQL database with service-specific schemas.
-   **Image Optimization**: Automatic image resizing and compression on upload (e.g., hero images, gallery images) to optimize performance, with PNG to JPEG conversion for transparency handling.
-   **Video Optimization**: Responsive video loading based on viewport and connection speed, with poster images for quick display.

### Feature Specifications
-   **Public Website**:
    -   **Homepage**: Hero section (video/image), combined About Us & Table Reservation section, gallery preview. Clean flowing design with no boxed sections.
    -   **Menu Page**: Dynamic menu display by categories, dietary icons, prices, and descriptions.
    -   **Order Page**: When online ordering is disabled, displays an engaging "Coming Soon" message with rocket animation, feature preview cards, and alternative CTA buttons (Browse Menu, Call to Order). Professional and positive user experience.
    -   **Gallery**: Admin-managed photo gallery.
    -   **Contact**: Modern two-column layout with gradient hero, contact form in elevated card, quick contact methods (phone, email, WhatsApp, social), and branch location cards with Waze/Google Maps navigation buttons. Fully responsive.
    -   **Legal & Compliance Pages**:
        -   **Terms of Use**: Dynamic bilingual content
        -   **Accessibility Statement**: Comprehensive IS 5568 / WCAG 2.1 Level AA compliance page with accessibility features list, coordinator contact information, and compliance dates
    -   **Newsletter Subscription**: Footer-integrated newsletter signup with email validation, duplicate checking, resubscription support, and database persistence. Tracks subscription source for analytics.
    -   **Cookie Consent Banner**: GDPR/Israeli-compliant cookie consent banner with LocalStorage persistence, Accept/Decline options, bilingual messaging, and link to privacy policy.
-   **Admin Dashboard**:
    -   **Site Settings**: Modern horizontal tabs interface with 5 tabs at the top:
        -   General: Hero section, about content, site info, social media links
        -   Branding: Hero images, logo, favicon, brand colors with live preview
        -   Features: Toggle switches for all major features (ordering, delivery, menu, gallery, etc.)
        -   Delivery: Costs, free delivery threshold, estimated times, zones info
        -   Advanced: Analytics IDs, announcement banners, maintenance mode
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
    -   **Payment Configuration**: Admin panel for managing multiple payment providers and API credentials.
    -   **User Management**: Role-Based Access Control (RBAC) with granular permissions.
    -   **Custom Sections**: Admin-controlled homepage sections supporting text, HTML, and embedded content.
-   **Core Functionality**:
    -   **Online Ordering**: Enable/disable via admin settings, configurable minimum order and tax rate. When disabled (or when delivery is disabled), the order page displays a professional disabled message with action buttons, and all "Add to Order" buttons are automatically removed from the menu page.
    -   **Table Reservations**: Integration with external reservation systems.
    -   **Branch Management**: Display with working hours, navigation links, and dynamic branch information.
    -   **Cart System**: Client-side cart management with server-side order processing.

### System Design Choices
-   **Configuration**: Environment variable-based for production settings.
-   **Data Models**: SQLAlchemy models for various entities including:
    -   Core: ContactMessage, Reservation, SiteSettings, CustomSection, TermsOfUse
    -   Menu: MenuCategory (with footer_text, show_in_menu, show_in_order, featured, image_path), MenuItem, MenuSettings
    -   Media: MediaFile, GalleryPhoto
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