from pydantic import BaseModel
from typing import Optional, Dict, Any
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
    status: BookingStatus
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
    status: BookingStatus
    total_amount: Decimal
    currency: str
    booking_details: Dict[str, Any]