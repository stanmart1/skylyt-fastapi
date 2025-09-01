from sqlalchemy import Column, String, Float, JSON, Text, Integer, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import BaseModel


class Hotel(BaseModel):
    __tablename__ = "hotels"
    
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    star_rating = Column(Float, nullable=False)  # 1-5 star rating
    price_per_night = Column(Float, nullable=False)
    room_count = Column(Integer, nullable=False)
    images = Column(JSON, nullable=True)  # Array of image URLs
    amenities = Column(JSON, nullable=True)  # Array of amenities
    description = Column(Text, nullable=True)
    features = Column(JSON, nullable=True)  # WiFi, Pool, Spa, etc.
    room_types = Column(JSON, nullable=True)  # Array of room types with details
    is_available = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    
    # Location relationships
    state_id = Column(Integer, ForeignKey("states.id"), nullable=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
    
    # Relationships
    state = relationship("State", backref="hotels")
    city = relationship("City", backref="hotels")
    hotel_images = relationship("HotelImage", back_populates="hotel", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_hotel_state', 'state_id'),
        Index('idx_hotel_city', 'city_id'),
        {"extend_existing": True}
    )