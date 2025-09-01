from sqlalchemy import Column, String, Integer, Float, JSON, Boolean
from app.core.database import Base
from datetime import datetime


class Car(Base):
    __tablename__ = "cars"
    
    id = Column(String, primary_key=True, index=True)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat(), nullable=False)
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), nullable=False)
    __tablename__ = "cars"
    
    name = Column(String, nullable=False)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
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
    is_available = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)