from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.settings import SystemSettings
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
    
    car_setting = db.query(SystemSettings).filter(SystemSettings.key == 'car_rental_enabled').first()
    hotel_setting = db.query(SystemSettings).filter(SystemSettings.key == 'hotel_booking_enabled').first()
    
    return {
        "car_rental_enabled": car_setting.value == 'true' if car_setting else True,
        "hotel_booking_enabled": hotel_setting.value == 'true' if hotel_setting else True
    }

@router.put("")
async def update_module_settings(
    settings: ModuleSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.has_permission('dashboard.view_modules'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    if settings.car_rental_enabled is not None:
        car_setting = db.query(SystemSettings).filter(SystemSettings.key == 'car_rental_enabled').first()
        if car_setting:
            car_setting.value = str(settings.car_rental_enabled).lower()
        else:
            car_setting = SystemSettings(key='car_rental_enabled', value=str(settings.car_rental_enabled).lower())
            db.add(car_setting)
    
    if settings.hotel_booking_enabled is not None:
        hotel_setting = db.query(SystemSettings).filter(SystemSettings.key == 'hotel_booking_enabled').first()
        if hotel_setting:
            hotel_setting.value = str(settings.hotel_booking_enabled).lower()
        else:
            hotel_setting = SystemSettings(key='hotel_booking_enabled', value=str(settings.hotel_booking_enabled).lower())
            db.add(hotel_setting)
    
    db.commit()
    return {"message": "Module settings updated successfully"}