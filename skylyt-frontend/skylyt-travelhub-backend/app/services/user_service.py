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
        return db.query(Booking).filter(Booking.user_id == user_id).distinct().all()
    
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