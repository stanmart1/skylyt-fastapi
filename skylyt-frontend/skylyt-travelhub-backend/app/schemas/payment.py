from pydantic import BaseModel
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from app.models.payment import PaymentStatus, PaymentMethod


class PaymentCreate(BaseModel):
    booking_id: int
    payment_method: PaymentMethod
    gateway: str = "stripe"
    amount: Optional[Decimal] = None


class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    amount: Decimal
    currency: str
    status: PaymentStatus
    payment_method: PaymentMethod
    transaction_id: Optional[str]
    transfer_reference: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PaymentRefund(BaseModel):
    amount: Optional[Decimal] = None
    reason: str = "Customer request"


class WebhookData(BaseModel):
    event_type: str
    data: Dict[str, Any]


class PaymentUpdateRequest(BaseModel):
    status: Optional[str] = None
    transaction_id: Optional[str] = None


class RefundRequest(BaseModel):
    amount: Optional[float] = None
    reason: Optional[str] = None