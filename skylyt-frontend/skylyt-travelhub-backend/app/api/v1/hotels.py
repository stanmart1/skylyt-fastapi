from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, List
from app.core.database import get_db
from app.schemas.hotel import HotelSearchRequest, HotelResponse
from app.schemas.search import SearchResponse
from app.services.hotel_service import HotelService
from decimal import Decimal

router = APIRouter(prefix="/hotels", tags=["hotels"])


@router.get("/")
async def get_all_hotels(
    page: int = Query(1, description="Page number"),
    per_page: int = Query(16, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get all hotels for admin management"""
    from app.utils.cache import api_cache
    from app.utils.query_optimizer import QueryOptimizer
    
    # Check cache first
    cached_result = await api_cache.get_cached_response("hotels_all", {"page": page, "per_page": per_page})
    if cached_result:
        return cached_result
    
    try:
        from app.models.hotel import Hotel
        
        # Use QueryOptimizer to eager load images
        query = QueryOptimizer.optimize_hotel_query(db.query(Hotel))
        total = query.count()
        hotels = query.offset((page - 1) * per_page).limit(per_page).all()
        
        hotel_list = []
        for hotel in hotels:
            # Use preloaded images instead of lazy loading
            image_url = None
            if hotel.hotel_images and len(hotel.hotel_images) > 0:
                # Get cover image or first image
                cover_image = next((img for img in hotel.hotel_images if img.is_cover), None)
                image_url = (cover_image.image_url if cover_image else hotel.hotel_images[0].image_url)
            
            hotel_list.append({
                "id": hotel.id,
                "name": hotel.name,
                "location": hotel.location,
                "rating": float(hotel.star_rating),
                "price": float(hotel.price_per_night),
                "image_url": image_url,
                "image_alt": f"{hotel.name} - Luxury hotel in {hotel.location}",
                "amenities": hotel.amenities or [],
                "description": hotel.description or "",
                "is_available": getattr(hotel, 'is_available', True),
                "is_featured": getattr(hotel, 'is_featured', False),
                "canonical_url": f"https://skylytluxury.com/hotels/{hotel.id}"
            })
        
        result = {"hotels": hotel_list, "total": total, "page": page, "per_page": per_page}
        
        # Cache for 10 minutes
        await api_cache.cache_response("hotels_all", {"page": page, "per_page": per_page}, result, ttl=600)
        
        return result
    except Exception as e:
        print(f"Error fetching hotels: {e}")
        return {"hotels": []}


@router.get("/search")
async def search_hotels(
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
    per_page: int = Query(16, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Search hotels with filters and caching"""
    from app.utils.cache import search_cache
    
    # Create cache key from search parameters
    search_params = {
        'destination': destination, 'city': city, 'checkin_date': checkin_date, 'checkout_date': checkout_date,
        'guests': guests, 'min_price': str(min_price) if min_price else None,
        'max_price': str(max_price) if max_price else None, 'star_rating': star_rating,
        'rating': rating, 'amenities': amenities, 'sort_by': sort_by,
        'currency': currency, 'page': page, 'per_page': per_page
    }
    
    # Try to get from cache first
    cached_result = await search_cache.get_search_results(search_params)
    if cached_result:
        return cached_result
    
    try:
        from app.models.hotel import Hotel
        from sqlalchemy import and_, desc, asc
        
        # Build query
        query = db.query(Hotel)
        
        # Apply filters with safe parameterized queries
        search_location = destination or city
        if search_location:
            # Use parameterized query to prevent SQL injection
            safe_location = str(search_location).replace('%', '\%').replace('_', '\_')
            query = query.filter(Hotel.location.ilike(f"%{safe_location}%"))
        if min_price:
            query = query.filter(Hotel.price_per_night >= min_price)
        if max_price:
            query = query.filter(Hotel.price_per_night <= max_price)
        
        # Handle both star_rating and rating parameters
        min_rating = star_rating or rating
        if min_rating:
            query = query.filter(Hotel.star_rating >= min_rating)
        
        # Filter by amenities with input validation
        if amenities:
            # Validate and sanitize amenity input
            amenity_list = [a.strip()[:50] for a in amenities.split(',') if a.strip() and a.strip().isalnum()]
            if amenity_list:
                for amenity in amenity_list:
                    # Use safe parameterized query
                    query = query.filter(Hotel.amenities.cast(JSONB).op('?')(amenity))
        
        # Apply sorting with whitelist validation
        if sort_by:
            # Whitelist of allowed sort fields to prevent injection
            allowed_sort_fields = ['price', 'name', 'location', 'star_rating', 'created_at']
            
            if sort_by.startswith('-'):
                sort_field = sort_by[1:]
                if sort_field == 'price':
                    query = query.order_by(desc(Hotel.price_per_night))
                elif sort_field in allowed_sort_fields and hasattr(Hotel, sort_field):
                    query = query.order_by(desc(getattr(Hotel, sort_field)))
            else:
                if sort_by == 'price':
                    query = query.order_by(asc(Hotel.price_per_night))
                elif sort_by in allowed_sort_fields and hasattr(Hotel, sort_by):
                    query = query.order_by(asc(getattr(Hotel, sort_by)))
        
        # Get total count
        total = query.count()
        
        # Apply pagination with optimization
        from app.utils.query_optimizer import QueryOptimizer
        optimized_query = QueryOptimizer.optimize_hotel_query(query)
        hotels = optimized_query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Format response with currency conversion
        from app.services.currency_service import CurrencyService
        
        from app.models.hotel_image import HotelImage
        
        # Optimize: Get currency once and preload images
        curr_obj = CurrencyService.get_currency_by_code(currency.upper(), db)
        symbol = curr_obj.symbol if curr_obj else currency.upper()
        
        # Preload all hotel images in one query
        hotel_ids = [hotel.id for hotel in hotels]
        hotel_images = db.query(HotelImage).filter(
            HotelImage.hotel_id.in_(hotel_ids)
        ).order_by(HotelImage.hotel_id, HotelImage.is_cover.desc(), HotelImage.display_order).all()
        
        # Group images by hotel_id
        images_by_hotel = {}
        for img in hotel_images:
            if img.hotel_id not in images_by_hotel:
                images_by_hotel[img.hotel_id] = img
        
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
            
            exchange_rate = CurrencyService.convert_currency(1.0, base_currency, currency.upper(), db)
            
            # Use preloaded image
            cover_image = images_by_hotel.get(hotel.id)
            
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
                "image_url": cover_image.image_url if cover_image else None,
                "image_alt": f"{hotel.name} - Luxury hotel in {hotel.location}",
                "amenities": hotel.amenities or [],
                "description": hotel.description or "",
                "is_available": getattr(hotel, 'is_available', True),
                "canonical_url": f"https://skylytluxury.com/hotels/{hotel.id}"
            })
        
        result = {"hotels": hotel_list, "total": total}
        
        # Cache the result for 5 minutes
        await search_cache.cache_search_results(search_params, result, ttl=300)
        
        return result
    except Exception as e:
        print(f"Error searching hotels: {e}")
        return {"hotels": [], "total": 0}


