from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from .search import LocationSearch, DateRange, PaginationParams


class CarSearchRequest(BaseModel):
    pickup_location: LocationSearch
    dropoff_location: Optional[LocationSearch] = None
    dates: DateRange
    driver_age: int = 25
    car_type: Optional[str] = None
    transmission: Optional[str] = None  # "automatic", "manual"
    fuel_type: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    pagination: PaginationParams = PaginationParams()


class CarFeature(BaseModel):
    name: str
    included: bool = True


class CarResponse(BaseModel):
    id: str
    make: str
    model: str
    year: int
    category: str  # "economy", "compact", "midsize", "luxury", etc.
    transmission: str
    fuel_type: str
    seats: int
    doors: int
    price_per_day: Decimal
    currency: str = "USD"
    features: List[CarFeature]
    images: List[str]
    supplier: str
    pickup_location: str
    mileage_policy: str