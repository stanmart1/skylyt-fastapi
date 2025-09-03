from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.utils.serializers import serialize_payment
from app.schemas.payment import PaymentUpdateRequest, RefundRequest

router = APIRouter()
DEFAULT_COMMISSION_RATE = 10.0

# Routes
@router.get("/admin/payments")
async def get_admin_payments(
    page: int = 1,
    per_page: int = 20,
    current_user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Get paginated payments for admin"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.payment import Payment
        offset = (page - 1) * per_page
        payments = db.query(Payment).offset(offset).limit(per_page).all()
        total = db.query(Payment).count()
        
        return {
            "payments": [serialize_payment(payment) for payment in payments],
            "total": total,
            "page": page,
            "per_page": per_page
        }
    except ImportError:
        return {"payments": [], "total": 0, "page": page, "per_page": per_page}

@router.get("/admin/payments/{payment_id}")
async def get_admin_payment(payment_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get single payment for admin"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.payment import Payment
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        return {
            "id": payment.id,
            "booking_id": payment.booking_id,
            "amount": float(payment.amount),
            "currency": payment.currency,
            "status": payment.status.value,
            "payment_method": payment.payment_method.value,
            "created_at": payment.created_at.isoformat(),
            "transaction_id": payment.transaction_id,
            "transfer_reference": payment.transfer_reference,
            "gateway_response": payment.gateway_response
        }
    except ImportError:
        raise HTTPException(status_code=404, detail="Payment not found")

@router.put("/admin/payments/{payment_id}")
async def update_payment(payment_id: int, payment_data: PaymentUpdateRequest, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update payment details (admin)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.payment import Payment, PaymentStatus
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        if payment_data.status:
            try:
                # Validate status value before assignment
                valid_statuses = [status.value for status in PaymentStatus]
                if payment_data.status in valid_statuses:
                    payment.status = PaymentStatus(payment_data.status)
                else:
                    raise HTTPException(status_code=400, detail="Invalid payment status")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid payment status")
        
        if payment_data.transaction_id:
            payment.transaction_id = payment_data.transaction_id
        
        db.commit()
        db.refresh(payment)
        
        return {
            "id": payment.id,
            "message": "Payment updated successfully",
            "status": payment.status.value
        }
    except ImportError:
        raise HTTPException(status_code=404, detail="Payment system not available")

@router.post("/admin/payments/{payment_id}/verify")
async def verify_payment(payment_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Verify payment for admin"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.payment import Payment, PaymentStatus
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        payment.status = PaymentStatus.COMPLETED
        db.commit()
        return {"message": "Payment verified", "payment_id": payment_id, "status": "completed"}
    except ImportError:
        raise HTTPException(status_code=404, detail="Payment system not available")

@router.delete("/admin/payments/{payment_id}")
async def delete_payment(payment_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete payment (admin only)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.payment import Payment
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        db.delete(payment)
        db.commit()
        
        return {"message": "Payment deleted successfully"}
    except ImportError:
        raise HTTPException(status_code=404, detail="Payment system not available")

@router.post("/admin/payments/{payment_id}/refund")
async def process_refund(payment_id: int, refund_data: RefundRequest, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Process payment refund"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.payment import Payment, PaymentStatus
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        payment.status = PaymentStatus.REFUNDED
        db.commit()
        return {"message": "Refund processed successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to process refund")

@router.get("/admin/payments/export")
async def export_payments(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Export payments to CSV"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.payment import Payment
        payments = db.query(Payment).all()
        
        # Create CSV content
        csv_content = "ID,Booking ID,Amount,Currency,Status,Payment Method,Created At\n"
        for payment in payments:
            csv_content += f"{payment.id},{payment.booking_id},{payment.amount},{payment.currency},{payment.status.value},{payment.payment_method.value},{payment.created_at}\n"
        
        return {"csv": csv_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to export payments")

@router.get("/admin/payments/{payment_id}/commission")
async def get_payment_commission(payment_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get payment commission details"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.models.payment import Payment
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # Calculate commission
        commission_rate = DEFAULT_COMMISSION_RATE
        commission_amount = float(payment.amount) * (commission_rate / 100)
        
        return {
            "commission_amount": commission_amount,
            "commission_rate": commission_rate,
            "currency": payment.currency
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get commission details")