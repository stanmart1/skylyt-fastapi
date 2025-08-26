from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.car import Car
from app.schemas.car import CarSearchRequest, CarResponse
from app.schemas.search import SearchResponse
from app.utils.cache_manager import cache_manager, cache_result
from decimal import Decimal


class CarService:
    
    @staticmethod
    def search_cars(search_request: CarSearchRequest, db: Session) -> Dict[str, Any]:
        # Build optimized query with indexes
        filters = [Car.is_available == True]
        
        if search_request.car_type:
            filters.append(Car.category == search_request.car_type)
        if search_request.transmission:
            filters.append(Car.transmission == search_request.transmission)
        if search_request.min_price:
            filters.append(Car.price_per_day >= search_request.min_price)
        if search_request.max_price:
            filters.append(Car.price_per_day <= search_request.max_price)
        
        # Single query with all filters
        query = db.query(Car).filter(and_(*filters))
        
        # Get total count efficiently
        total = query.count()
        
        # Pagination with optimized query
        offset = (search_request.pagination.page - 1) * search_request.pagination.limit
        cars = query.order_by(Car.price_per_day).offset(offset).limit(search_request.pagination.limit).all()
        
        # Optimized list comprehension
        car_list = [{
            "id": str(car.id),
            "name": f"{car.make} {car.model}",
            "category": car.category,
            "price": float(car.price_per_day),
            "image_url": car.images[0] if car.images else "/placeholder.svg",
            "passengers": car.seats,
            "transmission": car.transmission,
            "features": [f["name"] for f in car.features] if car.features else []
        } for car in cars]
        
        return {
            "cars": car_list,
            "total": total
        }
    
    @staticmethod
    def get_car_details(car_id: str) -> Dict[str, Any]:
        return {
            "id": car_id,
            "make": "Toyota",
            "model": "Camry",
            "detailed_specs": "2.5L 4-cylinder engine, CVT transmission",
            "rental_terms": ["Must be 21+ to rent", "Valid driver's license required"],
            "insurance_options": ["Basic", "Premium", "Full Coverage"]
        }
    
    @staticmethod
    def check_car_availability(car_id: str, pickup_date: str, return_date: str) -> bool:
        return True
    
    @staticmethod
    def calculate_car_pricing(car_id: str, pickup_date: str, return_date: str, insurance: str = None) -> Dict[str, Any]:
        base_price = Decimal("45.99")
        days = 3  # Mock calculation
        subtotal = base_price * days
        taxes = subtotal * Decimal("0.12")
        insurance_cost = Decimal("15.00") * days if insurance else Decimal("0")
        total = subtotal + taxes + insurance_cost
        
        return {
            "base_price_per_day": base_price,
            "days": days,
            "subtotal": subtotal,
            "taxes": taxes,
            "insurance": insurance_cost,
            "total_price": total,
            "currency": "USD"
        }
    
    @staticmethod
    def add_car_insurance(booking_id: int, insurance_type: str) -> Dict[str, Any]:
        return {
            "insurance_type": insurance_type,
            "daily_cost": Decimal("15.00"),
            "coverage": "Collision and comprehensive coverage"
        }