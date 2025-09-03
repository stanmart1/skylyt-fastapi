from fastapi import FastAPI, Request, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import List, Optional
import logging
import re
from datetime import datetime, timezone
from werkzeug.utils import secure_filename

from app.core.config import settings as config_settings
from app.core.database import engine
from app.models import Base
from app.middleware import SecurityMiddleware, MonitoringMiddleware, setup_cors
from app.middleware.database import DatabaseMiddleware
from app.middleware.maintenance import MaintenanceMiddleware
from app.middleware.performance import PerformanceMiddleware
from app.middleware.compression import ResponseCompressionMiddleware
from app.middleware.security_hardening import (
    RequestValidationMiddleware, 
    HTTPSRedirectMiddleware, 
    SecurityHeadersMiddleware
)
from app.middleware.db_monitoring import DatabaseMonitoringMiddleware
from app.monitoring.error_tracking import ErrorHandlingMiddleware, error_tracker
from app.utils.logger import setup_logging
from app.utils.cache import cache_warmer
from app.api.v1 import auth, users, hotels, cars, search, bookings, rbac, health, admin_cars, admin_hotels, roles, permissions, settings, emails, destinations, hotel_images, localization, payment_webhooks, payment_config, currency_rates, currencies, footer_settings, contact_settings, about_settings
from app.api.v1 import payments, bank_accounts, admin_reviews, admin_support, admin_notifications, notifications, drivers, admin_bookings, admin_payments, admin_stats, driver
from app.core.openapi import custom_openapi
from app.core.redis import RedisService

# Setup logging
setup_logging()

# Constants
ALLOWED_UPLOAD_FOLDERS = ["general", "hotels", "payment_proofs", "documents"]
ALLOWED_FILE_TYPES = ["image/jpeg", "image/png", "image/gif", "application/pdf"]
ALLOWED_FILE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".pdf"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
DEFAULT_COMMISSION_RATE = 10.0

# Import utility functions
from app.utils.serializers import serialize_booking, serialize_payment, parse_date_string
from app.utils.validators import validate_financial_data, VALID_BOOKING_STATUSES, VALID_CURRENCIES

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    
    # Initialize Dragonfly connection
    try:
        RedisService.get_client()
        logging.info("Dragonfly initialized successfully")
    except Exception as e:
        logging.warning(f"Dragonfly initialization failed: {e}")
    
    await cache_warmer.warm_static_data()
    
    # Initialize default currencies
    from app.services.currency_service import CurrencyService
    from app.core.database import SessionLocal
    db = None
    try:
        db = SessionLocal()
        CurrencyService.seed_default_currencies(db)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to initialize currencies: {e}")
    finally:
        if db:
            db.close()
    
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Skylyt Luxury API",
    description="""A comprehensive booking platform API for luxury car rentals and hotel reservations.
    
    ## Features
    * **Authentication** - JWT-based user authentication and authorization
    * **Hotels** - Search, book, and manage hotel reservations
    * **Cars** - Browse and rent luxury vehicles
    * **Bookings** - Complete booking management system
    * **Payments** - Secure payment processing with multiple gateways
    * **Admin** - Full administrative dashboard and controls
    * **Localization** - Multi-currency and location support
    """,
    version="1.0.0",
    
    license_info={
        "name": "Private",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Authentication", "description": "User authentication and authorization"},
        {"name": "Users", "description": "User profile and account management"},
        {"name": "Hotels", "description": "Hotel search and booking operations"},
        {"name": "Cars", "description": "Car rental operations"},
        {"name": "Bookings", "description": "Booking management and history"},
        {"name": "Payments", "description": "Payment processing and transactions"},
        {"name": "Admin", "description": "Administrative operations"},
        {"name": "Health", "description": "System health and monitoring"},
    ],
    lifespan=lifespan
)

# Configure custom OpenAPI to exclude database schemas
app.openapi = lambda: custom_openapi(app)

# Remove CSP completely for docs pages
@app.middleware("http")
async def remove_csp_for_docs(request, call_next):
    response = await call_next(request)
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
        # Remove ALL CSP headers completely
        headers_to_remove = []
        for header_name in list(response.headers.keys()):
            if "content-security-policy" in header_name.lower():
                headers_to_remove.append(header_name)
        for header in headers_to_remove:
            response.headers.pop(header, None)
    return response



