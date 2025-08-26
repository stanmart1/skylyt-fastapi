from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.booking import BookingResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_current_user_profile(current_user = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "full_name": f"{current_user.first_name} {current_user.last_name}",


        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at.isoformat(),
        "roles": [{
            "id": role.id,
            "name": role.name,
            "permissions": [{
                "id": perm.id,
                "name": perm.name,
                "resource": perm.resource,
                "action": perm.action
            } for perm in role.permissions]
        } for role in current_user.roles]
    }


@router.put("/me")
def update_user_profile(
    user_update: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    updated_user = UserService.update_user_profile(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": updated_user.id,
        "email": updated_user.email,
        "first_name": updated_user.first_name,
        "last_name": updated_user.last_name,
        "full_name": f"{updated_user.first_name} {updated_user.last_name}",

        "is_active": updated_user.is_active,
        "is_verified": updated_user.is_verified,
        "created_at": updated_user.created_at.isoformat(),
        "roles": [{
            "id": role.id,
            "name": role.name,
            "permissions": [{
                "id": perm.id,
                "name": perm.name,
                "resource": perm.resource,
                "action": perm.action
            } for perm in role.permissions]
        } for role in updated_user.roles]
    }


@router.delete("/me")
def delete_user_account(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account"""
    success = UserService.delete_user_account(db, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Account deleted successfully"}


@router.get("/me/bookings", response_model=List[BookingResponse])
def get_user_bookings(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user bookings"""
    bookings = UserService.get_user_bookings(db, current_user.id)
    return bookings


@router.get("/me/favorites")
def get_user_favorites(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user favorites"""
    return {"favorites": []}


@router.post("/me/favorites")
def add_to_favorites(
    item_type: str,
    item_id: str,
    item_data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add item to favorites"""
    success = UserService.manage_favorites(
        db, current_user.id, item_type, item_id, item_data, "add"
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add to favorites")
    return {"message": "Added to favorites"}


@router.delete("/me/favorites/{item_id}")
def remove_from_favorites(
    item_id: str,
    item_type: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from favorites"""
    success = UserService.manage_favorites(
        db, current_user.id, item_type, item_id, {}, "remove"
    )
    if not success:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"message": "Removed from favorites"}


@router.post("/me/change-password")
def change_password(
    password_data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    from app.core.security import verify_password, get_password_hash
    
    current_password = password_data.get("current_password")
    new_password = password_data.get("new_password")
    
    if not current_password or not new_password:
        raise HTTPException(status_code=400, detail="Current and new passwords are required")
    
    # Verify current password
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Update password
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.get("/me/notifications")
def get_user_notifications(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notification preferences"""
    # Check if user has preferences stored
    if hasattr(current_user, 'email_notifications') and hasattr(current_user, 'sms_notifications'):
        return {
            "email": current_user.email_notifications,
            "sms": current_user.sms_notifications
        }
    
    # Return defaults if not set
    return {
        "email": True,
        "sms": False
    }


@router.put("/me/notifications")
def update_user_notifications(
    notification_data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user notification preferences"""
    email_enabled = notification_data.get("email", True)
    sms_enabled = notification_data.get("sms", False)
    
    # Update user preferences
    current_user.email_notifications = email_enabled
    current_user.sms_notifications = sms_enabled
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "email": email_enabled,
        "sms": sms_enabled,
        "message": "Notification preferences updated successfully"
    }