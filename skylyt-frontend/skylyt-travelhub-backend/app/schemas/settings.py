from pydantic import BaseModel
from typing import Optional, Dict, Any


class GeneralSettingsUpdate(BaseModel):
    site_name: Optional[str] = None
    site_description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    maintenance_mode: Optional[bool] = None


class PaymentGatewaySettingsUpdate(BaseModel):
    stripe_public_key: Optional[str] = None
    stripe_secret_key: Optional[str] = None
    paystack_public_key: Optional[str] = None
    paystack_secret_key: Optional[str] = None
    flutterwave_public_key: Optional[str] = None
    flutterwave_secret_key: Optional[str] = None
    paypal_client_id: Optional[str] = None
    paypal_client_secret: Optional[str] = None
    paypal_sandbox: Optional[bool] = None


class SecuritySettingsUpdate(BaseModel):
    password_min_length: Optional[str] = None
    session_timeout: Optional[str] = None
    two_factor_enabled: Optional[bool] = None
    login_attempts_limit: Optional[str] = None


class BankTransferSettingsUpdate(BaseModel):
    bank_name: Optional[str] = None
    account_name: Optional[str] = None
    account_number: Optional[str] = None
    is_primary_account: Optional[bool] = None
    bank_address: Optional[str] = None
    account_type: Optional[str] = None
    currency: Optional[str] = None
    transfer_fee: Optional[str] = None
    processing_time_hours: Optional[str] = None
    auto_verification_enabled: Optional[bool] = None
    require_reference_number: Optional[bool] = None
    bank_transfer_instructions: Optional[str] = None


class GoogleAnalyticsSettingsUpdate(BaseModel):
    google_analytics_tracking_id: Optional[str] = None
    google_analytics_measurement_id: Optional[str] = None
    google_analytics_api_key: Optional[str] = None
    google_analytics_enabled: Optional[bool] = None


class SettingsResponse(BaseModel):
    id: int
    site_name: str
    site_description: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    maintenance_mode: bool
    stripe_public_key: Optional[str]
    paystack_public_key: Optional[str]
    flutterwave_public_key: Optional[str]
    paypal_client_id: Optional[str]
    paypal_sandbox: bool
    password_min_length: str
    session_timeout: str
    two_factor_enabled: bool
    login_attempts_limit: str
    bank_name: Optional[str]
    account_name: Optional[str]
    account_number: Optional[str]
    is_primary_account: bool
    smtp_server: Optional[str]
    smtp_port: Optional[int]
    smtp_username: Optional[str]
    from_email: Optional[str]
    email_notifications_enabled: Optional[bool]
    sms_enabled: Optional[bool]
    push_notifications_enabled: Optional[bool]
    booking_notifications: Optional[bool]
    payment_notifications: Optional[bool]
    system_notifications: Optional[bool]
    driver_notifications: Optional[bool]
    admin_notifications: Optional[bool]

    bank_transfer_instructions: Optional[str]
    webhook_secret_stripe: Optional[str]
    webhook_secret_paystack: Optional[str]
    webhook_secret_flutterwave: Optional[str]
    google_analytics_tracking_id: Optional[str]
    google_analytics_measurement_id: Optional[str]
    google_analytics_enabled: Optional[bool]
    
    class Config:
        from_attributes = True