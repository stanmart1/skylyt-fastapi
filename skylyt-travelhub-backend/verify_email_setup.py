#!/usr/bin/env python3
"""
Verify email service setup and configuration
Run: python verify_email_setup.py
"""

import os
from app.services.email_service import EmailService
from app.core.config import settings

def verify_email_setup():
    print("🔍 Verifying Email Service Setup...")
    
    # Check environment variables
    print(f"RESEND_API_KEY: {'✅ Set' if settings.RESEND_API_KEY else '❌ Missing'}")
    print(f"FROM_EMAIL: {settings.FROM_EMAIL}")
    
    # Test email service initialization
    try:
        email_service = EmailService()
        print("✅ EmailService initialized successfully")
        
        # Test template loading
        template_dir = email_service.jinja_env.loader.searchpath[0]
        print(f"📁 Template directory: {template_dir}")
        
        templates = ['welcome.html', 'booking_confirmation.html', 'payment_confirmation.html', 'booking_completion.html']
        for template in templates:
            try:
                email_service.jinja_env.get_template(template)
                print(f"✅ Template {template} found")
            except Exception as e:
                print(f"❌ Template {template} missing: {e}")
                
    except Exception as e:
        print(f"❌ EmailService initialization failed: {e}")

if __name__ == "__main__":
    verify_email_setup()