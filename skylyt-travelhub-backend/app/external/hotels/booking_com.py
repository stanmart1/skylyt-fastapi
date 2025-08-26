from .hotel_base import HotelAPIBase
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BookingComAPI(HotelAPIBase):
    """Booking.com API integration"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://distribution-xml.booking.com/json/bookings")
    
    def search_hotels(self, location: str, check_in: datetime, check_out: datetime,
                     guests: int, rooms: int, **filters) -> List[Dict[str, Any]]:
        """Search hotels via Booking.com API"""
        try:
            # Mock search - would make actual API call
            mock_results = [
                {
                    "hotel_id": "booking_hotel_1",
                    "name": "Grand Plaza Hotel",
                    "location": location,
                    "price": 199.99,
                    "currency": "USD",
                    "rating": 4.5,
                    "amenities": ["wifi", "pool", "gym"],
                    "supplier": "booking.com"
                },
                {
                    "hotel_id": "booking_hotel_2", 
                    "name": "City Center Inn",
                    "location": location,
                    "price": 129.99,
                    "currency": "USD",
                    "rating": 4.2,
                    "amenities": ["wifi", "breakfast"],
                    "supplier": "booking.com"
                }
            ]
            
            logger.info(f"Found {len(mock_results)} hotels from Booking.com")
            return mock_results
            
        except Exception as e:
            logger.error(f"Booking.com search failed: {e}")
            return []
    
    def get_hotel_details(self, hotel_id: str) -> Dict[str, Any]:
        """Get hotel details from Booking.com"""
        return {
            "hotel_id": hotel_id,
            "detailed_description": "Luxury hotel in prime location",
            "facilities": ["Restaurant", "Bar", "Spa", "Business Center"],
            "policies": {
                "check_in": "15:00",
                "check_out": "11:00",
                "cancellation": "Free cancellation until 24h before arrival"
            }
        }
    
    def check_availability(self, hotel_id: str, check_in: datetime,
                          check_out: datetime, rooms: int) -> Dict[str, Any]:
        """Check availability via Booking.com"""
        return {
            "available": True,
            "rooms_available": 5,
            "price": 199.99,
            "currency": "USD"
        }
    
    def create_booking(self, hotel_id: str, guest_info: Dict[str, Any],
                      booking_details: Dict[str, Any]) -> Dict[str, Any]:
        """Create booking via Booking.com"""
        return {
            "booking_id": f"booking_com_{hash(hotel_id)}",
            "confirmation_number": "BC123456789",
            "status": "confirmed"
        }
    
    def cancel_booking(self, booking_id: str) -> Dict[str, Any]:
        """Cancel booking via Booking.com"""
        return {
            "booking_id": booking_id,
            "status": "cancelled",
            "refund_amount": 199.99
        }