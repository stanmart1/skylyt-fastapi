from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from .search import LocationSearch, DateRange, PaginationParams


class HotelSearchRequest(BaseModel):
    location: LocationSearch
    dates: DateRange
    guests: int = 1
    rooms: int = 1
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    star_rating: Optional[int] = None
    amenities: Optional[List[str]] = None
    pagination: PaginationParams = PaginationParams()


class HotelAmenity(BaseModel):
    name: str
    icon: Optional[str] = None


class HotelResponse(BaseModel):
    id: str
    name: str
    location: str
    description: Optional[str] = None
    star_rating: float
    price_per_night: float
    room_count: int
    currency: str = "USD"
    amenities: Optional[List[str]] = None
    features: Optional[List[str]] = None
    images: Optional[List[str]] = None
    is_available: bool = True
    is_featured: bool = False