# CORS - Add explicit CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080", 
        "http://127.0.0.1:8080", 
        "https://skylyt.scaleitpro.com",
        "https://skylytapi.scaleitpro.com",
        "http://localhost:5173",
        "http://localhost:4173",  # Vite dev server
        "http://localhost:3000",   # Alternative dev port
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
)

# Middleware (order matters - last added is executed first)
# Redis client initialization moved to where it's actually used

# Error handling (outermost)
app.add_middleware(ErrorHandlingMiddleware, error_tracker=error_tracker)

# Security middleware (disabled for uploads)
if not config_settings.DEBUG:
    app.add_middleware(HTTPSRedirectMiddleware, force_https=True)

# Skip security headers that block Swagger UI and CORS
# app.add_middleware(SecurityHeadersMiddleware)  # Blocks Swagger UI resources
# app.add_middleware(RequestValidationMiddleware)

# Performance middleware - optimized compression
app.add_middleware(GZipMiddleware, minimum_size=500)  # Lower threshold for better compression
app.add_middleware(PerformanceMiddleware)

# Database connection handling
app.add_middleware(DatabaseMiddleware)
app.add_middleware(DatabaseMonitoringMiddleware)

# Monitoring and security
app.add_middleware(SecurityMiddleware)
app.add_middleware(MonitoringMiddleware)
app.add_middleware(MaintenanceMiddleware)

