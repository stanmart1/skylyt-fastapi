from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.settings import Settings
from app.services.payment_processor import PaymentProcessor

router = APIRouter(prefix="/payment-config", tags=["payment-config"])

class PaymentGatewayConfig(BaseModel):
    stripe_public_key: Optional[str] = None
    stripe_secret_key: Optional[str] = None
    paystack_public_key: Optional[str] = None
    paystack_secret_key: Optional[str] = None
    flutterwave_public_key: Optional[str] = None
    flutterwave_secret_key: Optional[str] = None
    paypal_client_id: Optional[str] = None
    paypal_client_secret: Optional[str] = None
    paypal_sandbox: Optional[bool] = True

@router.get("/gateways")
def get_payment_gateways(db: Session = Depends(get_db)):
    """Get available payment gateways for frontend"""
    result = PaymentProcessor.get_available_gateways(db)
    return result

@router.get("/config")
def get_payment_config(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get payment gateway configuration (admin only)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    settings = db.query(Settings).first()
    if not settings:
        return {}
    
    # Return only public keys and configuration status
    return {
        "stripe_configured": bool(settings.stripe_public_key and settings.stripe_secret_key),
        "stripe_public_key": settings.stripe_public_key,
        "paystack_configured": bool(settings.paystack_public_key and settings.paystack_secret_key),
        "paystack_public_key": settings.paystack_public_key,
        "flutterwave_configured": bool(settings.flutterwave_public_key and settings.flutterwave_secret_key),
        "flutterwave_public_key": settings.flutterwave_public_key,
        "paypal_configured": bool(settings.paypal_client_id and settings.paypal_client_secret),
        "paypal_client_id": settings.paypal_client_id,
        "paypal_sandbox": settings.paypal_sandbox
    }

@router.put("/config")
def update_payment_config(
    config: PaymentGatewayConfig,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update payment gateway configuration (superadmin only)"""
    if not current_user.is_superadmin():
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    settings = db.query(Settings).first()
    if not settings:
        settings = Settings()
        db.add(settings)
    
    # Update only provided fields
    update_data = config.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(settings, field):
            setattr(settings, field, value)
    
    db.commit()
    
    return {"message": "Payment gateway configuration updated successfully"}

@router.post("/test/{gateway_type}")
async def test_payment_gateway(
    gateway_type: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Test payment gateway configuration"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.services.payment.gateway_factory import PaymentGatewayFactory
    
    gateway = PaymentGatewayFactory.create_gateway(gateway_type, db)
    if not gateway:
        return {"success": False, "message": f"Gateway {gateway_type} not configured"}
    
    try:
        # Test with a small amount
        test_result = await gateway.create_payment(
            amount=1.00,
            currency="NGN",
            customer_email="test@example.com",
            booking_reference="TEST_" + gateway_type.upper(),
            metadata={"test": True}
        )
        
        return {
            "success": test_result.get('success', False),
            "message": "Gateway test successful" if test_result.get('success') else test_result.get('error', 'Test failed')
        }
    except Exception as e:
        return {"success": False, "message": f"Gateway test failed: {str(e)}"}