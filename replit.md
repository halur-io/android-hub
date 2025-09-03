# Restaurant Platform - Microservices Architecture

## Overview

This is a comprehensive restaurant management platform built with microservices architecture, featuring:
- **Ordering System**: Complete takeaway/delivery management with branch selection
- **Payment Gateway**: Multi-provider support (MAX, Bit, Cash, Apple Pay, Google Pay)
- **Driver Management**: Real-time tracking and assignment
- **Kitchen Display System**: Order flow management
- **Admin Dashboard**: Full control over all services
- **Customer Portal**: Responsive ordering interface with SMS verification

The platform is built for scalability with no hardcoded business logic - everything is configurable through the admin settings.

## User Preferences

Preferred communication style: Simple, everyday language.

## Microservices Architecture

### Core Services
1. **Auth Service** - Phone/SMS verification, user accounts, JWT tokens
2. **Order Service** - Order processing, status management, notifications
3. **Payment Service** - MAX gateway integration, payment processing
4. **Delivery Service** - Driver management, zone configuration, tracking
5. **Kitchen Service** - Order queue, preparation tracking, printer integration
6. **Notification Service** - SMS, WhatsApp, email, real-time updates
7. **Configuration Service** - Central settings for all services

### Communication
- **Internal APIs**: RESTful endpoints between services
- **Real-time**: WebSocket for live updates
- **Message Queue**: Order flow between services
- **Shared Database**: PostgreSQL with service-specific schemas

## Recent Changes

### September 3, 2025 - Enhanced Hebrew Checklist System with Templates & Group Tasks
- **Task Template System**: Save and reuse task board configurations
  - Save current tasks as reusable templates by shift type
  - Load templates to quickly populate tasks for any shift
  - Template management with descriptions and default settings
  - One-click template application without losing existing tasks
- **Group Task Creation**: Bulk add related tasks efficiently
  - Add multiple related tasks at once (up to 20 per group)
  - Shared category, priority, frequency, and shift settings
  - Simple textarea input - one task per line
  - Perfect for safety checks, cleaning routines, inventory lists
- **User-Friendly Notifications**: Professional notification system
  - Beautiful sliding notifications with emojis and clear messages
  - Success, error, and info message types with auto-dismiss
  - Contextual error messages explaining what went wrong
  - No more basic alerts - smooth UX throughout
- **Comprehensive Task Management System**: Complete checklist management for restaurant operations
  - Shift-based task organization (פתיחת בוקר, משמרת ערב, סגירה, משמרת לילה)
  - Hebrew interface with RTL support throughout
  - Category system: מטבח, ניקיון, שירות, מלאי, בטיחות, אחר
  - Priority levels: נמוכה, בינונית, גבוהה
  - Frequency options: יומי, שבועי, חודשי, לפי הצורך
- **Professional Printable Checklists**: Print-ready task lists for daily operations
  - Branch selection integration
  - Date and shift manager name fields
  - Organized by categories with checkboxes
  - Signature areas for accountability
  - Professional Hebrew formatting
- **Full CRUD API**: Complete backend functionality
  - RESTful endpoints: GET, POST, PUT, DELETE for tasks and templates
  - Database models: ChecklistTask, GeneratedChecklist, TaskTemplate
  - Sample data system for demonstration
- **Admin Panel Integration**: Seamless integration with existing admin system
  - New sidebar menu item: "רשימות משימות"
  - Modal-based task editing interface
  - Real-time task filtering by shift type
- **Database Architecture**: Enhanced models for task management and template operations

### August 29, 2025 - Advanced Menu Management System
- **Customizable Dietary Properties**: Complete CRUD system for managing dietary properties (vegetarian, vegan, etc.)
  - Dynamic property creation with custom names, icons, colors, and descriptions
  - Visual icon selector and color picker interfaces
  - Drag-and-drop reordering for display priority
  - Integration with menu item editing interface
- **Drag-and-Drop Menu Reordering**: Professional sorting system for complete menu organization
  - Category reordering with visual interface
  - Menu item reordering within and between categories
  - Real-time save functionality with progress indicators
  - Visual feedback and smooth animations
- **CSV/Excel Import System**: Comprehensive bulk import functionality
  - Support for CSV, XLS, and XLSX file formats
  - Intelligent column mapping with auto-detection
  - Preview interface with highlighting
  - Error handling and validation with detailed feedback
  - Sample file generation for user guidance
- **Enhanced Database Models**: Many-to-many relationships for dietary properties
- **Professional UI/UX**: Mobile-responsive interfaces with modern design patterns

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with functional components and hooks
- **Build Tool**: Vite for fast development and optimized production builds
- **Styling**: CSS Modules with CSS variables for consistent theming
- **Typography**: Google Fonts (Heebo) optimized for Hebrew/English text
- **Icons**: Font Awesome 6.4.0 for UI icons
- **Responsive Design**: Mobile-first approach with CSS Grid and Flexbox
- **Language Support**: Real-time language switching with localStorage persistence
- **RTL Support**: Full right-to-left support for Hebrew with dynamic direction switching

### Backend Architecture
- **Web Framework**: Flask with modular structure
- **Form Handling**: Flask-WTF with WTForms for form validation and CSRF protection
- **Email System**: Flask-Mail for sending contact and reservation notifications
- **Security**: CSRF protection enabled, environment-based configuration
- **Logging**: Python logging configured for debugging
- **Route Organization**: Separated routes module for better code organization

### Data Models
- **ContactMessage**: Stores customer contact form submissions
- **Reservation**: Manages table reservation requests
- **Database Schema**: SQLAlchemy models with timestamp tracking

### Configuration Management
- Environment variable-based configuration for production deployment
- Configurable email settings (SMTP server, credentials, TLS)
- Debug mode and secret key management
- Default fallback values for development

## External Dependencies

### Email Services
- **SMTP Integration**: Configurable SMTP server (default: Gmail)
- **Email Templates**: Hebrew-language email notifications for contact forms and reservations
- **Mail Configuration**: Environment-based email credentials and server settings

### Frontend Libraries
- **Bootstrap 5 RTL**: CSS framework with right-to-left language support
- **Font Awesome 6.4.0**: Icon library for UI elements
- **Google Fonts API**: Hebrew font families (Heebo, Assistant)

### Python Packages
- **Flask**: Core web framework
- **Flask-Mail**: Email sending functionality
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation and rendering
- **SQLAlchemy**: Database ORM (models defined but database connection not yet implemented)

### Development Tools
- **Logging**: Built-in Python logging for error tracking and debugging
- **Environment Variables**: Configuration management for different deployment environments