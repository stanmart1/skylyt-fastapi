from sqlalchemy import Column, String, Boolean, Text, JSON, Integer
from .base import BaseModel


class Settings(BaseModel):
    __tablename__ = "settings"
    
    # General Settings
    site_name = Column(String(255), default="Skylyt TravelHub")
    site_description = Column(Text, nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    maintenance_mode = Column(Boolean, default=False)
    
    # Payment Gateway Settings
    stripe_public_key = Column(String(255), nullable=True)
    stripe_secret_key = Column(String(255), nullable=True)
    paystack_public_key = Column(String(255), nullable=True)
    paystack_secret_key = Column(String(255), nullable=True)
    flutterwave_public_key = Column(String(255), nullable=True)
    flutterwave_secret_key = Column(String(255), nullable=True)
    paypal_client_id = Column(String(255), nullable=True)
    paypal_client_secret = Column(String(255), nullable=True)
    paypal_sandbox = Column(Boolean, default=True)
    
    # Security Settings
    password_min_length = Column(String(10), default="8")
    session_timeout = Column(String(10), default="30")
    two_factor_enabled = Column(Boolean, default=False)
    login_attempts_limit = Column(String(10), default="5")
    
    # Bank Transfer Settings
    bank_name = Column(String(255), nullable=True)
    account_name = Column(String(255), nullable=True)
    account_number = Column(String(100), nullable=True)
    is_primary_account = Column(Boolean, default=True)
    
    # Notification Settings
    smtp_server = Column(String(255), nullable=True)
    smtp_port = Column(Integer, default=587)
    smtp_username = Column(String(255), nullable=True)
    smtp_password = Column(String(255), nullable=True)
    from_email = Column(String(255), nullable=True)
    resend_api_key = Column(String(255), nullable=True)
    email_notifications_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    push_notifications_enabled = Column(Boolean, default=True)
    booking_notifications = Column(Boolean, default=True)
    payment_notifications = Column(Boolean, default=True)
    system_notifications = Column(Boolean, default=True)
    driver_notifications = Column(Boolean, default=True)
    admin_notifications = Column(Boolean, default=True)
    notification_frequency = Column(String(50), default='immediate')
    quiet_hours_start = Column(String(10), default='22:00')
    quiet_hours_end = Column(String(10), default='08:00')
    timezone = Column(String(50), default='UTC')
    
    # Google Analytics Settings
    google_analytics_tracking_id = Column(String(255), nullable=True)
    google_analytics_measurement_id = Column(String(255), nullable=True)
    google_analytics_api_key = Column(String(255), nullable=True)
    google_analytics_enabled = Column(Boolean, default=False)
    
    # General Settings Extensions
    site_logo = Column(String(500), nullable=True)
    favicon = Column(String(500), nullable=True)
    default_language = Column(String(10), default='en')
    default_timezone = Column(String(50), default='UTC')
    site_keywords = Column(Text, nullable=True)
    social_facebook = Column(String(255), nullable=True)
    social_twitter = Column(String(255), nullable=True)
    social_instagram = Column(String(255), nullable=True)
    social_linkedin = Column(String(255), nullable=True)
    terms_url = Column(String(255), nullable=True)
    privacy_url = Column(String(255), nullable=True)
    support_url = Column(String(255), nullable=True)
    company_address = Column(Text, nullable=True)
    company_registration = Column(String(255), nullable=True)
    vat_number = Column(String(255), nullable=True)
    
    # Security Settings Extensions
    password_require_uppercase = Column(Boolean, default=True)
    password_require_lowercase = Column(Boolean, default=True)
    password_require_numbers = Column(Boolean, default=True)
    password_require_symbols = Column(Boolean, default=False)
    account_lockout_duration = Column(String(10), default='30')
    password_expiry_days = Column(String(10), default='90')
    force_password_change = Column(Boolean, default=False)
    allow_password_reset = Column(Boolean, default=True)
    captcha_enabled = Column(Boolean, default=False)
    ip_whitelist_enabled = Column(Boolean, default=False)
    ip_whitelist = Column(Text, nullable=True)
    ssl_required = Column(Boolean, default=True)
    cookie_secure = Column(Boolean, default=True)
    session_cookie_httponly = Column(Boolean, default=True)
    
    # Payment Settings Extensions
    payment_currency = Column(String(10), default='USD')
    minimum_payment_amount = Column(String(20), default='1.00')
    maximum_payment_amount = Column(String(20), default='10000.00')
    payment_processing_fee = Column(String(10), default='2.9')
    auto_capture_payments = Column(Boolean, default=True)
    refund_policy_days = Column(String(10), default='30')
    partial_refunds_enabled = Column(Boolean, default=True)
    webhook_secret_stripe = Column(String(255), nullable=True)
    webhook_secret_paystack = Column(String(255), nullable=True)
    webhook_secret_flutterwave = Column(String(255), nullable=True)
    payment_retry_attempts = Column(String(10), default='3')
    payment_timeout_minutes = Column(String(10), default='15')
    
    # Bank Transfer Extensions
    routing_number = Column(String(50), nullable=True)
    swift_code = Column(String(20), nullable=True)
    iban = Column(String(50), nullable=True)
    bank_address = Column(Text, nullable=True)
    account_type = Column(String(20), default='checking')
    currency = Column(String(10), default='USD')
    minimum_transfer_amount = Column(String(20), default='10.00')
    maximum_transfer_amount = Column(String(20), default='50000.00')
    transfer_fee = Column(String(20), default='0.00')
    processing_time_hours = Column(String(10), default='24')
    auto_verification_enabled = Column(Boolean, default=False)
    require_reference_number = Column(Boolean, default=True)
    bank_transfer_instructions = Column(Text, nullable=True)
    
    # Feature Settings
    car_rental_enabled = Column(Boolean, default=True)
    hotel_booking_enabled = Column(Boolean, default=True)
    driver_service_enabled = Column(Boolean, default=True)
    multi_currency_enabled = Column(Boolean, default=True)
    reviews_enabled = Column(Boolean, default=True)
    loyalty_program_enabled = Column(Boolean, default=False)
    referral_program_enabled = Column(Boolean, default=False)
    chat_support_enabled = Column(Boolean, default=True)
    mobile_app_enabled = Column(Boolean, default=False)
    api_access_enabled = Column(Boolean, default=False)
    booking_modifications_enabled = Column(Boolean, default=True)
    cancellation_enabled = Column(Boolean, default=True)
    partial_payments_enabled = Column(Boolean, default=False)
    group_bookings_enabled = Column(Boolean, default=False)
    corporate_accounts_enabled = Column(Boolean, default=False)
    maintenance_notifications = Column(Boolean, default=True)
    feature_announcements = Column(Boolean, default=True)
    beta_features_enabled = Column(Boolean, default=False)
    
    # Additional settings as JSON
    additional_settings = Column(JSON, nullable=True)