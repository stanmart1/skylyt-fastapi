from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.settings import Settings
from app.schemas.settings import (
    GeneralSettingsUpdate, PaymentGatewaySettingsUpdate, 
    SecuritySettingsUpdate, BankTransferSettingsUpdate, 
    GoogleAnalyticsSettingsUpdate, SettingsResponse
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
    email_notifications_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_notifications_enabled: Optional[bool] = None
    booking_notifications: Optional[bool] = None
    payment_notifications: Optional[bool] = None
    system_notifications: Optional[bool] = None
    driver_notifications: Optional[bool] = None
    admin_notifications: Optional[bool] = None

class PaymentGatewaySettingsUpdateSimplified(BaseModel):
    stripe_public_key: Optional[str] = None
    stripe_secret_key: Optional[str] = None
    paystack_public_key: Optional[str] = None
    paystack_secret_key: Optional[str] = None
    flutterwave_public_key: Optional[str] = None
    flutterwave_secret_key: Optional[str] = None
    paypal_client_id: Optional[str] = None
    paypal_client_secret: Optional[str] = None
    paypal_sandbox: Optional[bool] = None
    webhook_secret_stripe: Optional[str] = None
    webhook_secret_paystack: Optional[str] = None
    webhook_secret_flutterwave: Optional[str] = None

class SecuritySettingsUpdateSimplified(BaseModel):
    password_min_length: Optional[str] = None
    session_timeout: Optional[str] = None
    two_factor_enabled: Optional[bool] = None
    login_attempts_limit: Optional[str] = None
    
    # General rate limiting
    general_rate_limit_enabled: Optional[bool] = None
    general_rate_limit_requests: Optional[str] = None
    general_rate_limit_window: Optional[str] = None
    
    # Auth rate limiting
    auth_rate_limit_enabled: Optional[bool] = None
    auth_rate_limit_requests: Optional[str] = None
    auth_rate_limit_window: Optional[str] = None
    
    # Booking rate limiting
    booking_rate_limit_enabled: Optional[bool] = None
    booking_rate_limit_requests: Optional[str] = None
    booking_rate_limit_window: Optional[str] = None
    
    # Admin rate limiting
    admin_rate_limit_enabled: Optional[bool] = None
    admin_rate_limit_requests: Optional[str] = None
    admin_rate_limit_window: Optional[str] = None

class BankTransferSettingsUpdateSimplified(BaseModel):
    bank_name: Optional[str] = None
    account_name: Optional[str] = None
    account_number: Optional[str] = None
    bank_transfer_instructions: Optional[str] = None

class FeatureSettingsUpdate(BaseModel):
    car_rental_enabled: Optional[bool] = None
    hotel_booking_enabled: Optional[bool] = None
    driver_service_enabled: Optional[bool] = None
    multi_currency_enabled: Optional[bool] = None
    reviews_enabled: Optional[bool] = None
    loyalty_program_enabled: Optional[bool] = None
    referral_program_enabled: Optional[bool] = None
    chat_support_enabled: Optional[bool] = None
    mobile_app_enabled: Optional[bool] = None
    api_access_enabled: Optional[bool] = None
    booking_modifications_enabled: Optional[bool] = None
    cancellation_enabled: Optional[bool] = None
    partial_payments_enabled: Optional[bool] = None
    group_bookings_enabled: Optional[bool] = None
    corporate_accounts_enabled: Optional[bool] = None
    maintenance_notifications: Optional[bool] = None
    feature_announcements: Optional[bool] = None
    beta_features_enabled: Optional[bool] = None


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
    from app.utils.cache_manager import cache_manager
    
    # Use cache for settings (5 minute cache)
    cache_key = "system_settings"
    cached_settings = cache_manager.get(cache_key)
    if cached_settings:
        return cached_settings
    
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
        # Rate limiting settings
        "general_rate_limit_enabled": getattr(settings, 'general_rate_limit_enabled', True),
        "general_rate_limit_requests": getattr(settings, 'general_rate_limit_requests', '100'),
        "general_rate_limit_window": getattr(settings, 'general_rate_limit_window', '60'),
        "auth_rate_limit_enabled": getattr(settings, 'auth_rate_limit_enabled', True),
        "auth_rate_limit_requests": getattr(settings, 'auth_rate_limit_requests', '5'),
        "auth_rate_limit_window": getattr(settings, 'auth_rate_limit_window', '60'),
        "booking_rate_limit_enabled": getattr(settings, 'booking_rate_limit_enabled', True),
        "booking_rate_limit_requests": getattr(settings, 'booking_rate_limit_requests', '20'),
        "booking_rate_limit_window": getattr(settings, 'booking_rate_limit_window', '60'),
        "admin_rate_limit_enabled": getattr(settings, 'admin_rate_limit_enabled', True),
        "admin_rate_limit_requests": getattr(settings, 'admin_rate_limit_requests', '30'),
        "admin_rate_limit_window": getattr(settings, 'admin_rate_limit_window', '600'),
        "paypal_sandbox": settings.paypal_sandbox,
        "bank_name": settings.bank_name,
        "account_name": settings.account_name,
        "account_number": settings.account_number,
        "is_primary_account": settings.is_primary_account,
        "smtp_server": settings.smtp_server,
        "smtp_port": settings.smtp_port,
        "smtp_username": settings.smtp_username,
        "from_email": settings.from_email,
        "email_notifications_enabled": settings.email_notifications_enabled,
        "sms_enabled": getattr(settings, 'sms_enabled', False),
        "push_notifications_enabled": getattr(settings, 'push_notifications_enabled', True),
        "booking_notifications": getattr(settings, 'booking_notifications', True),
        "payment_notifications": getattr(settings, 'payment_notifications', True),
        "system_notifications": getattr(settings, 'system_notifications', True),
        "driver_notifications": getattr(settings, 'driver_notifications', True),
        "admin_notifications": getattr(settings, 'admin_notifications', True),


        "bank_transfer_instructions": settings.bank_transfer_instructions,
        "webhook_secret_stripe": None,  # Never expose secrets
        "webhook_secret_paystack": None,
        "webhook_secret_flutterwave": None,
        "google_analytics_tracking_id": settings.google_analytics_tracking_id,
        "google_analytics_measurement_id": settings.google_analytics_measurement_id,
        "google_analytics_enabled": settings.google_analytics_enabled
    }
    
    # Public keys are safe to expose (no authentication needed)
    response_data.update({
        "stripe_public_key": settings.stripe_public_key,
        "paystack_public_key": settings.paystack_public_key,
        "flutterwave_public_key": settings.flutterwave_public_key,
        "paypal_client_id": settings.paypal_client_id
    })
    
    # Cache the response
    cache_manager.set(cache_key, response_data, 300)  # 5 minute cache
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
    settings_update: PaymentGatewaySettingsUpdateSimplified,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update payment gateway settings (Superadmin only)"""
    if not current_user.is_superadmin():
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    settings = get_or_create_settings(db)
    
    update_data = settings_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(settings, field) and value is not None:
            setattr(settings, field, value)
    
    db.commit()
    return {"message": "Payment gateway settings updated successfully"}


@router.put("/security")
def update_security_settings(
    settings_update: SecuritySettingsUpdateSimplified,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update security settings"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    settings = get_or_create_settings(db)
    
    update_data = settings_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(settings, field) and value is not None:
            setattr(settings, field, value)
    
    db.commit()
    return {"message": "Security settings updated successfully"}


@router.put("/bank-transfer")
def update_bank_transfer_settings(
    settings_update: BankTransferSettingsUpdateSimplified,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update bank transfer settings"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    settings = get_or_create_settings(db)
    
    update_data = settings_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(settings, field) and value is not None:
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
        if hasattr(settings, field) and value is not None:
            setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    return {"message": "Notification settings updated successfully", "settings": {
        "smtp_server": settings.smtp_server,
        "smtp_port": settings.smtp_port,
        "smtp_username": settings.smtp_username,
        "from_email": settings.from_email,
        "email_notifications_enabled": settings.email_notifications_enabled,
        "sms_enabled": settings.sms_enabled,
        "push_notifications_enabled": settings.push_notifications_enabled,
        "booking_notifications": settings.booking_notifications,
        "payment_notifications": settings.payment_notifications,
        "system_notifications": settings.system_notifications,
        "driver_notifications": settings.driver_notifications,
        "admin_notifications": settings.admin_notifications
    }}


@router.put("/google-analytics")
def update_google_analytics_settings(
    settings_update: GoogleAnalyticsSettingsUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update Google Analytics settings"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    settings = get_or_create_settings(db)
    
    update_data = settings_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(settings, field) and value is not None:
            setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    
    return {
        "message": "Google Analytics settings updated successfully",
        "settings": {
            "google_analytics_tracking_id": settings.google_analytics_tracking_id,
            "google_analytics_measurement_id": settings.google_analytics_measurement_id,
            "google_analytics_enabled": settings.google_analytics_enabled
        }
    }


@router.get("/features")
def get_feature_settings(db: Session = Depends(get_db)):
    """Get feature settings"""
    settings = get_or_create_settings(db)
    
    return {
        "car_rental_enabled": getattr(settings, 'car_rental_enabled', True),
        "hotel_booking_enabled": getattr(settings, 'hotel_booking_enabled', True),
        "driver_service_enabled": getattr(settings, 'driver_service_enabled', True),
        "multi_currency_enabled": getattr(settings, 'multi_currency_enabled', True),
        "reviews_enabled": getattr(settings, 'reviews_enabled', True),
        "loyalty_program_enabled": getattr(settings, 'loyalty_program_enabled', False),
        "referral_program_enabled": getattr(settings, 'referral_program_enabled', False),
        "chat_support_enabled": getattr(settings, 'chat_support_enabled', True),
        "mobile_app_enabled": getattr(settings, 'mobile_app_enabled', False),
        "api_access_enabled": getattr(settings, 'api_access_enabled', False),
        "booking_modifications_enabled": getattr(settings, 'booking_modifications_enabled', True),
        "cancellation_enabled": getattr(settings, 'cancellation_enabled', True),
        "partial_payments_enabled": getattr(settings, 'partial_payments_enabled', False),
        "group_bookings_enabled": getattr(settings, 'group_bookings_enabled', False),
        "corporate_accounts_enabled": getattr(settings, 'corporate_accounts_enabled', False),
        "maintenance_notifications": getattr(settings, 'maintenance_notifications', True),
        "feature_announcements": getattr(settings, 'feature_announcements', True),
        "beta_features_enabled": getattr(settings, 'beta_features_enabled', False)
    }


@router.put("/features")
def update_feature_settings(
    settings_update: FeatureSettingsUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update feature settings"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    settings = get_or_create_settings(db)
    
    update_data = settings_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(settings, field) and value is not None:
            setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    
    return {
        "message": "Feature settings updated successfully",
        "settings": {
            "car_rental_enabled": settings.car_rental_enabled,
            "hotel_booking_enabled": settings.hotel_booking_enabled,
            "driver_service_enabled": settings.driver_service_enabled,
            "multi_currency_enabled": settings.multi_currency_enabled,
            "reviews_enabled": settings.reviews_enabled,
            "loyalty_program_enabled": settings.loyalty_program_enabled,
            "referral_program_enabled": settings.referral_program_enabled,
            "chat_support_enabled": settings.chat_support_enabled,
            "mobile_app_enabled": settings.mobile_app_enabled,
            "api_access_enabled": settings.api_access_enabled,
            "booking_modifications_enabled": settings.booking_modifications_enabled,
            "cancellation_enabled": settings.cancellation_enabled,
            "partial_payments_enabled": settings.partial_payments_enabled,
            "group_bookings_enabled": settings.group_bookings_enabled,
            "corporate_accounts_enabled": settings.corporate_accounts_enabled,
            "maintenance_notifications": settings.maintenance_notifications,
            "feature_announcements": settings.feature_announcements,
            "beta_features_enabled": settings.beta_features_enabled
        }
    }