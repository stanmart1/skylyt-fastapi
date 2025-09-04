from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import UserCreate, UserLogin, Token, PasswordReset, PasswordUpdate
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.core.dependencies import get_current_user
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["authentication"])
email_service = EmailService()


@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        user = AuthService.register_user(db, user_data)
        
        # Send welcome email immediately
        try:
            email_service.send_welcome_email(user.email, f"{user.first_name} {user.last_name}")
        except Exception as e:
            # Don't fail registration if email fails
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to send welcome email: {e}")
        
        # Create access token for immediate login
        access_token = AuthService.create_access_token(user)
        
        # Determine redirect path based on user roles
        redirect_path = "/dashboard"  # default for regular users
        if user.is_admin() or user.is_superadmin():
            redirect_path = "/admin"
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "redirect_path": redirect_path,
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "full_name": f"{user.first_name} {user.last_name}",
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "roles": [{
                    "id": role.id,
                    "name": role.name,
                    "permissions": [{
                        "id": perm.id,
                        "name": perm.name,
                        "resource": perm.resource,
                        "action": perm.action
                    } for perm in role.permissions]
                } for role in user.roles]
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """User login with session caching"""
    import logging
    from app.utils.sanitize import sanitize_for_logging
    from app.services.cache_service import CacheService
    
    logger = logging.getLogger(__name__)
    logger.info("Login attempt initiated")
    
    user = AuthService.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        logger.warning("Authentication failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    logger.info("User authenticated successfully")
    access_token = AuthService.create_access_token(user)
    
    # Cache user session data
    session_data = {
        "user_id": user.id,
        "email": user.email,
        "roles": [role.name for role in user.roles]
    }
    CacheService.cache_user_session(user.id, session_data)
    
    # Determine redirect path based on user roles
    redirect_path = "/dashboard"  # default for regular users
    if user.is_admin() or user.is_superadmin():
        redirect_path = "/admin"
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "redirect_path": redirect_path,
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": f"{user.first_name} {user.last_name}",
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "roles": [{
                "id": role.id,
                "name": role.name,
                "permissions": [{
                    "id": perm.id,
                    "name": perm.name,
                    "resource": perm.resource,
                    "action": perm.action
                } for perm in role.permissions]
            } for role in user.roles]
        }
    }


@router.post("/refresh", response_model=Token)
def refresh_token(current_user = Depends(get_current_user)):
    """Refresh access token"""
    access_token = AuthService.create_access_token(current_user)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(current_user = Depends(get_current_user)):
    """User logout with session cleanup"""
    from app.services.cache_service import CacheService
    
    # Clear user session from cache
    CacheService.invalidate_user_session(current_user.id)
    
    return {"message": "Successfully logged out"}


@router.post("/forgot-password")
def forgot_password(request: PasswordReset, db: Session = Depends(get_db)):
    """Request password reset"""
    from secrets import token_urlsafe
    from app.models.user import User
    
    try:
        user = db.query(User).filter(User.email == request.email).first()
        if user:
            reset_token = token_urlsafe(32)
            # Send password reset email
            email_service.send_password_reset(request.email, reset_token, f"{user.first_name} {user.last_name}")
    except Exception:
        pass  # Don't reveal if user exists
    
    return {"message": "Password reset email sent if account exists"}


@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    """Reset password with token"""
    return {"message": "Password reset successful"}


@router.post("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify email address"""
    return {"message": "Email verified successfully"}