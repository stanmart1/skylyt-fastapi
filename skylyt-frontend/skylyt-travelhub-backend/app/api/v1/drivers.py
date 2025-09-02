from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import date, datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.driver import Driver
from app.models.booking import Booking, TripStatus

router = APIRouter(prefix="/drivers", tags=["drivers"])


class DriverCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    license_number: str
    license_expiry: Optional[date] = None
    license_class: Optional[str] = None
    employee_id: Optional[str] = None
    hire_date: Optional[date] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    notes: Optional[str] = None


class DriverUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    license_number: Optional[str] = None
    license_expiry: Optional[date] = None
    license_class: Optional[str] = None
    employee_id: Optional[str] = None
    hire_date: Optional[date] = None
    is_available: Optional[bool] = None
    is_active: Optional[bool] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    notes: Optional[str] = None


class DriverResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    license_number: str
    license_expiry: Optional[date]
    license_class: Optional[str]
    employee_id: Optional[str]
    hire_date: Optional[date]
    is_available: bool
    is_active: bool
    rating: float
    total_trips: int
    address: Optional[str]
    emergency_contact: Optional[str]
    emergency_phone: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.get("", response_model=List[DriverResponse])
async def get_drivers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    is_available: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all drivers with optional filtering"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = db.query(Driver)
    
    if is_active is not None:
        query = query.filter(Driver.is_active == is_active)
    
    if is_available is not None:
        query = query.filter(Driver.is_available == is_available)
    
    if search:
        query = query.filter(
            Driver.name.ilike(f"%{search}%") |
            Driver.email.ilike(f"%{search}%") |
            Driver.phone.ilike(f"%{search}%") |
            Driver.license_number.ilike(f"%{search}%")
        )
    
    drivers = query.offset(skip).limit(limit).all()
    return drivers


