from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class BookingStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class BookingType(enum.Enum):
    HOTEL = "hotel"
    CAR = "car"
    BUNDLE = "bundle"


class Booking(BaseModel):
    __tablename__ = "bookings"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    booking_reference = Column(String(50), unique=True, nullable=False)
    booking_type = Column(String(20), nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    
    # Customer details
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False)
    
    # Booking details
    hotel_name = Column(String(255), nullable=True)
    car_name = Column(String(255), nullable=True)
    check_in_date = Column(DateTime, nullable=True)
    check_out_date = Column(DateTime, nullable=True)
    number_of_guests = Column(Integer, nullable=True)
    special_requests = Column(String(1000), nullable=True)
    
    # Financial (always stored in NGN)
    total_amount_ngn = Column(Numeric(15, 2), nullable=False)
    display_currency = Column(String(3), default="NGN", nullable=False)
    display_amount = Column(Numeric(15, 2), nullable=True)  # For reference only
    payment_status = Column(String(20), default="pending", nullable=False)
    
    # Date fields for schema compatibility
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    external_booking_id = Column(String(255), nullable=True)
    confirmation_number = Column(String(255), nullable=True)
    
    # Additional data
    booking_data = Column(JSON, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking")