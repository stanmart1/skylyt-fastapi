from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime


class HotelAPIBase(ABC):
    """Base class for hotel supplier API integrations"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
    
    @abstractmethod
    def search_hotels(self, location: str, check_in: datetime, check_out: datetime, 
                     guests: int, rooms: int, **filters) -> List[Dict[str, Any]]:
        """Search for hotels"""
        pass
    
    @abstractmethod
    def get_hotel_details(self, hotel_id: str) -> Dict[str, Any]:
        """Get detailed hotel information"""
        pass
    
    @abstractmethod
    def check_availability(self, hotel_id: str, check_in: datetime, 
                          check_out: datetime, rooms: int) -> Dict[str, Any]:
        """Check hotel availability"""
        pass
    
    @abstractmethod
    def create_booking(self, hotel_id: str, guest_info: Dict[str, Any], 
                      booking_details: Dict[str, Any]) -> Dict[str, Any]:
        """Create hotel booking"""
        pass
    
    @abstractmethod
    def cancel_booking(self, booking_id: str) -> Dict[str, Any]:
        """Cancel hotel booking"""
        pass
    
    def _make_request(self, endpoint: str, method: str = "GET", 
                     data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to API"""
        # Mock implementation - would use httpx or requests
        return {"status": "success", "data": {}}
    
    def _handle_rate_limit(self):
        """Handle API rate limiting"""
        # Implementation for rate limiting
        pass
    
    def _transform_response(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform API response to standard format"""
        return raw_data