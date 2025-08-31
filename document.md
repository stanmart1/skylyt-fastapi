Task 1: Document Management System Setup (Updated)
Step 1.1: Database Schema Design

Create documents table with fields: id, entity_type (car/hotel/guest/driver), entity_id, document_type, expiry_date, created_at, updated_at
Create document_types table for storing document categories
Add foreign keys linking to cars, hotels, users tables

Step 1.2: Backend API Endpoints

Create CRUD endpoints for document management
Add endpoint to fetch expiring documents (within 7 days)
Create endpoint for bulk document expiry check

Step 1.3: Dual Notification System

Create background job/scheduler to check daily for expiring documents
Build email notification service (using FastAPI background tasks or Celery)
Create in-app notification system with notification table: id, user_id, message, type, read_status, created_at
Add endpoints to fetch/mark notifications as read

Step 1.4: Frontend Components

Create document list component
Add document form for adding/editing documents
Create expiry alerts dashboard for admin panel
Add notification bell/dropdown in header for in-app notifications

Task 2: Driver Management System (Updated)
Step 2.1: Driver Database Setup

Create drivers table: id, name, email, phone, status (available/busy/on_leave), location (city: Port Harcourt/Lagos/Abuja), created_at, updated_at
Link drivers table to documents table for license tracking
Add location field for assignment matching

Step 2.2: Dual Registration System

Create public driver registration endpoint (self-registration)
Create admin-only driver creation endpoint
Add email verification for self-registered drivers
Include location selection in registration process

Step 2.3: Driver License Management

Add license document tracking for each driver
Include license expiry notifications in existing dual notification system

Step 2.4: Frontend Driver Management

Create public driver registration page
Add admin driver creation form in admin panel
Create driver list/profile views
Add location filter/management in driver interfaces

Task 3: Driver Assignment System (Updated)
Step 3.1: Assignment Database Schema

Create driver_assignments table: id, booking_id, driver_id, car_id, assignment_location, status (pending/accepted/rejected), assigned_at, responded_at
Add foreign keys to existing bookings and cars tables
Include location field for assignment tracking

Step 3.2: Location-Based Assignment Logic

Create endpoint to fetch available drivers by location (same city as booking)
Add assignment endpoint with location matching logic
Create endpoints for drivers to accept/reject assignments
Add automatic filtering: only show assignments in driver's registered location

Step 3.3: Assignment Workflow

Build dual notification system for assignment alerts (email + in-app)
Create assignment history tracking
Add automatic status updates based on driver responses
Include location information in all assignment communications

Step 3.4: Frontend Assignment Interface

Create admin assignment panel with location filters
Build driver notification/response interface showing only location-relevant assignments
Add assignment status tracking views with location context

Task 4: Car Servicing Management (Updated)
Step 4.1: Service Database Schema

Create car_services table: id, car_id, service_type (maintenance/repair), service_date, next_service_date, description, cost, location, created_at
Create service_types table for categorizing services
Include service location tracking

Step 4.2: Manual Service Tracking Backend

Create endpoints for manually recording car services
Add service history endpoints
Create manual service scheduling endpoints (admin sets next service date)
Include overdue service in dual notification system

Step 4.3: Manual Service Management

Add functionality for admin to manually set next service dates
Include service reminders in dual notification system
Create service calendar for manual scheduling

Step 4.4: Frontend Service Management

Create service recording forms with manual date selection
Add service history views
Build manual service scheduling interface for admin

Additional Implementation Details:
Email Service Setup:

Configure email service (SMTP settings in FastAPI)
Create email templates for different notification types
Add email sending functionality to notification service

Location Management:

Add location validation (must be one of: Port Harcourt, Lagos, Abuja)
Create location-based filtering throughout the system
Ensure assignment logic respects location boundaries

Driver Self-Registration Flow:

Public registration page → email verification → admin approval (optional) → active driver
Include terms and conditions acceptance
Add profile completion requirements

Updated Implementation Priority:

Document Management with Dual Notifications
Driver Management with Self-Registration + Location
Location-Based Driver Assignment System
Manual Car Servicing Management