# Skylyt Luxury - Technical Handover Document

## Project Overview

**Project Name**: Skylyt Luxury Travel Platform  
**Version**: 1.0.0  
**Handover Date**: December 2024  
**Platform Type**: Full-stack web application (Hotel & Car Rental Booking)

## System Architecture

### Technology Stack

#### Backend (FastAPI)
- **Framework**: FastAPI 0.104.1 with Python 3.11+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Caching**: Redis/Dragonfly for session management
- **Authentication**: JWT-based with RBAC (Role-Based Access Control)
- **Background Tasks**: Celery for asynchronous processing
- **API Documentation**: Auto-generated OpenAPI/Swagger

#### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for development and production builds
- **UI Library**: Radix UI components with shadcn/ui design system
- **Styling**: Tailwind CSS with custom animations
- **State Management**: React Context API with custom hooks
- **HTTP Client**: Custom API service with fetch API
- **Routing**: React Router v6

### Infrastructure
- **Containerization**: Docker with multi-stage builds
- **Environment Management**: Separate configs for dev/staging/production
- **Database Migrations**: Alembic for schema versioning
- **Monitoring**: Prometheus metrics and health checks

## Application Features

### Core Functionality
1. **Hotel Booking System**
   - Real-time availability checking
   - Advanced search with 15+ filters
   - Dynamic pricing with currency conversion
   - Image management and gallery system
   - Amenity filtering and location-based search

2. **Car Rental System**
   - Fleet management with status tracking
   - Vehicle maintenance scheduling
   - Document management (insurance, registration)
   - Pricing configuration and availability management

3. **Booking Management**
   - Individual hotel and car bookings
   - Guest booking support (no account required)
   - Booking modification and cancellation
   - Email confirmations and notifications

4. **Payment Processing**
   - **5 Payment Gateways**: Stripe, Flutterwave, Paystack, PayPal, Bank Transfer
   - Multi-currency support with real-time conversion
   - Bank transfer with proof upload and manual verification
   - Automated refund processing

5. **User Management**
   - Role-based access control (Admin, Driver, Customer)
   - Profile management and preferences
   - Booking history and favorites system
   - Password reset and email verification

6. **Admin Dashboard**
   - Real-time business metrics and KPIs
   - Customer account management
   - Booking oversight and modification
   - Payment verification and processing
   - Fleet and hotel inventory management
   - Google Analytics integration

### Analytics & Reporting
- **Google Analytics Integration**: Advanced tracking and business intelligence
- **Real-time Metrics**: Dashboard with live business data
- **Financial Reporting**: Revenue tracking, payment analytics
- **User Analytics**: Customer behavior and conversion tracking
- **Export Capabilities**: CSV/PDF report generation

## Database Schema

### Core Models
- **User**: Customer accounts with authentication and preferences
- **Hotel**: Hotel inventory with amenities, pricing, and availability
- **Car**: Vehicle fleet with maintenance tracking and documentation
- **Booking**: Reservation management with status tracking (pending, confirmed, cancelled, payment_pending)
- **Payment**: Transaction records with multi-gateway support (pending, processing, completed, failed, refunded)
- **Driver**: Driver assignment and trip status management
- **Notification**: User communication and alerts
- **PaymentProof**: Bank transfer proof uploads and verification

### Key Relationships
- Users have multiple bookings and payments
- Bookings link to hotels or cars with payment records
- Hotels and cars have image galleries and feature sets
- RBAC system with roles and permissions

## API Endpoints

### Authentication
- `POST /auth/login` - User authentication
- `POST /auth/register` - User registration
- `POST /auth/forgot-password` - Password reset request
- `POST /auth/reset-password` - Password reset completion

### Hotels
- `GET /hotels/search` - Hotel search with filters
- `GET /hotels/{id}` - Hotel details
- `GET /hotels/featured` - Featured hotels for homepage

### Cars
- `GET /cars/search` - Car search with filters
- `GET /cars/{id}` - Car details
- `GET /cars/featured` - Featured cars for homepage

### Bookings
- `POST /bookings` - Create new booking (supports guest bookings)
- `GET /bookings` - User booking history
- `GET /bookings/{id}` - Get booking details
- `PUT /bookings/{id}/update` - Update booking details
- `PUT /bookings/{id}/status` - Update booking status
- `DELETE /bookings/{id}` - Cancel booking
- `POST /bookings/{id}/complete` - Mark booking as completed
- `POST /bookings/{id}/resend-confirmation` - Resend confirmation email
- `GET /bookings/summary/{item_type}/{item_id}` - Get booking summary with currency conversion

