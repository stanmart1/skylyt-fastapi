from sqlalchemy import Column, String, Boolean, Text, JSON
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
    
    # Additional settings as JSON
    additional_settings = Column(JSON, nullable=True)