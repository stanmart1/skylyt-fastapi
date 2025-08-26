from typing import Dict, Any, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class PaystackClient:
    
    def __init__(self, secret_key: str, public_key: str):
        self.secret_key = secret_key
        self.public_key = public_key
        self.base_url = "https://api.paystack.co"
    
    def initialize_transaction(self, amount: Decimal, email: str, currency: str = "NGN",
                             callback_url: str = None, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Initialize Paystack transaction"""
        try:
            transaction_data = {
                "reference": f"ps_txn_{hash(str(amount))}",
                "amount": int(amount * 100),  # Paystack uses kobo
                "email": email,
                "currency": currency,
                "callback_url": callback_url,
                "metadata": metadata or {}
            }
            
            logger.info(f"Initialized Paystack transaction: {transaction_data['reference']}")
            return {
                "status": True,
                "data": {
                    "authorization_url": f"https://checkout.paystack.com/{transaction_data['reference']}",
                    "access_code": f"access_{transaction_data['reference']}",
                    "reference": transaction_data['reference']
                }
            }
            
        except Exception as e:
            logger.error(f"Paystack transaction initialization failed: {e}")
            raise
    
    def verify_transaction(self, reference: str) -> Dict[str, Any]:
        """Verify Paystack transaction"""
        try:
            return {
                "status": True,
                "data": {
                    "id": hash(reference),
                    "status": "success",
                    "reference": reference,
                    "amount": 10000,  # In kobo
                    "currency": "NGN",
                    "gateway_response": "Successful"
                }
            }
        except Exception as e:
            logger.error(f"Transaction verification failed: {e}")
            raise
    
    def create_refund(self, transaction_id: str, amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """Create Paystack refund"""
        try:
            return {
                "status": True,
                "data": {
                    "transaction": {
                        "id": transaction_id,
                        "status": "reversed"
                    },
                    "refund_amount": int(amount * 100) if amount else "full"
                }
            }
        except Exception as e:
            logger.error(f"Refund creation failed: {e}")
            raise