### Payments
- `POST /payments/initialize` - Initialize payment with selected method
- `POST /payments/process` - Process payment
- `POST /payments/upload-proof` - Bank transfer proof upload
- `POST /payments/complete/{booking_id}` - Complete payment process
- `GET /payments/verify/{payment_id}` - Verify payment status
- `GET /payments/{payment_id}` - Get payment details
- `GET /payments/proof/{payment_id}` - Get proof of payment file
- `POST /payments/{payment_id}/verify` - Manual payment verification
- `POST /payments/{payment_id}/refund` - Process payment refund
- `PUT /payments/{payment_id}/status` - Update payment status
- `GET /payments/booking/{booking_id}/status` - Get payment status for booking

### Admin
- `GET /admin/stats` - Dashboard statistics with real-time metrics
- `GET /admin/bookings` - All bookings management with filtering
- `GET /admin/bookings/{id}` - Get booking details
- `POST /admin/bookings/{id}/resend-confirmation` - Resend booking confirmation
- `POST /admin/bookings/{id}/cancel` - Cancel booking with reason
- `GET /admin/payments` - Payment oversight with filtering
- `GET /admin/payments/{id}` - Get payment details
- `POST /admin/payments/{id}/verify` - Verify payment
- `PUT /admin/payments/{id}/status` - Update payment status
- `GET /admin/system/health` - System health monitoring
- `GET /admin/recent-activity` - Recent system activity

## Environment Configuration

### Required Environment Variables

#### Backend (.env)
```
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/skylyt
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=skylyt
DATABASE_USER=user
DATABASE_PASSWORD=password

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Payment Gateways
STRIPE_SECRET_KEY=sk_test_...
FLUTTERWAVE_SECRET_KEY=FLWSECK_TEST-...
PAYSTACK_SECRET_KEY=sk_test_...
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-client-secret

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@skylyt.com

# Frontend URL
FRONTEND_URL=https://skylytluxury.com
```

#### Frontend (.env)
```
VITE_API_BASE_URL=https://api.skylytluxury.com
VITE_APP_ENV=production
VITE_ONESIGNAL_APP_ID=your-onesignal-app-id
ONE_SIGNAL_API_KEY=your-onesignal-api-key
```

## Deployment Instructions

### Backend Deployment
1. **Prerequisites**
   - Python 3.11+
   - PostgreSQL 15+
   - Redis 7+

2. **Installation**
   ```bash
   cd skylyt-travelhub-backend
   pip install -r requirements.txt
   ```

3. **Database Setup**
   ```bash
   alembic upgrade head
   python scripts/create_db.py
   ```

4. **Run Application**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Frontend Deployment
1. **Prerequisites**
   - Node.js 18+
   - npm or yarn

2. **Installation**
   ```bash
   cd skylyt-frontend
   npm install
   ```

3. **Build for Production**
   ```bash
   npm run build
   ```

4. **Serve Static Files**
   - Deploy `dist/` folder to web server
   - Configure reverse proxy to backend API

### Docker Deployment
```bash
# Backend
docker build -t skylyt-backend ./skylyt-travelhub-backend
docker run -p 8000:8000 skylyt-backend

# Frontend
docker build -t skylyt-frontend ./skylyt-frontend
docker run -p 3000:3000 skylyt-frontend
```

## Admin Account Details

### Default Admin Access
- **Email**: admin@user.com
- **Password**: User123
- **Role**: Administrator
- **Permissions**: Full system access

### Admin Capabilities
- Customer account management
- Booking oversight and modification
- Payment verification and processing
- Fleet and hotel inventory management
- Business analytics and reporting
- System settings configuration

## Payment Gateway Configuration

### Stripe
- **Purpose**: International credit/debit card processing
- **Configuration**: Add secret key to environment variables
- **Webhook**: Configure webhook endpoint for payment confirmations

### Flutterwave
- **Purpose**: African payment methods and mobile money
- **Configuration**: Add public and secret keys
- **Supported**: Nigeria, Ghana, Kenya, South Africa

### Paystack
- **Purpose**: Nigerian payment solutions
- **Configuration**: Add public and secret keys
- **Features**: Bank transfer, USSD, QR codes

