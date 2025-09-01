from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime
import logging

from app.core.dependencies import get_current_user
from app.core.database import get_db

router = APIRouter()

# Constants
VALID_BOOKING_STATUSES = ["pending", "confirmed", "cancelled"]
VALID_CURRENCIES = ["USD", "EUR", "GBP", "NGN", "CAD", "AUD"]

# Helper Functions
def serialize_booking(booking) -> dict:
    """Serialize booking object to dictionary"""
    return {
        "id": booking.id,
        "booking_reference": booking.booking_reference,
        "booking_type": booking.booking_type,
        "status": booking.status,
        "customer_name": booking.customer_name,
        "customer_email": booking.customer_email,
        "customer_phone": getattr(booking, 'customer_phone', None),
        "user_id": booking.user_id,
        "driver_id": getattr(booking, 'driver_id', None),
        "driver_name": getattr(booking.driver, 'name', None) if hasattr(booking, 'driver') and booking.driver else None,
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

def parse_date_string(date_str: str) -> datetime.date:
    """Parse ISO date string to date object"""
    try:
        return datetime.fromisoformat(date_str).date()
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {date_str}")

def update_booking_status_helper(booking_id: int, status: str, db: Session) -> dict:
    """Helper function to update booking status"""
    from app.models.booking import Booking
    
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if status not in VALID_BOOKING_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(VALID_BOOKING_STATUSES)}")
    
    booking.status = status
    db.commit()
    db.refresh(booking)
    
    return {
        "success": True,
        "message": "Booking status updated successfully", 
        "booking_id": booking_id, 
        "status": booking.status
    }

# Pydantic Models
class BookingStatusUpdate(BaseModel):
    status: str
    
    @validator('status')
    def validate_status(cls, v):
        if v not in VALID_BOOKING_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(VALID_BOOKING_STATUSES)}")
        return v

