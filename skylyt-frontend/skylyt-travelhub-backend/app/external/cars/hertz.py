from .car_base import CarRentalAPIBase
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HertzAPI(CarRentalAPIBase):
    """Hertz car rental API integration"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://api.hertz.com/v1")
    
    def search_cars(self, pickup_location: str, dropoff_location: str,
                   pickup_date: datetime, dropoff_date: datetime, **filters) -> List[Dict[str, Any]]:
        """Search cars via Hertz API"""
        try:
            mock_results = [
                {
                    "car_id": "hertz_economy_1",
                    "make": "Nissan",
                    "model": "Versa",
                    "category": "economy",
                    "price_per_day": 35.99,
                    "currency": "USD",
                    "transmission": "automatic",
                    "seats": 5,
                    "supplier": "hertz"
                },
                {
                    "car_id": "hertz_luxury_1",
                    "make": "Mercedes",
                    "model": "C-Class",
                    "category": "luxury",
                    "price_per_day": 89.99,
                    "currency": "USD",
                    "transmission": "automatic",
                    "seats": 5,
                    "supplier": "hertz"
                }
            ]
            
            logger.info(f"Found {len(mock_results)} cars from Hertz")
            return mock_results
            
        except Exception as e:
            logger.error(f"Hertz search failed: {e}")
            return []
    
    def get_car_details(self, car_id: str) -> Dict[str, Any]:
        return {
            "car_id": car_id,
            "detailed_specs": "Full-size sedan with premium features",
            "included_features": ["GPS", "Bluetooth", "Air Conditioning"],
            "rental_terms": ["Minimum age 21", "Valid license required"]
        }
    
    def check_availability(self, car_id: str, pickup_date: datetime,
                          dropoff_date: datetime) -> Dict[str, Any]:
        return {
            "available": True,
            "cars_available": 3,
            "price_per_day": 35.99,
            "currency": "USD"
        }
    
    def create_booking(self, car_id: str, driver_info: Dict[str, Any],
                      booking_details: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "booking_id": f"hertz_{hash(car_id)}",
            "confirmation_number": "HZ123456789",
            "status": "confirmed"
        }
    
    def cancel_booking(self, booking_id: str) -> Dict[str, Any]:
        return {
            "booking_id": booking_id,
            "status": "cancelled",
            "refund_amount": 179.95
        }