import httpx
import hashlib
import hmac
from typing import Dict, Any
from decimal import Decimal
from .base import PaymentGatewayBase

class PaystackGateway(PaymentGatewayBase):
    """Paystack payment gateway implementation"""
    
    def __init__(self, public_key: str, secret_key: str, sandbox: bool = True):
        super().__init__(public_key, secret_key, sandbox)
        self.base_url = "https://api.paystack.co"
    
    async def create_payment(self, amount: Decimal, currency: str, customer_email: str, 
                           booking_reference: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create Paystack transaction"""
        try:
            # Convert amount to kobo for NGN or cents for other currencies
            amount_kobo = int(amount * 100)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/transaction/initialize",
                    headers={
                        "Authorization": f"Bearer {self.secret_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "amount": amount_kobo,
                        "currency": currency.upper(),
                        "email": customer_email,
                        "reference": booking_reference,
                        "metadata": metadata or {}
                    }
                )
                
                data = response.json()
                
                if data.get('status'):
                    return {
                        'success': True,
                        'transaction_id': data['data']['reference'],
                        'authorization_url': data['data']['authorization_url'],
                        'access_code': data['data']['access_code'],
                        'amount': float(amount),
                        'currency': currency
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('message', 'Transaction initialization failed')
                    }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'paystack_error'
            }
    
    async def verify_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Verify Paystack payment"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/transaction/verify/{transaction_id}",
                    headers={
                        "Authorization": f"Bearer {self.secret_key}"
                    }
                )
                
                data = response.json()
                
                if data.get('status'):
                    transaction = data['data']
                    return {
                        'success': True,
                        'status': transaction['status'],
                        'amount': transaction['amount'] / 100,
                        'currency': transaction['currency'],
                        'paid': transaction['status'] == 'success'
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
        """Process Paystack webhook"""
        try:
            # Verify webhook signature
            if signature:
                computed_signature = hmac.new(
                    self.secret_key.encode('utf-8'),
                    str(payload).encode('utf-8'),
                    hashlib.sha512
                ).hexdigest()
                
                if not hmac.compare_digest(signature, computed_signature):
                    return {'success': False, 'error': 'Invalid signature'}
            
            event = payload.get('event')
            data = payload.get('data', {})
            
            if event == 'charge.success':
                return {
                    'success': True,
                    'event_type': 'payment_succeeded',
                    'transaction_id': data.get('reference'),
                    'amount': data.get('amount', 0) / 100,
                    'currency': data.get('currency'),
                    'booking_reference': data.get('reference')
                }
            
            return {'success': True, 'event_type': 'unhandled'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_payment_url(self, payment_data: Dict[str, Any]) -> str:
        """Get Paystack payment URL"""
        return payment_data.get('authorization_url', '')