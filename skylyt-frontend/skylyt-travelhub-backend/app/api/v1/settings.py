from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.settings import Settings
from app.schemas.settings import (
    GeneralSettingsUpdate, PaymentGatewaySettingsUpdate, 
    SecuritySettingsUpdate, BankTransferSettingsUpdate, SettingsResponse
)
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/settings", tags=["settings"])

class NotificationSettingsUpdate(BaseModel):
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: Optional[str] = None
    resend_api_key: Optional[str] = None
    onesignal_app_id: Optional[str] = None
    onesignal_api_key: Optional[str] = None
    email_notifications_enabled: Optional[bool] = None
    push_notifications_enabled: Optional[bool] = None


def get_or_create_settings(db: Session) -> Settings:
    """Get existing settings or create default ones"""
    settings = db.query(Settings).first()
    if not settings:
        settings = Settings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.get("/", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    """Get current system settings - public access for basic settings"""
    
    settings = get_or_create_settings(db)
    
    # Return settings without sensitive data for non-superadmins
    response_data = {
        "id": settings.id,
        "site_name": settings.site_name,
        "site_description": settings.site_description,
        "contact_email": settings.contact_email,
        "contact_phone": settings.contact_phone,
        "maintenance_mode": settings.maintenance_mode,
        "password_min_length": settings.password_min_length,
        "session_timeout": settings.session_timeout,
        "two_factor_enabled": settings.two_factor_enabled,
        "login_attempts_limit": settings.login_attempts_limit,
        "paypal_sandbox": settings.paypal_sandbox,
        "bank_name": settings.bank_name,
        "account_name": settings.account_name,
        "account_number": settings.account_number,
        "is_primary_account": settings.is_primary_account
    }
    
    # Public keys are safe to expose (no authentication needed)
    response_data.update({
        "stripe_public_key": settings.stripe_public_key,
        "paystack_public_key": settings.paystack_public_key,
        "flutterwave_public_key": settings.flutterwave_public_key,
        "paypal_client_id": settings.paypal_client_id
    })
    
    return response_data


@router.put("/general")
def update_general_settings(
    settings_update: GeneralSettingsUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update general settings"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    settings = get_or_create_settings(db)
    
    update_data = settings_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    db.commit()
    return {"message": "General settings updated successfully"}


@router.put("/payment-gateway")
def update_payment_gateway_settings(
    settings_update: PaymentGatewaySettingsUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update payment gateway settings (Superadmin only)"""
    if not current_user.is_superadmin():
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    settings = get_or_create_settings(db)
    
    update_data = settings_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    db.commit()
    return {"message": "Payment gateway settings updated successfully"}


@router.put("/security")
def update_security_settings(
    settings_update: SecuritySettingsUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update security settings"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    settings = get_or_create_settings(db)
    
    update_data = settings_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    db.commit()
    return {"message": "Security settings updated successfully"}


@router.put("/bank-transfer")
def update_bank_transfer_settings(
    settings_update: BankTransferSettingsUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update bank transfer settings"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    settings = get_or_create_settings(db)
    
    update_data = settings_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    db.commit()
    return {"message": "Bank transfer settings updated successfully"}


@router.put("/notifications")
def update_notification_settings(
    settings_update: NotificationSettingsUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update notification settings"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    settings = get_or_create_settings(db)
    
    update_data = settings_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(settings, field):
            setattr(settings, field, value)
    
    db.commit()
    return {"message": "Notification settings updated successfully"}