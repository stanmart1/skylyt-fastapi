from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.car import Car

router = APIRouter(prefix="/admin/cars", tags=["admin-cars"])


@router.get("")
def get_all_cars(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all cars for admin management"""
    cars = db.query(Car).all()
    return [{
        "id": car.id,
        "name": car.name,
        "category": car.category,
        "price": float(car.price_per_day),
        "image_url": car.images[0] if car.images else None,
        "passengers": car.seats,
        "transmission": car.transmission,
        "features": car.features or [],
        "is_featured": getattr(car, 'is_featured', False)
    } for car in cars]


@router.post("")
def create_car(
    car_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new car"""
    car = Car(
        id=str(uuid.uuid4()),
        name=car_data["name"],
        make=car_data.get("make", "Unknown"),
        model=car_data.get("model", "Unknown"),
        category=car_data["category"],
        price_per_day=car_data["price"],
        images=[car_data.get("image_url")] if car_data.get("image_url") else [],
        seats=car_data["passengers"],
        transmission=car_data["transmission"],
        features=car_data.get("features", [])
    )
    db.add(car)
    db.commit()
    db.refresh(car)
    return {"message": "Car created successfully", "id": car.id}


@router.put("/{car_id}")
def update_car(
    car_id: str,
    car_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update car details"""
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    for field, value in car_data.items():
        if hasattr(car, field):
            setattr(car, field, value)
    
    db.commit()
    db.refresh(car)
    return {"message": "Car updated successfully"}


@router.delete("/{car_id}")
def delete_car(
    car_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete car"""
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    db.delete(car)
    db.commit()
    return {"message": "Car deleted successfully"}


@router.post("/{car_id}/feature")
def toggle_feature_car(
    car_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Toggle car as featured"""
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    # Toggle featured status (assuming we add this field)
    car.is_featured = not getattr(car, 'is_featured', False)
    db.commit()
    db.refresh(car)
    return {"message": f"Car {'featured' if car.is_featured else 'unfeatured'} successfully"}


@router.get("/maintenance")
def get_car_maintenance(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get car maintenance records"""
    # Return empty list for now - implement proper maintenance model later
    return []


@router.get("/stats")
def get_car_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get car fleet statistics"""
    from sqlalchemy import func, and_
    from datetime import datetime
    
    # Get basic car statistics
    total_cars = db.query(Car).count()
    available_cars = db.query(Car).filter(Car.is_available == True).count()
    
    # Initialize other stats
    active_bookings = 0
    today_revenue = 0
    
    try:
        from app.models.booking import Booking
        from app.models.payment import Payment
        
        # Get active car bookings
        active_bookings = db.query(Booking).filter(
            and_(
                Booking.booking_type == 'car',
                Booking.status.in_(['confirmed', 'ongoing'])
            )
        ).count()
        
        # Calculate today's revenue - check all payments first
        today = datetime.now().date()
        
        # Debug: Check all payments
        all_payments = db.query(Payment).join(Booking).filter(Booking.booking_type == 'car').all()
        print(f"Debug: Found {len(all_payments)} car payments")
        for p in all_payments:
            print(f"Payment {p.id}: status={p.status}, amount={p.amount}, date={p.created_at}")
        
        # Try different status values
        today_revenue = db.query(func.sum(Payment.amount)).join(Booking).filter(
            and_(
                Booking.booking_type == 'car',
                Payment.status.in_(['completed', 'COMPLETED', 'success', 'SUCCESS'])
            )
        ).scalar() or 0
        
        print(f"Debug: Today's revenue calculated: {today_revenue}")
    except Exception as e:
        # If booking/payment models don't exist, continue with 0 values
        print(f"Debug: Exception in revenue calculation: {e}")
        pass
    
    booked_cars = active_bookings
    maintenance_cars = total_cars - available_cars - booked_cars if total_cars > available_cars + booked_cars else 0
    
    # Calculate utilization rate
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