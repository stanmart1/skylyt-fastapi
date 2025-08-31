from typing import Optional
from sqlalchemy.orm import Session
from .base import PaymentGatewayBase
from .stripe_gateway import StripeGateway
from .paystack_gateway import PaystackGateway
from .flutterwave_gateway import FlutterwaveGateway
from .paypal_gateway import PayPalGateway
from app.models.settings import Settings

class PaymentGatewayFactory:
    """Factory class to create payment gateway instances"""
    
    @staticmethod
    def create_gateway(gateway_type: str, db: Session) -> Optional[PaymentGatewayBase]:
        """Create payment gateway instance based on type and settings"""
        
        # Get settings from database
        settings = db.query(Settings).first()
        if not settings:
            return None
        
        gateway_type = gateway_type.lower()
        
        if gateway_type == 'stripe':
            if not settings.stripe_public_key or not settings.stripe_secret_key:
                return None
            return StripeGateway(
                public_key=settings.stripe_public_key,
                secret_key=settings.stripe_secret_key,
                sandbox=True  # You can add a sandbox field to settings
            )
        
        elif gateway_type == 'paystack':
            if not settings.paystack_public_key or not settings.paystack_secret_key:
                return None
            return PaystackGateway(
                public_key=settings.paystack_public_key,
                secret_key=settings.paystack_secret_key,
                sandbox=True
            )
        
        elif gateway_type == 'flutterwave':
            if not settings.flutterwave_public_key or not settings.flutterwave_secret_key:
                return None
            return FlutterwaveGateway(
                public_key=settings.flutterwave_public_key,
                secret_key=settings.flutterwave_secret_key,
                sandbox=True
            )
        
        elif gateway_type == 'paypal':
            if not settings.paypal_client_id or not settings.paypal_client_secret:
                return None
            return PayPalGateway(
                public_key=settings.paypal_client_id,
                secret_key=settings.paypal_client_secret,
                sandbox=settings.paypal_sandbox
            )
        
        return None
    
    @staticmethod
    def get_available_gateways(db: Session) -> list:
        """Get list of available payment gateways based on configured keys"""
        settings = db.query(Settings).first()
        if not settings:
            return []
        
        available = []
        
        if settings.stripe_public_key and settings.stripe_secret_key:
            available.append('stripe')
        
        if settings.paystack_public_key and settings.paystack_secret_key:
            available.append('paystack')
        
        if settings.flutterwave_public_key and settings.flutterwave_secret_key:
            available.append('flutterwave')
        
        if settings.paypal_client_id and settings.paypal_client_secret:
            available.append('paypal')
        
        return available