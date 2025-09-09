#!/usr/bin/env python3
"""Test registration email flow with real user creation"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.schemas.auth import UserCreate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_registration_with_email():
    """Test complete registration flow with email"""
    db = next(get_db())
    email_service = EmailService()
    
    # Test user data
    test_user_data = UserCreate(
        email="test.registration@example.com",
        password="testpassword123",
        first_name="Test",
        last_name="Registration"
    )
    
    logger.info(f"Testing registration for: {test_user_data.email}")
    
    try:
        # Check if user already exists
        from app.models.user import User
        existing_user = db.query(User).filter(User.email == test_user_data.email).first()
        if existing_user:
            logger.info("Deleting existing test user...")
            db.delete(existing_user)
            db.commit()
        
        # Register user
        logger.info("Creating new user...")
        user = AuthService.register_user(db, test_user_data)
        logger.info(f"✅ User created with ID: {user.id}")
        
        # Test email sending
        logger.info("Sending welcome email...")
        email_sent = email_service.send_welcome_email(
            user.email, 
            f"{user.first_name} {user.last_name}"
        )
        
        if email_sent:
            logger.info("✅ Welcome email sent successfully")
        else:
            logger.error("❌ Welcome email failed to send")
            
        # Check notification creation
        try:
            from app.services.notification_service import NotificationService
            NotificationService.create_welcome_notification(
                db=db,
                user_id=user.id,
                user_name=f"{user.first_name} {user.last_name}"
            )
            logger.info("✅ Welcome notification created")
        except Exception as e:
            logger.error(f"❌ Notification creation failed: {e}")
            
        # Cleanup
        logger.info("Cleaning up test user...")
        db.delete(user)
        db.commit()
        
    except Exception as e:
        logger.error(f"❌ Registration test failed: {e}")
        db.rollback()

if __name__ == "__main__":
    test_registration_with_email()