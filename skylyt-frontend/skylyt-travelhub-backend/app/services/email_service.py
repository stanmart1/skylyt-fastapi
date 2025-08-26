from typing import Dict, Any, List
import logging
import httpx
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending notifications using Resend API"""
    
    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.base_url = "https://api.resend.com"
        self.from_email = settings.FROM_EMAIL
        
        # Setup Jinja2 for email templates
        template_dir = Path(__file__).parent.parent / "templates" / "email"
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    async def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email using Resend API"""
        if not self.api_key:
            logger.warning("RESEND_API_KEY not configured, skipping email")
            return False
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/emails",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "from": self.from_email,
                        "to": [to_email],
                        "subject": subject,
                        "html": html_content
                    }
                )
                
                if response.status_code == 200:
                    logger.info(f"Email sent successfully to {to_email}")
                    return True
                else:
                    logger.error(f"Failed to send email: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False
    
    def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Send welcome email to new users"""
        try:
            template = self.jinja_env.get_template("welcome.html")
            html_content = template.render(
                user_name=user_name,
                frontend_url=settings.FRONTEND_URL
            )
            
            import asyncio
            return asyncio.run(self._send_email(
                to_email, 
                "Welcome to Skylyt TravelHub!", 
                html_content
            ))
            
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")
            return False
    
    def send_booking_confirmation(self, to_email: str, booking_data: Dict[str, Any]) -> bool:
        """Send booking confirmation email"""
        try:
            template = self.jinja_env.get_template("booking_confirmation.html")
            html_content = template.render(booking=booking_data)
            
            import asyncio
            return asyncio.run(self._send_email(
                to_email,
                f"Booking Confirmation - {booking_data.get('booking_reference')}",
                html_content
            ))
            
        except Exception as e:
            logger.error(f"Failed to send booking confirmation: {e}")
            return False
    
    def send_payment_confirmation(self, to_email: str, payment_data: Dict[str, Any]) -> bool:
        """Send payment confirmation email"""
        try:
            template = self.jinja_env.get_template("payment_confirmation.html")
            html_content = template.render(payment=payment_data)
            
            import asyncio
            return asyncio.run(self._send_email(
                to_email,
                f"Payment Confirmed - {payment_data.get('transaction_id')}",
                html_content
            ))
            
        except Exception as e:
            logger.error(f"Failed to send payment confirmation: {e}")
            return False
    
    def send_booking_completion(self, to_email: str, booking_data: Dict[str, Any]) -> bool:
        """Send booking completion email"""
        try:
            template = self.jinja_env.get_template("booking_completion.html")
            html_content = template.render(
                booking=booking_data,
                frontend_url=settings.FRONTEND_URL
            )
            
            import asyncio
            return asyncio.run(self._send_email(
                to_email,
                f"Booking Completed - {booking_data.get('booking_reference')}",
                html_content
            ))
            
        except Exception as e:
            logger.error(f"Failed to send booking completion: {e}")
            return False
    
    def send_password_reset(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email"""
        try:
            template = self.jinja_env.get_template("password_reset.html")
            html_content = template.render(
                reset_link=f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
            )
            
            import asyncio
            return asyncio.run(self._send_email(
                to_email,
                "Password Reset Request",
                html_content
            ))
            
        except Exception as e:
            logger.error(f"Failed to send password reset: {e}")
            return False