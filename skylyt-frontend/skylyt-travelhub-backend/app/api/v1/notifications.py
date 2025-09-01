from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import requests
import os
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])

class PushNotificationRequest(BaseModel):
    title: str
    message: str
    userIds: Optional[List[str]] = None
    segments: Optional[List[str]] = None
    url: Optional[str] = None


@router.get("", response_model=List[NotificationResponse])
def get_user_notifications(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notifications"""
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).all()
    return notifications


@router.post("", response_model=NotificationResponse)
def create_notification(
    notification_data: NotificationCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new notification"""
    notification = Notification(
        user_id=current_user.id,
        **notification_data.dict()
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


@router.put("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete notification"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db.delete(notification)
    db.commit()
    return {"message": "Notification deleted"}


@router.put("/mark-all-read")
def mark_all_notifications_read(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read"}


@router.post("/push")
def send_push_notification(
    notification: PushNotificationRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send push notification via OneSignal"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    api_key = os.getenv("ONE_SIGNAL_API_KEY")
    app_id = os.getenv("ONESIGNAL_APP_ID")
    
    if not api_key:
        raise HTTPException(status_code=500, detail="OneSignal API key not configured")
    
    payload = {
        "app_id": app_id or "default-app-id",
        "headings": {"en": notification.title},
        "contents": {"en": notification.message},
    }
    
    if notification.userIds:
        payload["include_player_ids"] = notification.userIds
    elif notification.segments:
        payload["included_segments"] = notification.segments
    else:
        payload["included_segments"] = ["All"]
    
    if notification.url:
        payload["url"] = notification.url
    
    try:
        response = requests.post(
            "https://onesignal.com/api/v1/notifications",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Basic {api_key}"
            },
            json=payload
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to send notification")
        
        return response.json()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))