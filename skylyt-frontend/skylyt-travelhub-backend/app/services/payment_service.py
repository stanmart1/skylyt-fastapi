from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, date
from app.models.payment import Payment, PaymentStatus
from app.models.booking import Booking
import csv
import io


class PaymentProviderInterface(ABC):
    @abstractmethod
    def initialize_payment(self, amount: float, currency: str, booking_id: int) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def verify_payment(self, payment_reference: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass


class StripeService(PaymentProviderInterface):
    def initialize_payment(self, amount: float, currency: str, booking_id: int) -> Dict[str, Any]:
        return {
            "payment_url": f"/stripe-checkout?booking_id={booking_id}&amount={amount}",
            "reference": f"stripe_{booking_id}_{amount}"
        }
    
    def verify_payment(self, payment_reference: str) -> Dict[str, Any]:
        return {"status": "completed", "transaction_id": payment_reference}
    
    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "processed"}


class FlutterwaveService(PaymentProviderInterface):
    def initialize_payment(self, amount: float, currency: str, booking_id: int) -> Dict[str, Any]:
        return {
            "payment_url": f"/flutterwave-checkout?booking_id={booking_id}&amount={amount}",
            "reference": f"flw_{booking_id}_{amount}"
        }
    
    def verify_payment(self, payment_reference: str) -> Dict[str, Any]:
        return {"status": "completed", "transaction_id": payment_reference}
    
    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "processed"}


class PaystackService(PaymentProviderInterface):
    def initialize_payment(self, amount: float, currency: str, booking_id: int) -> Dict[str, Any]:
        return {
            "payment_url": f"/paystack-checkout?booking_id={booking_id}&amount={amount}",
            "reference": f"ps_{booking_id}_{amount}"
        }
    
    def verify_payment(self, payment_reference: str) -> Dict[str, Any]:
        return {"status": "completed", "transaction_id": payment_reference}
    
    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "processed"}


