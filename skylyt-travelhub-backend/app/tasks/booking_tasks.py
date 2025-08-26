from celery import Celery
from typing import Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.booking import Booking
from app.models.payment import Payment
from app.services.booking_service import BookingService
from app.tasks.email_tasks import celery_app, send_booking_confirmation_email
from app.utils.logger import get_logger

logger = get_logger(__name__)

@celery_app.task(bind=True, max_retries=3)
def process_booking_confirmation(self, booking_id: int):
    """Process booking confirmation after payment"""
    try:
        db = next(get_db())
        booking_service = BookingService(db)
        
        # Get booking details
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise Exception(f"Booking {booking_id} not found")
        
        # Update booking status to confirmed
        booking.status = "confirmed"
        booking.confirmed_at = datetime.utcnow()
        db.commit()
        
        # Prepare email data
        booking_data = {
            "booking_reference": booking.booking_reference,
            "user_email": booking.user.email,
            "user_name": booking.user.full_name,
            "booking_type": booking.booking_type,
            "check_in_date": booking.check_in_date.isoformat() if booking.check_in_date else None,
            "check_out_date": booking.check_out_date.isoformat() if booking.check_out_date else None,
            "total_amount": float(booking.total_amount),
            "currency": booking.currency,
            "hotel_name": booking.hotel_name,
            "room_type": booking.room_type,
            "guests": booking.guests,
        }
        
        # Send confirmation email
        send_booking_confirmation_email.delay(booking_data)
        
        logger.info(f"Booking {booking_id} confirmed successfully")
        return {"status": "confirmed", "booking_id": booking_id}
        
    except Exception as e:
        logger.error(f"Booking confirmation failed for {booking_id}: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        raise

@celery_app.task
def check_pending_bookings():
    """Check for bookings that are pending payment for too long"""
    try:
        db = next(get_db())
        
        # Find bookings pending for more than 30 minutes
        cutoff_time = datetime.utcnow() - timedelta(minutes=30)
        
        pending_bookings = db.query(Booking).filter(
            Booking.status == "pending",
            Booking.created_at < cutoff_time
        ).all()
        
        cancelled_count = 0
        for booking in pending_bookings:
            booking.status = "cancelled"
            booking.cancelled_at = datetime.utcnow()
            booking.cancellation_reason = "Payment timeout"
            cancelled_count += 1
        
        db.commit()
        
        logger.info(f"Cancelled {cancelled_count} expired bookings")
        return {"cancelled_bookings": cancelled_count}
        
    except Exception as e:
        logger.error(f"Failed to check pending bookings: {str(e)}")
        raise

@celery_app.task
def send_booking_reminders():
    """Send reminders for upcoming bookings"""
    try:
        db = next(get_db())
        
        # Find bookings with check-in tomorrow
        tomorrow = datetime.utcnow().date() + timedelta(days=1)
        
        upcoming_bookings = db.query(Booking).filter(
            Booking.status == "confirmed",
            Booking.check_in_date == tomorrow
        ).all()
        
        reminder_count = 0
        for booking in upcoming_bookings:
            # Send reminder email (implement template)
            booking_data = {
                "booking_reference": booking.booking_reference,
                "user_email": booking.user.email,
                "user_name": booking.user.full_name,
                "hotel_name": booking.hotel_name,
                "check_in_date": booking.check_in_date.isoformat(),
                "check_out_date": booking.check_out_date.isoformat(),
            }
            
            # You would create a send_booking_reminder_email task
            # send_booking_reminder_email.delay(booking_data)
            reminder_count += 1
        
        logger.info(f"Sent {reminder_count} booking reminders")
        return {"reminders_sent": reminder_count}
        
    except Exception as e:
        logger.error(f"Failed to send booking reminders: {str(e)}")
        raise

@celery_app.task(bind=True, max_retries=3)
def process_booking_cancellation(self, booking_id: int, cancellation_reason: str = None):
    """Process booking cancellation"""
    try:
        db = next(get_db())
        
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise Exception(f"Booking {booking_id} not found")
        
        # Update booking status
        booking.status = "cancelled"
        booking.cancelled_at = datetime.utcnow()
        booking.cancellation_reason = cancellation_reason or "User requested"
        
        # Process refund if applicable
        if booking.payment and booking.payment.status == "completed":
            # Calculate refund amount based on cancellation policy
            refund_amount = calculate_refund_amount(booking)
            
            if refund_amount > 0:
                # Create refund record
                # This would integrate with your payment service
                pass
        
        db.commit()
        
        logger.info(f"Booking {booking_id} cancelled successfully")
        return {"status": "cancelled", "booking_id": booking_id}
        
    except Exception as e:
        logger.error(f"Booking cancellation failed for {booking_id}: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        raise

def calculate_refund_amount(booking: Booking) -> float:
    """Calculate refund amount based on cancellation policy"""
    if not booking.check_in_date:
        return 0.0
    
    days_until_checkin = (booking.check_in_date - datetime.utcnow().date()).days
    total_amount = float(booking.total_amount)
    
    # Simple cancellation policy
    if days_until_checkin >= 7:
        return total_amount * 0.9  # 90% refund
    elif days_until_checkin >= 3:
        return total_amount * 0.5  # 50% refund
    elif days_until_checkin >= 1:
        return total_amount * 0.25  # 25% refund
    else:
        return 0.0  # No refund

@celery_app.task
def generate_booking_reports():
    """Generate daily booking reports"""
    try:
        db = next(get_db())
        
        today = datetime.utcnow().date()
        
        # Get booking statistics for today
        bookings_today = db.query(Booking).filter(
            Booking.created_at >= today,
            Booking.created_at < today + timedelta(days=1)
        ).all()
        
        stats = {
            "total_bookings": len(bookings_today),
            "confirmed_bookings": len([b for b in bookings_today if b.status == "confirmed"]),
            "pending_bookings": len([b for b in bookings_today if b.status == "pending"]),
            "cancelled_bookings": len([b for b in bookings_today if b.status == "cancelled"]),
            "total_revenue": sum(float(b.total_amount) for b in bookings_today if b.status == "confirmed"),
            "date": today.isoformat()
        }
        
        logger.info(f"Daily booking report: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Failed to generate booking reports: {str(e)}")
        raise