from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.settings import Settings

router = APIRouter()

@router.get("/features")
async def get_features(db: Session = Depends(get_db)):
    """Get feature toggles - public endpoint"""
    settings_record = db.query(Settings).first()
    if not settings_record:
        return {"car_rental_enabled": True, "hotel_booking_enabled": True}
    
    additional = settings_record.additional_settings or {}
    
    return {
        "car_rental_enabled": additional.get('car_rental_enabled', 'true') == 'true',
        "hotel_booking_enabled": additional.get('hotel_booking_enabled', 'true') == 'true'
    }