class PaymentService:
    def __init__(self):
        self.providers = {
            "stripe": StripeService(),
            "flutterwave": FlutterwaveService(),
            "paystack": PaystackService()
        }
    
    def get_payment_stats(self, db: Session) -> Dict[str, Any]:
        total_payments = db.query(Payment).count()
        completed_payments = db.query(Payment).filter(Payment.status == "completed").count()
        pending_payments = db.query(Payment).filter(Payment.status == "pending").count()
        failed_payments = db.query(Payment).filter(Payment.status == "failed").count()
        
        total_amount = db.query(Payment).filter(Payment.status == "completed").with_entities(
            db.func.sum(Payment.amount)
        ).scalar() or 0
        
        return {
            "total_payments": total_payments,
            "completed_payments": completed_payments,
            "pending_payments": pending_payments,
            "failed_payments": failed_payments,
            "total_amount": float(total_amount)
        }
    
    def initialize_payment(self, db: Session, booking_id: int, payment_method: str, proof_file_url: str = None, payment_reference: str = None) -> Dict[str, Any]:
        from app.models.user import User
        from app.models.payment import PaymentMethod, PaymentStatus
        
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise ValueError("Booking not found")
        
        # Get user details for customer snapshot
        user = db.query(User).filter(User.id == booking.user_id).first()
        
        # For bank transfer, create payment with pending verification status
        if payment_method == "bank_transfer":
            payment = Payment(
                booking_id=booking_id,
                payment_method=PaymentMethod.BANK_TRANSFER,
                amount=booking.total_amount,
                currency=booking.currency,
                status=PaymentStatus.PENDING.value,
                proof_of_payment_url=proof_file_url,
                payment_reference=payment_reference,
                customer_name=f"{user.first_name} {user.last_name}" if user else booking.customer_name,
                customer_email=user.email if user else booking.customer_email
            )
            db.add(payment)
            
            # Update booking payment status
            booking.payment_status = "pending_verification"
            
            db.commit()
            db.refresh(payment)
            
            # Queue payment verification task
            from app.tasks.payment_tasks import process_payment_verification
            process_payment_verification.delay(payment.id)
            
            return {
                "payment_id": payment.id,
                "status": "pending",
                "reference": payment_reference,
                "success": True
            }
        
        provider = self.providers.get(payment_method)
        if not provider:
            raise ValueError("Unsupported payment method")
        
        # Create payment record for other methods
        payment = Payment(
            booking_id=booking_id,
            payment_method=getattr(PaymentMethod, payment_method.upper()),
            amount=booking.total_amount,
            currency=booking.currency,
            status=PaymentStatus.PENDING.value,
            customer_name=f"{user.first_name} {user.last_name}" if user else booking.customer_name,
            customer_email=user.email if user else booking.customer_email
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        # Initialize with provider
        result = provider.initialize_payment(booking.total_amount, booking.currency, booking_id)
        
        # Update payment with provider reference
        payment.transfer_reference = result["reference"]
        db.commit()
        
        return {
            "payment_id": payment.id,
            "payment_url": result["payment_url"],
            "reference": result["reference"]
        }
    
    def verify_payment(self, db: Session, payment_id: int) -> Dict[str, Any]:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError("Payment not found")
        
        provider = self.providers.get(payment.payment_method)
        result = provider.verify_payment(payment.transfer_reference)
        
        # Update payment status
        payment.status = result["status"]
        payment.transaction_id = result.get("transaction_id")
        
        # Update booking status if payment completed
        if result["status"] == "completed":
            payment.booking.status = "confirmed"
        
        db.commit()
        return {"status": payment.status}
    
    def list_payments(self, db: Session, filters: Dict[str, Any] = None, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        query = db.query(Payment).join(Booking)
        
        if filters:
            if filters.get('status'):
                query = query.filter(Payment.status == filters['status'])
            if filters.get('provider'):
                query = query.filter(Payment.payment_method == filters['provider'])
            if filters.get('booking_type'):
                query = query.filter(Booking.booking_type == filters['booking_type'])
            if filters.get('date_from'):
                query = query.filter(Payment.created_at >= filters['date_from'])
            if filters.get('date_to'):
                query = query.filter(Payment.created_at <= filters['date_to'])
            if filters.get('amount_min'):
                query = query.filter(Payment.amount >= filters['amount_min'])
            if filters.get('amount_max'):
                query = query.filter(Payment.amount <= filters['amount_max'])
            if filters.get('search'):
                search = f"%{filters['search']}%"
                query = query.filter(or_(
                    Payment.transfer_reference.ilike(search),
                    Payment.transaction_id.ilike(search),
                    Payment.payment_reference.ilike(search),
                    Booking.customer_name.ilike(search)
                ))
        
        total = query.count()
        payments = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Serialize payments with booking info
        serialized_payments = []
        for payment in payments:
            payment_dict = {
                "id": payment.id,
                "booking_id": payment.booking_id,
                "amount": float(payment.amount),
                "currency": payment.currency,
                "status": payment.status.value if hasattr(payment.status, 'value') else payment.status,
                "payment_method": payment.payment_method.value if hasattr(payment.payment_method, 'value') else payment.payment_method,
                "payment_reference": payment.payment_reference,
                "transaction_id": payment.transaction_id,
                "proof_of_payment_url": payment.proof_of_payment_url,
                "customer_name": payment.customer_name,
                "customer_email": payment.customer_email,
                "created_at": payment.created_at.isoformat() if payment.created_at else None,
                "updated_at": payment.updated_at.isoformat() if payment.updated_at else None,
                "booking": {
                    "booking_reference": payment.booking.booking_reference,
                    "booking_type": payment.booking.booking_type,
                    "hotel_name": payment.booking.hotel_name,
                    "car_name": payment.booking.car_name,
                    "customer_name": payment.booking.customer_name
                }
            }
            serialized_payments.append(payment_dict)
        
        return {
            "payments": serialized_payments,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
    
    def get_payment_details(self, db: Session, payment_id: int) -> Optional[Payment]:
        return db.query(Payment).filter(Payment.id == payment_id).first()
    
    def manual_verify_payment(self, db: Session, payment_id: int) -> Dict[str, Any]:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError("Payment not found")
        
        provider = self.providers.get(payment.payment_method)
        if provider:
            result = provider.verify_payment(payment.transfer_reference)
            payment.status = result["status"]
            payment.transaction_id = result.get("transaction_id")
            
            if result["status"] == "completed":
                payment.booking.status = "confirmed"
            
            db.commit()
            return {"status": payment.status, "verified": True}
        
        return {"status": payment.status, "verified": False}
    
    def refund_payment(self, db: Session, payment_id: int, amount: float, reason: str) -> Dict[str, Any]:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError("Payment not found")
        
        if payment.status != "completed":
            raise ValueError("Can only refund completed payments")
        
        # Create refund record (simplified - in real implementation would call provider API)
        refund_data = {
            "amount": amount,
            "reason": reason,
            "date": datetime.utcnow(),
            "status": "processed"
        }
        
        # Update payment metadata
        if not payment.gateway_response:
            payment.gateway_response = {}
        
        if "refunds" not in payment.gateway_response:
            payment.gateway_response["refunds"] = []
        
        payment.gateway_response["refunds"].append(refund_data)
        
        # Update payment status if fully refunded
        total_refunded = sum(r["amount"] for r in payment.gateway_response["refunds"])
        if total_refunded >= payment.amount:
            payment.status = "refunded"
            payment.booking.status = "cancelled"
        
        db.commit()
        return refund_data
    
    def update_payment_status(self, db: Session, payment_id: int, status: str, notes: str = None) -> Dict[str, Any]:
        from app.models.payment import PaymentStatus
        
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError("Payment not found")
        
        old_status = payment.status
        
        # Convert string status to enum if needed
        if isinstance(status, str):
            try:
                payment.status = PaymentStatus(status)
            except ValueError:
                # Fallback for string values
                payment.status = status
        else:
            payment.status = status
        
        if notes:
            if not payment.gateway_response:
                payment.gateway_response = {}
            payment.gateway_response["admin_notes"] = notes
        
        # Update booking status based on payment status
        if status in ["completed", PaymentStatus.COMPLETED]:
            payment.booking.status = "confirmed"
            payment.booking.payment_status = "completed"
        elif status in ["failed", "cancelled", "refunded", PaymentStatus.FAILED]:
            payment.booking.status = "cancelled"
            payment.booking.payment_status = "failed"
        elif status in ["pending", PaymentStatus.PENDING]:
            payment.booking.payment_status = "pending_verification"
        
        db.commit()
        return {
            "old_status": old_status.value if hasattr(old_status, 'value') else old_status,
            "new_status": payment.status.value if hasattr(payment.status, 'value') else payment.status
        }
    
    def export_payments(self, db: Session, filters: Dict[str, Any] = None, format: str = "csv") -> str:
        query = db.query(Payment).join(Booking)
        
        if filters:
            if filters.get('status'):
                query = query.filter(Payment.status == filters['status'])
            if filters.get('provider'):
                query = query.filter(Payment.payment_method == filters['provider'])
            if filters.get('date_from'):
                query = query.filter(Payment.created_at >= filters['date_from'])
            if filters.get('date_to'):
                query = query.filter(Payment.created_at <= filters['date_to'])
        
        payments = query.all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow([
            'Payment ID', 'Booking ID', 'Guest Name', 'Provider', 'Amount', 
            'Currency', 'Status', 'Transaction ID', 'Created At', 'Updated At'
        ])
        
        # Data
        for payment in payments:
            writer.writerow([
                payment.id,
                payment.booking_id,
                payment.booking.guest_name,
                payment.payment_method,
                payment.amount,
                payment.currency,
                payment.status,
                payment.transaction_id or '',
                payment.created_at.isoformat() if payment.created_at else '',
                payment.updated_at.isoformat() if payment.updated_at else ''
            ])
        
        return output.getvalue()