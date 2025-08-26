from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.rbac import Role, Permission
from app.models.user import User
from typing import List, Dict, Any

router = APIRouter(prefix="/admin/roles", tags=["roles"])


@router.get("/{role_name}/permissions")
def get_role_permissions(
    role_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all permissions for a role with assignment status"""
    if not current_user.has_role("admin") and not current_user.has_role("superadmin"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Get all permissions
    all_permissions = db.query(Permission).all()
    role_permission_names = [p.name for p in role.permissions]
    
    permissions = []
    for permission in all_permissions:
        permissions.append({
            "name": permission.name,
            "resource": permission.resource,
            "action": permission.action,
            "description": permission.description,
            "assigned": permission.name in role_permission_names
        })
    
    return {"permissions": permissions}


@router.put("/{role_name}/permissions")
def update_role_permissions(
    role_name: str,
    permission_data: Dict[str, List[str]],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update permissions for a role"""
    if not current_user.has_role("admin") and not current_user.has_role("superadmin"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    assigned_permissions = permission_data.get("permissions", [])
    
    # Clear existing permissions
    role.permissions.clear()
    db.flush()  # Ensure the clear operation is flushed
    
    # Add new permissions
    for permission_name in assigned_permissions:
        permission = db.query(Permission).filter(Permission.name == permission_name).first()
        if permission:
            role.permissions.append(permission)
    
    db.commit()
    db.refresh(role)  # Refresh to get updated relationships
    
    # Get count of affected users
    user_count = len(role.users)
    
    return {
        "message": f"Permissions updated for role {role_name}",
        "affected_users": user_count,
        "permissions_count": len(role.permissions)
    }


@router.get("/")
def get_all_roles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all roles"""
    if not current_user.has_role("admin") and not current_user.has_role("superadmin"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    roles = db.query(Role).all()
    return {
        "roles": [
            {
                "name": role.name,
                "description": role.description,
                "permission_count": len(role.permissions),
                "user_count": len(role.users)
            }
            for role in roles
        ]
    }


@router.post("/")
def create_role(
    role_data: Dict[str, str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new role"""
    if not current_user.has_role("superadmin"):
        raise HTTPException(status_code=403, detail="Only superadmin can create roles")
    
    name = role_data.get("name")
    description = role_data.get("description", "")
    
    if not name:
        raise HTTPException(status_code=400, detail="Role name is required")
    
    existing_role = db.query(Role).filter(Role.name == name).first()
    if existing_role:
        raise HTTPException(status_code=400, detail="Role already exists")
    
    role = Role(name=name, description=description)
    db.add(role)
    db.commit()
    db.refresh(role)
    
    return {"message": f"Role {name} created successfully", "role": {"name": role.name, "description": role.description}}


@router.delete("/{role_name}")
def delete_role(
    role_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a role"""
    if not current_user.has_role("superadmin"):
        raise HTTPException(status_code=403, detail="Only superadmin can delete roles")
    
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Check if role has users
    if role.users:
        raise HTTPException(status_code=400, detail="Cannot delete role with assigned users")
    
    db.delete(role)
    db.commit()
    
    return {"message": f"Role {role_name} deleted successfully"}