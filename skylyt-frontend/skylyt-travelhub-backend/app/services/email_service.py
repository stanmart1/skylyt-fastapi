from typing import Dict, Any, List
import logging
import requests
import html
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending notifications using Resend API"""
    
    def __init__(self):
        if not settings.RESEND_API_KEY:
            logger.warning("RESEND_API_KEY not configured")
        if not settings.FROM_EMAIL:
            logger.warning("FROM_EMAIL not configured")
            
        self.api_key = settings.RESEND_API_KEY
        self.base_url = "https://api.resend.com"
        self.from_email = settings.FROM_EMAIL
        
        # Setup Jinja2 for email templates with enhanced security
        template_dir = Path(__file__).parent.parent / "templates" / "email"
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            # Disable dangerous features
            enable_async=False,
            # Remove potentially dangerous globals
            finalize=lambda x: x if x is not None else ''
        )
        # Remove dangerous built-ins
        self.jinja_env.globals.pop('range', None)
        self.jinja_env.globals.pop('lipsum', None)
        self.jinja_env.globals.pop('cycler', None)
        self.jinja_env.globals.pop('joiner', None)
    
    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email using Resend API"""
        if not self.api_key:
            logger.warning("RESEND_API_KEY not configured, skipping email")
            return False
            
        try:
            response = requests.post(
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
                },
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            return False
    
    def _sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize template context to prevent code injection"""
        sanitized = {}
        for key, value in context.items():
            if isinstance(value, str):
                # Escape HTML in string values
                sanitized[key] = html.escape(value)
            elif isinstance(value, dict):
                # Recursively sanitize nested dictionaries
                sanitized[key] = self._sanitize_context(value)
            elif isinstance(value, list):
                # Sanitize list items
                sanitized[key] = [html.escape(str(item)) if isinstance(item, str) else item for item in value]
            else:
                # Keep other types as-is (numbers, booleans, etc.)
                sanitized[key] = value
        return sanitized
    
    def _send_templated_email(self, to_email: str, template_name: str, context: Dict[str, Any], subject: str) -> bool:
        """Helper method to send templated emails"""
        try:
            # Validate template name to prevent path traversal
            if ".." in template_name or "/" in template_name or "\\" in template_name:
                logger.error(f"Invalid template name: {template_name}")
                return False
            
            template = self.jinja_env.get_template(f"{template_name}.html")
            # Sanitize context to prevent code injection
            safe_context = self._sanitize_context(context)
            html_content = template.render(**safe_context)
            return self._send_email(to_email, subject, html_content)
        except Exception as e:
            logger.error(f"Failed to send {template_name} email: {str(e)}")
            return False
    
    def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Send welcome email to new users"""
        return self._send_templated_email(
            to_email,
            "welcome",
            {"user_name": user_name, "frontend_url": settings.FRONTEND_URL},
            "Welcome to Skylyt Luxury!"
        )
    
    def send_booking_confirmation(self, to_email: str, booking_data: Dict[str, Any]) -> bool:
        """Send booking confirmation email"""
        return self._send_templated_email(
            to_email,
            "booking_confirmation",
            {"booking": booking_data, "frontend_url": settings.FRONTEND_URL},
            f"Booking Confirmation - {booking_data.get('booking_reference', 'N/A')}"
        )
    
    def send_payment_confirmation(self, to_email: str, payment_data: Dict[str, Any]) -> bool:
        """Send payment confirmation email"""
        return self._send_templated_email(
            to_email,
            "payment_confirmation",
            {"payment": payment_data, "frontend_url": settings.FRONTEND_URL},
            f"Payment Confirmed - {payment_data.get('transaction_id', 'N/A')}"
        )
    
    def send_booking_completion(self, to_email: str, booking_data: Dict[str, Any]) -> bool:
        """Send booking completion email"""
        return self._send_templated_email(
            to_email,
            "booking_completion",
            {"booking": booking_data, "frontend_url": settings.FRONTEND_URL},
            f"Booking Completed - {booking_data.get('booking_reference', 'N/A')}"
        )
    
    def send_password_reset(self, to_email: str, reset_token: str, user_name: str = "") -> bool:
        """Send password reset email"""
        return self._send_templated_email(
            to_email,
            "password_reset",
            {
                "user_name": user_name,
                "reset_link": f"https://skylytluxury.com/reset-password?token={reset_token}",
                "reset_token": reset_token
            },
            "Password Reset Request - Skylyt TravelHub"
        )
    
    def send_booking_status_update(self, to_email: str, booking_data: Dict[str, Any]) -> bool:
        """Send booking status update email"""
        return self._send_templated_email(
            to_email,
            "booking_confirmation",  # Reuse existing template
            {"booking": booking_data, "frontend_url": settings.FRONTEND_URL},
            f"Booking Update - {booking_data.get('booking_reference', 'N/A')}"
        )
    
    def send_booking_cancellation(self, to_email: str, booking_data: Dict[str, Any]) -> bool:
        """Send booking cancellation email"""
        return self._send_templated_email(
            to_email,
            "booking_confirmation",  # Reuse existing template
            {"booking": booking_data, "is_cancellation": True, "frontend_url": settings.FRONTEND_URL},
            f"Booking Cancelled - {booking_data.get('booking_reference', 'N/A')}"
        )
    
    def send_payment_failed(self, to_email: str, payment_data: Dict[str, Any]) -> bool:
        """Send payment failed notification email"""
        return self._send_templated_email(
            to_email,
            "payment_confirmation",  # Reuse existing template
            {"payment": payment_data, "is_failed": True, "frontend_url": settings.FRONTEND_URL},
            f"Payment Failed - {payment_data.get('booking_reference', 'N/A')}"
        )
    
    def send_driver_assignment(self, to_email: str, driver_data: Dict[str, Any], booking_data: Dict[str, Any]) -> bool:
        """Send driver assignment notification"""
        return self._send_templated_email(
            to_email,
            "booking_confirmation",  # Reuse existing template
            {"driver": driver_data, "booking": booking_data, "is_driver_assignment": True, "frontend_url": settings.FRONTEND_URL},
            f"New Trip Assignment - {booking_data.get('booking_reference', 'N/A')}"
        )
    
    def send_contact_form_notification(self, contact_email: str, form_data: Dict[str, Any]) -> bool:
        """Send contact form submission notification to admin"""
        try:
            # Create simple HTML email content
            html_content = f"""
            <html>
            <body>
                <h2>New Contact Form Submission</h2>
                <p><strong>Name:</strong> {html.escape(form_data.get('name', ''))}</p>
                <p><strong>Email:</strong> {html.escape(form_data.get('email', ''))}</p>
                <p><strong>Subject:</strong> {html.escape(form_data.get('subject', ''))}</p>
                <p><strong>Message:</strong></p>
                <p>{html.escape(form_data.get('message', ''))}</p>
            </body>
            </html>
            """
            
            return self._send_email(
                contact_email,
                f"Contact Form: {form_data.get('subject', 'New Message')}",
                html_content
            )
        except Exception as e:
            logger.error(f"Failed to send contact form notification: {str(e)}")
            return False