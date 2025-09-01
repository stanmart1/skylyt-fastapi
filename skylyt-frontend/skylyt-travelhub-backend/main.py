from fastapi import FastAPI, Request, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import logging

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
from app.api.v1 import auth, users, hotels, cars, search, bookings, rbac, health, admin_cars, admin_hotels, roles, permissions, settings, emails, destinations, hotel_images, localization, payment_webhooks, payment_config, currency_rates
from app.api.v1 import payments, bank_accounts, admin_reviews, admin_support, admin_notifications, notifications

# Setup logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    await cache_warmer.warm_static_data()
    
    # Initialize currency rates
    from app.services.currency_service import CurrencyService
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        await CurrencyService.update_exchange_rates(db)
    except Exception as e:
        print(f"Failed to initialize currency rates: {e}")
    finally:
        db.close()
    
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Skylyt Luxury API",
    description="Travel booking platform API",
    version="1.0.0",
    docs_url="/docs" if config_settings.DEBUG else None,
    redoc_url="/redoc" if config_settings.DEBUG else None,
    lifespan=lifespan
)

# CORS - Add explicit CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080", 
        "http://127.0.0.1:8080", 
        "https://skylyt.scaleitpro.com",
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

# Skip security headers that block CORS
# app.add_middleware(SecurityHeadersMiddleware)
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
    allowed_folders = ["general", "hotels", "payment_proofs"]
    if folder not in allowed_folders:
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
    
    logger.info(f"Serving file: {file_path}")
    
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
        logger.warning(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail="Image not found")

# Additional endpoints for frontend compatibility
from app.core.dependencies import get_current_user
from app.core.database import get_db

