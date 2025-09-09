from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.services.payment_service import PaymentService
from app.tasks.email_tasks import send_payment_confirmation_email
import logging
from decimal import Decimal
from typing import Optional
import os
from werkzeug.utils import secure_filename

router = APIRouter()
logger = logging.getLogger(__name__)

class ManualPaymentCreate(BaseModel):
    booking_id: int
    amount: float
    payment_method: str
    payment_reference: str
    notes: str = ""
    status: str = "completed"
    # Additional fields for different payment methods
    transfer_reference: Optional[str] = None
    transaction_id: Optional[str] = None
    gateway_reference: Optional[str] = None
    customer_email: Optional[str] = None

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

@router.post("/admin/payments/manual")
async def create_manual_payment(
    booking_id: int = Form(...),
    amount: float = Form(...),
    payment_method: str = Form(...),
    payment_reference: str = Form(...),
    status: str = Form("completed"),
    notes: str = Form(""),
    # Bank transfer specific fields
    transfer_reference: Optional[str] = Form(None),
    proof_of_payment: Optional[UploadFile] = File(None),
    # Gateway specific fields
    transaction_id: Optional[str] = Form(None),
    gateway_reference: Optional[str] = Form(None),
    customer_email: Optional[str] = Form(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create manual payment record for admin with file upload support"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.payment import Payment
        from app.models.booking import Booking
        
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Handle file upload for bank transfer
        proof_url = None
        if proof_of_payment and payment_method == 'bank_transfer':
            try:
                # Create upload directory if it doesn't exist
                upload_dir = "uploads/payment_proofs"
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generate secure filename
                filename = secure_filename(proof_of_payment.filename or "proof.jpg")
                file_path = os.path.join(upload_dir, f"{booking_id}_{filename}")
                
                # Save file
                with open(file_path, "wb") as buffer:
                    content = await proof_of_payment.read()
                    buffer.write(content)
                
                proof_url = file_path
            except Exception as e:
                logger.error(f"Failed to upload proof of payment: {e}")
        
        payment = Payment(
            booking_id=booking_id,
            amount=Decimal(str(amount)),
            currency=booking.currency,
            payment_method=payment_method,
            payment_reference=payment_reference,
            status=status,
            transaction_id=transaction_id or payment_reference,
            transfer_reference=transfer_reference,
            proof_of_payment_url=proof_url,
            customer_email=customer_email or booking.customer_email,
            gateway_response={'manual_entry': True, 'notes': notes, 'gateway_reference': gateway_reference}
        )
        
        db.add(payment)
        
        if status == "completed":
            booking.payment_status = "completed"
            booking.status = "confirmed"
        
        db.commit()
        db.refresh(payment)
        
        return {
            "message": "Manual payment record created successfully",
            "payment_id": payment.id,
            "booking_id": booking.id,
            "amount": float(payment.amount),
            "status": payment.status,
            "proof_uploaded": proof_url is not None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create manual payment: {e}")
        raise HTTPException(status_code=500, detail="Failed to create manual payment record")