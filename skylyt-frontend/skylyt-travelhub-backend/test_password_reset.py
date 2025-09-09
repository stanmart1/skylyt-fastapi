#!/usr/bin/env python3
"""Test password reset functionality"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.models.user import User
from app.services.email_service import EmailService
from secrets import token_urlsafe
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_password_reset():
    """Test password reset flow"""
    db = next(get_db())
    email_service = EmailService()
    
    # Find a test user
    user = db.query(User).filter(User.email == "adelodunpeter69@gmail.com").first()
    if not user:
        logger.error("Test user not found")
        return
    
    logger.info(f"Testing password reset for user: {user.email}")
    
    # Generate reset token
    reset_token = token_urlsafe(32)
    user.set_reset_token(reset_token, expires_in_hours=1)
    db.commit()
    
    logger.info(f"Reset token generated: {reset_token}")
    logger.info(f"Token expires: {user.reset_token_expires}")
    
    # Test token validation
    is_valid = user.is_reset_token_valid(reset_token)
    logger.info(f"Token validation: {is_valid}")
    
    # Send reset email
    email_sent = email_service.send_password_reset(
        user.email, 
        reset_token, 
        f"{user.first_name} {user.last_name}"
    )
    
    if email_sent:
        logger.info("✅ Password reset email sent successfully")
        logger.info(f"Reset URL: https://skylytluxury.com/reset-password?token={reset_token}")
    else:
        logger.error("❌ Failed to send password reset email")

if __name__ == "__main__":
    test_password_reset()