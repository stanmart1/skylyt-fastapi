from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.about_settings import AboutSettings
from app.core.auth import get_current_user, require_admin
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

router = APIRouter()

class AboutSettingsUpdate(BaseModel):
    page_title: Optional[str] = None
    page_description: Optional[str] = None
    company_story: Optional[str] = None
    mission_statement: Optional[str] = None
    vision_statement: Optional[str] = None
    core_values: Optional[List[str]] = None
    team_description: Optional[str] = None
    achievements: Optional[List[Dict[str, Any]]] = None

@router.get("/about-settings")
async def get_about_settings(db: Session = Depends(get_db)):
    """Get about page settings (public endpoint)"""
    settings = db.query(AboutSettings).first()
    if not settings:
        # Create default settings if none exist
        settings = AboutSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return {
        "page_title": settings.page_title,
        "page_description": settings.page_description,
        "company_story": settings.company_story,
        "mission_statement": settings.mission_statement,
        "vision_statement": settings.vision_statement,
        "core_values": settings.core_values or [],
        "team_description": settings.team_description,
        "achievements": settings.achievements or []
    }

@router.get("/admin/about-settings")
async def get_admin_about_settings(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Get about settings for admin management"""
    settings = db.query(AboutSettings).first()
    if not settings:
        settings = AboutSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return {
        "page_title": settings.page_title,
        "page_description": settings.page_description,
        "company_story": settings.company_story,
        "mission_statement": settings.mission_statement,
        "vision_statement": settings.vision_statement,
        "core_values": settings.core_values or [],
        "team_description": settings.team_description,
        "achievements": settings.achievements or []
    }

@router.put("/admin/about-settings")
async def update_about_settings(
    settings_update: AboutSettingsUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Update about page settings"""
    settings = db.query(AboutSettings).first()
    if not settings:
        settings = AboutSettings()
        db.add(settings)
    
    update_data = settings_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    
    return {"message": "About settings updated successfully"}