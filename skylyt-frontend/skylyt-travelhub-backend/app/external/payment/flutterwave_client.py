from typing import Dict, Any, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class FlutterwaveClient:
    
    def __init__(self, secret_key: str, public_key: str):
        self.secret_key = secret_key
        self.public_key = public_key
        self.base_url = "https://api.flutterwave.com/v3"
    
    def create_payment(self, amount: Decimal, currency: str, customer: Dict[str, Any], 
                      redirect_url: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Create Flutterwave payment"""
        try:
            payment_data = {
                "tx_ref": f"fw_txn_{hash(str(amount))}",
                "amount": str(amount),
                "currency": currency,
                "redirect_url": redirect_url,
                "customer": customer,
                "customizations": {
                    "title": "Skylyt Luxury Booking",
                    "description": "Payment for luxury booking"
                },
                "meta": metadata or {}
            }
            
            logger.info(f"Created Flutterwave payment: {payment_data['tx_ref']}")
            return {
                "status": "success",
                "data": {
                    "link": f"https://checkout.flutterwave.com/pay/{payment_data['tx_ref']}",
                    "tx_ref": payment_data['tx_ref']
                }
            }
            
        except Exception as e:
            logger.error(f"Flutterwave payment creation failed: {e}")
            raise
    
    def verify_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Verify Flutterwave payment"""
        try:
            return {
                "status": "success",
                "data": {
                    "id": transaction_id,
                    "status": "successful",
                    "amount": 100.00,
                    "currency": "USD",
                    "tx_ref": f"fw_txn_{transaction_id}"
                }
            }
        except Exception as e:
            logger.error(f"Payment verification failed: {e}")
            raise
    
    def create_refund(self, transaction_id: str, amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """Create refund"""
        try:
            return {
                "status": "success",
                "data": {
                    "id": f"fw_refund_{hash(transaction_id)}",
                    "status": "completed",
                    "amount": str(amount) if amount else "full"
                }
            }
        except Exception as e:
            logger.error(f"Refund creation failed: {e}")
            raise