# Routes
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])
app.include_router(hotels.router, prefix="/api/v1", tags=["Hotels"])
app.include_router(cars.router, prefix="/api/v1", tags=["Cars"])
app.include_router(search.router, prefix="/api/v1", tags=["Search"])
app.include_router(bookings.router, prefix="/api/v1", tags=["Bookings"])
app.include_router(payments.router, prefix="/api/v1", tags=["Payments"])
app.include_router(bank_accounts.router, prefix="/api/v1", tags=["Bank Accounts"])
app.include_router(rbac.router, prefix="/api/v1", tags=["RBAC"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(notifications.router, prefix="/api/v1", tags=["Notifications"])
app.include_router(admin_cars.router, prefix="/api/v1", tags=["Admin Cars"])
app.include_router(admin_hotels.router, prefix="/api/v1", tags=["Admin Hotels"])
app.include_router(roles.router, prefix="/api/v1", tags=["Roles"])
app.include_router(permissions.router, prefix="/api/v1", tags=["Permissions"])
app.include_router(settings.router, prefix="/api/v1", tags=["Settings"])
app.include_router(emails.router, prefix="/api/v1", tags=["Emails"])
app.include_router(destinations.router, prefix="/api/v1", tags=["Destinations"])
app.include_router(hotel_images.router, prefix="/api/v1", tags=["Hotel Images"])
app.include_router(localization.router, prefix="/api/v1", tags=["Localization"])
app.include_router(payment_webhooks.router, prefix="/api/v1", tags=["Payment Webhooks"])
app.include_router(payment_config.router, prefix="/api/v1", tags=["Payment Config"])
app.include_router(admin_reviews.router, prefix="/api/v1", tags=["Admin Reviews"])
app.include_router(admin_support.router, prefix="/api/v1", tags=["Admin Support"])
app.include_router(admin_notifications.router, prefix="/api/v1", tags=["Admin Notifications"])
app.include_router(currency_rates.router, prefix="/api/v1", tags=["Currency Rates"])
app.include_router(currencies.router, prefix="/api/v1", tags=["Currencies"])
app.include_router(drivers.router, prefix="/api/v1", tags=["Drivers"])
app.include_router(driver.router, prefix="/api/v1", tags=["Driver Dashboard"])
app.include_router(admin_bookings.router, prefix="/api/v1", tags=["Admin Bookings"])
app.include_router(admin_payments.router, prefix="/api/v1", tags=["Admin Payments"])
app.include_router(admin_stats.router, prefix="/api/v1", tags=["Admin Stats"])
app.include_router(footer_settings.router, prefix="/api/v1", tags=["Footer Settings"])
app.include_router(contact_settings.router, prefix="/api/v1", tags=["Contact Settings"])
app.include_router(about_settings.router, prefix="/api/v1", tags=["About Settings"])




# Simple image serving endpoint without security middleware
@app.get("/uploads/{folder}/{filename}")
async def serve_image(folder: str, filename: str):
    """Serve images with proper CORS headers"""
    from fastapi.responses import FileResponse
    from pathlib import Path
    from os.path import normpath, commonpath
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Validate folder and filename to prevent path traversal
    if folder not in ALLOWED_UPLOAD_FOLDERS:
        raise HTTPException(status_code=400, detail="Invalid folder")
    
    # Sanitize filename
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Construct safe file path
    base_path = Path("uploads").resolve()
    file_path = base_path / folder / filename
    
    # Ensure the resolved path is within uploads directory
    try:
        file_path = file_path.resolve()
        if not str(file_path).startswith(str(base_path)):
            raise HTTPException(status_code=400, detail="Invalid path")
    except (OSError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid path")
    
    safe_path = re.sub(r'[\r\n]', '', str(file_path))
    logger.info(f"Serving file: {safe_path}")
    
    if file_path.exists() and file_path.is_file():
        # Determine media type based on file extension
        suffix = file_path.suffix.lower()
        media_type_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg', 
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.pdf': 'application/pdf'
        }
        media_type = media_type_map.get(suffix, "application/octet-stream")
        
        # Use FileResponse for memory efficiency
        return FileResponse(
            path=file_path,
            media_type=media_type,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "*",
                "Cache-Control": "public, max-age=3600"
            }
        )
    else:
        safe_path = re.sub(r'[\r\n]', '', str(file_path))
        logger.warning(f"File not found: {safe_path}")
        raise HTTPException(status_code=404, detail="Image not found")

# Additional endpoints for frontend compatibility
from app.core.dependencies import get_current_user
from app.core.database import get_db

# Import schemas
from app.schemas.booking import BookingStatusUpdate, BookingCreateRequest, BookingUpdateRequest, CancelBookingRequest, BulkDeleteRequest
from app.schemas.car import CarCreateRequest
from app.schemas.payment import PaymentUpdateRequest, RefundRequest

# Booking status endpoints moved to admin_bookings.py

# Admin booking endpoints moved to admin_bookings.py

# Admin payment endpoints moved to admin_payments.py

# Admin system, analytics, and notification endpoints moved to respective router files

@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...), upload_type: str = "general", current_user = Depends(get_current_user)):
    """Upload file with security validation"""
    from os import path
    from uuid import uuid4
    from pathlib import Path
    
    # Validate upload type
    if upload_type not in ALLOWED_UPLOAD_FOLDERS:
        raise HTTPException(status_code=400, detail="Invalid upload type")
    
    # Validate file type and size
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Validate file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File extension not allowed")
    
    # Check file size before reading content
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Generate secure filename with proper validation
    original_name = secure_filename(file.filename or 'upload')
    secure_name = f"{uuid4()}{file_extension}"
    
    # Create upload directory if it doesn't exist
    base_upload_dir = Path("uploads").resolve()
    upload_dir = base_upload_dir / upload_type
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / secure_name
    
    # Ensure file path is within upload directory
    try:
        file_path = file_path.resolve()
        if not str(file_path).startswith(str(base_upload_dir)):
            raise HTTPException(status_code=400, detail="Invalid file path")
    except (OSError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    # Save file with error handling
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except (OSError, IOError) as e:
        raise HTTPException(status_code=500, detail="Failed to save file")
    
    return {"url": f"/uploads/{upload_type}/{secure_name}", "filename": secure_name}

@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle CORS preflight requests"""
    return {"message": "OK"}

@app.get("/")
async def root():
    return {"message": "Skylyt Luxury API", "version": "1.0.0"}

@app.get("/api/v1/test")
async def test_connection():
    """Test endpoint to verify frontend-backend connection"""
    from datetime import datetime
    return {
        "status": "success",
        "message": "Backend is connected and working!",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cors_enabled": True
    }

@app.get("/api/v1/test-admin")
async def test_admin(db: Session = Depends(get_db)):
    """Test admin user exists"""
    from app.models.user import User
    admin_user = db.query(User).filter(User.email == "admin@skylyt.com").first()
    if admin_user:
        return {
            "exists": True,
            "email": admin_user.email,
            "is_active": admin_user.is_active,
            "roles_count": len(admin_user.roles)
        }
    return {"exists": False}

@app.get("/cars-management")
async def cars_management_page(current_user = Depends(get_current_user)):
    """Serve cars management dashboard page"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"message": "Cars Management Dashboard", "user": current_user.email}

@app.get("/hotel-management")
async def hotel_management_page(current_user = Depends(get_current_user)):
    """Serve hotel management dashboard page"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"message": "Hotel Management Dashboard", "user": current_user.email}

# Admin car, stats, payment, and review endpoints moved to respective router files

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)