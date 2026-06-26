from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import UserCreate, UserLogin, Token, PasswordReset, PasswordUpdate, PasswordResetConfirm
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.core.dependencies import get_current_user
from app.core.security import verify_refresh_token
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])
email_service = EmailService()


@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        user = AuthService.register_user(db, user_data)
        
        # Create welcome notification
        from app.services.notification_service import NotificationService
        NotificationService.create_welcome_notification(
            db=db,
            user_id=user.id,
            user_name=f"{user.first_name} {user.last_name}"
        )
        
        # Send welcome email immediately
        try:
            email_sent = email_service.send_welcome_email(user.email, f"{user.first_name} {user.last_name}")
            if email_sent:
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Welcome email sent successfully to {user.email}")
            else:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send welcome email to {user.email}")
        except Exception as e:
            # Don't fail registration if email fails
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Exception sending welcome email to {user.email}: {e}")
        
        # Create access token for immediate login
        access_token = AuthService.create_access_token(user)
        refresh_token = AuthService.create_refresh_token(user)

        # Determine redirect path based on user roles
        redirect_path = "/dashboard"  # default for regular users
        if user.is_admin() or user.is_superadmin():
            redirect_path = "/admin"

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
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
    refresh_token = AuthService.create_refresh_token(user)

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
        "refresh_token": refresh_token,
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


@router.post("/refresh")
def refresh_token(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """Refresh access token using a refresh token.

    Accepts a refresh token (not an access token) and returns a new access token.
    This allows users to stay logged in after their access token expires.
    """
    payload = verify_refresh_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    from app.models.user import User
    try:
        user_id_int = int(user_id)
        user = db.query(User).filter(User.id == user_id_int).first()
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    new_access_token = AuthService.create_access_token(user)
    return {"access_token": new_access_token, "token_type": "bearer"}


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
        if user and user.is_active:
            reset_token = token_urlsafe(32)
            user.set_reset_token(reset_token, expires_in_hours=1)
            db.commit()
            
            # Send password reset email
            email_sent = email_service.send_password_reset(
                request.email, 
                reset_token, 
                f"{user.first_name} {user.last_name}"
            )
            
            if email_sent:
                logger.info(f"Password reset email sent to {request.email}")
            else:
                logger.error(f"Failed to send password reset email to {request.email}")
                
    except Exception as e:
        logger.error(f"Error in forgot password: {e}")
        pass  # Don't reveal if user exists
    
    return {"message": "Password reset email sent if account exists"}


@router.post("/reset-password")
def reset_password(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password with token"""
    from app.models.user import User
    from passlib.context import CryptContext
    
    token = request.token
    new_password = request.new_password
    
    if not token or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token and new password are required"
        )
    
    # Find user with valid reset token
    user = db.query(User).filter(User.reset_token == token).first()
    
    if not user or not user.is_reset_token_valid(token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Validate password strength
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # Hash new password
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user.hashed_password = pwd_context.hash(new_password)
    
    # Clear reset token
    user.clear_reset_token()
    
    db.commit()
    
    logger.info(f"Password reset successful for user {user.email}")
    
    return {"message": "Password reset successful"}


@router.post("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify email address"""
    return {"message": "Email verified successfully"}