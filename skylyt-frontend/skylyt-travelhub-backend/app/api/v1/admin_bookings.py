from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging

from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.schemas.booking import (
    BookingStatusUpdate, BookingCreateRequest, BookingUpdateRequest, 
    CancelBookingRequest, BulkDeleteRequest
)
from app.utils.serializers import serialize_booking, parse_date_string
from app.utils.validators import VALID_BOOKING_STATUSES, VALID_CURRENCIES

router = APIRouter()

class DriverAssignmentRequest(BaseModel):
    driver_id: int

# Remove duplicate helper functions - using imports instead

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
        from app.services.booking_service import BookingService
        from app.models.booking import Booking
        from app.tasks.email_tasks import send_booking_status_update_email
        
        booking_service = BookingService(db)
        result = booking_service.update_booking_status_helper(booking_id, status_update.status)
        
        # Send status update email immediately
        try:
            booking = db.query(Booking).filter(Booking.id == booking_id).first()
            if booking and booking.customer_email:
                from app.services.email_service import EmailService
                email_service = EmailService()
                email_service.send_booking_status_update(
                    booking.customer_email,
                    {
                        "user_name": booking.customer_name,
                        "booking_reference": booking.booking_reference,
                        "booking_type": booking.booking_type,
                        "new_status": status_update.status,
                        "total_amount": float(booking.total_amount),
                        "currency": booking.currency
                    }
                )
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to send status update email: {e}")
        
        return result
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
        from app.services.booking_service import BookingService
        booking_service = BookingService(db)
        return booking_service.update_booking_status_helper(booking_id, status_update.status)
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
        from app.models.payment import Payment
        
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Check for associated payments
        payments = db.query(Payment).filter(Payment.booking_id == booking_id).all()
        
        # Delete associated payments first (cascade delete)
        for payment in payments:
            db.delete(payment)
        
        # Now delete the booking
        db.delete(booking)
        db.commit()
        
        return {"message": "Booking deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to delete booking {booking_id}: {e}")
        
        # Provide more specific error messages
        error_msg = str(e).lower()
        if "foreign key" in error_msg or "constraint" in error_msg:
            raise HTTPException(status_code=400, detail="Cannot delete booking: it has associated records (payments, reviews, etc.)")
        elif "permission" in error_msg or "access" in error_msg:
            raise HTTPException(status_code=403, detail="Insufficient permissions to delete this booking")
        else:
            raise HTTPException(status_code=500, detail="Failed to delete booking")

@router.post("/admin/bookings")
async def create_booking(booking_data: BookingCreateRequest, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create new booking (admin)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.booking import Booking
        from app.models.user import User
        from app.services.email_service import EmailService
        import uuid
        
        # Generate booking reference
        booking_reference = f"BK{uuid.uuid4().hex[:8].upper()}"
        
        # Get user details for email
        user = db.query(User).filter(User.id == booking_data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        new_booking = Booking(
            user_id=booking_data.user_id,
            booking_reference=booking_reference,
            booking_type=booking_data.booking_type,
            status=booking_data.status,
            hotel_name=booking_data.hotel_name,
            car_name=booking_data.car_name,
            total_amount=booking_data.total_amount,
            currency=booking_data.currency,
            booking_data=booking_data.booking_data,
            customer_name=f"{user.first_name} {user.last_name}",
            customer_email=user.email
        )
        
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        
        # Send booking confirmation email immediately
        try:
            from app.services.email_service import EmailService
            email_service = EmailService()
            email_service.send_booking_confirmation(
                user.email,
                {
                    "user_name": f"{user.first_name} {user.last_name}",
                    "booking_reference": new_booking.booking_reference,
                    "booking_type": new_booking.booking_type,
                    "hotel_name": booking_data.hotel_name,
                    "car_name": booking_data.car_name,
                    "total_amount": float(booking_data.total_amount),
                    "currency": booking_data.currency,
                    "status": booking_data.status
                }
            )
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to send admin booking confirmation email: {e}")
        
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
    assignment_data: DriverAssignmentRequest,
    current_user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Assign driver to booking"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.booking import Booking
        from app.models.driver import Driver
        
        # Validate booking exists and is assignable
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        if booking.status in ['cancelled', 'completed']:
            raise HTTPException(status_code=400, detail="Cannot assign driver to cancelled or completed booking")
        
        if booking.booking_type != 'car':
            raise HTTPException(status_code=400, detail="Driver can only be assigned to car bookings")
        
        # Validate driver exists and is available
        driver = db.query(Driver).filter(Driver.id == assignment_data.driver_id).first()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        if not driver.is_active:
            raise HTTPException(status_code=400, detail="Driver is not active")
        
        if not driver.is_available:
            raise HTTPException(status_code=400, detail="Driver is not available")
        
        # Check if booking already has a driver assigned
        if booking.driver_id:
            raise HTTPException(status_code=400, detail="Booking already has a driver assigned")
        
        # Assign driver to booking
        booking.driver_id = assignment_data.driver_id
        
        # Set driver as busy
        driver.is_available = False
        
        db.commit()
        db.refresh(booking)
        db.refresh(driver)
        
        # Send email notifications
        try:
            from app.services.email_service import EmailService
            email_service = EmailService()
            
            # Send driver assignment email
            email_service.send_driver_assignment(
                driver.email,
                {
                    "name": driver.name,
                    "email": driver.email,
                    "phone": driver.phone
                },
                {
                    "booking_reference": booking.booking_reference,
                    "customer_name": booking.customer_name,
                    "customer_email": booking.customer_email,
                    "customer_phone": booking.customer_phone,
                    "pickup_date": booking.start_date.strftime("%B %d, %Y") if booking.start_date else "",
                    "return_date": booking.end_date.strftime("%B %d, %Y") if booking.end_date else "",
                    "total_amount": float(booking.total_amount),
                    "currency": booking.currency
                }
            )
            
            # Send customer notification about driver assignment
            email_service.send_booking_status_update(
                booking.customer_email,
                {
                    "user_name": booking.customer_name,
                    "booking_reference": booking.booking_reference,
                    "booking_type": booking.booking_type,
                    "driver_name": driver.name,
                    "driver_phone": driver.phone,
                    "driver_email": driver.email,
                    "pickup_date": booking.start_date.strftime("%B %d, %Y") if booking.start_date else "",
                    "return_date": booking.end_date.strftime("%B %d, %Y") if booking.end_date else "",
                    "total_amount": float(booking.total_amount),
                    "currency": booking.currency,
                    "status": "Driver Assigned"
                }
            )
        except Exception as email_error:
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to send email notifications: {email_error}")
        
        return {
            "message": "Driver assigned successfully. Notifications sent to driver and customer.",
            "booking_id": booking_id,
            "driver_id": assignment_data.driver_id,
            "driver_name": driver.name,
            "booking_reference": booking.booking_reference
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
    
    try:
        from app.models.booking import Booking
        from app.services.email_service import EmailService
        
        # Get booking details before cancellation
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Update booking status to cancelled
        booking.status = "cancelled"
        db.commit()
        db.refresh(booking)
        
        # Send cancellation email immediately
        if booking.customer_email:
            try:
                from app.services.email_service import EmailService
                email_service = EmailService()
                email_service.send_booking_cancellation(
                    booking.customer_email,
                    {
                        "user_name": booking.customer_name,
                        "booking_reference": booking.booking_reference,
                        "booking_type": booking.booking_type,
                        "status": "cancelled",
                        "cancellation_reason": cancel_data.reason,
                        "total_amount": float(booking.total_amount),
                        "currency": booking.currency
                    }
                )
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to send cancellation email: {e}")
        
        return {"message": "Booking cancelled successfully"}
    except Exception as e:
        db.rollback()
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to cancel booking: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel booking")

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