import stripe
import httpx
from typing import Dict, Any
from decimal import Decimal
from .base import PaymentGatewayBase

class StripeGateway(PaymentGatewayBase):
    """Stripe payment gateway implementation"""
    
    def __init__(self, public_key: str, secret_key: str, sandbox: bool = True):
        super().__init__(public_key, secret_key, sandbox)
        stripe.api_key = self.secret_key
    
    async def create_payment(self, amount: Decimal, currency: str, customer_email: str, 
                           booking_reference: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create Stripe payment intent"""
        try:
            # Convert amount to cents for Stripe
            amount_cents = int(amount * 100)
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                receipt_email=customer_email,
                metadata={
                    'booking_reference': booking_reference,
                    **(metadata or {})
                }
            )
            
            return {
                'success': True,
                'transaction_id': payment_intent.id,
                'client_secret': payment_intent.client_secret,
                'amount': float(amount),
                'currency': currency,
                'status': payment_intent.status
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'stripe_error'
            }
    
    async def verify_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Verify Stripe payment"""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(transaction_id)
            
            return {
                'success': True,
                'status': payment_intent.status,
                'amount': payment_intent.amount / 100,
                'currency': payment_intent.currency.upper(),
                'paid': payment_intent.status == 'succeeded'
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def process_webhook(self, payload: Dict[str, Any], signature: str = None) -> Dict[str, Any]:
        """Process Stripe webhook"""
        try:
            event = payload
            
            if event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                return {
                    'success': True,
                    'event_type': 'payment_succeeded',
                    'transaction_id': payment_intent['id'],
                    'amount': payment_intent['amount'] / 100,
                    'currency': payment_intent['currency'].upper(),
                    'booking_reference': payment_intent.get('metadata', {}).get('booking_reference')
                }
            
            return {'success': True, 'event_type': 'unhandled'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_payment_url(self, payment_data: Dict[str, Any]) -> str:
        """Stripe uses client-side integration, return client secret"""
        return payment_data.get('client_secret', '')