### PayPal
- **Purpose**: International payments
- **Configuration**: Add client ID and secret
- **Mode**: Sandbox for testing, live for production

### Bank Transfer
- **Purpose**: Direct bank transfers with manual verification
- **Process**: Customer uploads proof, admin verifies manually
- **Configuration**: Set bank account details in admin settings

## Security Considerations

### Authentication & Authorization
- JWT tokens with configurable expiration
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Email verification for new accounts

### Data Protection
- SQL injection prevention with parameterized queries
- XSS protection with input sanitization
- CORS configuration for cross-origin requests
- HTTPS enforcement in production

### File Upload Security
- File type validation and size limits
- Secure filename generation
- Path traversal prevention
- Malware scanning (recommended for production)

## Monitoring & Maintenance

### Health Checks
- `/health` endpoint for system status
- Database connection monitoring
- Redis connectivity checks
- External API status verification

### Logging
- Structured logging with different levels
- Error tracking and alerting
- Performance monitoring
- User activity logging

### Backup Strategy
- Daily automated database backups
- File upload backups
- Configuration backups
- Recovery procedures documented

## Known Issues & Limitations

### Current Limitations
1. **Multi-Currency Display Only**: Prices stored in base currency (NGN), converted for display
2. **Manual Bank Transfer Verification**: Requires admin approval for bank transfers
3. **Web-Only Platform**: Responsive web design, no native mobile applications
4. **Basic Bundle Features**: Bundle booking exists in model but not fully implemented in UI
5. **Driver Assignment**: Driver model exists but limited integration in booking flow

### Booking Status Types
- **Pending**: Awaiting confirmation or payment
- **Confirmed**: Booking approved and payment completed
- **Payment Pending**: Booking created, awaiting payment verification
- **Cancelled**: Booking cancelled by customer or admin

### Trip Status Types (for car rentals with drivers)
- **Pending**: Trip not yet started
- **En Route**: Driver on the way to pickup
- **In Progress**: Trip currently active
- **Completed**: Trip finished successfully
- **Cancelled**: Trip cancelled

### Payment Status Types
- **Pending**: Awaiting processing or verification
- **Processing**: Currently being verified (especially bank transfers)
- **Completed**: Payment successfully processed
- **Failed**: Payment processing failed
- **Refunded**: Payment refunded to customer (partial or full)

### Refund Status Types
- **None**: No refund requested or processed
- **Partial**: Partial refund processed
- **Full**: Full refund processed

### Recommended Improvements
1. **Multi-Currency Storage**: Store prices in multiple currencies instead of conversion-only
2. **Automated Bank Verification**: API integration with banks for instant verification
3. **Mobile Application**: React Native or Flutter native mobile app
4. **Advanced Analytics**: Custom analytics dashboard beyond Google Analytics
5. **Real-time Notifications**: WebSocket implementation for live updates
6. **Bundle UI Implementation**: Complete the bundle booking user interface
7. **Driver Integration**: Full driver assignment and tracking system

## Support & Maintenance

### Regular Maintenance Tasks
- **Daily**: Monitor system health, verify payments, respond to support
- **Weekly**: Review analytics, update pricing, check inventory
- **Monthly**: Database maintenance, security updates, performance review

### Support Contacts
- **Technical Issues**: tech@skylyt.com
- **Payment Problems**: payments@skylyt.com
- **General Support**: support@skylyt.com

### Documentation
- **API Documentation**: Available at `/docs` endpoint
- **Admin Guide**: `ADMIN_GUIDE.md`
- **User Guide**: `USER_GUIDE.md`
- **Executive Summary**: `EXECUTIVE_SUMMARY.md`

## Testing

### Test Coverage
- Unit tests for core business logic
- Integration tests for API endpoints
- End-to-end tests for critical user flows
- Payment gateway testing with sandbox accounts

### Test Execution
```bash
# Backend tests
cd skylyt-travelhub-backend
pytest

# Frontend tests
cd skylyt-frontend
npm test
```

## Performance Metrics

### Target Performance
- **Page Load Time**: < 3 seconds
- **API Response Time**: < 500ms average
- **Database Query Time**: < 100ms average
- **Uptime**: 99.9% availability

### Monitoring Tools
- Prometheus for metrics collection
- Health check endpoints
- Error tracking and alerting
- Performance monitoring dashboard

---

**Handover Completed By**: Development Team  
**Date**: December 2024  
**Next Review**: January 2025

*This document should be updated as the system evolves and new features are added.*