from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.rbac import Permission
from app.models.user import User
from typing import List, Dict, Any

router = APIRouter(prefix="/admin/permissions", tags=["permissions"])


@router.get("/")
def get_all_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all permissions"""
    if not current_user.has_role("admin") and not current_user.has_role("superadmin"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    permissions = db.query(Permission).all()
    return {
        "permissions": [
            {
                "id": permission.id,
                "name": permission.name,
                "resource": permission.resource,
                "action": permission.action,
                "description": permission.description
            }
            for permission in permissions
        ]
    }


@router.get("/{permission_id}")
def get_permission(
    permission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific permission"""
    if not current_user.has_role("admin") and not current_user.has_role("superadmin"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    return {
        "id": permission.id,
        "name": permission.name,
        "resource": permission.resource,
        "action": permission.action,
        "description": permission.description
    }


@router.post("/")
def create_permission(
    permission_data: Dict[str, str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new permission"""
    if not current_user.has_role("superadmin"):
        raise HTTPException(status_code=403, detail="Only superadmin can create permissions")
    
    name = permission_data.get("name")
    resource = permission_data.get("resource")
    action = permission_data.get("action")
    description = permission_data.get("description", "")
    
    if not all([name, resource, action]):
        raise HTTPException(status_code=400, detail="Name, resource, and action are required")
    
    # Check if permission already exists
    existing = db.query(Permission).filter(Permission.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Permission already exists")
    
    permission = Permission(
        name=name,
        resource=resource,
        action=action,
        description=description
    )
    db.add(permission)
    db.commit()
    db.refresh(permission)
    
    return {
        "message": f"Permission {name} created successfully",
        "permission": {
            "id": permission.id,
            "name": permission.name,
            "resource": permission.resource,
            "action": permission.action,
            "description": permission.description
        }
    }


@router.put("/{permission_id}")
def update_permission(
    permission_id: int,
    permission_data: Dict[str, str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a permission"""
    if not current_user.has_role("superadmin"):
        raise HTTPException(status_code=403, detail="Only superadmin can update permissions")
    
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    # Update fields if provided
    if "name" in permission_data:
        permission.name = permission_data["name"]
    if "resource" in permission_data:
        permission.resource = permission_data["resource"]
    if "action" in permission_data:
        permission.action = permission_data["action"]
    if "description" in permission_data:
        permission.description = permission_data["description"]
    
    db.commit()
    db.refresh(permission)
    
    return {
        "message": f"Permission {permission.name} updated successfully",
        "permission": {
            "id": permission.id,
            "name": permission.name,
            "resource": permission.resource,
            "action": permission.action,
            "description": permission.description
        }
    }


@router.delete("/{permission_id}")
def delete_permission(
    permission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a permission"""
    if not current_user.has_role("superadmin"):
        raise HTTPException(status_code=403, detail="Only superadmin can delete permissions")
    
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    # Check if permission is assigned to any roles
    if permission.roles:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete permission that is assigned to roles"
        )
    
    db.delete(permission)
    db.commit()
    
    return {"message": f"Permission {permission.name} deleted successfully"}


@router.get("/by-resource/{resource}")
def get_permissions_by_resource(
    resource: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all permissions for a specific resource"""
    if not current_user.has_role("admin") and not current_user.has_role("superadmin"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    permissions = db.query(Permission).filter(Permission.resource == resource).all()
    return {
        "resource": resource,
        "permissions": [
            {
                "id": permission.id,
                "name": permission.name,
                "action": permission.action,
                "description": permission.description
            }
            for permission in permissions
        ]
    }