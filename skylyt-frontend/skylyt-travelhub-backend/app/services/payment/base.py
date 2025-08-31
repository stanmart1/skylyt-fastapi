from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from decimal import Decimal

class PaymentGatewayBase(ABC):
    """Base class for all payment gateways"""
    
    def __init__(self, public_key: str, secret_key: str, sandbox: bool = True):
        self.public_key = public_key
        self.secret_key = secret_key
        self.sandbox = sandbox
    
    @abstractmethod
    async def create_payment(self, amount: Decimal, currency: str, customer_email: str, 
                           booking_reference: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a payment intent/transaction"""
        pass
    
    @abstractmethod
    async def verify_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Verify payment status"""
        pass
    
    @abstractmethod
    async def process_webhook(self, payload: Dict[str, Any], signature: str = None) -> Dict[str, Any]:
        """Process webhook from payment gateway"""
        pass
    
    @abstractmethod
    def get_payment_url(self, payment_data: Dict[str, Any]) -> str:
        """Get payment URL for redirect"""
        pass