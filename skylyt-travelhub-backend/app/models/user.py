from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True, nullable=False)
    sms_notifications = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    bookings = relationship("Booking", back_populates="user")
    search_history = relationship("SearchHistory", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    
    def has_permission(self, resource: str, action: str) -> bool:
        """Check if user has specific permission"""
        for role in self.roles:
            if not role.is_active:
                continue
            for permission in role.permissions:
                if permission.resource == resource and permission.action == action:
                    return True
        return False
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has specific role"""
        return any(role.name == role_name and role.is_active for role in self.roles)
    
    def is_superadmin(self) -> bool:
        """Check if user is superadmin"""
        return self.has_role("superadmin")
    
    def is_admin(self) -> bool:
        """Check if user is admin or superadmin"""
        return self.has_role("admin") or self.has_role("superadmin")