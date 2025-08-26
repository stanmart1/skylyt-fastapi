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
    
    class Config:
        from_attributes = True