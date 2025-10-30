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

-   **Complete Frontend Redesign**: Replaced React SPA with Flask-rendered templates for better SEO, simpler maintenance, and tighter integration with admin panel.
-   **Database Enhancements**:
    -   Extended `SiteSettings` model with feature toggles (`enable_online_ordering`, `enable_english_language`, `enable_delivery`, `enable_pickup`).
    -   Added `PaymentConfiguration` model for managing multiple payment providers.
    -   Leveraged existing `Order` and `OrderItem` models from `services/order/order_service.py`.
-   **Public Website Structure**: Created 5 main pages (Home, Menu, Order, Gallery, Contact) all controlled via admin panel settings.
-   **Cart System**: Client-side cart management using localStorage with server-side order processing ready for integration.
-   **Mobile-First Design**: 100% mobile-responsive layout following design guidelines in `design_guidelines.md`.