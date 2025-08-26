from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.hotel import Hotel

router = APIRouter(prefix="/admin/hotels", tags=["admin-hotels"])


@router.get("")
def get_all_hotels(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all hotels for admin management"""
    hotels = db.query(Hotel).all()
    return [{
        "id": hotel.id,
        "name": hotel.name,
        "location": hotel.location,
        "rating": float(hotel.star_rating),
        "price": float(hotel.price_per_night),
        "room_count": hotel.room_count,
        "image_url": hotel.images[0] if hotel.images and isinstance(hotel.images, list) and len(hotel.images) > 0 else None,
        "is_featured": getattr(hotel, 'is_featured', False),
        "amenities": hotel.amenities or [],
        "features": hotel.features or [],
        "description": hotel.description or "",
        "is_available": getattr(hotel, 'is_available', True),
        "is_featured": getattr(hotel, 'is_featured', False)
    } for hotel in hotels]


@router.post("")
def create_hotel(
    hotel_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new hotel"""
    hotel = Hotel(
        id=str(uuid.uuid4()),
        name=hotel_data.get("name", "New Hotel"),
        location=hotel_data.get("location", "Unknown Location"),
        star_rating=hotel_data.get("rating", hotel_data.get("star_rating", 4)),
        price_per_night=hotel_data.get("price", hotel_data.get("price_per_night", 100.0)),
        room_count=hotel_data.get("room_count", 10),
        images=[hotel_data.get("image_url")] if hotel_data.get("image_url") else [],
        amenities=hotel_data.get("amenities", []),
        features=hotel_data.get("features", []),
        description=hotel_data.get("description", ""),
        is_available=hotel_data.get("is_available", True),
        is_featured=hotel_data.get("is_featured", False)
    )
    db.add(hotel)
    db.commit()
    db.refresh(hotel)
    return {"message": "Hotel created successfully", "id": hotel.id}


@router.put("/{hotel_id}")
def update_hotel(
    hotel_id: str,
    hotel_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update hotel details"""
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    # Map frontend fields to backend fields
    field_mapping = {
        'rating': 'star_rating',
        'price': 'price_per_night'
    }
    
    for field, value in hotel_data.items():
        if field == 'image_url':
            hotel.images = [value] if value else []
        else:
            backend_field = field_mapping.get(field, field)
            if hasattr(hotel, backend_field):
                setattr(hotel, backend_field, value)
    
    db.commit()
    db.refresh(hotel)
    return {"message": "Hotel updated successfully"}


@router.delete("/{hotel_id}")
def delete_hotel(
    hotel_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete hotel"""
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    db.delete(hotel)
    db.commit()
    return {"message": "Hotel deleted successfully"}


@router.post("/{hotel_id}/feature")
def toggle_feature_hotel(
    hotel_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Toggle hotel as featured"""
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    # Toggle featured status
    hotel.is_featured = not hotel.is_featured
    db.commit()
    db.refresh(hotel)
    return {"message": f"Hotel {'featured' if hotel.is_featured else 'unfeatured'} successfully"}