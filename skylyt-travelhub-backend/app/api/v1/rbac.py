from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.rbac_dependencies import get_superadmin_user, get_admin_user
from app.services.rbac_service import RBACService
from app.models.rbac import Role, Permission
from app.models.user import User
from app.schemas.rbac import (
    RoleCreate, RoleResponse, RoleUpdate,
    PermissionCreate, PermissionResponse,
    UserRoleAssignment, RolePermissionAssignment
)

router = APIRouter(prefix="/rbac", tags=["rbac"])


# Role Management (Superadmin only)
@router.post("/roles", response_model=RoleResponse)
def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_superadmin_user)
):
    """Create new role (Superadmin only)"""
    try:
        role = RBACService.create_role(db, role_data.name, role_data.description)
        
        # Assign permissions to role
        for permission_name in role_data.permission_names:
            RBACService.assign_permission_to_role(db, role.name, permission_name)
        
        db.refresh(role)
        return role
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/roles", response_model=List[RoleResponse])
def list_roles(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all roles (Admin+)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    roles = db.query(Role).all()
    return roles


@router.get("/roles/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Get role details (Admin+)"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_superadmin_user)
):
    """Update role (Superadmin only)"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Update role fields
    if role_update.description is not None:
        role.description = role_update.description
    if role_update.is_active is not None:
        role.is_active = role_update.is_active
    
    # Update permissions
    if role_update.permission_names is not None:
        # Clear existing permissions
        role.permissions.clear()
        
        # Add new permissions
        for permission_name in role_update.permission_names:
            permission = db.query(Permission).filter(Permission.name == permission_name).first()
            if permission:
                role.permissions.append(permission)
    
    db.commit()
    db.refresh(role)
    return role


@router.delete("/roles/{role_id}")
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_superadmin_user)
):
    """Delete role (Superadmin only)"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Prevent deletion of system roles
    if role.name in ["superadmin", "admin", "accountant", "customer"]:
        raise HTTPException(status_code=400, detail="Cannot delete system roles")
    
    db.delete(role)
    db.commit()
    return {"message": "Role deleted successfully"}


