from sqlalchemy import Column, String, Integer, Float, JSON, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid


class Car(Base):
    __tablename__ = "cars"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    name = Column(String, nullable=False)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
    plate_number = Column(String, nullable=True, unique=True)
    category = Column(String, nullable=False)
    transmission = Column(String, nullable=False)
    fuel_type = Column(String, nullable=True)
    seats = Column(Integer, nullable=False)
    doors = Column(Integer, nullable=True)
    price_per_day = Column(Float, nullable=False)
    currency = Column(String, default="USD", nullable=False)
    features = Column(JSON, nullable=True)
    images = Column(JSON, nullable=True)
    supplier = Column(String, nullable=True)
    location = Column(String, nullable=True)
    description = Column(String, nullable=True)
    rating = Column(Float, nullable=True)
    mileage_policy = Column(String, nullable=True)
    current_mileage = Column(Integer, default=0, nullable=False)
    
    # Status: available, booked, out_with_customer, maintenance, out_of_service
    status = Column(String, default="available", nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    
    # Document fields
    insurance_doc_url = Column(String, nullable=True)
    insurance_expiry = Column(DateTime, nullable=True)
    registration_doc_url = Column(String, nullable=True)
    registration_expiry = Column(DateTime, nullable=True)
    roadworthiness_doc_url = Column(String, nullable=True)
    roadworthiness_expiry = Column(DateTime, nullable=True)
    
    # Maintenance relationship
    maintenance_records = relationship("CarMaintenance", back_populates="car")


class CarMaintenance(Base):
    __tablename__ = "car_maintenance"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    car_id = Column(String, ForeignKey("cars.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    maintenance_type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    cost = Column(Float, nullable=False)
    currency = Column(String, default="USD", nullable=False)
    
    scheduled_date = Column(DateTime, nullable=False)
    completed_date = Column(DateTime, nullable=True)
    next_due_date = Column(DateTime, nullable=True)
    next_due_mileage = Column(Integer, nullable=True)
    
    status = Column(String, default="scheduled", nullable=False)
    service_provider = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    
    car = relationship("Car", back_populates="maintenance_records")