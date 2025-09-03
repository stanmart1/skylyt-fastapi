from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.contact_settings import ContactSettings
from app.models.contact_message import ContactMessage
from app.core.dependencies import get_current_user, get_admin_user as require_admin
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import logging

router = APIRouter()

class ContactSettingsUpdate(BaseModel):
    page_title: Optional[str] = None
    page_description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_address: Optional[str] = None
    office_hours: Optional[str] = None

class ContactMessageRequest(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str

class ContactMessageResponse(BaseModel):
    id: int
    name: str
    email: str
    subject: str
    message: str
    is_read: bool
    created_at: str
    
    class Config:
        from_attributes = True

@router.get("/contact-settings")
async def get_contact_settings(db: Session = Depends(get_db)):
    """Get contact page settings (public endpoint)"""
    settings = db.query(ContactSettings).first()
    if not settings:
        # Create default settings if none exist
        settings = ContactSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return {
        "page_title": settings.page_title,
        "page_description": settings.page_description,
        "contact_email": settings.contact_email,
        "contact_phone": settings.contact_phone,
        "contact_address": settings.contact_address,
        "office_hours": settings.office_hours
    }

@router.get("/admin/contact-settings")
async def get_admin_contact_settings(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Get contact settings for admin management"""
    settings = db.query(ContactSettings).first()
    if not settings:
        settings = ContactSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return {
        "page_title": settings.page_title,
        "page_description": settings.page_description,
        "contact_email": settings.contact_email,
        "contact_phone": settings.contact_phone,
        "contact_address": settings.contact_address,
        "office_hours": settings.office_hours
    }

@router.put("/admin/contact-settings")
async def update_contact_settings(
    settings_update: ContactSettingsUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Update contact page settings"""
    settings = db.query(ContactSettings).first()
    if not settings:
        settings = ContactSettings()
        db.add(settings)
    
    update_data = settings_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    
    return {"message": "Contact settings updated successfully"}

@router.post("/contact/submit")
async def submit_contact_message(
    message_data: ContactMessageRequest,
    db: Session = Depends(get_db)
):
    """Submit contact form message"""
    try:
        # Save message to database
        contact_message = ContactMessage(
            name=message_data.name,
            email=message_data.email,
            subject=message_data.subject,
            message=message_data.message
        )
        
        db.add(contact_message)
        db.commit()
        db.refresh(contact_message)
        
        # Send email notification (optional)
        try:
            from app.services.email_service import send_contact_notification
            await send_contact_notification(message_data.dict())
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to send email notification: {e}")
        
        return {"message": "Message submitted successfully", "id": contact_message.id}
    
    except Exception as e:
        db.rollback()
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to submit contact message: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit message")

@router.get("/admin/contact-messages", response_model=List[ContactMessageResponse])
async def get_contact_messages(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Get all contact messages for admin"""
    messages = db.query(ContactMessage).order_by(ContactMessage.created_at.desc()).all()
    return messages

@router.put("/admin/contact-messages/{message_id}/read")
async def mark_message_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Mark contact message as read"""
    message = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message.is_read = True
    db.commit()
    
    return {"message": "Message marked as read"}