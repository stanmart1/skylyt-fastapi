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
    
    # Rate Limiting - General
    general_rate_limit_enabled = Column(Boolean, default=True)
    general_rate_limit_requests = Column(String(10), default="100")
    general_rate_limit_window = Column(String(10), default="60")
    
    # Rate Limiting - Authentication
    auth_rate_limit_enabled = Column(Boolean, default=True)
    auth_rate_limit_requests = Column(String(10), default="5")
    auth_rate_limit_window = Column(String(10), default="60")
    
    # Rate Limiting - Booking/Payment
    booking_rate_limit_enabled = Column(Boolean, default=True)
    booking_rate_limit_requests = Column(String(10), default="20")
    booking_rate_limit_window = Column(String(10), default="60")
    
    # Rate Limiting - Admin
    admin_rate_limit_enabled = Column(Boolean, default=True)
    admin_rate_limit_requests = Column(String(10), default="30")
    admin_rate_limit_window = Column(String(10), default="600")
    
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
    google_analytics_enabled = Column(Boolean, default=False)
    
    # Webhook secrets
    webhook_secret_stripe = Column(String(255), nullable=True)
    webhook_secret_paystack = Column(String(255), nullable=True)
    webhook_secret_flutterwave = Column(String(255), nullable=True)
    
    # Bank Transfer Settings
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