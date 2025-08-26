from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


# Association table for many-to-many relationship between roles and permissions
role_permissions = Table(
    'role_permissions',
    BaseModel.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

# Association table for many-to-many relationship between users and roles
user_roles = Table(
    'user_roles',
    BaseModel.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)


class Role(BaseModel):
    __tablename__ = "roles"
    
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = relationship("User", secondary=user_roles, back_populates="roles")


class Permission(BaseModel):
    __tablename__ = "permissions"
    
    name = Column(String(100), unique=True, nullable=False, index=True)
    resource = Column(String(50), nullable=False)  # e.g., 'bookings', 'users', 'payments'
    action = Column(String(50), nullable=False)    # e.g., 'create', 'read', 'update', 'delete'
    description = Column(String(255), nullable=True)
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")