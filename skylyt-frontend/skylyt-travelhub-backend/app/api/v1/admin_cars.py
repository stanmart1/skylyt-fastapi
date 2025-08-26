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