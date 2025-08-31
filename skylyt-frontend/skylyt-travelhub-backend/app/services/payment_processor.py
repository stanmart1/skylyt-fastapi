from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from decimal import Decimal
from app.services.payment.gateway_factory import PaymentGatewayFactory
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.booking import Booking

class PaymentProcessor:
    """Service for processing payments with multiple gateways"""
    
    @staticmethod
    async def create_payment(
        db: Session,
        booking_id: int,
        payment_method: str,
        customer_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new payment with the specified gateway"""
        
        # Get booking
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return {'success': False, 'error': 'Booking not found'}
        
        # Create gateway
        gateway = PaymentGatewayFactory.create_gateway(payment_method, db)
        if not gateway:
            return {'success': False, 'error': f'Payment method {payment_method} not configured'}
        
        try:
            # Create payment with gateway
            payment_result = await gateway.create_payment(
                amount=booking.total_amount,
                currency=booking.currency or 'NGN',
                customer_email=customer_email or booking.customer_email or 'customer@example.com',
                booking_reference=booking.booking_reference,
                metadata={'booking_id': booking.id}
            )
            
            if not payment_result.get('success'):
                return payment_result
            
            # Save payment record
            payment = Payment(
                booking_id=booking.id,
                amount=booking.total_amount,
                currency=booking.currency or 'NGN',
                payment_method=payment_method,
                status=PaymentStatus.PENDING.value,
                transaction_id=payment_result.get('transaction_id'),
                gateway_response=payment_result,
                customer_email=customer_email or booking.customer_email
            )
            
            db.add(payment)
            db.commit()
            db.refresh(payment)
            
            return {
                'success': True,
                'payment_id': payment.id,
                'payment_url': gateway.get_payment_url(payment_result),
                'transaction_id': payment_result.get('transaction_id'),
                **payment_result
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    async def verify_payment(
        db: Session,
        payment_id: int
    ) -> Dict[str, Any]:
        """Verify payment status with gateway"""
        
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            return {'success': False, 'error': 'Payment not found'}
        
        gateway = PaymentGatewayFactory.create_gateway(payment.payment_method, db)
        if not gateway:
            return {'success': False, 'error': 'Payment gateway not configured'}
        
        try:
            verification_result = await gateway.verify_payment(payment.transaction_id)
            
            if verification_result.get('success'):
                # Update payment status based on verification
                if verification_result.get('paid'):
                    payment.status = PaymentStatus.COMPLETED.value
                    
                    # Update booking status
                    booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
                    if booking:
                        booking.status = 'confirmed'
                    
                    db.commit()
                
                return {
                    'success': True,
                    'payment_id': payment.id,
                    'status': payment.status,
                    'verified': verification_result.get('paid', False),
                    **verification_result
                }
            
            return verification_result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    async def process_webhook(
        db: Session,
        gateway_type: str,
        payload: Dict[str, Any],
        signature: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process webhook from payment gateway"""
        
        gateway = PaymentGatewayFactory.create_gateway(gateway_type, db)
        if not gateway:
            return {'success': False, 'error': 'Gateway not configured'}
        
        try:
            webhook_result = await gateway.process_webhook(payload, signature)
            
            if webhook_result.get('success') and webhook_result.get('event_type') == 'payment_succeeded':
                transaction_id = webhook_result.get('transaction_id')
                payment = db.query(Payment).filter(Payment.transaction_id == transaction_id).first()
                
                if payment:
                    payment.status = PaymentStatus.COMPLETED.value
                    
                    # Update booking status
                    booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
                    if booking:
                        booking.status = 'confirmed'
                    
                    db.commit()
                    
                    return {'success': True, 'message': 'Payment confirmed'}
            
            return webhook_result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_available_gateways(db: Session) -> Dict[str, Any]:
        """Get available payment gateways"""
        try:
            gateways = PaymentGatewayFactory.get_available_gateways(db)
            
            # Add gateway display information
            gateway_info = {
                'stripe': {'name': 'Stripe', 'description': 'Credit/Debit Cards'},
                'paystack': {'name': 'Paystack', 'description': 'Nigerian Payment Gateway'},
                'flutterwave': {'name': 'Flutterwave', 'description': 'African Payment Gateway'},
                'paypal': {'name': 'PayPal', 'description': 'PayPal Account'}
            }
            
            available_gateways = []
            for gateway in gateways:
                if gateway in gateway_info:
                    available_gateways.append({
                        'id': gateway,
                        **gateway_info[gateway]
                    })
            
            return {'success': True, 'gateways': available_gateways}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}