class BookingCreateRequest(BaseModel):
    user_id: int
    booking_type: str
    status: Optional[str] = "pending"
    hotel_name: Optional[str] = None
    car_name: Optional[str] = None
    total_amount: float
    currency: Optional[str] = "USD"
    booking_data: Optional[dict] = None
    
    @validator('total_amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v
    
    @validator('currency')
    def validate_currency(cls, v):
        if v not in VALID_CURRENCIES:
            raise ValueError(f"Invalid currency. Must be one of: {', '.join(VALID_CURRENCIES)}")
        return v

class BookingUpdateRequest(BaseModel):
    status: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    special_requests: Optional[str] = None
    booking_type: Optional[str] = None
    hotel_name: Optional[str] = None
    car_name: Optional[str] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    driver_id: Optional[int] = None
    
    @validator('total_amount')
    def validate_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Amount must be positive")
        return v
    
    @validator('currency')
    def validate_currency(cls, v):
        if v is not None and v not in VALID_CURRENCIES:
            raise ValueError(f"Invalid currency. Must be one of: {', '.join(VALID_CURRENCIES)}")
        return v

class CancelBookingRequest(BaseModel):
    reason: Optional[str] = "Cancelled by admin"

class BulkDeleteRequest(BaseModel):
    ids: List[int]
    
    @validator('ids')
    def validate_ids(cls, v):
        if not v:
            raise ValueError("No IDs provided")
        return v

# Routes
@router.get("/admin/bookings")
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

@router.get("/admin/bookings/{booking_id}")
async def get_admin_booking(booking_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get detailed booking information"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.booking import Booking
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        return serialize_booking(booking)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to fetch booking details: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch booking details")

@router.get("/admin/bookings/{booking_id}/details")
async def get_booking_details(booking_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get comprehensive booking details for modal display"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.booking import Booking
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        return serialize_booking(booking)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to fetch booking details: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch booking details")

@router.put("/bookings/{booking_id}/status")
async def update_booking_status_api(booking_id: int, status_update: BookingStatusUpdate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update booking status - API method for frontend"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        return update_booking_status_helper(booking_id, status_update.status, db)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to update booking status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update booking status")

@router.put("/admin/bookings/{booking_id}/status")
async def update_booking_status(booking_id: int, status_update: BookingStatusUpdate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update booking status - Admin endpoint"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        return update_booking_status_helper(booking_id, status_update.status, db)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to update booking status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update booking status")

@router.delete("/admin/bookings/bulk")
async def bulk_delete_bookings(request: BulkDeleteRequest, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Bulk delete bookings (admin only)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.models.booking import Booking
    
    try:
        deleted_count = db.query(Booking).filter(Booking.id.in_(request.ids)).delete(synchronize_session=False)
        db.commit()
        
        return {"message": f"{deleted_count} bookings deleted successfully", "deleted_count": deleted_count}
    except Exception as e:
        db.rollback()
        logger = logging.getLogger(__name__)
        logger.error(f"Bulk delete failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete bookings")

@router.delete("/admin/bookings/{booking_id}")
async def delete_booking(booking_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete booking (admin only)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.booking import Booking
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        db.delete(booking)
        db.commit()
        
        return {"message": "Booking deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to delete booking {booking_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete booking")

@router.post("/admin/bookings")
async def create_booking(booking_data: BookingCreateRequest, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create new booking (admin)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.booking import Booking
        import uuid
        
        # Generate booking reference
        booking_reference = f"BK{uuid.uuid4().hex[:8].upper()}"
        
        new_booking = Booking(
            user_id=booking_data.user_id,
            booking_reference=booking_reference,
            booking_type=booking_data.booking_type,
            status=booking_data.status,
            hotel_name=booking_data.hotel_name,
            car_name=booking_data.car_name,
            total_amount=booking_data.total_amount,
            currency=booking_data.currency,
            booking_data=booking_data.booking_data
        )
        
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        
        return {
            "id": new_booking.id,
            "booking_reference": new_booking.booking_reference,
            "message": "Booking created successfully"
        }
    except Exception as e:
        db.rollback()
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to create booking: {e}")
        raise HTTPException(status_code=500, detail="Failed to create booking")

@router.put("/admin/bookings/{booking_id}")
async def update_booking(booking_id: int, booking_data: BookingUpdateRequest, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update booking details (admin)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.booking import Booking
        
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Update fields from validated Pydantic model
        update_data = booking_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(booking, field):
                setattr(booking, field, value)
        
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
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to update booking {booking_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update booking")

@router.put("/admin/bookings/{booking_id}/assign-driver")
async def assign_driver_to_booking(
    booking_id: int, 
    driver_id: int = None,
    current_user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Assign or unassign driver to/from booking"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.booking import Booking
        from app.models.driver import Driver
        
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        if driver_id:
            driver = db.query(Driver).filter(Driver.id == driver_id).first()
            if not driver:
                raise HTTPException(status_code=404, detail="Driver not found")
            if not driver.is_active or not driver.is_available:
                raise HTTPException(status_code=400, detail="Driver is not available")
        
        booking.driver_id = driver_id
        db.commit()
        
        return {
            "message": "Driver assignment updated successfully",
            "booking_id": booking_id,
            "driver_id": driver_id
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to assign driver to booking {booking_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to assign driver")

@router.post("/admin/bookings/{booking_id}/resend-confirmation")
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

@router.get("/admin/bookings/{booking_id}/invoice")
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

@router.post("/admin/bookings/{booking_id}/cancel")
async def cancel_booking_admin(booking_id: int, cancel_data: CancelBookingRequest, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Cancel booking with reason"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.services.booking_service import BookingService
    booking_service = BookingService(db)
    
    success = booking_service.cancel_booking(booking_id, cancel_data.reason, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return {"message": "Booking cancelled successfully"}

# Hotel-specific booking endpoints
@router.get("/admin/hotel-bookings")
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
    
    booking_service = BookingService(db)
    
    # Parse date strings
    parsed_start_date = parse_date_string(start_date) if start_date else None
    parsed_end_date = parse_date_string(end_date) if end_date else None
    
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
@router.get("/admin/car-bookings")
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
    
    booking_service = BookingService(db)
    
    # Parse date strings
    parsed_start_date = parse_date_string(start_date) if start_date else None
    parsed_end_date = parse_date_string(end_date) if end_date else None
    
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