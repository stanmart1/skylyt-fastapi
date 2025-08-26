from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime


class CarRentalAPIBase(ABC):
    """Base class for car rental API integrations"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
    
    @abstractmethod
    def search_cars(self, pickup_location: str, dropoff_location: str, 
                   pickup_date: datetime, dropoff_date: datetime, **filters) -> List[Dict[str, Any]]:
        """Search for available cars"""
        pass
    
    @abstractmethod
    def get_car_details(self, car_id: str) -> Dict[str, Any]:
        """Get detailed car information"""
        pass
    
    @abstractmethod
    def check_availability(self, car_id: str, pickup_date: datetime, 
                          dropoff_date: datetime) -> Dict[str, Any]:
        """Check car availability"""
        pass
    
    @abstractmethod
    def create_booking(self, car_id: str, driver_info: Dict[str, Any], 
                      booking_details: Dict[str, Any]) -> Dict[str, Any]:
        """Create car rental booking"""
        pass
    
    @abstractmethod
    def cancel_booking(self, booking_id: str) -> Dict[str, Any]:
        """Cancel car rental booking"""
        pass