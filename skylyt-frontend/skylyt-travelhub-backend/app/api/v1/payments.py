from fastapi import APIRouter, Depends, HTTPException, Query, Response, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel
from app.core.database import get_db
from app.services.payment_service import PaymentService
import os
import uuid

router = APIRouter(prefix="/payments", tags=["payments"])
payment_service = PaymentService()


class PaymentInitRequest(BaseModel):
    booking_id: int
    payment_method: str
    payment_reference: Optional[str] = None


@router.post("/initialize")
def initialize_payment(
    request: PaymentInitRequest,
    db: Session = Depends(get_db)
):
    """Initialize payment with selected method"""
    try:
        result = payment_service.initialize_payment(
            db, request.booking_id, request.payment_method, 
            payment_reference=request.payment_reference
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Payment initialization failed")


@router.post("/upload-proof")
def upload_proof_of_payment(
    booking_id: int = Form(...),
    payment_reference: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload proof of payment for bank transfer"""
    try:
        # Validate booking exists first
        from app.models.booking import Booking
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail=f"Booking with ID {booking_id} not found")
        
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads/payment_proofs"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        # Initialize payment with proof
        result = payment_service.initialize_payment(
            db, booking_id, "bank_transfer", 
            proof_file_url=file_path, 
            payment_reference=payment_reference
        )
        
        return {
            "message": "Proof of payment uploaded successfully",
            "file_path": file_path,
            "payment_id": result["payment_id"]
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        print(f"Upload error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/verify/{payment_id}")
def verify_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    """Verify payment status"""
    try:
        result = payment_service.verify_payment(db, payment_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Payment verification failed")


@router.get("/booking/{booking_id}/status")
def get_payment_status(
    booking_id: int,
    db: Session = Depends(get_db)
):
    """Get payment status for booking"""
    from app.models.payment import Payment
    
    payment = db.query(Payment).filter(Payment.booking_id == booking_id).first()
    if not payment:
        return {"status": "no_payment"}
    
    return {
        "payment_id": payment.id,
        "status": payment.status,
        "method": payment.payment_method,
        "amount": payment.amount
    }


class RefundRequest(BaseModel):
    amount: float
    reason: str


class StatusUpdateRequest(BaseModel):
    status: str
    notes: Optional[str] = None


@router.get("/")
def list_payments(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    amount_min: Optional[float] = Query(None),
    amount_max: Optional[float] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List payments with filtering and pagination"""
    filters = {
        "status": status,
        "provider": provider,
        "date_from": date_from,
        "date_to": date_to,
        "amount_min": amount_min,
        "amount_max": amount_max,
        "search": search
    }
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    try:
        result = payment_service.list_payments(db, filters, page, per_page)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch payments")


@router.get("/stats")
def get_payment_stats(db: Session = Depends(get_db)):
    """Get payment statistics"""
    try:
        return payment_service.get_payment_stats(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch payment stats")


@router.get("/{payment_id}")
def get_payment_details(
    payment_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed payment information"""
    try:
        payment = payment_service.get_payment_details(db, payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        return payment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch payment details")


@router.post("/{payment_id}/verify")
def manual_verify_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    """Manually verify payment with provider"""
    try:
        result = payment_service.manual_verify_payment(db, payment_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Payment verification failed")


@router.post("/{payment_id}/refund")
def refund_payment(
    payment_id: int,
    refund_request: RefundRequest,
    db: Session = Depends(get_db)
):
    """Process payment refund"""
    try:
        result = payment_service.refund_payment(
            db, payment_id, refund_request.amount, refund_request.reason
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Refund processing failed")


@router.put("/{payment_id}/status")
def update_payment_status(
    payment_id: int,
    status_request: StatusUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update payment status manually"""
    try:
        result = payment_service.update_payment_status(
            db, payment_id, status_request.status, status_request.notes
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Status update failed")


@router.get("/export/csv")
def export_payments_csv(
    status: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Export payments to CSV"""
    filters = {
        "status": status,
        "provider": provider,
        "date_from": date_from,
        "date_to": date_to
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    
    try:
        csv_data = payment_service.export_payments(db, filters, "csv")
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=payments_export.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Export failed")


@router.get("/proof/{payment_id}")
def get_proof_of_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    """Get proof of payment file"""
    from fastapi.responses import FileResponse
    from app.models.payment import Payment
    
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment or not payment.proof_of_payment_url:
        raise HTTPException(status_code=404, detail="Proof of payment not found")
    
    try:
        return FileResponse(payment.proof_of_payment_url)
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")