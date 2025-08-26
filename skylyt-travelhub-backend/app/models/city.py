from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class City(BaseModel):
    __tablename__ = "cities"
    
    name = Column(String(100), nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)
    slug = Column(String(120), nullable=False)
    featured_image_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    popularity_ranking = Column(Integer, default=0)
    hotel_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    is_featured = Column(Integer, default=0)
    
    # Relationships
    state = relationship("State", backref="cities")
    
    __table_args__ = (
        {"extend_existing": True}
    )