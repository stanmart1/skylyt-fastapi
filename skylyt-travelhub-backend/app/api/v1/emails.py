from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_admin_user
from app.services.email_service import EmailService
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter(prefix="/emails", tags=["emails"])
email_service = EmailService()


class EmailRequest(BaseModel):
    to_email: str
    email_type: str
    data: Dict[str, Any] = {}


@router.post("/send")
def send_email(
    email_request: EmailRequest,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Admin endpoint to send emails manually"""
    try:
        if email_request.email_type == "welcome":
            success = email_service.send_welcome_email(
                email_request.to_email,
                email_request.data.get("user_name", "User")
            )
        elif email_request.email_type == "booking_confirmation":
            success = email_service.send_booking_confirmation(
                email_request.to_email,
                email_request.data
            )
        elif email_request.email_type == "payment_confirmation":
            success = email_service.send_payment_confirmation(
                email_request.to_email,
                email_request.data
            )
        elif email_request.email_type == "booking_completion":
            success = email_service.send_booking_completion(
                email_request.to_email,
                email_request.data
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid email type")
        
        if success:
            return {"message": "Email sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
def test_email_service(
    current_user = Depends(get_current_user)
):
    """Test email service configuration"""
    try:
        success = email_service.send_welcome_email(
            current_user.email,
            f"{current_user.first_name} {current_user.last_name}"
        )
        
        if success:
            return {"message": "Test email sent successfully"}
        else:
            return {"message": "Email service not configured or failed"}
            
    except Exception as e:
        return {"message": f"Email test failed: {str(e)}"}