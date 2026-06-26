from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Redis/Dragonfly
    DRAGONFLY_URL: str = "redis://localhost:6379/0"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Email
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: str = "noreply@skylytluxury.com"
    
    # Frontend URL
    FRONTEND_URL: str = "https://skylyt.scaleitpro.com"
    
    # External APIs
    STRIPE_SECRET_KEY: Optional[str] = None
    
    # Flutterwave
    FLUTTERWAVE_SECRET_KEY: Optional[str] = None
    FLUTTERWAVE_PUBLIC_KEY: Optional[str] = None
    
    # Paystack
    PAYSTACK_SECRET_KEY: Optional[str] = None
    PAYSTACK_PUBLIC_KEY: Optional[str] = None
    
    # PayPal
    PAYPAL_CLIENT_ID: Optional[str] = None
    PAYPAL_CLIENT_SECRET: Optional[str] = None
    PAYPAL_SANDBOX: bool = True
    
    # Travel APIs
    BOOKING_COM_API_KEY: Optional[str] = None
    EXPEDIA_API_KEY: Optional[str] = None
    HERTZ_API_KEY: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    
    # Resend Email API
    RESEND_API_KEY: Optional[str] = None
    
    # Exchange Rate API
    EXCHANGE_RATE_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()