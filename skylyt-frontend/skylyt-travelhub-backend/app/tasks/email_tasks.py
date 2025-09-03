from celery import Celery
from typing import Dict, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from jinja2 import Environment, FileSystemLoader
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Celery app configuration
celery_app = Celery(
    "skylyt_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Email templates
template_env = Environment(
    loader=FileSystemLoader("app/templates/email")
)

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str = None,
        attachments: List[str] = None
    ) -> bool:
        """Send email using SMTP"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, "plain")
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename= {os.path.basename(file_path)}"
                        )
                        msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

email_service = EmailService()

@celery_app.task(bind=True, max_retries=3)
def send_booking_confirmation_email(self, booking_data: Dict):
    """Send booking confirmation email"""
    try:
        template = template_env.get_template("booking_confirmation.html")
        html_content = template.render(booking=booking_data)
        
        subject = f"Booking Confirmation - {booking_data['booking_reference']}"
        
        success = email_service.send_email(
            to_email=booking_data["user_email"],
            subject=subject,
            html_content=html_content
        )
        
        if not success:
            raise Exception("Failed to send email")
        
        return {"status": "sent", "email": booking_data["user_email"]}
        
    except Exception as e:
        logger.error(f"Booking confirmation email failed: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        raise

@celery_app.task(bind=True, max_retries=3)
def send_password_reset_email(self, email: str, reset_token: str, user_name: str):
    """Send password reset email"""
    try:
        template = template_env.get_template("password_reset.html")
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        html_content = template.render(
            user_name=user_name,
            reset_url=reset_url
        )
        
        subject = "Password Reset Request - Skylyt TravelHub"
        
        success = email_service.send_email(
            to_email=email,
            subject=subject,
            html_content=html_content
        )
        
        if not success:
            raise Exception("Failed to send email")
        
        return {"status": "sent", "email": email}
        
    except Exception as e:
        logger.error(f"Password reset email failed: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        raise

@celery_app.task(bind=True, max_retries=3)
def send_welcome_email(self, email: str, user_name: str):
    """Send welcome email to new users"""
    try:
        template = template_env.get_template("welcome.html")
        html_content = template.render(user_name=user_name)
        
        subject = "Welcome to Skylyt TravelHub!"
        
        success = email_service.send_email(
            to_email=email,
            subject=subject,
            html_content=html_content
        )
        
        if not success:
            raise Exception("Failed to send email")
        
        return {"status": "sent", "email": email}
        
    except Exception as e:
        logger.error(f"Welcome email failed: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        raise

@celery_app.task(bind=True, max_retries=3)
def send_payment_confirmation_email(self, payment_data: Dict):
    """Send payment confirmation email"""
    try:
        template = template_env.get_template("payment_confirmation.html")
        html_content = template.render(payment=payment_data)
        
        subject = f"Payment Confirmation - {payment_data['transaction_id']}"
        
        success = email_service.send_email(
            to_email=payment_data["user_email"],
            subject=subject,
            html_content=html_content
        )
        
        if not success:
            raise Exception("Failed to send email")
        
        return {"status": "sent", "email": payment_data["user_email"]}
        
    except Exception as e:
        logger.error(f"Payment confirmation email failed: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        raise

@celery_app.task(bind=True, max_retries=3)
def send_booking_status_update_email(self, booking_data: Dict):
    """Send booking status update email"""
    try:
        template = template_env.get_template("booking_confirmation.html")
        html_content = template.render(booking=booking_data)
        
        subject = f"Booking Update - {booking_data['booking_reference']}"
        
        success = email_service.send_email(
            to_email=booking_data["user_email"],
            subject=subject,
            html_content=html_content
        )
        
        if not success:
            raise Exception("Failed to send email")
        
        return {"status": "sent", "email": booking_data["user_email"]}
        
    except Exception as e:
        logger.error(f"Booking status update email failed: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        raise

@celery_app.task(bind=True, max_retries=3)
def send_driver_assignment_email(self, driver_data: Dict, booking_data: Dict):
    """Send driver assignment notification email"""
    try:
        template = template_env.get_template("booking_confirmation.html")
        html_content = template.render(
            booking=booking_data,
            driver=driver_data,
            is_driver_assignment=True
        )
        
        subject = f"New Trip Assignment - {booking_data['booking_reference']}"
        
        success = email_service.send_email(
            to_email=driver_data["email"],
            subject=subject,
            html_content=html_content
        )
        
        if not success:
            raise Exception("Failed to send email")
        
        return {"status": "sent", "email": driver_data["email"]}
        
    except Exception as e:
        logger.error(f"Driver assignment email failed: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        raise

@celery_app.task
def send_bulk_promotional_email(email_list: List[str], template_name: str, context: Dict):
    """Send bulk promotional emails"""
    try:
        template = template_env.get_template(f"{template_name}.html")
        html_content = template.render(**context)
        
        subject = context.get("subject", "Special Offer from Skylyt TravelHub")
        
        results = []
        for email in email_list:
            success = email_service.send_email(
                to_email=email,
                subject=subject,
                html_content=html_content
            )
            results.append({"email": email, "sent": success})
        
        return {"total": len(email_list), "results": results}
        
    except Exception as e:
        logger.error(f"Bulk email failed: {str(e)}")
        raise