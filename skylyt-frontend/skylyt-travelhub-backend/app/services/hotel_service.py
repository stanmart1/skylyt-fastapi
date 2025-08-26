from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.hotel import Hotel
from app.schemas.hotel import HotelSearchRequest, HotelResponse
from app.schemas.search import SearchResponse
from decimal import Decimal


class HotelService:
    
    @staticmethod
    def search_hotels(search_request: HotelSearchRequest, db: Session) -> Dict[str, Any]:
        query = db.query(Hotel).filter(Hotel.is_available == True)
        
        # Apply filters
        if search_request.location.city:
            query = query.filter(Hotel.city.ilike(f"%{search_request.location.city}%"))
        if search_request.location.country:
            query = query.filter(Hotel.country.ilike(f"%{search_request.location.country}%"))
        if search_request.min_price:
            query = query.filter(Hotel.price_per_night >= search_request.min_price)
        if search_request.max_price:
            query = query.filter(Hotel.price_per_night <= search_request.max_price)
        if search_request.star_rating:
            query = query.filter(Hotel.star_rating >= search_request.star_rating)
        
        # Pagination
        total = query.count()
        offset = (search_request.pagination.page - 1) * search_request.pagination.limit
        hotels = query.offset(offset).limit(search_request.pagination.limit).all()
        
        # Convert to API format
        hotel_list = []
        for hotel in hotels:
            hotel_list.append({
                "id": str(hotel.id),
                "name": hotel.name,
                "location": f"{hotel.city}, {hotel.country}",
                "rating": hotel.rating or 0,
                "price": float(hotel.price_per_night),
                "image_url": hotel.images[0] if hotel.images else "/placeholder.svg",
                "amenities": [a["name"] for a in hotel.amenities] if hotel.amenities else [],
                "description": hotel.description or ""
            })
        
        return {
            "hotels": hotel_list,
            "total": total
        }
    
    @staticmethod
    def get_hotel_details(hotel_id: str) -> Dict[str, Any]:
        # Mock hotel details
        return {
            "id": hotel_id,
            "name": "Grand Luxury Hotel",
            "description": "5-star luxury hotel in city center",
            "star_rating": 5,
            "detailed_description": "Experience luxury at its finest...",
            "check_in_time": "15:00",
            "check_out_time": "11:00",
            "policies": ["No smoking", "Pet friendly"],
            "amenities": [
                {"name": "WiFi", "icon": "wifi"},
                {"name": "Pool", "icon": "pool"}
            ]
        }
    
    @staticmethod
    def check_availability(hotel_id: str, check_in: str, check_out: str, rooms: int) -> bool:
        # Mock availability check
        return True
    
    @staticmethod
    def calculate_pricing(hotel_id: str, check_in: str, check_out: str, rooms: int) -> Dict[str, Any]:
        # Mock pricing calculation
        base_price = Decimal("299.99")
        taxes = base_price * Decimal("0.15")
        total = base_price + taxes
        
        return {
            "base_price": base_price,
            "taxes": taxes,
            "total_price": total,
            "currency": "USD"
        }