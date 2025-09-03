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
    destination: Optional[str] = Query(None, description="Destination city"),
    city: Optional[str] = Query(None, description="City to search in"),
    checkin_date: Optional[str] = Query(None, description="Check-in date (YYYY-MM-DD)"),
    checkout_date: Optional[str] = Query(None, description="Check-out date (YYYY-MM-DD)"),
    guests: int = Query(1, description="Number of guests"),
    min_price: Optional[Decimal] = Query(None, description="Minimum price"),
    max_price: Optional[Decimal] = Query(None, description="Maximum price"),
    star_rating: Optional[float] = Query(None, description="Minimum star rating"),
    rating: Optional[float] = Query(None, description="Minimum rating (alias)"),
    amenities: Optional[str] = Query(None, description="Comma-separated amenities"),
    sort_by: Optional[str] = Query("price", description="Sort by field"),
    currency: str = Query("NGN", description="Currency code"),
    page: int = Query(1, description="Page number"),
    per_page: int = Query(20, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Search hotels with filters and caching"""
    from app.services.cache_service import CacheService
    
    # Create cache key from search parameters
    search_params = {
        'destination': destination, 'city': city, 'checkin_date': checkin_date, 'checkout_date': checkout_date,
        'guests': guests, 'min_price': str(min_price) if min_price else None,
        'max_price': str(max_price) if max_price else None, 'star_rating': star_rating,
        'rating': rating, 'amenities': amenities, 'sort_by': sort_by,
        'currency': currency, 'page': page, 'per_page': per_page
    }
    
    # Try to get from cache first
    cached_result = CacheService.get_cached_hotel_search(search_params)
    if cached_result:
        return cached_result
    
    try:
        from app.models.hotel import Hotel
        from sqlalchemy import and_, desc, asc
        
        # Build query
        query = db.query(Hotel)
        
        # Apply filters
        search_location = destination or city
        if search_location:
            query = query.filter(Hotel.location.ilike(f"%{search_location}%"))
        if min_price:
            query = query.filter(Hotel.price_per_night >= min_price)
        if max_price:
            query = query.filter(Hotel.price_per_night <= max_price)
        
        # Handle both star_rating and rating parameters
        min_rating = star_rating or rating
        if min_rating:
            query = query.filter(Hotel.star_rating >= min_rating)
        
        # Filter by amenities
        if amenities:
            amenity_list = [a.strip() for a in amenities.split(',') if a.strip()]
            if amenity_list:
                for amenity in amenity_list:
                    query = query.filter(Hotel.amenities.op('?')(amenity))
        
        # Apply sorting
        if sort_by:
            if sort_by.startswith('-'):
                sort_field = sort_by[1:]
                if sort_field == 'price':
                    query = query.order_by(desc(Hotel.price_per_night))
                elif hasattr(Hotel, sort_field):
                    query = query.order_by(desc(getattr(Hotel, sort_field)))
            else:
                if sort_by == 'price':
                    query = query.order_by(asc(Hotel.price_per_night))
                elif hasattr(Hotel, sort_by):
                    query = query.order_by(asc(getattr(Hotel, sort_by)))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        hotels = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Format response with currency conversion
        from app.services.currency_service import CurrencyService
        
        hotel_list = []
        for hotel in hotels:
            base_price = Decimal(str(hotel.price_per_night))
            base_currency = getattr(hotel, 'base_currency', 'NGN')
            
            if currency.upper() != base_currency:
                converted_price = CurrencyService.convert_currency(
                    float(base_price), base_currency, currency.upper(), db
                )
            else:
                converted_price = float(base_price)
            
            curr_obj = CurrencyService.get_currency_by_code(currency.upper(), db)
            symbol = curr_obj.symbol if curr_obj else currency.upper()
            exchange_rate = CurrencyService.convert_currency(1.0, base_currency, currency.upper(), db)
            
            hotel_list.append({
                "id": hotel.id,
                "name": hotel.name,
                "location": hotel.location,
                "rating": float(hotel.star_rating),
                "price": converted_price,
                "original_price": float(base_price),
                "base_currency": base_currency,
                "currency": currency.upper(),
                "currency_symbol": symbol,
                "exchange_rate": exchange_rate,
                "image_url": hotel.images[0] if hotel.images and len(hotel.images) > 0 else None,
                "amenities": hotel.amenities or [],
                "description": hotel.description or "",
                "is_available": getattr(hotel, 'is_available', True)
            })
        
        result = {"hotels": hotel_list, "total": total}
        
        # Cache the result for 5 minutes
        CacheService.cache_hotel_search(search_params, result, ttl=300)
        
        return result
    except Exception as e:
        print(f"Error searching hotels: {e}")
        return {"hotels": [], "total": 0}


@router.get("/featured")
def get_featured_hotels(
    currency: str = Query("NGN", description="Currency code"),
    db: Session = Depends(get_db)
):
    """Get featured hotels for landing page"""
    try:
        from app.models.hotel import Hotel
        
        hotels = db.query(Hotel).filter(Hotel.is_featured == True).limit(6).all()
        
        from app.services.currency_service import CurrencyService
        
        hotel_list = []
        for hotel in hotels:
            base_price = Decimal(str(hotel.price_per_night))
            base_currency = getattr(hotel, 'base_currency', 'NGN')
            
            converted_price = CurrencyService.convert_currency(
                float(base_price), base_currency, currency.upper(), db
            )
            
            curr_obj = CurrencyService.get_currency_by_code(currency.upper(), db)
            symbol = curr_obj.symbol if curr_obj else currency.upper()
            
            hotel_list.append({
                "id": hotel.id,
                "name": hotel.name,
                "location": hotel.location,
                "rating": float(hotel.star_rating),
                "price": converted_price,
                "currency": currency.upper(),
                "currency_symbol": symbol,
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