from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import datetime
from app.models.booking import BookingStatus, BookingType


class BookingCreate(BaseModel):
    booking_type: BookingType
    booking_data: Dict[str, Any]
    start_date: datetime
    end_date: datetime
    total_amount: Decimal
    currency: str = "USD"


class BookingResponse(BaseModel):
    id: int
    user_id: int
    booking_type: BookingType
    status: str
    booking_data: Dict[str, Any]
    total_amount: Decimal
    currency: str
    start_date: datetime
    end_date: datetime
    confirmation_number: Optional[str]
    customer_name: str
    customer_email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class BookingUpdate(BaseModel):
    booking_data: Optional[Dict[str, Any]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class BookingConfirmation(BaseModel):
    booking_id: int
    confirmation_number: str
    status: str
    total_amount: Decimal
    currency: str
    booking_details: Dict[str, Any]


class BookingStatusUpdate(BaseModel):
    status: str
    
    @validator('status')
    def validate_status(cls, v):
        from app.utils.validators import VALID_BOOKING_STATUSES
        if v not in VALID_BOOKING_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(VALID_BOOKING_STATUSES)}")
        return v


class BookingCreateRequest(BaseModel):
    user_id: int
    booking_type: str
    status: Optional[str] = "pending"
    hotel_name: Optional[str] = None
    car_name: Optional[str] = None
    total_amount: float
    currency: Optional[str] = "USD"
    booking_data: Optional[dict] = None
    
    @validator('total_amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v
    
    @validator('currency')
    def validate_currency(cls, v):
        from app.utils.validators import VALID_CURRENCIES
        if v not in VALID_CURRENCIES:
            raise ValueError(f"Invalid currency. Must be one of: {', '.join(VALID_CURRENCIES)}")
        return v


class BookingUpdateRequest(BaseModel):
    status: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    special_requests: Optional[str] = None
    booking_type: Optional[str] = None
    hotel_name: Optional[str] = None
    car_name: Optional[str] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    driver_id: Optional[int] = None
    
    @validator('total_amount')
    def validate_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Amount must be positive")
        return v
    
    @validator('currency')
    def validate_currency(cls, v):
        from app.utils.validators import VALID_CURRENCIES
        if v is not None and v not in VALID_CURRENCIES:
            raise ValueError(f"Invalid currency. Must be one of: {', '.join(VALID_CURRENCIES)}")
        return v


class CancelBookingRequest(BaseModel):
    reason: Optional[str] = "Cancelled by admin"


class BulkDeleteRequest(BaseModel):
    ids: List[int]
    
    @validator('ids')
    def validate_ids(cls, v):
        if not v:
            raise ValueError("No IDs provided")
        return v