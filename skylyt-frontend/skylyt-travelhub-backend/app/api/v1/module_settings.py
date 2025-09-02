from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.settings import Settings
from pydantic import BaseModel

router = APIRouter()

class ModuleSettingsUpdate(BaseModel):
    car_rental_enabled: bool = None
    hotel_booking_enabled: bool = None

@router.get("")
async def get_module_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.has_permission('dashboard.view_modules'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    car_setting = db.query(Settings).filter(Settings.additional_settings['car_rental_enabled'].astext == 'true').first()
    hotel_setting = db.query(Settings).filter(Settings.additional_settings['hotel_booking_enabled'].astext == 'true').first()
    
    # Get first settings record or create default
    settings_record = db.query(Settings).first()
    if not settings_record:
        return {"car_rental_enabled": True, "hotel_booking_enabled": True}
    
    additional = settings_record.additional_settings or {}
    
    return {
        "car_rental_enabled": additional.get('car_rental_enabled', 'true') == 'true',
        "hotel_booking_enabled": additional.get('hotel_booking_enabled', 'true') == 'true'
    }

@router.put("")
async def update_module_settings(
    settings: ModuleSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.has_permission('dashboard.view_modules'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Get or create settings record
    settings_record = db.query(Settings).first()
    if not settings_record:
        settings_record = Settings(additional_settings={})
        db.add(settings_record)
    
    additional = settings_record.additional_settings or {}
    
    if settings.car_rental_enabled is not None:
        additional['car_rental_enabled'] = str(settings.car_rental_enabled).lower()
    
    if settings.hotel_booking_enabled is not None:
        additional['hotel_booking_enabled'] = str(settings.hotel_booking_enabled).lower()
    
    settings_record.additional_settings = additional
    
    db.commit()
    return {"message": "Module settings updated successfully"}