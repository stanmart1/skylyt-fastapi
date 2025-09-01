from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.booking import BookingResponse
from app.services.user_service import UserService
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_current_user_profile(current_user = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "full_name": f"{current_user.first_name} {current_user.last_name}",
        "phone": current_user.phone,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at.isoformat(),
        "roles": [{
            "id": role.id,
            "name": role.name,
            "permissions": [{
                "id": perm.id,
                "name": perm.name,
                "resource": perm.resource,
                "action": perm.action
            } for perm in role.permissions]
        } for role in current_user.roles]
    }


@router.put("/me")
def update_user_profile(
    user_update: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    updated_user = UserService.update_user_profile(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": updated_user.id,
        "email": updated_user.email,
        "first_name": updated_user.first_name,
        "last_name": updated_user.last_name,
        "full_name": f"{updated_user.first_name} {updated_user.last_name}",
        "phone": updated_user.phone,
        "is_active": updated_user.is_active,
        "is_verified": updated_user.is_verified,
        "created_at": updated_user.created_at.isoformat(),
        "roles": [{
            "id": role.id,
            "name": role.name,
            "permissions": [{
                "id": perm.id,
                "name": perm.name,
                "resource": perm.resource,
                "action": perm.action
            } for perm in role.permissions]
        } for role in updated_user.roles]
    }


@router.delete("/me")
def delete_user_account(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account"""
    success = UserService.delete_user_account(db, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Account deleted successfully"}


@router.get("/me/bookings", response_model=List[BookingResponse])
def get_user_bookings(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user bookings"""
    bookings = UserService.get_user_bookings(db, current_user.id)
    return bookings


@router.put("/me/bookings/{booking_id}/extend")
def extend_booking(
    booking_id: str,
    extension_data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Extend booking dates"""
    from app.models.booking import Booking
    from datetime import datetime
    
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status not in ['confirmed', 'in_progress']:
        raise HTTPException(status_code=400, detail="Cannot extend this booking")
    
    new_checkout_date = extension_data.get("new_checkout_date")
    if not new_checkout_date:
        raise HTTPException(status_code=400, detail="New checkout date required")
    
    try:
        new_date = datetime.fromisoformat(new_checkout_date.replace('Z', '+00:00'))
        if new_date <= booking.check_out_date:
            raise HTTPException(status_code=400, detail="New date must be after current checkout")
        
        # Calculate additional cost (simplified)
        days_extended = (new_date - booking.check_out_date).days
        daily_rate = booking.total_amount / ((booking.check_out_date - booking.check_in_date).days or 1)
        additional_cost = daily_rate * days_extended
        
        booking.check_out_date = new_date
        booking.total_amount += additional_cost
        
        db.commit()
        db.refresh(booking)
        
        return {
            "message": "Booking extended successfully",
            "new_checkout_date": new_date.isoformat(),
            "additional_cost": float(additional_cost),
            "new_total": float(booking.total_amount)
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")


@router.put("/me/bookings/{booking_id}/modify")
def modify_booking(
    booking_id: str,
    modification_data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Modify booking details"""
    from app.models.booking import Booking
    
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status not in ['confirmed', 'pending']:
        raise HTTPException(status_code=400, detail="Cannot modify this booking")
    
    # Update allowed fields
    if 'special_requests' in modification_data:
        booking.special_requests = modification_data['special_requests']
    
    if 'guest_count' in modification_data and booking.booking_type == 'hotel':
        booking.guest_count = modification_data['guest_count']
    
    db.commit()
    db.refresh(booking)
    
    return {"message": "Booking modified successfully"}


@router.get("/me/bookings/{booking_id}/payment-status")
def get_booking_payment_status(
    booking_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get booking payment status"""
    from app.models.booking import Booking
    
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return {
        "booking_id": booking.id,
        "payment_status": booking.payment_status,
        "total_amount": float(booking.total_amount),
        "currency": booking.currency,
        "payment_method": getattr(booking, 'payment_method', None),
        "paid_amount": float(getattr(booking, 'paid_amount', 0)),
        "pending_amount": float(booking.total_amount - getattr(booking, 'paid_amount', 0))
    }


@router.get("/me/upcoming-reminders")
def get_upcoming_reminders(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get upcoming booking reminders"""
    from app.models.booking import Booking
    from datetime import datetime, timedelta
    from sqlalchemy import and_
    
    # Get bookings in next 3 days
    reminder_date = datetime.now() + timedelta(days=3)
    
    upcoming_bookings = db.query(Booking).filter(
        and_(
            Booking.user_id == current_user.id,
            Booking.status == 'confirmed',
            Booking.check_in_date <= reminder_date,
            Booking.check_in_date >= datetime.now()
        )
    ).all()
    
    reminders = []
    for booking in upcoming_bookings:
        days_until = (booking.check_in_date - datetime.now()).days
        reminders.append({
            "booking_id": booking.id,
            "booking_reference": booking.booking_reference,
            "type": booking.booking_type,
            "name": booking.hotel_name or booking.car_name,
            "check_in_date": booking.check_in_date.isoformat(),
            "days_until": days_until,
            "reminder_type": "check_in_soon" if days_until <= 1 else "upcoming_trip"
        })
    
    return {"reminders": reminders}


@router.get("/me/favorites")
def get_user_favorites(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user favorites"""
    from app.models.favorite import Favorite
    
    favorites = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    
    return {
        "favorites": [
            {
                "id": fav.id,
                "item_type": fav.item_type,
                "item_id": fav.item_id,
                "name": fav.item_data.get("name", "Unknown"),
                "item_data": fav.item_data,
                "created_at": fav.created_at.isoformat()
            }
            for fav in favorites
        ]
    }


@router.post("/me/favorites")
def add_to_favorites(
    favorite_data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add item to favorites"""
    from app.models.favorite import Favorite
    
    item_type = favorite_data.get("item_type")
    item_id = favorite_data.get("item_id")
    name = favorite_data.get("name")
    
    if not all([item_type, item_id, name]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    # Check if already exists
    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.item_type == item_type,
        Favorite.item_id == item_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Item already in favorites")
    
    # Create new favorite
    favorite = Favorite(
        user_id=current_user.id,
        item_type=item_type,
        item_id=item_id,
        item_data={"name": name}
    )
    
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    
    return {"message": "Added to favorites", "id": favorite.id}


@router.delete("/me/favorites/{favorite_id}")
def remove_from_favorites(
    favorite_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from favorites"""
    from app.models.favorite import Favorite
    
    favorite = db.query(Favorite).filter(
        Favorite.id == favorite_id,
        Favorite.user_id == current_user.id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    db.delete(favorite)
    db.commit()
    
    return {"message": "Removed from favorites"}


@router.post("/me/change-password")
def change_password(
    password_data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    from app.core.security import verify_password, get_password_hash
    
    current_password = password_data.get("current_password")
    new_password = password_data.get("new_password")
    
    if not current_password or not new_password:
        raise HTTPException(status_code=400, detail="Current and new passwords are required")
    
    # Verify current password
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Update password
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.get("/me/stats")
def get_user_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user dashboard statistics"""
    from app.models.booking import Booking
    from app.models.favorite import Favorite
    from sqlalchemy import func, and_
    from datetime import datetime, timedelta
    
    # Total bookings
    total_bookings = db.query(func.count(Booking.id)).filter(
        Booking.user_id == current_user.id
    ).scalar() or 0
    
    # Active bookings (confirmed, in_progress)
    active_bookings = db.query(func.count(Booking.id)).filter(
        and_(
            Booking.user_id == current_user.id,
            Booking.status.in_(['confirmed', 'in_progress'])
        )
    ).scalar() or 0
    
    # Total spent
    total_spent = db.query(func.sum(Booking.total_amount)).filter(
        and_(
            Booking.user_id == current_user.id,
            Booking.status.in_(['confirmed', 'completed'])
        )
    ).scalar() or 0
    
    # Upcoming bookings (next 7 days)
    upcoming_date = datetime.now() + timedelta(days=7)
    upcoming_bookings = db.query(func.count(Booking.id)).filter(
        and_(
            Booking.user_id == current_user.id,
            Booking.status == 'confirmed',
            Booking.check_in_date <= upcoming_date,
            Booking.check_in_date >= datetime.now()
        )
    ).scalar() or 0
    
    # Total favorites
    total_favorites = db.query(func.count(Favorite.id)).filter(
        Favorite.user_id == current_user.id
    ).scalar() or 0
    
    return {
        "total_bookings": total_bookings,
        "active_bookings": active_bookings,
        "total_spent": float(total_spent),
        "upcoming_bookings": upcoming_bookings,
        "total_favorites": total_favorites
    }


@router.get("/me/notifications")
def get_user_notifications(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notification preferences"""
    # Check if user has preferences stored
    if hasattr(current_user, 'email_notifications') and hasattr(current_user, 'sms_notifications'):
        return {
            "email": current_user.email_notifications,
            "sms": current_user.sms_notifications
        }
    
    # Return defaults if not set
    return {
        "email": True,
        "sms": False
    }


@router.put("/me/notifications")
def update_user_notifications(
    notification_data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user notification preferences"""
    email_enabled = notification_data.get("email", True)
    sms_enabled = notification_data.get("sms", False)
    
    # Update user preferences
    current_user.email_notifications = email_enabled
    current_user.sms_notifications = sms_enabled
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "email": email_enabled,
        "sms": sms_enabled,
        "message": "Notification preferences updated successfully"
    }


@router.get("/admin/users")
def get_admin_users(
    role: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get admin users for ticket assignment"""
    if not current_user.has_role("admin") and not current_user.has_role("superadmin"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    query = db.query(User).join(User.roles)
    
    if role:
        from app.models.rbac import Role
        query = query.filter(Role.name == role)
    else:
        from app.models.rbac import Role
        query = query.filter(Role.name.in_(['admin', 'superadmin']))
    
    users = query.all()
    
    return [
        {
            "id": user.id,
            "full_name": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "roles": [role.name for role in user.roles]
        }
        for user in users
    ]