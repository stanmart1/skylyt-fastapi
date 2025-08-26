from fastapi import Depends, HTTPException, status
from functools import wraps
from app.core.dependencies import get_current_user


def require_permission(resource: str, action: str):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                # Try to get from dependencies
                for key, value in kwargs.items():
                    if hasattr(value, 'has_permission'):
                        current_user = value
                        break
            
            if not current_user or not current_user.has_permission(resource, action):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {resource}.{action}"
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role_name: str):
    """Decorator to require specific role"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                for key, value in kwargs.items():
                    if hasattr(value, 'has_role'):
                        current_user = value
                        break
            
            if not current_user or not current_user.has_role(role_name):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role required: {role_name}"
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def get_superadmin_user(current_user = Depends(get_current_user)):
    """Dependency to ensure user is superadmin - server-side validation only"""
    # Server-side role validation - never trust client data
    if not current_user.is_superadmin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin access required"
        )
    return current_user


def get_admin_user(current_user = Depends(get_current_user)):
    """Dependency to ensure user is admin or superadmin - server-side validation only"""
    # Server-side role validation - never trust client data
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def get_accountant_user(current_user = Depends(get_current_user)):
    """Dependency to ensure user is accountant, admin, or superadmin"""
    if not (current_user.has_role("accountant") or current_user.is_admin()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accountant access required"
        )
    return current_user


def check_permission(resource: str, action: str):
    """Dependency factory for permission checking - server-side validation only"""
    def permission_checker(current_user = Depends(get_current_user)):
        # Server-side permission validation - never trust client data
        if not current_user.has_permission(resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {resource}.{action}"
            )
        return current_user
    return permission_checker