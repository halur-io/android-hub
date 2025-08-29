# Sumo Restaurant Website

## Overview

This is a modern restaurant website for Sumo Asian Kitchen, featuring a React frontend with Flask backend API and a comprehensive admin panel. The application provides a bilingual (Hebrew/English) interface with full RTL support, WhatsApp/phone integration, dynamic menu display, reservation system, and complete content management capabilities through the admin dashboard.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

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