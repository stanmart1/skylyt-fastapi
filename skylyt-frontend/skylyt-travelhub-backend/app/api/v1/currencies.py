from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.currency import Currency
from app.schemas.currency import (
    CurrencyCreate, CurrencyUpdate, CurrencyResponse, 
    CurrencyConversionRequest, CurrencyConversionResponse, BulkRateUpdate
)
from app.services.currency_service import CurrencyService

router = APIRouter()


@router.get("/currencies", response_model=List[CurrencyResponse])
def get_currencies(db: Session = Depends(get_db)):
    """Get all active currencies"""
    currencies = CurrencyService.get_active_currencies(db)
    return currencies


@router.post("/currencies/convert", response_model=CurrencyConversionResponse)
def convert_currency(
    request: CurrencyConversionRequest,
    db: Session = Depends(get_db)
):
    """Convert amount between currencies"""
    try:
        converted_amount = CurrencyService.convert_currency(
            request.amount, request.from_currency, request.to_currency, db
        )
        
        # Calculate exchange rate for display
        rate = CurrencyService.convert_currency(1.0, request.from_currency, request.to_currency, db)
        
        return CurrencyConversionResponse(
            original_amount=request.amount,
            converted_amount=converted_amount,
            from_currency=request.from_currency,
            to_currency=request.to_currency,
            exchange_rate=rate
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/admin/currencies", response_model=CurrencyResponse)
def create_currency(
    currency: CurrencyCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new currency (Admin only)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if currency already exists
    existing = db.query(Currency).filter(Currency.code == currency.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Currency already exists")
    
    db_currency = Currency(**currency.dict())
    db.add(db_currency)
    db.commit()
    db.refresh(db_currency)
    return db_currency


@router.put("/admin/currencies/{currency_id}", response_model=CurrencyResponse)
def update_currency(
    currency_id: int,
    currency_update: CurrencyUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update currency (Admin only)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    currency = db.query(Currency).filter(Currency.id == currency_id).first()
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    
    for field, value in currency_update.dict(exclude_unset=True).items():
        setattr(currency, field, value)
    
    db.commit()
    db.refresh(currency)
    return currency


@router.delete("/admin/currencies/{currency_id}")
def delete_currency(
    currency_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete currency (Admin only)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    currency = db.query(Currency).filter(Currency.id == currency_id).first()
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    
    if currency.code == "NGN":
        raise HTTPException(status_code=400, detail="Cannot delete base currency")
    
    db.delete(currency)
    db.commit()
    return {"message": "Currency deleted successfully"}


@router.put("/admin/currencies/bulk-update")
def bulk_update_rates(
    bulk_update: BulkRateUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk update exchange rates (Admin only)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    updated_count = 0
    for code, rate in bulk_update.updates.items():
        currency = db.query(Currency).filter(Currency.code == code.upper()).first()
        if currency and rate > 0:
            currency.rate_to_ngn = rate
            updated_count += 1
    
    db.commit()
    return {"message": f"Updated {updated_count} exchange rates"}


@router.get("/admin/currencies", response_model=List[CurrencyResponse])
def get_all_currencies_admin(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all currencies including inactive (Admin only)"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return db.query(Currency).all()