from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel


class Driver(BaseModel):
    __tablename__ = "drivers"
    
    # Basic Information
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    
    # License Details
    license_number = Column(String(50), unique=True, nullable=False)
    license_expiry = Column(Date, nullable=True)
    license_class = Column(String(10), nullable=True)  # e.g., 'B', 'C', 'D'
    
    # Employment Details
    employee_id = Column(String(20), unique=True, nullable=True)
    hire_date = Column(Date, nullable=True)
    
    # Status & Availability
    is_available = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Performance Metrics
    rating = Column(Float, default=0.0, nullable=False)
    total_trips = Column(Integer, default=0, nullable=False)
    
    # Additional Information
    address = Column(Text, nullable=True)
    emergency_contact = Column(String(100), nullable=True)
    emergency_phone = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    bookings = relationship("Booking", back_populates="driver")