from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import logging

from app.core.dependencies import get_current_user
from app.core.database import get_db

router = APIRouter()

# Pydantic Models
class DriverProfileUpdate(BaseModel):
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    notes: Optional[str] = None

class AvailabilityUpdate(BaseModel):
    is_available: bool

class TripStatusUpdate(BaseModel):
    trip_status: str

class NotificationReadUpdate(BaseModel):
    is_read: bool = True

# Helper Functions
def serialize_driver(driver) -> dict:
    """Serialize driver object to dictionary"""
    return {
        "id": driver.id,
        "name": driver.name,
        "email": driver.email,
        "phone": driver.phone,
        "license_number": driver.license_number,
        "license_expiry": driver.license_expiry.isoformat() if driver.license_expiry else None,
        "license_class": driver.license_class,
        "is_available": driver.is_available,
        "is_active": driver.is_active,
        "rating": float(driver.rating) if driver.rating else 0.0,
        "total_trips": driver.total_trips,
        "address": driver.address,
        "emergency_contact": driver.emergency_contact,
        "emergency_phone": driver.emergency_phone,
        "notes": driver.notes,
        "created_at": driver.created_at.isoformat() if driver.created_at else None,
        "updated_at": driver.updated_at.isoformat() if driver.updated_at else None
    }

def serialize_trip(booking) -> dict:
    """Serialize booking/trip object to dictionary"""
    return {
        "id": booking.id,
        "booking_reference": booking.booking_reference,
        "booking_type": booking.booking_type,
        "status": booking.status,
        "trip_status": booking.booking_data.get('trip_status', 'pending') if booking.booking_data else 'pending',
        "customer_name": booking.customer_name,
        "customer_email": booking.customer_email,
        "customer_phone": getattr(booking, 'customer_phone', None),
        "start_date": booking.start_date.isoformat() if booking.start_date else None,
        "end_date": booking.end_date.isoformat() if booking.end_date else None,
        "pickup_location": booking.booking_data.get('pickup_location') if booking.booking_data else None,
        "dropoff_location": booking.booking_data.get('dropoff_location') if booking.booking_data else None,
        "special_requests": booking.special_requests,
        "total_amount": float(booking.total_amount) if booking.total_amount else 0,
        "currency": booking.currency,
        "created_at": booking.created_at.isoformat() if booking.created_at else None
    }

def serialize_notification(notification) -> dict:
    """Serialize notification object to dictionary"""
    return {
        "id": notification.id,
        "title": notification.title,
        "message": notification.message,
        "type": notification.type,
        "is_read": notification.is_read,
        "created_at": notification.created_at.isoformat() if notification.created_at else None
    }

def get_driver_by_user_id(user_id: int, db: Session):
    """Get driver record by user ID"""
    from app.models.driver import Driver
    from app.models.user import User
    
    # First get the user to find their email
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # Find driver by email (assuming driver email matches user email)
    driver = db.query(Driver).filter(Driver.email == user.email).first()
    return driver

# Routes
@router.get("/driver/profile")
async def get_driver_profile(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current driver's profile"""
    driver = get_driver_by_user_id(current_user.id, db)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")
    
    return serialize_driver(driver)

@router.put("/driver/profile")
async def update_driver_profile(
    profile_data: DriverProfileUpdate,
    current_user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Update current driver's profile"""
    driver = get_driver_by_user_id(current_user.id, db)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")
    
    try:
        # Update fields from validated Pydantic model
        update_data = profile_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(driver, field):
                setattr(driver, field, value)
        
        db.commit()
        db.refresh(driver)
        
        return {
            "message": "Profile updated successfully",
            "profile": serialize_driver(driver)
        }
    except Exception as e:
        db.rollback()
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to update driver profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")

@router.put("/driver/availability")
async def update_driver_availability(
    availability_data: AvailabilityUpdate,
    current_user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Update driver availability status"""
    driver = get_driver_by_user_id(current_user.id, db)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")
    
    try:
        driver.is_available = availability_data.is_available
        db.commit()
        db.refresh(driver)
        
        return {
            "message": "Availability updated successfully",
            "is_available": driver.is_available
        }
    except Exception as e:
        db.rollback()
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to update driver availability: {e}")
        raise HTTPException(status_code=500, detail="Failed to update availability")

@router.get("/driver/trips")
async def get_driver_trips(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get trips assigned to current driver"""
    driver = get_driver_by_user_id(current_user.id, db)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")
    
    try:
        from app.models.booking import Booking
        
        # Get bookings assigned to this driver
        bookings = db.query(Booking).filter(
            Booking.driver_id == driver.id,
            Booking.booking_type == 'car'
        ).order_by(Booking.created_at.desc()).all()
        
        trips = [serialize_trip(booking) for booking in bookings]
        
        return {
            "trips": trips,
            "total": len(trips)
        }
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to fetch driver trips: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch trips")

@router.put("/driver/trips/{trip_id}/status")
async def update_trip_status(
    trip_id: int,
    status_data: TripStatusUpdate,
    current_user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Update trip status"""
    driver = get_driver_by_user_id(current_user.id, db)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")
    
    try:
        from app.models.booking import Booking
        
        # Get the booking and verify it's assigned to this driver
        booking = db.query(Booking).filter(
            Booking.id == trip_id,
            Booking.driver_id == driver.id
        ).first()
        
        if not booking:
            raise HTTPException(status_code=404, detail="Trip not found or not assigned to you")
        
        # Validate trip status
        valid_statuses = ['pending', 'en_route', 'in_progress', 'completed', 'cancelled']
        if status_data.trip_status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid trip status. Must be one of: {', '.join(valid_statuses)}")
        
        # Update trip status in booking_data
        if not booking.booking_data:
            booking.booking_data = {}
        
        booking.booking_data['trip_status'] = status_data.trip_status
        
        # Mark the booking_data as modified for SQLAlchemy to detect changes
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(booking, 'booking_data')
        
        # If trip is completed, mark driver as available
        if status_data.trip_status == 'completed':
            driver.is_available = True
            driver.total_trips += 1
        
        db.commit()
        db.refresh(booking)
        db.refresh(driver)
        
        return {
            "message": "Trip status updated successfully",
            "trip_id": trip_id,
            "trip_status": status_data.trip_status
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to update trip status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update trip status")

@router.get("/driver/notifications")
async def get_driver_notifications(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get notifications for current driver"""
    try:
        from app.models.notification import Notification
        
        notifications = db.query(Notification).filter(
            Notification.user_id == current_user.id
        ).order_by(Notification.created_at.desc()).limit(50).all()
        
        return {
            "notifications": [serialize_notification(n) for n in notifications],
            "unread_count": sum(1 for n in notifications if not n.is_read)
        }
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to fetch notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch notifications")

@router.put("/driver/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to mark notification as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to update notification")

@router.put("/driver/notifications/mark-all-read")
async def mark_all_notifications_read(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Mark all notifications as read"""
    try:
        from app.models.notification import Notification
        
        db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        ).update({"is_read": True})
        
        db.commit()
        
        return {"message": "All notifications marked as read"}
    except Exception as e:
        db.rollback()
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to mark all notifications as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to update notifications")