from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
import logging

from app.core.dependencies import get_current_user
from app.core.database import get_db

router = APIRouter()

@router.get("/admin/stats")
async def get_admin_stats(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get admin dashboard statistics with caching"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.services.analytics_service import AnalyticsService
    from app.utils.cache_manager import cache_manager
    
    # Try cache first (5 minute cache)
    cache_key = "admin_stats"
    cached_stats = cache_manager.get(cache_key)
    if cached_stats:
        return cached_stats
    
    stats = AnalyticsService.get_admin_stats(db)
    cache_manager.set(cache_key, stats, 300)
    return stats

@router.get("/admin/active-users")
async def get_active_users(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get count of active users online"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.user import User
        # Count all active users as a simple metric
        active_count = db.query(User).filter(User.is_active == True).count()
        return {"active_users": active_count}
    except Exception as e:
        return {"active_users": 0}

@router.get("/admin/recent-activity")
async def get_recent_activity(
    activity_type: str = None,
    current_user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Get recent activity for admin dashboard"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from sqlalchemy import desc
        activities = []
        
        from app.models.user import User
        
        # Recent user registrations only (real data from database)
        if not activity_type or activity_type == "user":
            recent_users = db.query(User).order_by(desc(User.created_at)).limit(10).all()
            for user in recent_users:
                activities.append({
                    "id": f"user_{user.id}",
                    "type": "user",
                    "title": "New user registration",
                    "description": f"{user.first_name} {user.last_name} joined the platform",
                    "timestamp": user.created_at.isoformat(),
                    "status": "active" if user.is_active else "inactive"
                })
        
        # Sort by timestamp (most recent first)
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {"activities": activities[:10]}
    except Exception as e:
        # Return empty activities if there's an error
        return {"activities": []}

@router.get("/admin/car-stats")
async def get_car_stats(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get car management statistics"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.car import Car
        from app.models.booking import Booking
        from app.models.payment import Payment
        from sqlalchemy import func, and_
        
        # Get car statistics
        total_cars = db.query(Car).count()
        available_cars = db.query(Car).filter(Car.status == 'available').count()
        
        # Get active car bookings
        active_bookings = db.query(Booking).filter(
            and_(
                Booking.booking_type == 'car',
                Booking.status.in_(['confirmed', 'ongoing'])
            )
        ).count()
        
        # Calculate revenue (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        sixty_days_ago = datetime.now() - timedelta(days=60)
        
        current_revenue = db.query(func.sum(Payment.amount)).join(Booking).filter(
            and_(
                Booking.booking_type == 'car',
                Payment.status == 'completed',
                Payment.created_at >= thirty_days_ago
            )
        ).scalar() or 0
        
        previous_revenue = db.query(func.sum(Payment.amount)).join(Booking).filter(
            and_(
                Booking.booking_type == 'car',
                Payment.status == 'completed',
                Payment.created_at >= sixty_days_ago,
                Payment.created_at < thirty_days_ago
            )
        ).scalar() or 0
        
        # Calculate revenue change percentage
        revenue_change = 0
        if previous_revenue > 0:
            revenue_change = ((current_revenue - previous_revenue) / previous_revenue) * 100
        
        return {
            "totalCars": total_cars,
            "availableCars": available_cars,
            "activeBookings": active_bookings,
            "totalRevenue": float(current_revenue),
            "revenueChange": round(revenue_change, 1)
        }
    except Exception as e:
        # Return default stats if there's an error
        return {
            "totalCars": 0,
            "availableCars": 0,
            "activeBookings": 0,
            "totalRevenue": 0.0,
            "revenueChange": 0.0
        }

@router.get("/admin/hotel-stats")
async def get_hotel_stats(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get hotel management statistics"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.hotel import Hotel
        from app.models.booking import Booking
        from app.models.payment import Payment
        from sqlalchemy import func, and_
        
        # Get hotel statistics
        total_hotels = db.query(Hotel).count()
        total_rooms = db.query(func.sum(Hotel.room_count)).scalar() or 0
        
        # Get active hotel bookings
        active_bookings = db.query(Booking).filter(
            and_(
                Booking.booking_type == 'hotel',
                Booking.status.in_(['confirmed', 'ongoing'])
            )
        ).count()
        
        # Calculate occupancy rate
        occupancy_rate = 0
        if total_rooms > 0:
            occupancy_rate = round((active_bookings / total_rooms) * 100, 1)
        
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
    except Exception as e:
        # Return default stats if there's an error
        return {
            "totalHotels": 0,
            "totalRooms": 0,
            "activeBookings": 0,
            "totalRevenue": 0.0,
            "revenueChange": 0.0,
            "occupancyRate": 0.0
        }

@router.get("/admin/system/health")
async def get_system_health_admin(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get system health for admin dashboard"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Reuse the health endpoint logic
    from app.api.v1.health import health_check
    return await health_check(db)