#!/usr/bin/env python3
"""Test all email notifications in the application"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.email_service import EmailService
from app.core.database import get_db
from app.models.user import User
from secrets import token_urlsafe
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_all_emails():
    """Test all email notification types"""
    email_service = EmailService()
    db = next(get_db())
    
    # Test emails
    test_emails = ["adelodunpeter69@gmail.com", "scaleitpro@gmail.com"]
    
    logger.info("🚀 Starting comprehensive email testing...")
    
    for i, email in enumerate(test_emails):
        logger.info(f"\n📧 Testing with email: {email}")
        
        # 1. Welcome Email
        logger.info("1. Testing welcome email...")
        result = email_service.send_welcome_email(email, "Test User")
        logger.info(f"   Welcome email: {'✅ SUCCESS' if result else '❌ FAILED'}")
        
        # 2. Booking Confirmation
        logger.info("2. Testing booking confirmation...")
        booking_data = {
            "booking_reference": f"BK{1000 + i}",
            "user_name": "Test User",
            "hotel_name": "Luxury Hotel Test",
            "room_type": "Deluxe Suite",
            "check_in_date": "2024-12-01",
            "check_out_date": "2024-12-05",
            "guests": "2 Adults",
            "total_amount": "500.00",
            "currency": "USD"
        }
        result = email_service.send_booking_confirmation(email, booking_data)
        logger.info(f"   Booking confirmation: {'✅ SUCCESS' if result else '❌ FAILED'}")
        
        # 3. Payment Confirmation
        logger.info("3. Testing payment confirmation...")
        payment_data = {
            "user_name": "Test User",
            "booking_reference": f"BK{1000 + i}",
            "transaction_id": f"TXN{2000 + i}",
            "payment_method": "Credit Card",
            "amount": "500.00",
            "currency": "USD",
            "status": "completed"
        }
        result = email_service.send_payment_confirmation(email, payment_data)
        logger.info(f"   Payment confirmation: {'✅ SUCCESS' if result else '❌ FAILED'}")
        
        # 4. Payment Failed
        logger.info("4. Testing payment failed...")
        payment_failed_data = {
            "user_name": "Test User",
            "booking_reference": f"BK{1000 + i}",
            "transaction_id": f"TXN{3000 + i}",
            "payment_method": "Credit Card",
            "amount": "500.00",
            "currency": "USD",
            "is_failed": True,
            "error_message": "Insufficient funds"
        }
        result = email_service.send_payment_failed(email, payment_failed_data)
        logger.info(f"   Payment failed: {'✅ SUCCESS' if result else '❌ FAILED'}")
        
        # 5. Booking Status Update
        logger.info("5. Testing booking status update...")
        status_update_data = {
            "booking_reference": f"BK{1000 + i}",
            "user_name": "Test User",
            "hotel_name": "Luxury Hotel Test",
            "status": "confirmed"
        }
        result = email_service.send_booking_status_update(email, status_update_data)
        logger.info(f"   Booking status update: {'✅ SUCCESS' if result else '❌ FAILED'}")
        
        # 6. Booking Cancellation
        logger.info("6. Testing booking cancellation...")
        cancellation_data = {
            "booking_reference": f"BK{1000 + i}",
            "user_name": "Test User",
            "hotel_name": "Luxury Hotel Test",
            "is_cancellation": True,
            "cancellation_reason": "Customer request"
        }
        result = email_service.send_booking_cancellation(email, cancellation_data)
        logger.info(f"   Booking cancellation: {'✅ SUCCESS' if result else '❌ FAILED'}")
        
        # 7. Booking Completion
        logger.info("7. Testing booking completion...")
        completion_data = {
            "booking_reference": f"BK{1000 + i}",
            "user_name": "Test User",
            "hotel_name": "Luxury Hotel Test",
            "check_in_date": "2024-12-01",
            "check_out_date": "2024-12-05",
            "total_amount": "500.00",
            "currency": "USD"
        }
        result = email_service.send_booking_completion(email, completion_data)
        logger.info(f"   Booking completion: {'✅ SUCCESS' if result else '❌ FAILED'}")
        
        # 8. Driver Assignment
        logger.info("8. Testing driver assignment...")
        driver_data = {
            "name": "John Driver",
            "phone": "+1234567890",
            "vehicle": "Mercedes S-Class"
        }
        driver_booking_data = {
            "booking_reference": f"BK{1000 + i}",
            "pickup_location": "Airport Terminal 1",
            "pickup_time": "10:00 AM"
        }
        result = email_service.send_driver_assignment(email, driver_data, driver_booking_data)
        logger.info(f"   Driver assignment: {'✅ SUCCESS' if result else '❌ FAILED'}")
        
        # 9. Password Reset
        logger.info("9. Testing password reset...")
        reset_token = token_urlsafe(32)
        result = email_service.send_password_reset(email, reset_token, "Test User")
        logger.info(f"   Password reset: {'✅ SUCCESS' if result else '❌ FAILED'}")
        logger.info(f"   Reset URL: https://skylytluxury.com/reset-password?token={reset_token}")
        
        # 10. Contact Form Notification
        logger.info("10. Testing contact form notification...")
        contact_data = {
            "name": "Test Contact",
            "email": email,
            "subject": "Test Contact Form",
            "message": "This is a test contact form submission."
        }
        result = email_service.send_contact_form_notification("admin@skylytluxury.com", contact_data)
        logger.info(f"   Contact form notification: {'✅ SUCCESS' if result else '❌ FAILED'}")
        
        logger.info(f"\n✨ Completed testing for {email}")
    
    logger.info("\n🎉 Email testing completed!")
    logger.info("Check the test email inboxes for all notifications.")

if __name__ == "__main__":
    test_all_emails()