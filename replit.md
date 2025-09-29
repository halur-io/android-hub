# Restaurant Platform - Microservices Architecture

## Overview

This project is a comprehensive restaurant management platform built with a microservices architecture. Its purpose is to provide a scalable and configurable solution for restaurant operations. Key capabilities include:

-   **Ordering System**: Manages takeaway/delivery with branch selection.
-   **Payment Gateway**: Supports multiple payment providers (MAX, Bit, Cash, Apple Pay, Google Pay).
-   **Driver Management**: Features real-time tracking and assignment.
-   **Kitchen Display System**: Streamlines order flow.
-   **Admin Dashboard**: Provides full control over all services.
-   **Customer Portal**: Offers a responsive ordering interface with SMS verification.

The platform prioritizes scalability and flexibility, with all business logic configurable via admin settings to avoid hardcoding.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### UI/UX Decisions
-   **Frontend Framework**: React 18 with functional components and hooks.
-   **Styling**: CSS Modules with CSS variables, Google Fonts (Heebo) for typography, Font Awesome 6.4.0 for icons.
-   **Responsive Design**: Mobile-first approach using CSS Grid and Flexbox.
-   **Language Support**: Real-time language switching with full Right-to-Left (RTL) support for Hebrew.

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
-   **Stock Management**: Comprehensive system with real-time analytics, alerts, and optimized database queries.
-   **Checklist System**: Shift-based task organization with templates, group task creation, and printable checklists.
-   **Menu Management**: Customizable dietary properties, drag-and-drop reordering, and CSV/Excel import functionality.
-   **Admin Panel**: Mobile-responsive design with comprehensive Role-Based Access Control (RBAC) and granular permissions.

### System Design Choices
-   **Configuration**: Environment variable-based for production, configurable email settings, debug mode, and secret key management.
-   **Data Models**: SQLAlchemy models for ContactMessage and Reservation, with timestamp tracking.
-   **Database Architecture**: Robust models with proper relationships (e.g., many-to-many for roles and permissions), default data seeding, and safe migration practices.

## External Dependencies

-   **SMTP Integration**: Configurable SMTP server (default: Gmail) for email services.
-   **Bootstrap 5 RTL**: Frontend CSS framework.
-   **Font Awesome 6.4.0**: Icon library.
-   **Google Fonts API**: For Hebrew font families (Heebo, Assistant).
-   **Python Packages**: Flask, Flask-Mail, Flask-WTF, WTForms, SQLAlchemy.