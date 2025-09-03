import asyncio
import os
from app.services.email_service import EmailService
from app.core.config import settings

async def test_email_functionality():
    """Test email service functionality"""
    print("=== TESTING EMAIL FUNCTIONALITY ===")
    
    email_service = EmailService()
    
    # Test configuration
    print(f"✅ RESEND_API_KEY configured: {bool(settings.RESEND_API_KEY)}")
    print(f"✅ FROM_EMAIL: {settings.FROM_EMAIL}")
    
    # Test welcome email (without actually sending)
    try:
        # This will test template rendering without sending
        template = email_service.jinja_env.get_template("welcome.html")
        html_content = template.render(
            user_name="Test User",
            frontend_url=settings.FRONTEND_URL
        )
        print("✅ Welcome email template renders successfully")
        print(f"   Template length: {len(html_content)} characters")
    except Exception as e:
        print(f"❌ Welcome email template error: {e}")
    
    # Test booking confirmation template
    try:
        template = email_service.jinja_env.get_template("booking_confirmation.html")
        html_content = template.render(booking={
            "booking_reference": "TEST123",
            "customer_name": "Test User",
            "total_amount": 100.00
        })
        print("✅ Booking confirmation template renders successfully")
    except Exception as e:
        print(f"❌ Booking confirmation template error: {e}")

def test_notification_model():
    """Test notification database model"""
    print("\n=== TESTING NOTIFICATION MODEL ===")
    
    try:
        from app.models.notification import Notification
        print("✅ Notification model imports successfully")
        
        # Check model attributes
        required_fields = ['user_id', 'title', 'message', 'type', 'is_read']
        for field in required_fields:
            if hasattr(Notification, field):
                print(f"✅ Field '{field}' exists")
            else:
                print(f"❌ Field '{field}' missing")
                
    except Exception as e:
        print(f"❌ Notification model error: {e}")

def test_api_endpoints():
    """Test API endpoint configuration"""
    print("\n=== TESTING API ENDPOINTS ===")
    
    try:
        from app.api.v1.notifications import router as notification_router
        from app.api.v1.emails import router as email_router
        
        print("✅ Notification router imports successfully")
        print("✅ Email router imports successfully")
        
        # Check routes
        notification_routes = [route.path for route in notification_router.routes]
        email_routes = [route.path for route in email_router.routes]
        
        print(f"✅ Notification routes: {notification_routes}")
        print(f"✅ Email routes: {email_routes}")
        
    except Exception as e:
        print(f"❌ API endpoint error: {e}")

if __name__ == "__main__":
    asyncio.run(test_email_functionality())
    test_notification_model()
    test_api_endpoints()