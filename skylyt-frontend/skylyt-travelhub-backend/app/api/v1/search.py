from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.hotel_service import HotelService
from app.services.car_service import CarService
from app.services.booking_service import BookingService
from decimal import Decimal
import decimal

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/bundles")
def search_bundles(
    city: str = Query(..., description="Destination city"),
    check_in: str = Query(..., description="Check-in date"),
    check_out: str = Query(..., description="Check-out date"),
    guests: int = Query(1, description="Number of guests"),
    rooms: int = Query(1, description="Number of rooms")
):
    """Search for hotel + car bundles"""
    from app.schemas.search import LocationSearch, DateRange, PaginationParams
    from app.schemas.hotel import HotelSearchRequest
    from app.schemas.car import CarSearchRequest
    from datetime import datetime
    
    # Search hotels
    hotel_search = HotelSearchRequest(
        location=LocationSearch(city=city),
        dates=DateRange(
            start_date=datetime.strptime(check_in, "%Y-%m-%d").date(),
            end_date=datetime.strptime(check_out, "%Y-%m-%d").date()
        ),
        guests=guests,
        rooms=rooms,
        pagination=PaginationParams(page=1, limit=5)
    )
    
    # Search cars
    car_search = CarSearchRequest(
        pickup_location=LocationSearch(city=city),
        dates=DateRange(
            start_date=datetime.strptime(check_in, "%Y-%m-%d").date(),
            end_date=datetime.strptime(check_out, "%Y-%m-%d").date()
        ),
        pagination=PaginationParams(page=1, limit=5)
    )
    
    hotels = HotelService.search_hotels(hotel_search)
    cars = CarService.search_cars(car_search)
    
    # Calculate bundle savings
    bundles = []
    for hotel in hotels.items[:3]:
        for car in cars.items[:3]:
            try:
                hotel_price_str = str(hotel["price_per_night"])
                car_price_str = str(car["price_per_day"])
                if hotel_price_str.lower() in ['nan', 'inf', '-inf'] or car_price_str.lower() in ['nan', 'inf', '-inf']:
                    continue
                hotel_price = Decimal(hotel_price_str)
                car_price = Decimal(car_price_str)
            except (ValueError, TypeError, decimal.InvalidOperation):
                continue
            savings = BookingService.calculate_bundle_savings(hotel_price, car_price)
            
            bundles.append({
                "hotel": hotel,
                "car": car,
                "individual_total": float(savings["individual_total"]),
                "bundle_price": float(savings["bundle_price"]),
                "savings": float(savings["savings"]),
                "discount_percentage": float(savings["discount_percentage"])
            })
    
    return {"bundles": bundles}


@router.post("/compare")
def compare_options(options: dict):
    """Compare multiple booking options"""
    return {
        "comparison": {
            "cheapest": options.get("options", [{}])[0] if options.get("options") else {},
            "best_value": options.get("options", [{}])[0] if options.get("options") else {},
            "luxury": options.get("options", [{}])[0] if options.get("options") else {}
        }
    }


@router.get("/suggestions")
def get_search_suggestions(query: str = Query(..., description="Search query")):
    """Get search suggestions"""
    suggestions = [
        {"type": "city", "name": f"{query} City", "country": "USA"},
        {"type": "hotel", "name": f"Grand {query} Hotel", "rating": 4.5},
        {"type": "destination", "name": f"{query} Beach Resort", "category": "beach"}
    ]
    return {"suggestions": suggestions}


@router.get("/history")
def get_search_history(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user search history"""
    return {
        "history": [
            {"query": "New York Hotels", "date": "2024-01-15", "type": "hotel"},
            {"query": "Los Angeles Cars", "date": "2024-01-14", "type": "car"},
            {"query": "Miami Bundle", "date": "2024-01-13", "type": "bundle"}
        ]
    }