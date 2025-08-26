from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel


class Favorite(BaseModel):
    __tablename__ = "favorites"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_type = Column(String(50), nullable=False)  # 'hotel', 'car'
    item_id = Column(String(255), nullable=False)  # External ID from supplier
    item_data = Column(JSON, nullable=False)  # Cached item details
    
    # Relationships
    user = relationship("User", back_populates="favorites")