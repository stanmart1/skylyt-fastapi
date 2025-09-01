from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import date, datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.driver import Driver
from app.models.booking import Booking

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
    """Get bookings assigned to a specific driver"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    bookings = db.query(Booking).filter(
        Booking.driver_id == driver_id
    ).offset(skip).limit(limit).all()
    
    return {
        "driver_name": driver.name,
        "bookings": bookings
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