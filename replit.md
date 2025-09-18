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

### September 18, 2025 - Solved Hebrew RTL Printing System
- **Perfect RTL Alignment**: Completely redesigned print system to fix persistent Hebrew right-to-left printing issues
  - Created new simple RTL printing functions: generateSimpleRTLPrint(), generateSimpleColumnsRTL(), openSimplePrintWindow()
  - Direct HTML generation with inline RTL styles that cannot be overridden by browser defaults
  - Proper page margins: 15mm 0mm 15mm 15mm (zero right margin for perfect Hebrew alignment)
  - Simple table-based column layout instead of complex CSS grid for print compatibility
- **Security Enhancement**: Added HTML escaping (escapeHtml function) to prevent XSS in print content
  - All user inputs (task names, group names, shift manager, dates) properly escaped
  - Secure template string interpolation throughout print system
- **Simplified Print Pipeline**: Replaced complex multi-layer print functions with direct, reliable approach
  - Clean HTML document generation with minimal CSS conflicts
  - Native browser printing with automatic print dialog
  - Cross-browser compatible approach for Hebrew text rendering

### September 8, 2025 - Complete Stock Management System with Error Resolution
- **Fixed All 500 Errors**: Resolved critical SQLAlchemy query issues in all stock management endpoints
  - Changed tuple-returning joins to proper model relationships for template access
  - Fixed stock levels, transactions, alerts, and analytics data access patterns
  - All 9 stock management endpoints now working without internal server errors
- **Enhanced Navigation**: Made all action buttons functional with proper JavaScript navigation
  - Branch-aware navigation preserving selected branch across all stock sections
  - Clickable cards directing to appropriate stock management sections
- **Robust Analytics**: Added comprehensive stock analytics with proper calculations
  - Real-time statistics for low stock, out of stock, and total inventory value
  - Enhanced alert system with detailed severity-based statistics
- **Database Query Optimization**: Improved all stock management database queries
  - Proper joins using SQLAlchemy relationships instead of raw tuple queries
  - Consistent data access patterns across all templates

### September 7, 2025 - Clean & Simplified Checklist Management Interface
- **Card-Based Layout**: Redesigned main checklist page with clean, modern interface
  - 3 primary action cards: Create Checklist, Saved Checklists, and Management
  - Replaced cluttered button rows with organized card system
  - Gradient backgrounds and hover effects for better visual hierarchy
  - Mobile-responsive design with touch-friendly interactions
- **Smart Dropdown Menu**: Management functions organized in collapsible dropdown
  - Add Task, Create Task Group, Templates, and Export functions
  - Click-outside-to-close functionality for better UX
  - Clean separation of primary and secondary actions
- **Contextual Task Controls**: Intelligent control panel that appears only when needed
  - Shows when tasks are selected for bulk operations
  - Compact action buttons for select all, clear, mark complete, and delete
  - Real-time counter showing number of selected tasks
- **Improved Filter Section**: Dedicated area for shift filtering with clear visual separation
  - Organized shift tabs in contained box layout
  - Better visual hierarchy with proper spacing and typography
  - RTL-optimized layout maintaining Hebrew text flow

### September 5, 2025 - Mobile-Responsive Admin Panel with Comprehensive Role-Based Access Control
- **Mobile-First Responsive Design**: Complete mobile responsiveness for admin dashboard
  - Fully responsive grid layouts that adapt to mobile, tablet, and desktop screens
  - Touch-friendly navigation with mobile sidebar overlay system
  - Optimized form inputs and buttons for mobile devices
  - iOS zoom prevention and proper viewport handling
  - Landscape orientation support with adjusted layouts
- **Comprehensive Roles & Permissions System**: Complete RBAC implementation controlling all features
  - **Role Model**: Full role management with system/custom role distinction
  - **Permission Model**: Granular permissions organized by functional categories
  - **User-Role Relationships**: Many-to-many relationships with proper permission inheritance
  - **7 Default Roles**: Superadmin, Admin, Manager, Kitchen Staff, Delivery Manager, Cashier, Viewer
  - **25+ Granular Permissions**: Covering all system features (users, orders, kitchen, delivery, payments, menu, settings, etc.)
- **Permission Protection System**: Route-level security implementation
  - **Advanced Decorators**: require_permission, require_role, superadmin_required, require_any_permission
  - **Route Protection**: All admin routes now protected with appropriate permission checks
  - **Template Utilities**: Helper functions for permission checking in templates
  - **Error Handling**: Graceful permission denied handling with Hebrew messages
- **Role Management Interface**: Professional admin UI for role administration
  - **Role Listing**: Visual cards showing role details, permissions count, and user count
  - **Create/Edit Roles**: Full CRUD interface for role management with permission assignment
  - **Permission Categories**: Organized permission assignment by functional areas
  - **System Role Protection**: Prevents deletion of critical system roles
  - **Mobile-Responsive Design**: All role management screens fully mobile-optimized
- **Enhanced User Management**: Extended user system with role assignment
  - **Permission-Protected Routes**: All user management routes now require appropriate permissions
  - **Role Integration**: Users can be assigned multiple roles with inherited permissions
  - **Advanced User Model**: Extended with role relationships and permission checking methods
- **Secure Database Architecture**: Robust data models with proper relationships
  - **Association Tables**: Proper many-to-many relationships between users-roles and roles-permissions  
  - **Default Data Seeding**: Automatic creation of roles and permissions on system startup
  - **Migration Safety**: Safe database schema updates with error handling

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