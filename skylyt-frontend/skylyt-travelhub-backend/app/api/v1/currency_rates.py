from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.currency_rate import CurrencyRate

router = APIRouter(prefix="/admin/currency-rates", tags=["currency-rates"])

@router.get("")
def get_currency_rates(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all currency rates"""
    rates = db.query(CurrencyRate).all()
    return [{"id": rate.id, "base_currency": rate.base_currency, "target_currency": rate.target_currency, "rate": rate.rate} for rate in rates]

@router.put("/{rate_id}")
def update_currency_rate(
    rate_id: int,
    rate_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update currency rate"""
    rate = db.query(CurrencyRate).filter(CurrencyRate.id == rate_id).first()
    if not rate:
        raise HTTPException(status_code=404, detail="Currency rate not found")
    
    rate.rate = rate_data["rate"]
    db.commit()
    return {"message": "Currency rate updated successfully"}

@router.get("/convert/{amount}/{from_currency}/{to_currency}")
def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
    db: Session = Depends(get_db)
):
    """Convert currency using manual rates"""
    if from_currency == to_currency:
        return {"converted_amount": amount}
    
    # If converting from NGN to other currency
    if from_currency == "NGN":
        rate = db.query(CurrencyRate).filter(
            CurrencyRate.base_currency == "NGN",
            CurrencyRate.target_currency == to_currency
        ).first()
        if not rate:
            raise HTTPException(status_code=404, detail=f"Rate not found for NGN to {to_currency}")
        return {"converted_amount": amount * rate.rate}
    
    # If converting from other currency to NGN
    elif to_currency == "NGN":
        rate = db.query(CurrencyRate).filter(
            CurrencyRate.base_currency == "NGN",
            CurrencyRate.target_currency == from_currency
        ).first()
        if not rate:
            raise HTTPException(status_code=404, detail=f"Rate not found for {from_currency} to NGN")
        return {"converted_amount": amount / rate.rate}
    
    # If converting between two non-NGN currencies (via NGN pivot)
    else:
        # Convert from_currency to NGN first
        from_rate = db.query(CurrencyRate).filter(
            CurrencyRate.base_currency == "NGN",
            CurrencyRate.target_currency == from_currency
        ).first()
        if not from_rate:
            raise HTTPException(status_code=404, detail=f"Rate not found for {from_currency}")
        
        # Convert NGN to to_currency
        to_rate = db.query(CurrencyRate).filter(
            CurrencyRate.base_currency == "NGN",
            CurrencyRate.target_currency == to_currency
        ).first()
        if not to_rate:
            raise HTTPException(status_code=404, detail=f"Rate not found for {to_currency}")
        
        # Convert: amount -> NGN -> target currency
        ngn_amount = amount / from_rate.rate
        converted_amount = ngn_amount * to_rate.rate
        return {"converted_amount": converted_amount}