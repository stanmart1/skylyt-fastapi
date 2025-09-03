from celery import Celery
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.payment import Payment, PaymentStatus
from app.models.booking import Booking
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

celery_app = Celery(
    "skylyt_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

@celery_app.task(bind=True, max_retries=3)
def process_payment_verification(self, payment_id: int):
    """Background task to verify payment status"""
    db = SessionLocal()
    try:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            logger.error(f"Payment {payment_id} not found")
            return {"status": "error", "message": "Payment not found"}
        
        # Simulate payment verification logic
        if payment.status == PaymentStatus.PENDING:
            payment.status = PaymentStatus.COMPLETED
            
            # Update booking status
            booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
            if booking:
                booking.payment_status = "completed"
                booking.status = "confirmed"
            
            db.commit()
            
            # Trigger confirmation email
            from app.tasks.email_tasks import send_payment_confirmation_email
            send_payment_confirmation_email.delay({
                "user_email": payment.customer_email,
                "transaction_id": payment.transaction_id,
                "amount": float(payment.amount),
                "currency": payment.currency
            })
            
            logger.info(f"Payment {payment_id} verified successfully")
            return {"status": "success", "payment_id": payment_id}
        
    except Exception as e:
        logger.error(f"Payment verification failed for {payment_id}: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        raise
    finally:
        db.close()

@celery_app.task
def process_refund(payment_id: int, refund_amount: float, reason: str):
    """Background task to process payment refunds"""
    db = SessionLocal()
    try:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            return {"status": "error", "message": "Payment not found"}
        
        payment.refund_amount = refund_amount
        payment.refund_status = "processed"
        payment.refund_reason = reason
        
        db.commit()
        
        logger.info(f"Refund processed for payment {payment_id}: {refund_amount}")
        return {"status": "success", "refund_amount": refund_amount}
        
    except Exception as e:
        logger.error(f"Refund processing failed: {str(e)}")
        raise
    finally:
        db.close()

@celery_app.task
def check_pending_payments():
    """Periodic task to check and update pending payments"""
    db = SessionLocal()
    try:
        pending_payments = db.query(Payment).filter(
            Payment.status == PaymentStatus.PENDING
        ).all()
        
        processed_count = 0
        for payment in pending_payments:
            # Check payment status with provider
            process_payment_verification.delay(payment.id)
            processed_count += 1
        
        logger.info(f"Queued {processed_count} pending payments for verification")
        return {"processed": processed_count}
        
    except Exception as e:
        logger.error(f"Pending payments check failed: {str(e)}")
        raise
    finally:
        db.close()