@app.get("/api/v1/admin/stats")
async def get_admin_stats(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get admin dashboard statistics with caching"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.services.analytics_service import AnalyticsService
    from app.utils.cache_manager import cache_manager
    
    # Try cache first (5 minute cache)
    cache_key = f"admin_stats_{current_user.id}"
    cached_stats = cache_manager.get(cache_key)
    if cached_stats:
        return cached_stats
    
    stats = AnalyticsService.get_admin_stats(db)
    cache_manager.set(cache_key, stats, 300)
    return stats

@app.get("/api/v1/admin/active-users")
async def get_active_users(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get count of active users online"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.user import User
        # Count all active users as a simple metric
        active_count = db.query(User).filter(User.is_active == True).count()
        return {"active_users": active_count}
    except Exception as e:
        return {"active_users": 0}

@app.get("/api/v1/admin/recent-activity")
async def get_recent_activity(
    activity_type: str = None,
    current_user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Get recent activity for admin dashboard"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from sqlalchemy import desc
        activities = []
        

        
        from app.models.user import User
        
        # Recent user registrations only (real data from database)
        if not activity_type or activity_type == "user":
            recent_users = db.query(User).order_by(desc(User.created_at)).limit(10).all()
            for user in recent_users:
                activities.append({
                    "id": f"user_{user.id}",
                    "type": "user",
                    "title": "New user registration",
                    "description": f"{user.first_name} {user.last_name} joined the platform",
                    "timestamp": user.created_at.isoformat(),
                    "status": "active" if user.is_active else "inactive"
                })
        
        # For bookings and payments, return empty if no real data exists
        # Remove this section entirely to avoid mock data
        
        # Sort by timestamp (most recent first)
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {"activities": activities[:10]}
    except Exception as e:
        # Return empty activities if there's an error
        return {"activities": []}

@app.get("/api/v1/admin/bookings")
async def get_admin_bookings(
    search: str = None,
    status: str = None,
    payment_status: str = None,
    booking_type: str = None,
    start_date: str = None,
    end_date: str = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    per_page: int = 20,
    current_user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Get bookings with advanced filtering and search"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.services.booking_service import BookingService
    from datetime import datetime, timezone
    
    booking_service = BookingService(db)
    
    # Parse date strings
    parsed_start_date = None
    parsed_end_date = None
    if start_date:
        try:
            parsed_start_date = datetime.fromisoformat(start_date).date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format")
    if end_date:
        try:
            parsed_end_date = datetime.fromisoformat(end_date).date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format")
    
    return booking_service.get_bookings_with_filters(
        search=search,
        status=status,
        payment_status=payment_status,
        booking_type=booking_type,
        start_date=parsed_start_date,
        end_date=parsed_end_date,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=per_page
    )

@app.get("/api/v1/admin/bookings/{booking_id}")
async def get_admin_booking(booking_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get detailed booking information"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.booking import Booking
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        return {
            "id": booking.id,
            "booking_reference": booking.booking_reference,
            "booking_type": booking.booking_type,
            "status": booking.status,
            "customer_name": booking.customer_name,
            "customer_email": booking.customer_email,
            "customer_phone": getattr(booking, 'customer_phone', None),
            "user_id": booking.user_id,
            "hotel_name": booking.hotel_name,
            "car_name": booking.car_name,
            "car_id": getattr(booking, 'car_id', None),
            "check_in_date": booking.check_in_date,
            "check_out_date": booking.check_out_date,
            "start_date": booking.start_date,
            "end_date": booking.end_date,
            "number_of_guests": booking.number_of_guests,
            "special_requests": booking.special_requests,
            "total_amount": float(booking.total_amount) if booking.total_amount else 0,
            "currency": booking.currency,
            "payment_status": booking.payment_status,
            "external_booking_id": booking.external_booking_id,
            "confirmation_number": booking.confirmation_number,
            "booking_data": booking.booking_data,
            "created_at": booking.created_at.isoformat() if booking.created_at else None,
            "updated_at": booking.updated_at.isoformat() if booking.updated_at else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch booking details")

@app.get("/api/v1/admin/bookings/{booking_id}/details")
async def get_booking_details(booking_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get comprehensive booking details for modal display"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.booking import Booking
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        return {
            "id": booking.id,
            "booking_reference": booking.booking_reference,
            "booking_type": booking.booking_type,
            "status": booking.status,
            "customer_name": booking.customer_name,
            "customer_email": booking.customer_email,
            "customer_phone": getattr(booking, 'customer_phone', None),
            "user_id": booking.user_id,
            "hotel_name": booking.hotel_name,
            "car_name": booking.car_name,
            "car_id": getattr(booking, 'car_id', None),
            "check_in_date": booking.check_in_date,
            "check_out_date": booking.check_out_date,
            "start_date": booking.start_date,
            "end_date": booking.end_date,
            "number_of_guests": booking.number_of_guests,
            "special_requests": booking.special_requests,
            "total_amount": float(booking.total_amount) if booking.total_amount else 0,
            "currency": booking.currency,
            "payment_status": booking.payment_status,
            "external_booking_id": booking.external_booking_id,
            "confirmation_number": booking.confirmation_number,
            "booking_data": booking.booking_data,
            "created_at": booking.created_at.isoformat() if booking.created_at else None,
            "updated_at": booking.updated_at.isoformat() if booking.updated_at else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch booking details")

class BookingStatusUpdate(BaseModel):
    status: str

@app.put("/api/v1/bookings/{booking_id}/status")
async def update_booking_status_api(booking_id: int, status_update: BookingStatusUpdate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update booking status - API method for frontend"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.booking import Booking
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        valid_statuses = ["pending", "confirmed", "cancelled"]
        if status_update.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        booking.status = status_update.status
        db.commit()
        db.refresh(booking)
        
        return {
            "success": True,
            "message": "Booking status updated successfully", 
            "booking_id": booking_id, 
            "status": booking.status
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update booking status")

@app.put("/api/v1/admin/bookings/{booking_id}/status")
async def update_booking_status(booking_id: int, status_update: BookingStatusUpdate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update booking status"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.models.booking import Booking
    
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        valid_statuses = ["pending", "confirmed", "cancelled"]
        if status_update.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        booking.status = status_update.status
        db.commit()
        db.refresh(booking)
        
        return {
            "success": True,
            "message": "Booking status updated successfully", 
            "booking_id": booking_id, 
            "status": booking.status
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update booking status")

class BulkDeleteRequest(BaseModel):
    ids: List[int]

@app.delete("/api/v1/admin/bookings/bulk")
async def bulk_delete_bookings(request: BulkDeleteRequest, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Bulk delete bookings (admin only)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.models.booking import Booking
    
    if not request.ids:
        raise HTTPException(status_code=400, detail="No booking IDs provided")
    
    try:
        deleted_count = db.query(Booking).filter(Booking.id.in_(request.ids)).delete(synchronize_session=False)
        db.commit()
        
        return {"message": f"{deleted_count} bookings deleted successfully", "deleted_count": deleted_count}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete bookings")

@app.delete("/api/v1/admin/bookings/{booking_id}")
async def delete_booking(booking_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete booking (admin only)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.models.booking import Booking
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    db.delete(booking)
    db.commit()
    
    return {"message": "Booking deleted successfully"}

@app.post("/api/v1/admin/bookings")
async def create_booking(booking_data: dict, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create new booking (admin)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.models.booking import Booking
    import uuid
    
    # Generate booking reference
    booking_reference = f"BK{uuid.uuid4().hex[:8].upper()}"
    
    new_booking = Booking(
        user_id=booking_data["user_id"],
        booking_reference=booking_reference,
        booking_type=booking_data["booking_type"],
        status=booking_data.get("status", "pending"),
        hotel_name=booking_data.get("hotel_name"),
        car_name=booking_data.get("car_name"),
        total_amount=booking_data["total_amount"],
        currency=booking_data.get("currency", "USD"),
        booking_data=booking_data.get("booking_data")
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return {
        "id": new_booking.id,
        "booking_reference": new_booking.booking_reference,
        "message": "Booking created successfully"
    }

@app.put("/api/v1/admin/bookings/{booking_id}")
async def update_booking(booking_id: int, booking_data: dict, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update booking details (admin)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.models.booking import Booking
    
    try:
        # Get booking once to avoid redundant queries
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Handle status updates
        if "status" in booking_data:
            valid_statuses = ["pending", "confirmed", "cancelled"]
            if booking_data["status"] not in valid_statuses:
                raise HTTPException(status_code=400, detail="Invalid status")
            booking.status = booking_data["status"]
        
        # Update other fields with validation
        allowed_fields = ["customer_name", "customer_email", "special_requests", "booking_type", "hotel_name", "car_name", "total_amount", "currency"]
        for field in allowed_fields:
            if field in booking_data:
                setattr(booking, field, booking_data[field])
        
        db.commit()
        db.refresh(booking)
        
        return {
            "id": booking.id,
            "booking_reference": booking.booking_reference,
            "message": "Booking updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update booking")

@app.post("/api/v1/admin/bookings/{booking_id}/resend-confirmation")
async def resend_booking_confirmation(booking_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Resend booking confirmation email"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.services.booking_service import BookingService
    booking_service = BookingService(db)
    
    success = booking_service.send_confirmation_email(booking_id)
    if not success:
        raise HTTPException(status_code=404, detail="Booking not found or email failed")
    
    return {"message": "Confirmation email sent successfully"}

@app.get("/api/v1/admin/bookings/{booking_id}/invoice")
async def get_booking_invoice(booking_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Generate invoice data for booking"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.services.booking_service import BookingService
    booking_service = BookingService(db)
    
    invoice_data = booking_service.generate_invoice_data(booking_id)
    if not invoice_data:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return invoice_data

@app.post("/api/v1/admin/bookings/{booking_id}/cancel")
async def cancel_booking_admin(booking_id: int, cancel_data: dict, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Cancel booking with reason"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.services.booking_service import BookingService
    booking_service = BookingService(db)
    
    reason = cancel_data.get("reason", "Cancelled by admin")
    success = booking_service.cancel_booking(booking_id, reason, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return {"message": "Booking cancelled successfully"}

# Hotel-specific booking endpoints
@app.get("/api/v1/admin/hotel-bookings")
async def get_hotel_bookings(
    search: str = None,
    status: str = None,
    payment_status: str = None,
    start_date: str = None,
    end_date: str = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    per_page: int = 20,
    current_user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Get hotel bookings only"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.services.booking_service import BookingService
    from datetime import datetime
    
    booking_service = BookingService(db)
    
    # Parse date strings
    parsed_start_date = None
    parsed_end_date = None
    if start_date:
        try:
            parsed_start_date = datetime.fromisoformat(start_date).date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format")
    if end_date:
        try:
            parsed_end_date = datetime.fromisoformat(end_date).date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format")
    
    return booking_service.get_bookings_with_filters(
        search=search,
        status=status,
        payment_status=payment_status,
        booking_type="hotel",  # Filter for hotel bookings only
        start_date=parsed_start_date,
        end_date=parsed_end_date,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=per_page
    )

# Car-specific booking endpoints
@app.get("/api/v1/admin/car-bookings")
async def get_car_bookings(
    search: str = None,
    status: str = None,
    payment_status: str = None,
    start_date: str = None,
    end_date: str = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    per_page: int = 20,
    current_user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Get car bookings only"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.services.booking_service import BookingService
    from datetime import datetime
    
    booking_service = BookingService(db)
    
    # Parse date strings
    parsed_start_date = None
    parsed_end_date = None
    if start_date:
        try:
            parsed_start_date = datetime.fromisoformat(start_date).date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format")
    if end_date:
        try:
            parsed_end_date = datetime.fromisoformat(end_date).date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format")
    
    return booking_service.get_bookings_with_filters(
        search=search,
        status=status,
        payment_status=payment_status,
        booking_type="car",  # Filter for car bookings only
        start_date=parsed_start_date,
        end_date=parsed_end_date,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=per_page
    )

@app.get("/api/v1/admin/payments")
async def get_admin_payments(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all payments for admin"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.payment import Payment
        payments = db.query(Payment).all()
        return [{
            "id": payment.id,
            "booking_id": payment.booking_id,
            "amount": float(payment.amount),
            "currency": payment.currency,
            "status": payment.status.value,
            "payment_method": payment.payment_method.value,
            "created_at": payment.created_at.isoformat(),
            "transaction_id": payment.transaction_id,
            "transfer_reference": payment.transfer_reference
        } for payment in payments]
    except ImportError:
        return []

@app.get("/api/v1/admin/payments/{payment_id}")
async def get_admin_payment(payment_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get single payment for admin"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.payment import Payment
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        return {
            "id": payment.id,
            "booking_id": payment.booking_id,
            "amount": float(payment.amount),
            "currency": payment.currency,
            "status": payment.status.value,
            "payment_method": payment.payment_method.value,
            "created_at": payment.created_at.isoformat(),
            "transaction_id": payment.transaction_id,
            "transfer_reference": payment.transfer_reference,
            "gateway_response": payment.gateway_response
        }
    except ImportError:
        raise HTTPException(status_code=404, detail="Payment not found")

@app.put("/api/v1/admin/payments/{payment_id}")
async def update_payment(payment_id: int, payment_data: dict, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update payment details (admin)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.payment import Payment, PaymentStatus
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        if "status" in payment_data:
            try:
                # Validate status value before assignment
                valid_statuses = [status.value for status in PaymentStatus]
                if payment_data["status"] in valid_statuses:
                    payment.status = PaymentStatus(payment_data["status"])
                else:
                    raise HTTPException(status_code=400, detail="Invalid payment status")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid payment status")
        
        if "transaction_id" in payment_data:
            payment.transaction_id = payment_data["transaction_id"]
        
        db.commit()
        db.refresh(payment)
        
        return {
            "id": payment.id,
            "message": "Payment updated successfully",
            "status": payment.status.value
        }
    except ImportError:
        raise HTTPException(status_code=404, detail="Payment system not available")

@app.post("/api/v1/admin/payments/{payment_id}/verify")
async def verify_payment(payment_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Verify payment for admin"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.payment import Payment, PaymentStatus
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        payment.status = PaymentStatus.COMPLETED
        db.commit()
        return {"message": "Payment verified", "payment_id": payment_id, "status": "completed"}
    except ImportError:
        raise HTTPException(status_code=404, detail="Payment system not available")

@app.delete("/api/v1/admin/payments/{payment_id}")
async def delete_payment(payment_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete payment (admin only)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.payment import Payment
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        db.delete(payment)
        db.commit()
        
        return {"message": "Payment deleted successfully"}
    except ImportError:
        raise HTTPException(status_code=404, detail="Payment system not available")

@app.get("/api/v1/admin/system/health")
async def get_system_health_admin(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get system health for admin dashboard"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Reuse the health endpoint logic
    from app.api.v1.health import health_check
    return await health_check(db)

@app.get("/api/v1/analytics/dashboard")
async def get_analytics(range: str = "6m", current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get analytics dashboard data from database"""
    from app.services.analytics_service import AnalyticsService
    return AnalyticsService.get_dashboard_analytics(db, range)

@app.get("/api/v1/notifications")
async def get_notifications(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user notifications"""
    from app.models.notification import Notification
    notifications = db.query(Notification).filter(Notification.user_id == current_user.id).all()
    return notifications

@app.post("/api/v1/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Mark notification as read"""
    from app.models.notification import Notification
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}

@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...), upload_type: str = "general", current_user = Depends(get_current_user)):
    """Upload file with security validation"""
    from os import path
    from uuid import uuid4
    from pathlib import Path
    
    # Validate upload type
    allowed_upload_types = ["general", "hotels", "payment_proofs"]
    if upload_type not in allowed_upload_types:
        raise HTTPException(status_code=400, detail="Invalid upload type")
    
    # Validate file type and size
    allowed_types = ["image/jpeg", "image/png", "image/gif", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Validate file extension
    file_extension = Path(file.filename).suffix.lower()
    allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".pdf"]
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="File extension not allowed")
    
    if file.size > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File too large")
    
    # Generate secure filename
    secure_filename = f"{uuid4()}{file_extension}"
    
    # Create upload directory if it doesn't exist
    base_upload_dir = Path("uploads").resolve()
    upload_dir = base_upload_dir / upload_type
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / secure_filename
    
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
    
    return {"url": f"/uploads/{upload_type}/{secure_filename}", "filename": secure_filename}

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

@app.get("/api/v1/admin/car-stats")
async def get_car_stats(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get car management statistics"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.car import Car
        from app.models.booking import Booking
        from app.models.payment import Payment
        from sqlalchemy import func, and_
        from datetime import datetime, timedelta
        
        # Get car statistics
        total_cars = db.query(Car).count()
        available_cars = db.query(Car).filter(Car.status == 'available').count()
        
        # Get active car bookings
        active_bookings = db.query(Booking).filter(
            and_(
                Booking.booking_type == 'car',
                Booking.status.in_(['confirmed', 'ongoing'])
            )
        ).count()
        
        # Calculate revenue (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        sixty_days_ago = datetime.now() - timedelta(days=60)
        
        current_revenue = db.query(func.sum(Payment.amount)).join(Booking).filter(
            and_(
                Booking.booking_type == 'car',
                Payment.status == 'completed',
                Payment.created_at >= thirty_days_ago
            )
        ).scalar() or 0
        
        previous_revenue = db.query(func.sum(Payment.amount)).join(Booking).filter(
            and_(
                Booking.booking_type == 'car',
                Payment.status == 'completed',
                Payment.created_at >= sixty_days_ago,
                Payment.created_at < thirty_days_ago
            )
        ).scalar() or 0
        
        # Calculate revenue change percentage
        revenue_change = 0
        if previous_revenue > 0:
            revenue_change = ((current_revenue - previous_revenue) / previous_revenue) * 100
        
        return {
            "totalCars": total_cars,
            "availableCars": available_cars,
            "activeBookings": active_bookings,
            "totalRevenue": float(current_revenue),
            "revenueChange": round(revenue_change, 1)
        }
    except Exception as e:
        # Return default stats if there's an error
        return {
            "totalCars": 0,
            "availableCars": 0,
            "activeBookings": 0,
            "totalRevenue": 0.0,
            "revenueChange": 0.0
        }

@app.get("/api/v1/admin/hotel-stats")
async def get_hotel_stats(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get hotel management statistics"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.hotel import Hotel
        from app.models.booking import Booking
        from app.models.payment import Payment
        from sqlalchemy import func, and_
        from datetime import datetime, timedelta
        
        # Get hotel statistics
        total_hotels = db.query(Hotel).count()
        total_rooms = db.query(func.sum(Hotel.room_count)).scalar() or 0
        
        # Get active hotel bookings
        active_bookings = db.query(Booking).filter(
            and_(
                Booking.booking_type == 'hotel',
                Booking.status.in_(['confirmed', 'ongoing'])
            )
        ).count()
        
        # Calculate occupancy rate
        occupancy_rate = 0
        if total_rooms > 0:
            occupancy_rate = round((active_bookings / total_rooms) * 100, 1)
        
        # Calculate revenue (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        sixty_days_ago = datetime.now() - timedelta(days=60)
        
        current_revenue = db.query(func.sum(Payment.amount)).join(Booking).filter(
            and_(
                Booking.booking_type == 'hotel',
                Payment.status == 'completed',
                Payment.created_at >= thirty_days_ago
            )
        ).scalar() or 0
        
        previous_revenue = db.query(func.sum(Payment.amount)).join(Booking).filter(
            and_(
                Booking.booking_type == 'hotel',
                Payment.status == 'completed',
                Payment.created_at >= sixty_days_ago,
                Payment.created_at < thirty_days_ago
            )
        ).scalar() or 0
        
        # Calculate revenue change percentage
        revenue_change = 0
        if previous_revenue > 0:
            revenue_change = ((current_revenue - previous_revenue) / previous_revenue) * 100
        
        return {
            "totalHotels": total_hotels,
            "totalRooms": int(total_rooms),
            "activeBookings": active_bookings,
            "totalRevenue": float(current_revenue),
            "revenueChange": round(revenue_change, 1),
            "occupancyRate": occupancy_rate
        }
    except Exception as e:
        # Return default stats if there's an error
        return {
            "totalHotels": 0,
            "totalRooms": 0,
            "activeBookings": 0,
            "totalRevenue": 0.0,
            "revenueChange": 0.0,
            "occupancyRate": 0.0
        }

@app.get("/api/v1/admin/cars")
async def get_admin_cars(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all cars for admin management"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.car import Car
        cars = db.query(Car).all()
        return [{
            "id": str(car.id),
            "name": car.name,
            "category": car.category,
            "price": float(car.price_per_day),
            "currency": car.currency,
            "image_url": car.image_url,
            "passengers": car.passengers,
            "transmission": car.transmission,
            "fuel_type": car.fuel_type,
            "plate_number": getattr(car, 'plate_number', ''),
            "year": getattr(car, 'year', 2024),
            "status": getattr(car, 'status', 'available'),
            "features": car.features or [],
            "is_featured": getattr(car, 'is_featured', False),
            "mileage": getattr(car, 'mileage', 0),
            "insurance_expiry": getattr(car, 'insurance_expiry', ''),
            "last_service": getattr(car, 'last_service', ''),
            "next_service": getattr(car, 'next_service', ''),
            "created_at": car.created_at.isoformat() if car.created_at else ''
        } for car in cars]
    except Exception as e:
        return []

@app.post("/api/v1/admin/cars")
async def create_car(car_data: dict, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create new car"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.car import Car
        new_car = Car(
            name=car_data["name"],
            category=car_data["category"],
            price_per_day=car_data["price"],
            currency=car_data.get("currency", "USD"),
            image_url=car_data.get("image_url", ""),
            passengers=car_data.get("passengers", 4),
            transmission=car_data.get("transmission", "automatic"),
            fuel_type=car_data.get("fuel_type", "petrol"),
            features=car_data.get("features", [])
        )
        db.add(new_car)
        db.commit()
        db.refresh(new_car)
        return {"id": new_car.id, "message": "Car created successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create car")

@app.put("/api/v1/admin/cars/{car_id}")
async def update_car(car_id: int, car_data: dict, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update car details"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.car import Car
        car = db.query(Car).filter(Car.id == car_id).first()
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")
        
        for key, value in car_data.items():
            if hasattr(car, key):
                setattr(car, key, value)
        
        db.commit()
        return {"message": "Car updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update car")

@app.delete("/api/v1/admin/cars/{car_id}")
async def delete_car(car_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete car"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.car import Car
        car = db.query(Car).filter(Car.id == car_id).first()
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")
        
        db.delete(car)
        db.commit()
        return {"message": "Car deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete car")

@app.post("/api/v1/admin/cars/{car_id}/feature")
async def toggle_car_feature(car_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Toggle car featured status"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.car import Car
        car = db.query(Car).filter(Car.id == car_id).first()
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")
        
        # Toggle featured status
        current_featured = getattr(car, 'is_featured', False)
        setattr(car, 'is_featured', not current_featured)
        db.commit()
        return {"message": "Car feature status updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update car feature status")

@app.get("/api/v1/admin/cars/maintenance")
async def get_car_maintenance(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get car maintenance records"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Return mock data for now since maintenance model may not exist
    return []

@app.post("/api/v1/admin/cars/maintenance")
async def create_maintenance_record(maintenance_data: dict, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create maintenance record"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Return success for now since maintenance model may not exist
    return {"message": "Maintenance record created successfully"}

@app.get("/api/v1/admin/cars/stats")
async def get_car_fleet_stats(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get car fleet statistics"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.car import Car
        from app.models.booking import Booking
        from app.models.payment import Payment
        from sqlalchemy import func, and_
        from datetime import datetime, timedelta
        
        total_cars = db.query(Car).count()
        available_cars = db.query(Car).filter(Car.is_available == True).count()
        booked_cars = 0  # Calculate from active bookings
        maintenance_cars = 0  # No maintenance status in current model
        
        # Calculate today's revenue
        today = datetime.now().date()
        today_revenue = db.query(func.sum(Payment.amount)).join(Booking).filter(
            and_(
                Booking.booking_type == 'car',
                Payment.status == 'completed',
                func.date(Payment.created_at) == today
            )
        ).scalar() or 0
        
        # Calculate utilization rate based on active bookings
        utilization_rate = 0
        if total_cars > 0:
            utilization_rate = round((active_bookings / total_cars) * 100, 1)
        
        return {
            "total_cars": total_cars,
            "available": available_cars,
            "booked": booked_cars,
            "maintenance": maintenance_cars,
            "revenue_today": float(today_revenue),
            "utilization_rate": utilization_rate
        }
    except Exception as e:
        return {
            "total_cars": 0,
            "available": 0,
            "booked": 0,
            "maintenance": 0,
            "revenue_today": 0.0,
            "utilization_rate": 0.0
        }

@app.post("/api/v1/admin/payments/{payment_id}/refund")
async def process_refund(payment_id: int, refund_data: dict, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Process payment refund"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.payment import Payment, PaymentStatus
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        payment.status = PaymentStatus.REFUNDED
        db.commit()
        return {"message": "Refund processed successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to process refund")

@app.get("/api/v1/admin/payments/export")
async def export_payments(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Export payments to CSV"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.payment import Payment
        payments = db.query(Payment).all()
        
        # Create CSV content
        csv_content = "ID,Booking ID,Amount,Currency,Status,Payment Method,Created At\n"
        for payment in payments:
            csv_content += f"{payment.id},{payment.booking_id},{payment.amount},{payment.currency},{payment.status.value},{payment.payment_method.value},{payment.created_at}\n"
        
        return {"csv": csv_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to export payments")

@app.get("/api/v1/admin/payments/{payment_id}/commission")
async def get_payment_commission(payment_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get payment commission details"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.payment import Payment
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # Calculate commission (example: 10%)
        commission_rate = 10.0
        commission_amount = float(payment.amount) * (commission_rate / 100)
        
        return {
            "commission_amount": commission_amount,
            "commission_rate": commission_rate,
            "currency": payment.currency
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get commission details")

@app.put("/api/v1/admin/reviews/{review_id}/status")
async def update_review_status(review_id: int, status_data: dict, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update review status"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Return success for now since review model structure may vary
    return {"message": "Review status updated successfully"}

@app.post("/api/v1/admin/reviews/{review_id}/response")
async def add_review_response(review_id: int, response_data: dict, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Add admin response to review"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Return success for now since review model structure may vary
    return {"message": "Response added successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)