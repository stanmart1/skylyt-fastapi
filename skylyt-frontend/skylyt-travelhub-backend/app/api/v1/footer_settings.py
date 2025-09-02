from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.models.footer_settings import FooterSettings

router = APIRouter()


class FooterSettingsUpdate(BaseModel):
    company_name: Optional[str] = None
    company_description: Optional[str] = None
    twitter_url: Optional[str] = None
    instagram_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    contact_address: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None


@router.get("/admin/footer-settings")
async def get_footer_settings(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get footer settings (admin only)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    settings = db.query(FooterSettings).first()
    if not settings:
        # Create default settings if none exist
        settings = FooterSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return {
        "id": settings.id,
        "company_name": settings.company_name,
        "company_description": settings.company_description,
        "twitter_url": settings.twitter_url,
        "instagram_url": settings.instagram_url,
        "linkedin_url": settings.linkedin_url,
        "contact_address": settings.contact_address,
        "contact_phone": settings.contact_phone,
        "contact_email": settings.contact_email
    }


@router.put("/admin/footer-settings")
async def update_footer_settings(
    settings_data: FooterSettingsUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update footer settings (admin only)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    settings = db.query(FooterSettings).first()
    if not settings:
        settings = FooterSettings()
        db.add(settings)
    
    # Update fields
    update_data = settings_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(settings, field):
            setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    
    return {"message": "Footer settings updated successfully"}


@router.get("/footer-settings")
async def get_public_footer_settings(db: Session = Depends(get_db)):
    """Get footer settings for public use"""
    settings = db.query(FooterSettings).first()
    if not settings:
        # Return default settings
        return {
            "company_name": "Skylyt Luxury",
            "company_description": "Your perfect journey awaits. Rent premium cars and book luxurious hotels with confidence.",
            "twitter_url": None,
            "instagram_url": None,
            "linkedin_url": None,
            "contact_address": "123 Business Ave, Suite 100\nNew York, NY 10001",
            "contact_phone": "+1 (555) 123-4567",
            "contact_email": "support@skylytluxury.com"
        }
    
    return {
        "company_name": settings.company_name,
        "company_description": settings.company_description,
        "twitter_url": settings.twitter_url,
        "instagram_url": settings.instagram_url,
        "linkedin_url": settings.linkedin_url,
        "contact_address": settings.contact_address,
        "contact_phone": settings.contact_phone,
        "contact_email": settings.contact_email
    }