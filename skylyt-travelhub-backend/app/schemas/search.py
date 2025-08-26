from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime, date


class LocationSearch(BaseModel):
    city: str
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class DateRange(BaseModel):
    start_date: date
    end_date: date


class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 20


class SearchResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool