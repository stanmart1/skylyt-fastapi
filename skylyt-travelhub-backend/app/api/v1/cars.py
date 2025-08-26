from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.schemas.car import CarSearchRequest, CarResponse
from app.schemas.search import SearchResponse
from app.services.car_service import CarService
from decimal import Decimal

router = APIRouter(prefix="/cars", tags=["cars"])


@router.get("/search")
def search_cars(
    pickup_city: Optional[str] = Query(None, description="Pickup city"),
    pickup_country: Optional[str] = Query(None, description="Pickup country"),
    dropoff_city: Optional[str] = Query(None, description="Dropoff city"),
    pickup_date: Optional[str] = Query(None, description="Pickup date (YYYY-MM-DD)"),
    dropoff_date: Optional[str] = Query(None, description="Dropoff date (YYYY-MM-DD)"),
    driver_age: int = Query(25, description="Driver age"),
    car_type: Optional[str] = Query(None, description="Car category"),
    transmission: Optional[str] = Query(None, description="Transmission type"),
    min_price: Optional[Decimal] = Query(None, description="Minimum price per day"),
    max_price: Optional[Decimal] = Query(None, description="Maximum price per day"),
    page: int = Query(1, description="Page number"),
    limit: int = Query(20, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Search cars with filters"""
    from app.models.car import Car
    
    # Simple query for all available cars
    query = db.query(Car).filter(Car.is_available == True)
    
    # Apply filters if provided
    if car_type:
        query = query.filter(Car.category == car_type)
    if transmission:
        query = query.filter(Car.transmission == transmission)
    if min_price:
        query = query.filter(Car.price_per_day >= min_price)
    if max_price:
        query = query.filter(Car.price_per_day <= max_price)
    
    # Get total and paginated results
    total = query.count()
    offset = (page - 1) * limit
    cars = query.offset(offset).limit(limit).all()
    
    cars_data = [{
        "id": car.id,
        "name": car.name or f"{car.make} {car.model}",
        "category": car.category,
        "price": float(car.price_per_day),
        "image_url": car.images[0] if car.images else None,
        "passengers": car.seats,
        "transmission": car.transmission,
        "features": car.features or []
    } for car in cars]
    
    return {"cars": cars_data, "total": total}

@router.get("/")
def get_all_cars(db: Session = Depends(get_db)):
    """Get all cars for cars page"""
    from app.models.car import Car
    
    cars = db.query(Car).filter(Car.is_available == True).all()
    return [{
        "id": car.id,
        "name": car.name or f"{car.make} {car.model}",
        "category": car.category,
        "price": float(car.price_per_day),
        "image_url": car.images[0] if car.images else None,
        "passengers": car.seats,
        "transmission": car.transmission,
        "features": car.features or []
    } for car in cars]


@router.get("/featured")
def get_featured_cars(db: Session = Depends(get_db)):
    """Get featured cars for landing page"""
    try:
        from app.models.car import Car
        
        cars = db.query(Car).filter(Car.is_featured == True).limit(6).all()
        
        car_list = []
        for car in cars:
            car_list.append({
                "id": car.id,
                "name": car.name,
                "category": car.category,
                "price": float(car.price_per_day),
                "image_url": car.images[0] if car.images and len(car.images) > 0 else None,
                "passengers": car.seats,
                "transmission": car.transmission,
                "features": car.features or [],
                "is_featured": car.is_featured
            })
        
        return {"cars": car_list}
    except Exception as e:
        print(f"Error fetching featured cars: {e}")
        return {"cars": []}


@router.get("/locations")
def get_pickup_locations():
    """Get available pickup/dropoff locations"""
    return {
        "locations": [
            {"city": "New York", "country": "USA", "airport_code": "JFK"},
            {"city": "Los Angeles", "country": "USA", "airport_code": "LAX"},
            {"city": "London", "country": "UK", "airport_code": "LHR"},
            {"city": "Paris", "country": "France", "airport_code": "CDG"}
        ]
    }


@router.get("/categories")
def get_car_categories():
    """Get car categories and types"""
    return {
        "categories": [
            {"name": "Economy", "description": "Compact and fuel-efficient"},
            {"name": "Compact", "description": "Small and easy to park"},
            {"name": "Midsize", "description": "Comfortable for longer trips"},
            {"name": "Full-size", "description": "Spacious and comfortable"},
            {"name": "Luxury", "description": "Premium vehicles with high-end features"},
            {"name": "SUV", "description": "Sport utility vehicles for all terrains"}
        ]
    }


@router.get("/{car_id}")
def get_car_details(car_id: str, db: Session = Depends(get_db)):
    """Get detailed car information"""
    from app.models.car import Car
    from fastapi import HTTPException
    
    try:
        car_id_int = int(car_id)
        car = db.query(Car).filter(Car.id == car_id_int).first()
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid car ID")
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    return {
        "id": car.id,
        "name": car.name,
        "category": car.category,
        "price": float(car.price_per_day),
        "passengers": car.seats,
        "transmission": car.transmission,
        "fuel_type": car.fuel_type,
        "year": car.year,
        "brand": car.make,
        "model": car.model,
        "description": car.description,
        "features": car.features,
        "image_url": car.images[0] if car.images and len(car.images) > 0 else None,
        "location": car.location,
        "rating": car.rating,
        "available": car.is_available
    }


@router.post("/{car_id}/check-availability")
def check_car_availability(
    car_id: str,
    pickup_date: str,
    return_date: str
):
    """Check car availability"""
    available = CarService.check_car_availability(car_id, pickup_date, return_date)
    return {"available": available, "car_id": car_id}