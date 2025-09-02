from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.settings import SystemSettings

router = APIRouter()

@router.get("/features")
async def get_features(db: Session = Depends(get_db)):
    """Get feature toggles - public endpoint"""
    car_setting = db.query(SystemSettings).filter(SystemSettings.key == 'car_rental_enabled').first()
    hotel_setting = db.query(SystemSettings).filter(SystemSettings.key == 'hotel_booking_enabled').first()
    
    return {
        "car_rental_enabled": car_setting.value == 'true' if car_setting else True,
        "hotel_booking_enabled": hotel_setting.value == 'true' if hotel_setting else True
    }