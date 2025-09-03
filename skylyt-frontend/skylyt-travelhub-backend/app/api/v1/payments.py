from fastapi import APIRouter, Depends, HTTPException, Query, Response, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel
from pathlib import Path
import os
import uuid
import logging
from werkzeug.utils import secure_filename
from app.core.database import get_db
from app.services.payment_service import PaymentService
from app.services.payment.gateway_factory import PaymentGatewayFactory
from app.services.payment_processor import PaymentProcessor
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])
email_service = EmailService()

def get_payment_service() -> PaymentService:
    return PaymentService()

# Security constants
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/jpg', 'application/pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_upload_file(file: UploadFile) -> str:
    """Validate uploaded file and return secure filename"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Only JPEG, PNG, and PDF files are allowed."
        )
    
    # Validate file extension
    file_path = Path(file.filename)
    extension = file_path.suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file extension. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Use secure filename
    secure_name = secure_filename(file.filename)
    if not secure_name:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    return secure_name


class PaymentInitRequest(BaseModel):
    booking_id: int
    payment_method: str
    payment_reference: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    gateway: Optional[str] = None
    transfer_date: Optional[str] = None
    notes: Optional[str] = None


@router.post("/initialize")
async def initialize_payment(
    request: PaymentInitRequest,
    db: Session = Depends(get_db)
):
    """Initialize payment with selected method"""
    return await _process_payment_internal(request, db)

@router.post("/process")
async def process_payment(
    request: PaymentInitRequest,
    db: Session = Depends(get_db)
):
    """Process payment (alias for initialize for frontend compatibility)"""
    return await _process_payment_internal(request, db)

async def _process_payment_internal(
    request: PaymentInitRequest,
    db: Session = Depends(get_db)
):
    """Initialize payment with selected method"""
    try:
        # Get booking details
        from app.models.booking import Booking
        booking = db.query(Booking).filter(Booking.id == request.booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Use payment processor
        result = await PaymentProcessor.create_payment(
            db=db,
            booking_id=request.booking_id,
            payment_method=request.payment_method
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Payment creation failed'))
        
        # Send payment confirmation email if payment was successful
        if result.get('success') and result.get('payment_id'):
            try:
                email_service.send_payment_confirmation(
                    booking.customer_email,
                    {
                        "user_name": booking.customer_name,
                        "booking_reference": booking.booking_reference,
                        "payment_method": request.payment_method,
                        "amount": float(booking.total_amount),
                        "currency": booking.currency,
                        "transaction_id": result.get('transaction_id', 'N/A')
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to send payment confirmation email: {e}")
        
        return result
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment initialization failed: {str(e)}")


@router.post("/upload-proof")
async def upload_proof_of_payment(
    booking_id: int = Form(...),
    payment_reference: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Upload proof of payment for bank transfer"""
    try:
        # Validate file size
        if file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
        
        # Validate and get secure filename
        secure_name = validate_upload_file(file)
        
        # Validate booking exists first
        from app.models.booking import Booking
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail=f"Booking with ID {booking_id} not found")
        
        # Create secure upload directory
        upload_dir = Path("uploads/payment_proofs")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename with timestamp
        import time
        timestamp = int(time.time())
        file_extension = Path(secure_name).suffix
        unique_filename = f"{booking_id}_{timestamp}_{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename
        
        # Ensure file path is within upload directory (prevent path traversal)
        if not str(file_path.resolve()).startswith(str(upload_dir.resolve())):
            raise HTTPException(status_code=400, detail="Invalid file path")
        
        # Read and validate file content
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File content too large")
        
        # Save file securely
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Initialize payment with proof
        result = payment_service.initialize_payment(
            db, booking_id, "bank_transfer", 
            proof_file_url=str(file_path), 
            payment_reference=payment_reference
        )
        
        # Send payment proof upload confirmation email
        try:
            email_service.send_payment_confirmation(
                booking.customer_email,
                {
                    "user_name": booking.customer_name,
                    "booking_reference": booking.booking_reference,
                    "payment_method": "Bank Transfer",
                    "amount": float(booking.total_amount),
                    "currency": booking.currency,
                    "transaction_id": payment_reference,
                    "status": "Proof uploaded - pending verification"
                }
            )
        except Exception as e:
            logger.warning(f"Failed to send payment proof confirmation email: {e}")
        
        logger.info(f"Payment proof uploaded for booking {booking_id}")
        return {
            "success": True,
            "message": "Proof of payment uploaded successfully",
            "file_path": f"/uploads/payment_proofs/{unique_filename}",
            "payment_id": result.get("payment_id") if isinstance(result, dict) else None
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload error for booking {booking_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Upload failed")


@router.get("/verify/{payment_id}")
def verify_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Verify payment status"""
    try:
        result = payment_service.verify_payment(db, payment_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Payment verification failed for payment {payment_id}: {str(e)}")
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
    booking_type: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    amount_min: Optional[float] = Query(None),
    amount_max: Optional[float] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """List payments with filtering and pagination"""
    filters = {
        "status": status,
        "provider": provider,
        "booking_type": booking_type,
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
        logger.error(f"Failed to fetch payments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch payments")

@router.get("/hotel-payments")
def list_hotel_payments(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """List hotel payments only"""
    filters = {
        "status": status,
        "provider": provider,
        "booking_type": "hotel",
        "date_from": date_from,
        "date_to": date_to,
        "search": search
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    
    try:
        result = payment_service.list_payments(db, filters, page, per_page)
        return result
    except Exception as e:
        logger.error(f"Failed to fetch hotel payments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch hotel payments")

@router.get("/car-payments")
def list_car_payments(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """List car payments only"""
    filters = {
        "status": status,
        "provider": provider,
        "booking_type": "car",
        "date_from": date_from,
        "date_to": date_to,
        "search": search
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    
    try:
        result = payment_service.list_payments(db, filters, page, per_page)
        return result
    except Exception as e:
        logger.error(f"Failed to fetch car payments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch car payments")


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


@router.post("/complete/{booking_id}")
def complete_payment(
    booking_id: int,
    db: Session = Depends(get_db)
):
    """Complete payment process for bank transfer"""
    try:
        from app.models.booking import Booking
        from app.models.payment import Payment, PaymentStatus
        
        # Get booking
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Get payment for this booking
        payment = db.query(Payment).filter(Payment.booking_id == booking_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # Update payment status to processing (awaiting verification)
        payment.status = PaymentStatus.PROCESSING.value
        
        # Update booking status
        booking.status = "payment_pending"
        
        db.commit()
        
        return {
            "success": True,
            "message": "Payment completed successfully. Awaiting verification.",
            "booking_id": booking_id,
            "payment_status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to complete payment for booking {booking_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete payment")

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
        file_path = Path(payment.proof_of_payment_url)
        upload_dir = Path("uploads/payment_proofs")
        
        # Ensure file path is within upload directory (prevent path traversal)
        try:
            file_path.resolve().relative_to(upload_dir.resolve())
        except ValueError:
            logger.warning(f"Path traversal attempt detected for payment {payment_id}")
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=str(file_path),
            filename=file_path.name,
            media_type='application/octet-stream'
        )
    except HTTPException:
        raise
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except PermissionError:
        logger.error(f"Permission denied accessing file for payment {payment_id}")
        raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        logger.error(f"Error retrieving payment proof {payment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving file")