@router.get("/{driver_id}", response_model=DriverResponse)
async def get_driver(
    driver_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific driver by ID"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    return driver


@router.post("/", response_model=DriverResponse)
async def create_driver(
    driver_data: DriverCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new driver"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if email or license number already exists
    existing_driver = db.query(Driver).filter(
        (Driver.email == driver_data.email) | 
        (Driver.license_number == driver_data.license_number)
    ).first()
    
    if existing_driver:
        if existing_driver.email == driver_data.email:
            raise HTTPException(status_code=400, detail="Email already registered")
        if existing_driver.license_number == driver_data.license_number:
            raise HTTPException(status_code=400, detail="License number already registered")
    
    driver = Driver(**driver_data.dict())
    db.add(driver)
    db.commit()
    db.refresh(driver)
    
    return driver


@router.put("/{driver_id}", response_model=DriverResponse)
async def update_driver(
    driver_id: int,
    driver_data: DriverUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a driver"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Check for email/license conflicts if being updated
    update_data = driver_data.dict(exclude_unset=True)
    
    if 'email' in update_data or 'license_number' in update_data:
        conflict_query = db.query(Driver).filter(Driver.id != driver_id)
        
        if 'email' in update_data:
            conflict_query = conflict_query.filter(Driver.email == update_data['email'])
        if 'license_number' in update_data:
            conflict_query = conflict_query.filter(Driver.license_number == update_data['license_number'])
        
        if conflict_query.first():
            raise HTTPException(status_code=400, detail="Email or license number already exists")
    
    for field, value in update_data.items():
        setattr(driver, field, value)
    
    db.commit()
    db.refresh(driver)
    
    return driver


@router.delete("/{driver_id}")
async def delete_driver(
    driver_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a driver"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Check if driver has active bookings
    active_bookings = db.query(Booking).filter(
        Booking.driver_id == driver_id,
        Booking.status.in_(["confirmed", "ongoing"])
    ).count()
    
    if active_bookings > 0:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete driver with active bookings"
        )
    
    db.delete(driver)
    db.commit()
    
    return {"message": "Driver deleted successfully"}


@router.get("/{driver_id}/bookings")
async def get_driver_bookings(
    driver_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get bookings assigned to a specific driver - Restricted Data Access"""
    # Allow driver to view their own bookings or admin to view any driver's bookings
    if not (current_user.is_admin() or current_user.is_superadmin() or 
            (hasattr(current_user, 'driver_id') and current_user.driver_id == driver_id)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Only return bookings assigned to this specific driver
    bookings = db.query(Booking).filter(
        Booking.driver_id == driver_id
    ).offset(skip).limit(limit).all()
    
    # Return only essential customer info for assigned trips
    booking_data = []
    for booking in bookings:
        booking_data.append({
            "id": booking.id,
            "booking_reference": booking.booking_reference,
            "booking_type": booking.booking_type,
            "status": booking.status,
            "trip_status": booking.trip_status.value if booking.trip_status else "pending",
            "customer_name": booking.customer_name,
            "customer_email": booking.customer_email,
            "customer_phone": booking.customer_phone,
            "start_date": booking.start_date,
            "end_date": booking.end_date,
            "pickup_location": booking.booking_data.get("pickup_location") if booking.booking_data else None,
            "dropoff_location": booking.booking_data.get("dropoff_location") if booking.booking_data else None,
            "special_requests": booking.special_requests,
            "created_at": booking.created_at
        })
    
    return {
        "driver_name": driver.name,
        "bookings": booking_data
    }


@router.put("/{driver_id}/availability")
async def update_driver_availability(
    driver_id: int,
    is_available: bool,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update driver availability status"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    driver.is_available = is_available
    db.commit()
    
    return {
        "message": f"Driver availability updated to {'available' if is_available else 'unavailable'}",
        "driver_id": driver_id,
        "is_available": is_available
    }

class TripStatusUpdate(BaseModel):
    trip_status: str

@router.put("/{driver_id}/trips/{trip_id}/status")
async def update_trip_status(
    driver_id: int,
    trip_id: int,
    status_update: TripStatusUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update trip status - 5-stage workflow"""
    # Allow driver to update their own trips or admin to update any trip
    if not (current_user.is_admin() or current_user.is_superadmin() or 
            (hasattr(current_user, 'driver_id') and current_user.driver_id == driver_id)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Validate trip status
    valid_statuses = [status.value for status in TripStatus]
    if status_update.trip_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid trip status. Must be one of: {valid_statuses}")
    
    # Get booking assigned to this driver
    booking = db.query(Booking).filter(
        Booking.id == trip_id,
        Booking.driver_id == driver_id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Trip not found or not assigned to this driver")
    
    # Update trip status
    booking.trip_status = TripStatus(status_update.trip_status)
    db.commit()
    
    # Send notification about status update
    await send_trip_notification(
        booking_id=trip_id,
        driver_id=driver_id,
        status=status_update.trip_status,
        db=db
    )
    
    return {
        "message": "Trip status updated successfully",
        "trip_id": trip_id,
        "new_status": status_update.trip_status
    }

@router.post("/{driver_id}/trips/{trip_id}/assign")
async def assign_trip_to_driver(
    driver_id: int,
    trip_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign trip to driver and send notification"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    booking = db.query(Booking).filter(Booking.id == trip_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Assign trip to driver
    booking.driver_id = driver_id
    booking.trip_status = TripStatus.PENDING
    db.commit()
    
    # Send trip assignment notification
    await send_trip_notification(
        booking_id=trip_id,
        driver_id=driver_id,
        status="assigned",
        db=db
    )
    
    return {
        "message": "Trip assigned successfully",
        "trip_id": trip_id,
        "driver_id": driver_id
    }

async def send_trip_notification(
    booking_id: int,
    driver_id: int,
    status: str,
    db: Session
):
    """Send real-time notification for trip updates"""
    try:
        from app.models.driver import Driver
        
        driver = db.query(Driver).filter(Driver.id == driver_id).first()
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        
        if not driver or not booking:
            return
        
        # Create notification record (you can extend this to save to database)
        notification_data = {
            "driver_id": driver_id,
            "driver_email": driver.email,
            "booking_id": booking_id,
            "booking_reference": booking.booking_reference,
            "status": status,
            "customer_name": booking.customer_name,
            "pickup_location": booking.booking_data.get("pickup_location") if booking.booking_data else None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Here you would integrate with your notification service
        # For now, we'll just log it
        print(f"TRIP NOTIFICATION: {notification_data}")
        
        # TODO: Integrate with email service, SMS service, or push notifications
        # await send_email_notification(notification_data)
        # await send_sms_notification(notification_data)
        # await send_push_notification(notification_data)
        
    except Exception as e:
        print(f"Failed to send notification: {e}")