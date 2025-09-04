#!/usr/bin/env python3
"""
Simple test script to verify email service is working
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.email_service import EmailService
from app.core.config import settings
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_email_service():
    """Test the email service"""
    logger.info("Testing email service...")
    
    # Check configuration
    logger.info(f"RESEND_API_KEY configured: {'Yes' if settings.RESEND_API_KEY else 'No'}")
    logger.info(f"FROM_EMAIL: {settings.FROM_EMAIL}")
    
    # Initialize email service
    email_service = EmailService()
    
    # Test sending welcome email
    test_email = "adelodunpeter24@gmail.com"  # Verified email for testing
    test_name = "Test User"
    
    logger.info(f"Attempting to send welcome email to {test_email}")
    
    try:
        result = email_service.send_welcome_email(test_email, test_name)
        if result:
            logger.info("✅ Email sent successfully!")
        else:
            logger.error("❌ Email sending failed")
    except Exception as e:
        logger.error(f"❌ Exception occurred: {e}")

if __name__ == "__main__":
    test_email_service()