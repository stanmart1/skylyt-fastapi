from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.services.payment_service import PaymentService
from app.tasks.email_tasks import send_payment_confirmation_email
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.put("/admin/payments/{payment_id}/verify")
async def verify_payment_admin(
    payment_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin verify payment and send confirmation email"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.payment import Payment, PaymentStatus
        from app.models.booking import Booking
        
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Associated booking not found")
        
        # Update payment status to completed
        payment.status = PaymentStatus.COMPLETED.value
        
        # Update booking status to confirmed
        booking.status = "confirmed"
        booking.payment_status = "completed"
        
        db.commit()
        
        # Send payment verification confirmation email
        try:
            send_payment_confirmation_email.delay({
                "user_email": booking.customer_email,
                "user_name": booking.customer_name,
                "booking_reference": booking.booking_reference,
                "payment_method": payment.payment_method,
                "amount": float(payment.amount),
                "currency": payment.currency,
                "transaction_id": payment.transaction_id or payment.payment_reference or "N/A",
                "status": "Payment verified and confirmed"
            })
        except Exception as e:
            logger.warning(f"Failed to send payment verification email: {e}")
        
        return {
            "message": "Payment verified successfully",
            "payment_id": payment_id,
            "booking_id": booking.id,
            "status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to verify payment {payment_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify payment")

@router.put("/admin/payments/{payment_id}/reject")
async def reject_payment_admin(
    payment_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin reject payment and send notification email"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.payment import Payment, PaymentStatus
        from app.models.booking import Booking
        
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Associated booking not found")
        
        # Update payment status to failed
        payment.status = PaymentStatus.FAILED.value
        
        # Update booking status back to pending
        booking.status = "pending"
        booking.payment_status = "failed"
        
        db.commit()
        
        # Send payment rejection notification email
        try:
            send_payment_confirmation_email.delay({
                "user_email": booking.customer_email,
                "user_name": booking.customer_name,
                "booking_reference": booking.booking_reference,
                "payment_method": payment.payment_method,
                "amount": float(payment.amount),
                "currency": payment.currency,
                "transaction_id": payment.transaction_id or payment.payment_reference or "N/A",
                "status": "Payment rejected - please contact support or try again"
            })
        except Exception as e:
            logger.warning(f"Failed to send payment rejection email: {e}")
        
        return {
            "message": "Payment rejected successfully",
            "payment_id": payment_id,
            "booking_id": booking.id,
            "status": "failed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to reject payment {payment_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to reject payment")