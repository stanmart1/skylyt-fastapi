from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(enum.Enum):
    STRIPE = "stripe"
    FLUTTERWAVE = "flutterwave"
    PAYSTACK = "paystack"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"


class Payment(BaseModel):
    __tablename__ = "payments"
    
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    payment_method = Column(String(20), nullable=False)
    
    # Provider specific fields (matching actual database schema)
    stripe_payment_intent_id = Column(String(255), nullable=True)
    transaction_id = Column(String(255), nullable=True)
    transfer_reference = Column(String(255), nullable=True)
    gateway_response = Column(JSON, nullable=True)
    
    # Proof of payment and refund tracking
    proof_of_payment_url = Column(String(500), nullable=True)
    refund_status = Column(String(20), default="none", nullable=False)  # none, partial, full
    refund_amount = Column(Numeric(10, 2), nullable=True)
    refund_date = Column(DateTime, nullable=True)
    refund_reason = Column(String(500), nullable=True)
    payment_reference = Column(String(100), nullable=True)
    
    # Customer snapshot at payment time
    customer_name = Column(String(255), nullable=True)
    customer_email = Column(String(255), nullable=True)
    
    # Relationships
    booking = relationship("Booking", back_populates="payments")
    proofs = relationship("PaymentProof", back_populates="payment")