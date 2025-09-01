from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.currency_service import CurrencyService
from app.services.location_service import LocationService

router = APIRouter(prefix="/localization", tags=["localization"])


@router.get("/detect")
async def detect_user_location(request: Request, db: Session = Depends(get_db)):
    """Auto-detect user location and currency"""
    client_ip = request.client.host
    if request.headers.get("X-Forwarded-For"):
        client_ip = request.headers.get("X-Forwarded-For").split(",")[0].strip()
    
    location_data = await LocationService.detect_location_from_ip(client_ip)
    
    # Get supported currencies from database
    currencies = CurrencyService.get_active_currencies(db)
    supported_currencies = [curr.code for curr in currencies]
    currency_symbols = {curr.code: curr.symbol for curr in currencies}
    
    return {
        "location": location_data,
        "supported_currencies": supported_currencies,
        "currency_symbols": currency_symbols
    }


@router.get("/countries")
async def get_supported_countries():
    """Get list of supported countries"""
    return {
        "countries": LocationService.get_supported_countries(),
        "nigerian_cities": LocationService.NIGERIAN_CITIES
    }


@router.get("/convert/{amount}/{from_currency}/{to_currency}")
async def convert_currency(
    amount: float, 
    from_currency: str, 
    to_currency: str,
    db: Session = Depends(get_db)
):
    """Convert amount between currencies"""
    try:
        converted = CurrencyService.convert_currency(
            amount, from_currency.upper(), to_currency.upper(), db
        )
        
        # Calculate exchange rate
        rate = CurrencyService.convert_currency(
            1.0, from_currency.upper(), to_currency.upper(), db
        )
        
        return {
            "original_amount": amount,
            "from_currency": from_currency.upper(),
            "to_currency": to_currency.upper(),
            "converted_amount": converted,
            "exchange_rate": rate
        }
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))