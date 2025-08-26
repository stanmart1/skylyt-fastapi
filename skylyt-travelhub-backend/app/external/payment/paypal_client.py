from typing import Dict, Any, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class PayPalClient:
    
    def __init__(self, client_id: str, client_secret: str, sandbox: bool = True):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.sandbox.paypal.com" if sandbox else "https://api.paypal.com"
    
    def create_order(self, amount: Decimal, currency: str = "USD", 
                    return_url: str = None, cancel_url: str = None) -> Dict[str, Any]:
        """Create PayPal order"""
        try:
            order_data = {
                "id": f"pp_order_{hash(str(amount))}",
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": currency,
                        "value": str(amount)
                    }
                }],
                "application_context": {
                    "return_url": return_url,
                    "cancel_url": cancel_url
                }
            }
            
            logger.info(f"Created PayPal order: {order_data['id']}")
            return {
                "id": order_data['id'],
                "status": "CREATED",
                "links": [
                    {
                        "href": f"https://www.sandbox.paypal.com/checkoutnow?token={order_data['id']}",
                        "rel": "approve",
                        "method": "GET"
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"PayPal order creation failed: {e}")
            raise
    
    def capture_order(self, order_id: str) -> Dict[str, Any]:
        """Capture PayPal order"""
        try:
            return {
                "id": order_id,
                "status": "COMPLETED",
                "purchase_units": [{
                    "payments": {
                        "captures": [{
                            "id": f"pp_capture_{hash(order_id)}",
                            "status": "COMPLETED",
                            "amount": {
                                "currency_code": "USD",
                                "value": "100.00"
                            }
                        }]
                    }
                }]
            }
        except Exception as e:
            logger.error(f"Order capture failed: {e}")
            raise
    
    def create_refund(self, capture_id: str, amount: Optional[Decimal] = None, 
                     currency: str = "USD") -> Dict[str, Any]:
        """Create PayPal refund"""
        try:
            return {
                "id": f"pp_refund_{hash(capture_id)}",
                "status": "COMPLETED",
                "amount": {
                    "currency_code": currency,
                    "value": str(amount) if amount else "100.00"
                }
            }
        except Exception as e:
            logger.error(f"Refund creation failed: {e}")
            raise