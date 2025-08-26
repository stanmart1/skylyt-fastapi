from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class HotelImage(BaseModel):
    __tablename__ = "hotel_images"
    
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    is_cover = Column(Boolean, default=False, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    
    # Relationships
    hotel = relationship("Hotel", back_populates="hotel_images")