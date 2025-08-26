from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from .base import BaseModel


class Notification(BaseModel):
    __tablename__ = "notifications"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="info", nullable=False)  # info, success, warning, error
    is_read = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notifications")