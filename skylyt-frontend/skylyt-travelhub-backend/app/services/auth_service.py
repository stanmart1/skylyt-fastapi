from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import UserCreate
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.settings import Settings
from datetime import timedelta
from typing import Optional


class AuthService:
    
    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Email already registered")
        
        # Validate password against settings
        settings = db.query(Settings).first()
        if settings:
            min_length = int(settings.password_min_length)
            if len(user_data.password) < min_length:
                raise ValueError(f"Password must be at least {min_length} characters long")
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,

        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Assign default customer role
        from app.models.rbac import Role
        customer_role = db.query(Role).filter(Role.name == "customer").first()
        if customer_role:
            db_user.roles.append(customer_role)
            db.commit()
        
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        from app.models.rbac import Role, Permission
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        
        # Load user roles and permissions
        user = db.query(User).filter(User.id == user.id).first()
        return user
    
    @staticmethod
    def create_access_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
        data = {"sub": str(user.id), "email": user.email}
        return create_access_token(data, expires_delta)
    
    @staticmethod
    def verify_email(db: Session, user_id: int) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_verified = True
            db.commit()
            return True
        return False
    
    @staticmethod
    def reset_password(db: Session, email: str, new_password: str) -> bool:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.hashed_password = get_password_hash(new_password)
            db.commit()
            return True
        return False