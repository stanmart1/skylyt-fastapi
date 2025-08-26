from typing import Union
from .stripe_client import StripeClient
from .flutterwave_client import FlutterwaveClient
from .paystack_client import PaystackClient
from .paypal_client import PayPalClient
from .bank_transfer_client import BankTransferClient
from app.core.config import settings


class PaymentFactory:
    """Factory class to create payment gateway clients"""
    
    @staticmethod
    def create_client(gateway: str) -> Union[StripeClient, FlutterwaveClient, PaystackClient, PayPalClient, BankTransferClient]:
        """Create payment gateway client based on gateway type"""
        
        if gateway.lower() == "stripe":
            return StripeClient(settings.STRIPE_SECRET_KEY)
        
        elif gateway.lower() == "flutterwave":
            return FlutterwaveClient(
                settings.FLUTTERWAVE_SECRET_KEY,
                settings.FLUTTERWAVE_PUBLIC_KEY
            )
        
        elif gateway.lower() == "paystack":
            return PaystackClient(
                settings.PAYSTACK_SECRET_KEY,
                settings.PAYSTACK_PUBLIC_KEY
            )
        
        elif gateway.lower() == "paypal":
            return PayPalClient(
                settings.PAYPAL_CLIENT_ID,
                settings.PAYPAL_CLIENT_SECRET,
                sandbox=settings.PAYPAL_SANDBOX
            )
        
        elif gateway.lower() == "bank_transfer":
            return BankTransferClient()
        
        else:
            raise ValueError(f"Unsupported payment gateway: {gateway}")
    
    @staticmethod
    def get_supported_gateways() -> list:
        """Get list of supported payment gateways"""
        return ["stripe", "flutterwave", "paystack", "paypal", "bank_transfer"]