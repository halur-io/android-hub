# Restaurant Platform - Microservices Architecture

## Overview

This project is a scalable and configurable restaurant management platform built with a microservices architecture. It offers a comprehensive solution for restaurant operations, including a mobile-responsive public website for online ordering, menu display, and customer interaction, alongside a robust admin dashboard for dynamic menu management, payment configuration, and operational control. The platform's core vision is to provide a highly flexible solution where business logic is configurable via admin settings, ensuring adaptability and avoiding hardcoded dependencies.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### UI/UX Decisions
-   **Frontend Framework**: Flask-rendered Jinja2 templates (SEO-friendly).
-   **Styling**: Bootstrap 5 RTL with custom CSS, Google Fonts, and Font Awesome 6.4.0.
-   **Color Scheme**: Navy Blue (#1a3a6e) and Red (#dc3545) for the main theme; a parallel "Example2 Theme" uses deep blacks, gold accents, and burgundy highlights for an upscale aesthetic.
-   **Responsive Design**: Mobile-first approach with 100% mobile optimization.
-   **Language Support**: Session-based language switching with full Right-to-Left (RTL) support for Hebrew and English.
-   **Dynamic Visuals**: Incorporates hero videos/images with parallax, animated elements, gradient overlays, SVG dividers, and rotating icon dividers.
-   **Admin Dashboard UI**: Modern horizontal tabs layout with a professional SaaS-style design, modern form components, responsive grid layouts, sticky action bar, and a dedicated admin.css design system. Mobile-optimized pages for stock, menu, and orders.

### Technical Implementations
-   **Backend Framework**: Flask with a modular structure.
-   **Form Handling**: Flask-WTF with WTForms.
-   **Email System**: Flask-Mail.
-   **Security**: CSRF protection.
-   **Logging**: Python logging.
-   **Theme System**: Conditional CSS loading based on a context variable for parallel design versions.
-   **Microservices Architecture**: Core services (Auth, Order, Payment, Delivery, Kitchen, Notification, Configuration) communicating via internal RESTful APIs, WebSockets, Message Queues, and a shared PostgreSQL database.
-   **Image Optimization**: Automatic image resizing, compression, and PNG to JPEG conversion on upload. Menu dish images undergo an AI-powered processing pipeline for background removal, cropping, squaring, and optimized compression with transparent backgrounds.
-   **Video Optimization**: Responsive video loading based on viewport and connection speed.

### Feature Specifications
-   **Public Website**:
    -   **Homepage**: Hero, About Us & Table Reservation, gallery preview.
    -   **Menu Page**: Dynamic menu display with categories, dietary icons, and mobile-optimized images with lightbox functionality.
    -   **Order Page**: Redirects to app download when online ordering is disabled.
    -   **Gallery**: Admin-managed photo gallery.
    -   **Contact**: Two-column layout with form, quick contact methods, and branch location cards.
    -   **App Download Section**: Minimalist section emphasizing app-only ordering with download buttons.
    -   **Smart App Banner**: Mobile-only dismissible banner for app download.
    -   **Legal & Compliance Pages**: Dynamic bilingual Terms of Use and IS 5568 / WCAG 2.1 Level AA Accessibility Statement.
    -   **Newsletter Subscription**: Footer-integrated signup with validation and database persistence.
    -   **Cookie Consent Banner**: GDPR/Israeli-compliant banner with LocalStorage persistence.
-   **Admin Dashboard**:
    -   **Site Settings**: Horizontal tabs for General (hero, about, catering, careers, site info, social media), Branding, Features, Delivery, and Advanced settings (analytics, announcements, maintenance mode). General settings use collapsible accordions.
    -   **Menu Management**: Tabbed interface for categories, items (with quick availability toggle), and Excel/Word import.
    -   **Stock Management**: 
        -   **Simplified Mobile-First Interface** (PRIMARY - `/admin/stock-management`): Clean, elegant interface with neutral hospitality color palette (soft off-white #F7F5F0, charcoal #2F2F2F, muted terracotta #C96F44, sage #6B8F71). Features sticky header with stats (items, suppliers, categories, receipts), horizontal navigation tabs (Items, Suppliers, Categories, **Receipts**), dual view modes (card/list) with segmented control toggle, integrated toolbar with action buttons (no floating buttons), and Excel/CSV export. 100% mobile optimized with touch-friendly design, tighter spacing, and professional minimal aesthetic. View mode persists across tabs via URL parameters. **Stock Quantity Display** (CRITICAL FIX): Server-side aggregation of stock levels across all branches with prominent display showing total_available quantity. Card view shows quantity with fa-boxes icon in terracotta color as first detail row. List view displays quantity in bold within subtitle. Low stock detection triggers red "מלאי נמוך" badge when available < minimum_stock threshold. Backend computes total_current, total_reserved, total_available per StockItem via SQLAlchemy sum aggregation, with branch-level breakdown available for future expandability. **Full CRUD Operations**: Edit routes (`/stock/item/<id>/edit`, `/stock/category/<id>/edit`) with elegant mobile-friendly forms, delete operations with confirmation dialogs, both integrated seamlessly into card and list views. **Receipt Scanning**: Blue camera button in toolbar links to AI-powered receipt scanner (`/admin/receipt-scanner`) using OpenAI Vision API for Hebrew-optimized OCR with intelligent fuzzy matching (rapidfuzz library) to auto-match products to existing stock items (60% confidence threshold). Unmatched items automatically create new stock items linked to the supplier upon approval. Review/approval workflow saves receipts with full supplier information. **Quick Supplier Creation with Auto-Detection**: In-context supplier creation during receipt review via "+ ספק חדש" button that opens a responsive modal (fullscreen on mobile) with minimal required fields (name, optional contact info including phone, email, and address). When supplier doesn't exist in system, OCR-detected supplier details (name, phone, email, address, contact person) are automatically pre-filled in the modal with a blue informational banner explaining the AI-detected values, allowing user to review and confirm before creation. Dynamic AI notice toggles based on field content - shows when pre-filled data exists and fields have values, hides when all fields cleared. AJAX endpoint (`POST /admin/suppliers/quick-create`, CSRF-exempt, login/permission protected) validates uniqueness (case-insensitive), returns 201 on success or 409 on duplicate, auto-selects newly created supplier in dropdown. **Supplier Filter**: Dropdown filter in Items tab to display only items from selected supplier, with filter persistence across view modes and export functionality. **Receipts Tab** (NEW): Supplier-grouped view organizing all receipts by supplier with analytics cards showing receipt count, total spending, and latest receipt date. Includes receipts without assigned suppliers under "ללא ספק" group. Each supplier card displays aggregated data and links to detailed receipt list. Empty state with "Scan Receipt" call-to-action. **Custom Fields System**: Flexible metadata system allowing creation of custom fields (dropdown, text, number, date, checkbox) for receipts. Field definitions include validation rules (min/max, regex, date ranges), scoped assignments (global/branch/supplier), and audit tracking. Models: CustomFieldDefinition (field templates), CustomFieldAssignment (scoping), ReceiptCustomFieldValue (values per receipt), ReceiptCustomFieldAudit (change history). Receipt model enhanced with created_by and processed_by user tracking fields.
        -   **Legacy Advanced Interface** (`/admin/stock-management-old`): Full-featured system with tabs for Inventory, Suppliers, Orders, Transactions, and Reports. Includes table/card view toggles and complete editing capabilities.
    -   **Media Management**: Admin upload for hero videos/images and gallery images.
    -   **Messages Management**: Unified interface for contact, catering, and career messages with unread counts and email forwarding.
    -   **Catering Gallery Management**: Dedicated interface for managing catering page images.
    -   **Careers Management**: Dedicated interface for managing job positions.
    -   **Payment Configuration**: Admin panel for managing payment providers.
    -   **User Management**: Role-Based Access Control (RBAC).
    -   **Custom Sections**: Admin-controlled homepage sections.
-   **Core Functionality**:
    -   **Online Ordering**: App-only system; web order page redirects to app download.
    -   **Catering Page**: Customizable page with hero, gallery, and dedicated contact form for inquiries.
    -   **Careers Page**: Customizable page with hero, job listings, and application form.
    -   **Table Reservations**: Integration with external systems.
    -   **Branch Management**: Display of branch information, working hours, and navigation links.
    -   **Cart System**: Client-side cart with server-side processing.

### System Design Choices
-   **Configuration**: Environment variable-based.
-   **Data Models**: SQLAlchemy models for Core, Menu, Media, Catering, Careers, Branch, Compliance, and Stock Management entities, including detailed fields for each.
-   **Database Architecture**: Robust models, default data seeding, and safe migration practices.
-   **Accessibility Compliance**: IS 5568 and WCAG 2.1 Level AA implementation with ARIA labels, semantic HTML, keyboard navigation, color contrast, screen reader compatibility, full RTL support, and text resizing.
-   **Privacy & Consent**: Cookie consent management with LocalStorage persistence.

## External Dependencies

-   **SMTP Integration**: Configurable SMTP server (e.g., Gmail).
-   **Bootstrap 5 RTL**: Frontend CSS framework.
-   **Font Awesome 6.4.0**: Icon library.
-   **Google Fonts API**: Playfair Display, Inter, Rubik.
-   **Python Packages**: Flask, Flask-Mail, Flask-WTF, WTForms, SQLAlchemy, Gunicorn.
-   **External Reservation System**: Integration with platforms like `tbit.be`.
-   **Mapping Services**: Waze, Google Maps.