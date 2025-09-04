from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from typing import List

router = APIRouter(prefix="/admin", tags=["admin-notifications"])

@router.get("/notification-templates")
def get_notification_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all notification templates"""
    if not current_user.has_role("admin") and not current_user.has_role("superadmin"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return []

@router.post("/notification-templates")
def create_notification_template(
    template_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create notification template"""
    if not current_user.has_role("admin") and not current_user.has_role("superadmin"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return {"message": "Template created successfully"}

@router.put("/notification-templates/{template_id}")
def update_notification_template(
    template_id: int,
    template_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update notification template"""
    if not current_user.has_role("admin") and not current_user.has_role("superadmin"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return {"message": "Template updated successfully"}

@router.get("/notification-settings")
def get_notification_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification settings"""
    if not current_user.has_role("admin") and not current_user.has_role("superadmin"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Return default settings for now - implement proper settings model later
    return {
        "email_enabled": True,
        "sms_enabled": False,
        "push_enabled": True
    }

@router.put("/notification-settings")
def update_notification_settings(
    settings_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update notification settings"""
    if not current_user.has_role("admin") and not current_user.has_role("superadmin"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return {"message": "Settings updated successfully"}

@router.post("/send-notification")
def send_notification(
    notification_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send notification to users"""
    if not current_user.has_role("admin") and not current_user.has_role("superadmin"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return {"message": "Notification sent successfully"}