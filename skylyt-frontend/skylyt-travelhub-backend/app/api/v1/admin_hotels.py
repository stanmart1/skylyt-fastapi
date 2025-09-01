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


@router.get("/room-types")
def get_room_types(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get hotel room types from database"""
    hotels = db.query(Hotel).filter(Hotel.room_types.isnot(None)).all()
    room_types = []
    for hotel in hotels:
        if hotel.room_types:
            for room_type in hotel.room_types:
                room_types.append({
                    "id": f"{hotel.id}_{room_type.get('type', 'standard')}",
                    "hotel_id": hotel.id,
                    "hotel_name": hotel.name,
                    "type": room_type.get('type', 'Standard'),
                    "price": room_type.get('price', hotel.price_per_night),
                    "capacity": room_type.get('capacity', 2),
                    "available_rooms": room_type.get('available_rooms', 1),
                    "amenities": room_type.get('amenities', [])
                })
    return room_types


@router.get("/stats")
def get_hotel_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get hotel management statistics"""
    from sqlalchemy import func, and_
    from datetime import datetime, timedelta
    
    # Get hotel statistics
    total_hotels = db.query(Hotel).count()
    total_rooms = db.query(func.sum(Hotel.room_count)).scalar() or 0
    
    # Initialize other stats
    active_bookings = 0
    current_revenue = 0
    previous_revenue = 0
    
    try:
        from app.models.booking import Booking
        from app.models.payment import Payment
        
        # Get active hotel bookings
        active_bookings = db.query(Booking).filter(
            and_(
                Booking.booking_type == 'hotel',
                Booking.status.in_(['confirmed', 'ongoing'])
            )
        ).count()
        
        # Calculate revenue (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        sixty_days_ago = datetime.now() - timedelta(days=60)
        
        current_revenue = db.query(func.sum(Payment.amount)).join(Booking).filter(
            and_(
                Booking.booking_type == 'hotel',
                Payment.status == 'completed',
                Payment.created_at >= thirty_days_ago
            )
        ).scalar() or 0
        
        previous_revenue = db.query(func.sum(Payment.amount)).join(Booking).filter(
            and_(
                Booking.booking_type == 'hotel',
                Payment.status == 'completed',
                Payment.created_at >= sixty_days_ago,
                Payment.created_at < thirty_days_ago
            )
        ).scalar() or 0
    except Exception as e:
        # If booking/payment models don't exist, continue with 0 values
        pass
    
    # Calculate occupancy rate
    occupancy_rate = 0
    if total_rooms > 0:
        occupancy_rate = round((active_bookings / total_rooms) * 100, 1)
    
    # Calculate revenue change percentage
    revenue_change = 0
    if previous_revenue > 0:
        revenue_change = ((current_revenue - previous_revenue) / previous_revenue) * 100
    
    return {
        "totalHotels": total_hotels,
        "totalRooms": int(total_rooms),
        "activeBookings": active_bookings,
        "totalRevenue": float(current_revenue),
        "revenueChange": round(revenue_change, 1),
        "occupancyRate": occupancy_rate
    }

@router.get("/overview-stats")
def get_hotel_overview_stats(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get comprehensive hotel overview statistics with booking trends"""
    from sqlalchemy import func, and_
    from datetime import datetime, timedelta
    
    # Validate days parameter
    if days not in [7, 30]:
        days = 7
    
    # Hotel status summary
    total_hotels = db.query(Hotel).count()
    total_rooms = db.query(func.sum(Hotel.room_count)).scalar() or 0
    
    # Initialize booking stats
    pending_bookings = 0
    confirmed_bookings = 0
    cancelled_bookings = 0
    occupied_rooms = 0
    
    try:
        from app.models.booking import Booking
        
        # Booking status breakdown
        pending_bookings = db.query(Booking).filter(
            and_(
                Booking.booking_type == 'hotel',
                Booking.status == 'pending'
            )
        ).count()
        
        confirmed_bookings = db.query(Booking).filter(
            and_(
                Booking.booking_type == 'hotel',
                Booking.status.in_(['confirmed', 'ongoing'])
            )
        ).count()
        
        cancelled_bookings = db.query(Booking).filter(
            and_(
                Booking.booking_type == 'hotel',
                Booking.status == 'cancelled'
            )
        ).count()
        
        # Occupied rooms (active bookings)
        occupied_rooms = confirmed_bookings
        
        # Booking trends over selected days
        booking_trends = []
        for i in range(days):
            date = datetime.now().date() - timedelta(days=i)
            daily_bookings = db.query(func.count(Booking.id)).filter(
                and_(
                    Booking.booking_type == 'hotel',
                    func.date(Booking.created_at) == date
                )
            ).scalar() or 0
            
            booking_trends.insert(0, {
                "date": date.strftime("%Y-%m-%d"),
                "bookings": daily_bookings
            })
            
    except Exception as e:
        # If booking model doesn't exist, return default data
        booking_trends = []
        for i in range(days):
            date = datetime.now().date() - timedelta(days=i)
            booking_trends.insert(0, {
                "date": date.strftime("%Y-%m-%d"),
                "bookings": 0
            })
    
    available_rooms = max(0, total_rooms - occupied_rooms)
    
    return {
        "hotel_status": {
            "total_hotels": total_hotels,
            "total_rooms": int(total_rooms),
            "available_rooms": available_rooms,
            "occupied_rooms": occupied_rooms
        },
        "booking_status": {
            "pending": pending_bookings,
            "confirmed": confirmed_bookings,
            "cancelled": cancelled_bookings
        },
        "booking_trends": booking_trends
    }