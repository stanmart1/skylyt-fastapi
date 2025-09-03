from pydantic import BaseModel, validator
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


class CarCreateRequest(BaseModel):
    name: str
    category: str
    price_per_day: float
    currency: Optional[str] = "USD"
    images: Optional[List[str]] = []
    passengers: Optional[int] = 4
    transmission: Optional[str] = "automatic"
    fuel_type: Optional[str] = "petrol"
    features: Optional[List[str]] = []
    
    @validator('price_per_day')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("Price must be positive")
        return v