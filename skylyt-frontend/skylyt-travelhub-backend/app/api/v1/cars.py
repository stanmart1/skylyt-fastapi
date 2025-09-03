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
    location: Optional[str] = Query(None, description="Pickup location"),
    pickup_date: Optional[str] = Query(None, description="Pickup date (YYYY-MM-DD)"),
    return_date: Optional[str] = Query(None, description="Return date (YYYY-MM-DD)"),
    category: Optional[str] = Query(None, description="Car category"),
    transmission: Optional[str] = Query(None, description="Transmission type"),
    min_price: Optional[Decimal] = Query(None, description="Minimum price per day"),
    max_price: Optional[Decimal] = Query(None, description="Maximum price per day"),
    guests: Optional[int] = Query(None, description="Number of passengers"),
    amenities: Optional[str] = Query(None, description="Comma-separated features"),
    rating: Optional[float] = Query(None, description="Minimum rating"),
    sort_by: Optional[str] = Query("price", description="Sort by field"),
    currency: str = Query("NGN", description="Currency code"),
    page: int = Query(1, description="Page number"),
    per_page: int = Query(20, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Search cars with filters and caching"""
    from app.services.cache_service import CacheService
    from app.models.car import Car
    from sqlalchemy import desc, asc, and_, or_
    
    # Create cache key from search parameters
    search_params = {
        'location': location, 'pickup_date': pickup_date, 'return_date': return_date,
        'category': category, 'transmission': transmission, 'min_price': str(min_price) if min_price else None,
        'max_price': str(max_price) if max_price else None, 'guests': guests,
        'amenities': amenities, 'rating': rating, 'sort_by': sort_by,
        'currency': currency, 'page': page, 'per_page': per_page
    }
    
    # Try to get from cache first
    cached_result = CacheService.get_cached_car_search(search_params)
    if cached_result:
        return cached_result
    
    # Build query with filters
    query = db.query(Car).filter(Car.is_available == True)
    
    # Apply filters
    if location:
        query = query.filter(Car.location.ilike(f"%{location}%"))
    if category:
        query = query.filter(Car.category.ilike(f"%{category}%"))
    if transmission:
        query = query.filter(Car.transmission.ilike(f"%{transmission}%"))
    if min_price:
        query = query.filter(Car.price_per_day >= min_price)
    if max_price:
        query = query.filter(Car.price_per_day <= max_price)
    if guests:
        query = query.filter(Car.seats >= guests)
    if rating:
        query = query.filter(Car.rating >= rating)
    
    # Filter by features/amenities
    if amenities:
        feature_list = [f.strip() for f in amenities.split(',') if f.strip()]
        if feature_list:
            for feature in feature_list:
                query = query.filter(Car.features.op('?')(feature))
    
    # Apply sorting
    if sort_by:
        if sort_by.startswith('-'):
            sort_field = sort_by[1:]
            if hasattr(Car, sort_field):
                query = query.order_by(desc(getattr(Car, sort_field)))
        else:
            if hasattr(Car, sort_by):
                query = query.order_by(asc(getattr(Car, sort_by)))
    
    # Get total and paginated results
    total = query.count()
    offset = (page - 1) * per_page
    cars = query.offset(offset).limit(per_page).all()
    
    from app.services.currency_service import CurrencyService
    
    cars_data = []
    for car in cars:
        base_price = float(car.price_per_day)
        base_currency = getattr(car, 'base_currency', 'NGN')
        
        converted_price = CurrencyService.convert_currency(
            base_price, base_currency, currency.upper(), db
        )
        
        curr_obj = CurrencyService.get_currency_by_code(currency.upper(), db)
        symbol = curr_obj.symbol if curr_obj else currency.upper()
        
        cars_data.append({
            "id": car.id,
            "name": car.name or f"{car.make} {car.model}",
            "category": car.category,
            "price": converted_price,
            "currency": currency.upper(),
            "currency_symbol": symbol,
            "image_url": car.images[0] if car.images else None,
            "passengers": car.seats,
            "transmission": car.transmission,
            "features": car.features or []
        })
    
    result = {"cars": cars_data, "total": total}
    
    # Cache the result for 5 minutes
    CacheService.cache_car_search(search_params, result, ttl=300)
    
    return result

@router.get("/")
def get_all_cars(
    currency: str = Query("NGN", description="Currency code"),
    db: Session = Depends(get_db)
):
    """Get all cars for cars page"""
    from app.models.car import Car
    
    from app.services.currency_service import CurrencyService
    
    cars = db.query(Car).filter(Car.is_available == True).all()
    
    cars_data = []
    for car in cars:
        base_price = float(car.price_per_day)
        base_currency = getattr(car, 'base_currency', 'NGN')
        
        converted_price = CurrencyService.convert_currency(
            base_price, base_currency, currency.upper(), db
        )
        
        curr_obj = CurrencyService.get_currency_by_code(currency.upper(), db)
        symbol = curr_obj.symbol if curr_obj else currency.upper()
        
        cars_data.append({
            "id": car.id,
            "name": car.name or f"{car.make} {car.model}",
            "category": car.category,
            "price": converted_price,
            "currency": currency.upper(),
            "currency_symbol": symbol,
            "image_url": car.images[0] if car.images else None,
            "passengers": car.seats,
            "transmission": car.transmission,
            "features": car.features or []
        })
    
    return cars_data


@router.get("/featured")
def get_featured_cars(
    currency: str = Query("NGN", description="Currency code"),
    db: Session = Depends(get_db)
):
    """Get featured cars for landing page"""
    try:
        from app.models.car import Car
        
        cars = db.query(Car).filter(Car.is_featured == True).limit(6).all()
        
        from app.services.currency_service import CurrencyService
        
        car_list = []
        for car in cars:
            base_price = float(car.price_per_day)
            base_currency = getattr(car, 'base_currency', 'NGN')
            
            converted_price = CurrencyService.convert_currency(
                base_price, base_currency, currency.upper(), db
            )
            
            curr_obj = CurrencyService.get_currency_by_code(currency.upper(), db)
            symbol = curr_obj.symbol if curr_obj else currency.upper()
            
            car_list.append({
                "id": car.id,
                "name": car.name,
                "category": car.category,
                "price": converted_price,
                "currency": currency.upper(),
                "currency_symbol": symbol,
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
    
    # Query using string ID (database uses UUID strings)
    car = db.query(Car).filter(Car.id == car_id).first()
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
        "images": car.images or [],
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