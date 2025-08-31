import httpx
import hashlib
from typing import Dict, Any
from decimal import Decimal
from .base import PaymentGatewayBase

class FlutterwaveGateway(PaymentGatewayBase):
    """Flutterwave payment gateway implementation"""
    
    def __init__(self, public_key: str, secret_key: str, sandbox: bool = True):
        super().__init__(public_key, secret_key, sandbox)
        self.base_url = "https://api.flutterwave.com/v3"
    
    async def create_payment(self, amount: Decimal, currency: str, customer_email: str, 
                           booking_reference: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create Flutterwave payment"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/payments",
                    headers={
                        "Authorization": f"Bearer {self.secret_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "tx_ref": booking_reference,
                        "amount": str(amount),
                        "currency": currency.upper(),
                        "redirect_url": "https://skylyt.scaleitpro.com/payment/callback",
                        "customer": {
                            "email": customer_email
                        },
                        "customizations": {
                            "title": "Skylyt Booking Payment",
                            "description": f"Payment for booking {booking_reference}"
                        },
                        "meta": metadata or {}
                    }
                )
                
                data = response.json()
                
                if data.get('status') == 'success':
                    return {
                        'success': True,
                        'transaction_id': booking_reference,
                        'payment_link': data['data']['link'],
                        'amount': float(amount),
                        'currency': currency
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('message', 'Payment creation failed')
                    }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'flutterwave_error'
            }
    
    async def verify_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Verify Flutterwave payment"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/transactions/verify_by_reference",
                    headers={
                        "Authorization": f"Bearer {self.secret_key}"
                    },
                    params={"tx_ref": transaction_id}
                )
                
                data = response.json()
                
                if data.get('status') == 'success':
                    transaction = data['data']
                    return {
                        'success': True,
                        'status': transaction['status'],
                        'amount': float(transaction['amount']),
                        'currency': transaction['currency'],
                        'paid': transaction['status'] == 'successful'
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('message', 'Verification failed')
                    }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def process_webhook(self, payload: Dict[str, Any], signature: str = None) -> Dict[str, Any]:
        """Process Flutterwave webhook"""
        try:
            # Verify webhook signature if provided
            if signature:
                computed_signature = hashlib.sha256(
                    (str(payload) + self.secret_key).encode('utf-8')
                ).hexdigest()
                
                if signature != computed_signature:
                    return {'success': False, 'error': 'Invalid signature'}
            
            event = payload.get('event')
            data = payload.get('data', {})
            
            if event == 'charge.completed' and data.get('status') == 'successful':
                return {
                    'success': True,
                    'event_type': 'payment_succeeded',
                    'transaction_id': data.get('tx_ref'),
                    'amount': float(data.get('amount', 0)),
                    'currency': data.get('currency'),
                    'booking_reference': data.get('tx_ref')
                }
            
            return {'success': True, 'event_type': 'unhandled'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_payment_url(self, payment_data: Dict[str, Any]) -> str:
        """Get Flutterwave payment URL"""
        return payment_data.get('payment_link', '')