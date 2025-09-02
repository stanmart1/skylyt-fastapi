from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.contact_settings import ContactSettings
from app.core.auth import get_current_user, require_admin
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ContactSettingsUpdate(BaseModel):
    page_title: Optional[str] = None
    page_description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_address: Optional[str] = None
    office_hours: Optional[str] = None

class ContactMessage(BaseModel):
    name: str
    email: str
    subject: str
    message: str

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
    message: ContactMessage,
    db: Session = Depends(get_db)
):
    """Submit contact form message"""
    # Here you would typically save to database and/or send email
    # For now, we'll just return success
    return {"message": "Message submitted successfully"}