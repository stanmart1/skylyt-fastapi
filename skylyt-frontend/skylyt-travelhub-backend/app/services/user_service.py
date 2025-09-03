from sqlalchemy.orm import Session
from app.models.user import User
from app.models.booking import Booking
from app.models.favorite import Favorite
from app.schemas.user import UserUpdate
from typing import Optional, List


class UserService:
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def update_user_profile(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user_account(db: Session, user_id: int) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = False
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_user_bookings(db: Session, user_id: int) -> List[Booking]:
        # Get all bookings for the user
        all_bookings = db.query(Booking).filter(Booking.user_id == user_id).all()
        
        # Group bookings by similar characteristics to identify duplicates
        unique_bookings = {}
        for booking in all_bookings:
            # Create a key based on booking characteristics
            key = (
                booking.customer_email,
                booking.total_amount,
                booking.booking_type,
                booking.start_date,
                booking.end_date
            )
            
            # Keep the booking with the most recent status (payment_pending over pending)
            if key not in unique_bookings:
                unique_bookings[key] = booking
            else:
                existing = unique_bookings[key]
                # Prioritize confirmed > payment_pending > pending
                status_priority = {
                    'confirmed': 3,
                    'payment_pending': 2, 
                    'pending': 1,
                    'cancelled': 0
                }
                
                current_priority = status_priority.get(booking.status, 0)
                existing_priority = status_priority.get(existing.status, 0)
                
                if current_priority > existing_priority:
                    unique_bookings[key] = booking
                elif current_priority == existing_priority and booking.created_at > existing.created_at:
                    # If same priority, keep the newer one
                    unique_bookings[key] = booking
        
        return list(unique_bookings.values())
    
    @staticmethod
    def manage_favorites(db: Session, user_id: int, item_type: str, item_id: str, item_data: dict, action: str) -> bool:
        if action == "add":
            favorite = Favorite(
                user_id=user_id,
                item_type=item_type,
                item_id=item_id,
                item_data=item_data
            )
            db.add(favorite)
            db.commit()
            return True
        elif action == "remove":
            favorite = db.query(Favorite).filter(
                Favorite.user_id == user_id,
                Favorite.item_type == item_type,
                Favorite.item_id == item_id
            ).first()
            if favorite:
                db.delete(favorite)
                db.commit()
                return True
        return False