@router.get("/featured")
async def get_featured_hotels(
    currency: str = Query("NGN", description="Currency code"),
    db: Session = Depends(get_db)
):
    """Get featured hotels for landing page"""
    from app.utils.cache import api_cache
    from app.utils.query_optimizer import QueryOptimizer
    
    cache_key = f"featured_hotels_{currency}"
    cached_result = await api_cache.get_cached_response("featured_hotels", {"currency": currency})
    if cached_result:
        return cached_result
    
    try:
        from app.models.hotel import Hotel
        from app.models.hotel_image import HotelImage
        
        # Use QueryOptimizer to eager load images
        query = QueryOptimizer.optimize_hotel_query(db.query(Hotel))
        hotels = query.filter(Hotel.is_featured == True).limit(6).all()
        
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
            
            # Use preloaded images instead of N+1 query
            image_url = None
            if hotel.hotel_images and len(hotel.hotel_images) > 0:
                cover_image = next((img for img in hotel.hotel_images if img.is_cover), None)
                image_url = (cover_image.image_url if cover_image else hotel.hotel_images[0].image_url)
            
            hotel_list.append({
                "id": hotel.id,
                "name": hotel.name,
                "location": hotel.location,
                "rating": float(hotel.star_rating),
                "price": converted_price,
                "currency": currency.upper(),
                "currency_symbol": symbol,
                "image_url": image_url,
                "image_alt": f"{hotel.name} - Featured luxury hotel in {hotel.location}",
                "amenities": hotel.amenities or [],
                "description": hotel.description or "",
                "is_available": getattr(hotel, 'is_available', True),
                "is_featured": hotel.is_featured,
                "canonical_url": f"https://skylytluxury.com/hotels/{hotel.id}"
            })
        
        result = {"hotels": hotel_list}
        
        # Cache for 15 minutes
        await api_cache.cache_response("featured_hotels", {"currency": currency}, result, ttl=900)
        
        return result
    except Exception as e:
        print(f"Error fetching featured hotels: {e}")
        return {"hotels": []}


@router.get("/destinations")
async def get_popular_destinations():
    """Get popular hotel destinations with caching"""
    from app.utils.cache import cache_manager
    
    # Cache for 1 hour since destinations don't change frequently
    cached_destinations = await cache_manager.get("popular_destinations")
    if cached_destinations:
        return cached_destinations
    
    destinations = [
        {"city": "New York", "country": "USA", "hotels_count": 1250},
        {"city": "London", "country": "UK", "hotels_count": 890},
        {"city": "Paris", "country": "France", "hotels_count": 1100},
        {"city": "Tokyo", "country": "Japan", "hotels_count": 750}
    ]
    
    result = {"destinations": destinations}
    await cache_manager.set("popular_destinations", result, 3600)
    return result


@router.get("/{hotel_id}")
def get_hotel_details(hotel_id: str, db: Session = Depends(get_db)):
    """Get detailed hotel information"""
    try:
        from app.models.hotel import Hotel
        
        hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        if not hotel:
            raise HTTPException(status_code=404, detail="Hotel not found")
        
        # Get all images from HotelImage table
        from app.models.hotel_image import HotelImage
        hotel_images = db.query(HotelImage).filter(
            HotelImage.hotel_id == hotel.id
        ).order_by(HotelImage.display_order).all()
        
        images = [img.image_url for img in hotel_images]
        
        return {
            "id": hotel.id,
            "name": hotel.name,
            "location": hotel.location,
            "star_rating": float(hotel.star_rating),
            "price_per_night": float(hotel.price_per_night),
            "description": hotel.description or "",
            "images": images,
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