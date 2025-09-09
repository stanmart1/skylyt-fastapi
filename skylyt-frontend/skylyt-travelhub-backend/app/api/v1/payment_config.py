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
    try:
        available_gateways = PaymentProcessor.get_available_gateways(db)
        
        # Enhanced gateway information
        gateway_info = {
            'stripe': {'name': 'Stripe', 'description': 'Credit/Debit Cards', 'type': 'card'},
            'paystack': {'name': 'Paystack', 'description': 'Nigerian Payment Gateway', 'type': 'redirect'},
            'flutterwave': {'name': 'Flutterwave', 'description': 'African Payment Gateway', 'type': 'redirect'},
            'paypal': {'name': 'PayPal', 'description': 'PayPal Account', 'type': 'redirect'}
        }
        
        configured_gateways = []
        if available_gateways.get('success'):
            for gateway_id in available_gateways.get('gateways', []):
                if gateway_id in gateway_info:
                    configured_gateways.append({
                        'id': gateway_id,
                        **gateway_info[gateway_id],
                        'configured': True
                    })
        
        # Always return all gateways, marking which are configured
        all_gateways = []
        for gateway_id, info in gateway_info.items():
            configured = any(g['id'] == gateway_id for g in configured_gateways)
            all_gateways.append({
                'id': gateway_id,
                **info,
                'configured': configured
            })
        
        return {
            'success': True,
            'gateways': all_gateways
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'gateways': [
                {'id': 'stripe', 'name': 'Stripe', 'description': 'Credit/Debit Cards', 'configured': False},
                {'id': 'paystack', 'name': 'Paystack', 'description': 'Nigerian Payment Gateway', 'configured': False},
                {'id': 'flutterwave', 'name': 'Flutterwave', 'description': 'African Payment Gateway', 'configured': False},
                {'id': 'paypal', 'name': 'PayPal', 'description': 'PayPal Account', 'configured': False}
            ]
        }

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
        return {
            "stripe_configured": False,
            "paystack_configured": False,
            "flutterwave_configured": False,
            "paypal_configured": False
        }
    
    # Return configuration status and public keys (safe to expose)
    return {
        "stripe_configured": bool(settings.stripe_public_key and settings.stripe_secret_key),
        "stripe_public_key": settings.stripe_public_key or "",
        "paystack_configured": bool(settings.paystack_public_key and settings.paystack_secret_key),
        "paystack_public_key": settings.paystack_public_key or "",
        "flutterwave_configured": bool(settings.flutterwave_public_key and settings.flutterwave_secret_key),
        "flutterwave_public_key": settings.flutterwave_public_key or "",
        "paypal_configured": bool(settings.paypal_client_id and settings.paypal_client_secret),
        "paypal_client_id": settings.paypal_client_id or "",
        "paypal_sandbox": settings.paypal_sandbox if settings.paypal_sandbox is not None else True
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
    
    # Update only provided fields (skip empty strings for secret keys)
    update_data = config.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(settings, field) and value is not None:
            # Don't update secret keys if they're empty (keep existing)
            if field.endswith('_secret_key') or field.endswith('_client_secret'):
                if value.strip():  # Only update if not empty
                    setattr(settings, field, value)
            else:
                setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    
    return {
        "message": "Payment gateway configuration updated successfully",
        "configured_gateways": {
            "stripe": bool(settings.stripe_public_key and settings.stripe_secret_key),
            "paystack": bool(settings.paystack_public_key and settings.paystack_secret_key),
            "flutterwave": bool(settings.flutterwave_public_key and settings.flutterwave_secret_key),
            "paypal": bool(settings.paypal_client_id and settings.paypal_client_secret)
        }
    }

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
        return {"success": False, "message": f"Gateway {gateway_type} not configured or missing API keys"}
    
    try:
        # Test with a small amount
        test_result = await gateway.create_payment(
            amount=1.00,
            currency="NGN",
            customer_email="test@skylyt.com",
            booking_reference=f"TEST_{gateway_type.upper()}_{int(__import__('time').time())}",
            metadata={"test": True, "environment": "test"}
        )
        
        if test_result.get('success'):
            return {
                "success": True,
                "message": f"{gateway_type.title()} gateway is properly configured and functional",
                "test_data": {
                    "transaction_id": test_result.get('transaction_id'),
                    "amount": test_result.get('amount'),
                    "currency": test_result.get('currency')
                }
            }
        else:
            return {
                "success": False,
                "message": f"{gateway_type.title()} gateway test failed: {test_result.get('error', 'Unknown error')}"
            }
    except Exception as e:
        return {
            "success": False, 
            "message": f"{gateway_type.title()} gateway test failed: {str(e)}"
        }