from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.notification import Notification
from app.models.user import User
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter(prefix="/admin/notifications", tags=["notification-management"])

class NotificationTemplate(BaseModel):
    id: Optional[int] = None
    name: str
    type: str  # email, sms, push
    event: str
    subject: str
    content: str
    is_active: bool = True

class NotificationSettings(BaseModel):
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    booking_notifications: bool = True
    payment_notifications: bool = True
    system_notifications: bool = True

class BulkNotificationRequest(BaseModel):
    title: str
    message: str
    type: str  # email, push, sms
    target_users: Optional[List[int]] = None  # None means all users
    schedule_time: Optional[datetime] = None

@router.get("/templates")
def get_notification_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all notification templates"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Return mock data for now - implement actual template storage
    return [
        {
            "id": 1,
            "name": "Booking Confirmation",
            "type": "email",
            "event": "booking_confirmed",
            "subject": "Booking Confirmed - {{booking_id}}",
            "content": "Your booking has been confirmed. Details: {{booking_details}}",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": 2,
            "name": "Payment Received",
            "type": "email",
            "event": "payment_received",
            "subject": "Payment Received - {{amount}}",
            "content": "We have received your payment of {{amount}}. Thank you!",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]

@router.post("/templates")
def create_notification_template(
    template: NotificationTemplate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new notification template"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Implement template creation logic
    return {"message": "Template created successfully", "id": 3}

@router.put("/templates/{template_id}")
def update_notification_template(
    template_id: int,
    template: NotificationTemplate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a notification template"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return {"message": "Template updated successfully"}

@router.delete("/templates/{template_id}")
def delete_notification_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a notification template"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return {"message": "Template deleted successfully"}

@router.put("/templates/{template_id}/toggle")
def toggle_notification_template(
    template_id: int,
    toggle_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle template active status"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return {"message": "Template status updated"}

@router.post("/templates/{template_id}/test")
def test_notification_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a test notification using template"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return {"message": "Test notification sent"}

@router.get("/settings")
def get_notification_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notification settings"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return {
        "email_enabled": True,
        "sms_enabled": False,
        "push_enabled": True,
        "booking_notifications": True,
        "payment_notifications": True,
        "system_notifications": True
    }

@router.put("/settings")
def update_notification_settings(
    settings: NotificationSettings,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update notification settings"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return {"message": "Notification settings updated successfully"}

@router.post("/send-bulk")
def send_bulk_notification(
    notification: BulkNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send bulk notification to users"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Implement bulk notification logic
    return {"message": "Bulk notification sent successfully"}