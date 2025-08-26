from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class PermissionBase(BaseModel):
    name: str
    resource: str
    action: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class RoleCreate(RoleBase):
    permission_names: Optional[List[str]] = []


class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    permissions: List[PermissionResponse] = []
    
    class Config:
        from_attributes = True


class RoleUpdate(BaseModel):
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permission_names: Optional[List[str]] = None


class UserRoleAssignment(BaseModel):
    user_id: int
    role_names: List[str]


class RolePermissionAssignment(BaseModel):
    role_name: str
    permission_names: List[str]