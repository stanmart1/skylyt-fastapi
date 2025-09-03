from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.payment.gateway_factory import PaymentGatewayFactory
import json

router = APIRouter(prefix="/payment-webhooks", tags=["payment-webhooks"])

@router.post("/webhook/{gateway_type}")
async def payment_webhook(
    gateway_type: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle payment gateway webhooks"""
    try:
        # Get request body and headers
        body = await request.body()
        signature = request.headers.get('x-paystack-signature') or request.headers.get('verif-hash') or request.headers.get('stripe-signature')
        
        # Parse JSON payload
        payload = json.loads(body.decode('utf-8'))
        
        # Create gateway instance
        gateway = PaymentGatewayFactory.create_gateway(gateway_type, db)
        if not gateway:
            raise HTTPException(status_code=400, detail=f"Gateway {gateway_type} not configured")
        
        # Process webhook
        webhook_result = await gateway.process_webhook(payload, signature)
        
        if webhook_result.get('success') and webhook_result.get('event_type') == 'payment_succeeded':
            # Update payment status
            from app.models.payment import Payment, PaymentStatus
            
            transaction_id = webhook_result.get('transaction_id')
            payment = db.query(Payment).filter(Payment.transaction_id == transaction_id).first()
            
            if payment:
                payment.status = PaymentStatus.COMPLETED.value.value
                
                # Update booking status
                from app.models.booking import Booking
                booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
                if booking:
                    booking.status = 'confirmed'
                
                db.commit()
                
                return {'status': 'success', 'message': 'Payment confirmed'}
        
        return {'status': 'received'}
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@router.get("/gateways/available")
def get_available_gateways(db: Session = Depends(get_db)):
    """Get list of available payment gateways"""
    try:
        gateways = PaymentGatewayFactory.get_available_gateways(db)
        return {'gateways': gateways}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch available gateways")

@router.post("/verify-gateway/{gateway_type}")
async def verify_gateway_payment(
    gateway_type: str,
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """Manually verify payment with gateway"""
    try:
        gateway = PaymentGatewayFactory.create_gateway(gateway_type, db)
        if not gateway:
            raise HTTPException(status_code=400, detail=f"Gateway {gateway_type} not configured")
        
        verification_result = await gateway.verify_payment(transaction_id)
        
        if verification_result.get('success') and verification_result.get('paid'):
            # Update payment status
            from app.models.payment import Payment, PaymentStatus
            
            payment = db.query(Payment).filter(Payment.transaction_id == transaction_id).first()
            if payment:
                payment.status = PaymentStatus.COMPLETED.value
                
                # Update booking status
                from app.models.booking import Booking
                booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
                if booking:
                    booking.status = 'confirmed'
                
                db.commit()
        
        return verification_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")