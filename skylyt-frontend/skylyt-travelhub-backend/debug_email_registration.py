#!/usr/bin/env python3
"""Debug email sending during registration"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.email_service import EmailService
from app.core.config import settings
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_email_config():
    """Debug email configuration"""
    logger.info("=== EMAIL CONFIGURATION DEBUG ===")
    
    # Check environment variables
    logger.info(f"RESEND_API_KEY configured: {'Yes' if settings.RESEND_API_KEY else 'No'}")
    if settings.RESEND_API_KEY:
        logger.info(f"API Key starts with: {settings.RESEND_API_KEY[:10]}...")
    
    logger.info(f"FROM_EMAIL: {settings.FROM_EMAIL}")
    logger.info(f"FRONTEND_URL: {settings.FRONTEND_URL}")
    
    # Test email service initialization
    try:
        email_service = EmailService()
        logger.info("✅ EmailService initialized successfully")
        
        # Test template loading
        try:
            template = email_service.jinja_env.get_template("welcome.html")
            logger.info("✅ Welcome template loaded successfully")
        except Exception as e:
            logger.error(f"❌ Template loading failed: {e}")
            
        # Test email sending
        test_email = "test@example.com"
        test_name = "Test User"
        
        logger.info(f"Testing welcome email to {test_email}...")
        result = email_service.send_welcome_email(test_email, test_name)
        
        if result:
            logger.info("✅ Email sending test successful")
        else:
            logger.error("❌ Email sending test failed")
            
    except Exception as e:
        logger.error(f"❌ EmailService initialization failed: {e}")

def check_registration_flow():
    """Check if registration flow calls email service"""
    logger.info("\n=== REGISTRATION FLOW DEBUG ===")
    
    # Check if notification service exists
    try:
        from app.services.notification_service import NotificationService
        logger.info("✅ NotificationService import successful")
    except Exception as e:
        logger.error(f"❌ NotificationService import failed: {e}")
    
    # Check auth service
    try:
        from app.services.auth_service import AuthService
        logger.info("✅ AuthService import successful")
    except Exception as e:
        logger.error(f"❌ AuthService import failed: {e}")

if __name__ == "__main__":
    debug_email_config()
    check_registration_flow()