from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.user import User
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for creating and managing in-app notifications"""
    
    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        title: str,
        message: str,
        notification_type: str = "info"
    ) -> Optional[Notification]:
        """Create a new notification for a user"""
        try:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=notification_type
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
            return notification
        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def create_booking_confirmation_notification(
        db: Session,
        user_id: int,
        booking_reference: str,
        booking_type: str
    ):
        """Create notification for booking confirmation"""
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            title="Booking Confirmed",
            message=f"Your {booking_type} booking {booking_reference} has been confirmed.",
            notification_type="success"
        )
    
    @staticmethod
    def create_payment_confirmation_notification(
        db: Session,
        user_id: int,
        booking_reference: str,
        amount: float,
        currency: str
    ):
        """Create notification for payment confirmation"""
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            title="Payment Confirmed",
            message=f"Payment of {currency} {amount} for booking {booking_reference} has been confirmed.",
            notification_type="success"
        )
    
    @staticmethod
    def create_driver_assignment_notification(
        db: Session,
        driver_email: str,
        booking_reference: str,
        customer_name: str
    ):
        """Create notification for driver assignment"""
        # Find user by driver email
        user = db.query(User).filter(User.email == driver_email).first()
        if user:
            return NotificationService.create_notification(
                db=db,
                user_id=user.id,
                title="New Trip Assignment",
                message=f"You have been assigned to booking {booking_reference}. Customer: {customer_name}",
                notification_type="info"
            )
        return None
    
    @staticmethod
    def create_booking_status_update_notification(
        db: Session,
        user_id: int,
        booking_reference: str,
        new_status: str
    ):
        """Create notification for booking status updates"""
        status_messages = {
            "confirmed": "Your booking has been confirmed",
            "cancelled": "Your booking has been cancelled",
            "completed": "Your booking has been completed",
            "in_progress": "Your booking is now in progress"
        }
        
        message = status_messages.get(new_status, f"Your booking status has been updated to {new_status}")
        notification_type = "success" if new_status in ["confirmed", "completed"] else "warning" if new_status == "cancelled" else "info"
        
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            title="Booking Status Update",
            message=f"{message} - {booking_reference}",
            notification_type=notification_type
        )
    
    @staticmethod
    def create_welcome_notification(db: Session, user_id: int, user_name: str):
        """Create welcome notification for new users"""
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            title="Welcome to Skylyt TravelHub!",
            message=f"Welcome {user_name}! Your account has been created successfully. Start exploring our services.",
            notification_type="success"
        )
    
    @staticmethod
    def create_trip_status_notification(
        db: Session,
        customer_user_id: int,
        booking_reference: str,
        trip_status: str,
        driver_name: str
    ):
        """Create notification for trip status updates (for customers)"""
        status_messages = {
            "en_route": f"Your driver {driver_name} is on the way",
            "in_progress": f"Your trip with {driver_name} has started",
            "completed": f"Your trip with {driver_name} has been completed"
        }
        
        message = status_messages.get(trip_status, f"Trip status updated to {trip_status}")
        
        return NotificationService.create_notification(
            db=db,
            user_id=customer_user_id,
            title="Trip Update",
            message=f"{message} - {booking_reference}",
            notification_type="info"
        )