# Permission Management (Superadmin only)
@router.post("/permissions", response_model=PermissionResponse)
def create_permission(
    permission_data: PermissionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_superadmin_user)
):
    """Create new permission (Superadmin only)"""
    try:
        permission = RBACService.create_permission(
            db, 
            permission_data.name,
            permission_data.resource,
            permission_data.action,
            permission_data.description
        )
        return permission
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/permissions", response_model=List[PermissionResponse])
def list_permissions(
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """List all permissions (Admin+)"""
    permissions = db.query(Permission).all()
    return permissions


# User Role Assignment
@router.post("/users/assign-roles")
def assign_roles_to_user(
    assignment: UserRoleAssignment,
    db: Session = Depends(get_db),
    current_user = Depends(get_superadmin_user)
):
    """Assign roles to user (Superadmin only)"""
    user = db.query(User).filter(User.id == assignment.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Clear existing roles
    user.roles.clear()
    
    # Assign new roles
    for role_name in assignment.role_names:
        success = RBACService.assign_role_to_user(db, assignment.user_id, role_name)
        if not success:
            raise HTTPException(status_code=400, detail=f"Failed to assign role: {role_name}")
    
    return {"message": "Roles assigned successfully"}


@router.get("/users")
def get_all_users(
    search: str = None,
    role: str = None,
    status: str = None,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all users with filtering and pagination"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = db.query(User)
    
    # Apply filters
    if search:
        query = query.filter(
            (User.first_name.ilike(f"%{search}%")) |
            (User.last_name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )
    
    if role:
        query = query.join(User.roles).filter(Role.name == role)
    
    if status == "active":
        query = query.filter(User.is_active == True)
    elif status == "inactive":
        query = query.filter(User.is_active == False)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    users = query.offset((page - 1) * per_page).limit(per_page).all()
    
    # Filter out superadmin users if current user is not superadmin
    if not current_user.is_superadmin():
        users = [user for user in users if not any(role.name == 'superadmin' for role in user.roles)]
        total = len([u for u in query.all() if not any(role.name == 'superadmin' for role in u.roles)])
    
    return {
        "users": [{
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": f"{user.first_name} {user.last_name}",

            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat(),
            "roles": [{
                "id": role.id,
                "name": role.name,
                "description": role.description
            } for role in user.roles]
        } for user in users],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }

@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    user_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update user details (Admin+)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent non-superadmin from updating superadmin users
    if not current_user.is_superadmin() and any(role.name == 'superadmin' for role in user.roles):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update user fields
    if 'first_name' in user_data:
        user.first_name = user_data['first_name']
    if 'last_name' in user_data:
        user.last_name = user_data['last_name']
    if 'email' in user_data:
        # Check if email is already taken by another user
        existing_user = db.query(User).filter(User.email == user_data['email'], User.id != user_id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")
        user.email = user_data['email']

    if 'is_active' in user_data:
        user.is_active = user_data['is_active']
    if 'is_verified' in user_data:
        user.is_verified = user_data['is_verified']
    
    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": f"{user.first_name} {user.last_name}",
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat(),
        "roles": [{
            "id": role.id,
            "name": role.name,
            "description": role.description
        } for role in user.roles]
    }

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete user (Admin+)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent deletion of superadmin users
    if any(role.name == 'superadmin' for role in user.roles):
        raise HTTPException(status_code=400, detail="Cannot delete superadmin users")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@router.post("/users/{user_id}/roles")
def assign_role_to_user(
    user_id: int,
    role_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Assign role to user (Admin+)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    role_id = role_data.get("role_id")
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent non-superadmin from managing superadmin users or assigning superadmin role
    if not current_user.is_superadmin():
        if any(r.name == 'superadmin' for r in user.roles) or role.name == 'superadmin':
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Clear existing roles and assign new one
    user.roles.clear()
    user.roles.append(role)
    db.commit()
    
    return {"message": "Role assigned successfully"}

@router.put("/users/{user_id}/password")
def change_user_password(
    user_id: int,
    password_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Change user password (Admin+)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_password = password_data.get("password")
    if not new_password:
        raise HTTPException(status_code=400, detail="Password is required")
    
    from app.core.security import get_password_hash
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}

@router.put("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    status_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update user active status (Admin+)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if 'is_active' in status_data:
        user.is_active = status_data['is_active']
    if 'is_verified' in status_data:
        user.is_verified = status_data['is_verified']
    
    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "message": "User status updated successfully"
    }

@router.delete("/users/{user_id}/roles/{role_id}")
def remove_role_from_user(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove specific role from user (Admin+)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    if role in user.roles:
        user.roles.remove(role)
        db.commit()
        return {"message": "Role removed successfully"}
    else:
        raise HTTPException(status_code=400, detail="User does not have this role")

@router.post("/users/bulk-update")
def bulk_update_users(
    bulk_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Bulk update multiple users (Admin+)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user_ids = bulk_data.get("user_ids", [])
    updates = bulk_data.get("updates", {})
    
    if not user_ids:
        raise HTTPException(status_code=400, detail="No user IDs provided")
    
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    
    for user in users:
        if 'is_active' in updates:
            user.is_active = updates['is_active']
        if 'is_verified' in updates:
            user.is_verified = updates['is_verified']
    
    db.commit()
    
    return {"message": f"Updated {len(users)} users successfully"}

@router.post("/users/bulk-assign-role")
def bulk_assign_role(
    bulk_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Bulk assign role to multiple users (Admin+)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user_ids = bulk_data.get("user_ids", [])
    role_id = bulk_data.get("role_id")
    
    if not user_ids or not role_id:
        raise HTTPException(status_code=400, detail="User IDs and role ID are required")
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    
    for user in users:
        user.roles.clear()
        user.roles.append(role)
    
    db.commit()
    
    return {"message": f"Assigned role to {len(users)} users successfully"}

@router.get("/users/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get single user details"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent non-superadmin from accessing superadmin users
    if not current_user.is_superadmin() and any(role.name == 'superadmin' for role in user.roles):
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": f"{user.first_name} {user.last_name}",
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat(),
        "roles": [{
            "id": role.id,
            "name": role.name,
            "description": role.description
        } for role in user.roles]
    }

@router.post("/users")
def create_user(
    user_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new user"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data["email"]).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    from app.core.security import get_password_hash
    
    new_user = User(
        email=user_data["email"],
        hashed_password=get_password_hash(user_data["password"]),
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],

        is_active=user_data.get("is_active", True),
        is_verified=user_data.get("is_verified", False)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "email": new_user.email,
        "first_name": new_user.first_name,
        "last_name": new_user.last_name,
        "message": "User created successfully"
    }

@router.get("/users/{user_id}/roles")
def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get user roles"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user_id,
        "roles": [{"id": role.id, "name": role.name, "description": role.description} for role in user.roles]
    }


@router.post("/initialize")
def initialize_rbac(
    db: Session = Depends(get_db),
    current_user = Depends(get_superadmin_user)
):
    """Initialize default roles and permissions (Superadmin only)"""
    try:
        RBACService.initialize_default_roles_and_permissions(db)
        return {"message": "RBAC initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))