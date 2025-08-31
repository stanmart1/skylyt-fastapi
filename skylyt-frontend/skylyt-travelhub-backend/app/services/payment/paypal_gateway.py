import httpx
import base64
from typing import Dict, Any
from decimal import Decimal
from .base import PaymentGatewayBase

class PayPalGateway(PaymentGatewayBase):
    """PayPal payment gateway implementation"""
    
    def __init__(self, public_key: str, secret_key: str, sandbox: bool = True):
        super().__init__(public_key, secret_key, sandbox)
        self.base_url = "https://api.sandbox.paypal.com" if sandbox else "https://api.paypal.com"
        self.client_id = public_key
        self.client_secret = secret_key
    
    async def get_access_token(self) -> str:
        """Get PayPal access token"""
        try:
            credentials = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/oauth2/token",
                    headers={
                        "Authorization": f"Basic {credentials}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    data="grant_type=client_credentials"
                )
                
                data = response.json()
                return data.get('access_token', '')
        except Exception:
            return ''
    
    async def create_payment(self, amount: Decimal, currency: str, customer_email: str, 
                           booking_reference: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create PayPal payment"""
        try:
            access_token = await self.get_access_token()
            if not access_token:
                return {'success': False, 'error': 'Failed to get access token'}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v2/checkout/orders",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "intent": "CAPTURE",
                        "purchase_units": [{
                            "reference_id": booking_reference,
                            "amount": {
                                "currency_code": currency.upper(),
                                "value": str(amount)
                            },
                            "description": f"Skylyt booking payment - {booking_reference}"
                        }],
                        "application_context": {
                            "return_url": "https://skylyt.scaleitpro.com/payment/success",
                            "cancel_url": "https://skylyt.scaleitpro.com/payment/cancel"
                        }
                    }
                )
                
                data = response.json()
                
                if response.status_code == 201:
                    # Find approval URL
                    approval_url = ''
                    for link in data.get('links', []):
                        if link.get('rel') == 'approve':
                            approval_url = link.get('href', '')
                            break
                    
                    return {
                        'success': True,
                        'transaction_id': data['id'],
                        'approval_url': approval_url,
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
                'error_type': 'paypal_error'
            }
    
    async def verify_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Verify PayPal payment"""
        try:
            access_token = await self.get_access_token()
            if not access_token:
                return {'success': False, 'error': 'Failed to get access token'}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v2/checkout/orders/{transaction_id}",
                    headers={
                        "Authorization": f"Bearer {access_token}"
                    }
                )
                
                data = response.json()
                
                if response.status_code == 200:
                    status = data.get('status', '')
                    purchase_unit = data.get('purchase_units', [{}])[0]
                    amount_data = purchase_unit.get('amount', {})
                    
                    return {
                        'success': True,
                        'status': status,
                        'amount': float(amount_data.get('value', 0)),
                        'currency': amount_data.get('currency_code', ''),
                        'paid': status == 'COMPLETED'
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
        """Process PayPal webhook"""
        try:
            event_type = payload.get('event_type')
            resource = payload.get('resource', {})
            
            if event_type == 'CHECKOUT.ORDER.APPROVED':
                return {
                    'success': True,
                    'event_type': 'payment_succeeded',
                    'transaction_id': resource.get('id'),
                    'amount': float(resource.get('purchase_units', [{}])[0].get('amount', {}).get('value', 0)),
                    'currency': resource.get('purchase_units', [{}])[0].get('amount', {}).get('currency_code', ''),
                    'booking_reference': resource.get('purchase_units', [{}])[0].get('reference_id')
                }
            
            return {'success': True, 'event_type': 'unhandled'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_payment_url(self, payment_data: Dict[str, Any]) -> str:
        """Get PayPal payment URL"""
        return payment_data.get('approval_url', '')