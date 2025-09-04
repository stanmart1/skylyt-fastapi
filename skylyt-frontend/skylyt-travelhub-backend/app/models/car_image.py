from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import BaseModel


class CarImage(BaseModel):
    __tablename__ = "car_images"
    
    car_id = Column(String, ForeignKey("cars.id"), nullable=False)
    image_url = Column(Text, nullable=False)
    is_cover = Column(Boolean, default=False, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    
    # Relationships
    car = relationship("Car", back_populates="car_images")