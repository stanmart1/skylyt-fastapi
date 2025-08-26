from sqlalchemy import Column, String, Integer, Float, Text
from .base import BaseModel


class State(BaseModel):
    __tablename__ = "states"
    
    name = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False, default="USA")
    state_code = Column(String(10), nullable=False, unique=True)
    slug = Column(String(120), nullable=False, unique=True)
    featured_image_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    popularity_score = Column(Float, default=0.0)
    hotel_count = Column(Integer, default=0)
    is_featured = Column(Integer, default=0)