from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel


class SearchHistory(BaseModel):
    __tablename__ = "search_history"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    search_type = Column(String(50), nullable=False)  # 'hotel', 'car', 'bundle'
    search_params = Column(JSON, nullable=False)
    results_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="search_history")