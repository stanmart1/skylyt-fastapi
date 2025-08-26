from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.schemas.hotel import HotelSearchRequest, HotelResponse
from app.schemas.search import SearchResponse
from app.services.hotel_service import HotelService
from decimal import Decimal

router = APIRouter(prefix="/hotels", tags=["hotels"])


@router.get("/")
def get_all_hotels(db: Session = Depends(get_db)):
    """Get all hotels for admin management"""
    try:
        from app.models.hotel import Hotel
        
        hotels = db.query(Hotel).all()
        
        hotel_list = []
        for hotel in hotels:
            hotel_list.append({
                "id": hotel.id,
                "name": hotel.name,
                "location": hotel.location,
                "rating": float(hotel.star_rating),
                "price": float(hotel.price_per_night),
                "image_url": hotel.images[0] if hotel.images and len(hotel.images) > 0 else None,
                "amenities": hotel.amenities or [],
                "description": hotel.description or "",
                "is_available": getattr(hotel, 'is_available', True),
                "is_featured": getattr(hotel, 'is_featured', False)
            })
        
        return {"hotels": hotel_list}
    except Exception as e:
        print(f"Error fetching hotels: {e}")
        return {"hotels": []}


@router.get("/search")
def search_hotels(
    city: Optional[str] = Query(None, description="City to search in"),
    country: Optional[str] = Query(None, description="Country"),
    check_in: Optional[str] = Query(None, description="Check-in date (YYYY-MM-DD)"),
    check_out: Optional[str] = Query(None, description="Check-out date (YYYY-MM-DD)"),
    guests: int = Query(1, description="Number of guests"),
    rooms: int = Query(1, description="Number of rooms"),
    min_price: Optional[Decimal] = Query(None, description="Minimum price"),
    max_price: Optional[Decimal] = Query(None, description="Maximum price"),
    star_rating: Optional[int] = Query(None, description="Minimum star rating"),
    page: int = Query(1, description="Page number"),
    limit: int = Query(20, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Search hotels with filters"""
    try:
        from app.models.hotel import Hotel
        from sqlalchemy import and_
        
        # Build query
        query = db.query(Hotel)
        
        # Apply filters
        if city:
            query = query.filter(Hotel.location.ilike(f"%{city}%"))
        if min_price:
            query = query.filter(Hotel.price_per_night >= min_price)
        if max_price:
            query = query.filter(Hotel.price_per_night <= max_price)
        if star_rating:
            query = query.filter(Hotel.star_rating >= star_rating)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        hotels = query.offset((page - 1) * limit).limit(limit).all()
        
        # Format response
        hotel_list = []
        for hotel in hotels:
            hotel_list.append({
                "id": hotel.id,
                "name": hotel.name,
                "location": hotel.location,
                "rating": float(hotel.star_rating),
                "price": float(hotel.price_per_night),
                "image_url": hotel.images[0] if hotel.images and len(hotel.images) > 0 else None,
                "amenities": hotel.amenities or [],
                "description": hotel.description or "",
                "is_available": getattr(hotel, 'is_available', True)
            })
        
        return {"hotels": hotel_list, "total": total}
    except Exception as e:
        print(f"Error searching hotels: {e}")
        return {"hotels": [], "total": 0}


@router.get("/featured")
def get_featured_hotels(db: Session = Depends(get_db)):
    """Get featured hotels for landing page"""
    try:
        from app.models.hotel import Hotel
        
        hotels = db.query(Hotel).filter(Hotel.is_featured == True).limit(6).all()
        
        hotel_list = []
        for hotel in hotels:
            hotel_list.append({
                "id": hotel.id,
                "name": hotel.name,
                "location": hotel.location,
                "rating": float(hotel.star_rating),
                "price": float(hotel.price_per_night),
                "image_url": hotel.images[0] if hotel.images and len(hotel.images) > 0 else None,
                "amenities": hotel.amenities or [],
                "description": hotel.description or "",
                "is_available": getattr(hotel, 'is_available', True),
                "is_featured": hotel.is_featured
            })
        
        return {"hotels": hotel_list}
    except Exception as e:
        print(f"Error fetching featured hotels: {e}")
        return {"hotels": []}


@router.get("/destinations")
def get_popular_destinations():
    """Get popular hotel destinations with caching"""
    from app.utils.cache_manager import cache_manager
    
    # Cache for 1 hour since destinations don't change frequently
    cached_destinations = cache_manager.get("popular_destinations")
    if cached_destinations:
        return {"destinations": cached_destinations}
    
    destinations = [
        {"city": "New York", "country": "USA", "hotels_count": 1250},
        {"city": "London", "country": "UK", "hotels_count": 890},
        {"city": "Paris", "country": "France", "hotels_count": 1100},
        {"city": "Tokyo", "country": "Japan", "hotels_count": 750}
    ]
    
    cache_manager.set("popular_destinations", destinations, 3600)
    return {"destinations": destinations}


@router.get("/{hotel_id}")
def get_hotel_details(hotel_id: str, db: Session = Depends(get_db)):
    """Get detailed hotel information"""
    try:
        from app.models.hotel import Hotel
        
        hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        if not hotel:
            raise HTTPException(status_code=404, detail="Hotel not found")
        
        return {
            "id": hotel.id,
            "name": hotel.name,
            "location": hotel.location,
            "star_rating": float(hotel.star_rating),
            "price_per_night": float(hotel.price_per_night),
            "description": hotel.description or "",
            "images": hotel.images or [],
            "amenities": hotel.amenities or [],
            "room_count": getattr(hotel, 'room_count', 0),
            "is_available": getattr(hotel, 'is_available', True),
            "is_featured": hotel.is_featured,
            "check_in_time": "15:00",
            "check_out_time": "11:00",
            "policies": ["No smoking in rooms", "Pets allowed with fee", "Free cancellation up to 24 hours"]
        }
    except Exception as e:
        print(f"Error fetching hotel details: {e}")
        raise HTTPException(status_code=404, detail="Hotel not found")


@router.post("/{hotel_id}/check-availability")
def check_hotel_availability(
    hotel_id: str,
    check_in: str,
    check_out: str,
    rooms: int = 1
):
    """Check hotel availability"""
    available = HotelService.check_availability(hotel_id, check_in, check_out, rooms)
    return {"available": available, "hotel_id": hotel_id}

@router.get("/amenities")
def get_hotel_amenities():
    """Get available hotel amenities"""
    return {
        "amenities": [
            {"name": "WiFi", "icon": "wifi"},
            {"name": "Pool", "icon": "pool"},
            {"name": "Gym", "icon": "gym"},
            {"name": "Spa", "icon": "spa"},
            {"name": "Restaurant", "icon": "restaurant"},
            {"name": "Bar", "icon": "bar"},
            {"name": "Business Center", "icon": "business"}
        ]
    }