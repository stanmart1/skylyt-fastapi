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
    
    return {
        "location": location_data,
        "supported_currencies": CurrencyService.SUPPORTED_CURRENCIES,
        "currency_symbols": {
            currency: CurrencyService.get_currency_symbol(currency)
            for currency in CurrencyService.SUPPORTED_CURRENCIES
        }
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
    converted = CurrencyService.convert_amount(
        db, amount, from_currency.upper(), to_currency.upper()
    )
    
    return {
        "original_amount": amount,
        "from_currency": from_currency.upper(),
        "to_currency": to_currency.upper(),
        "converted_amount": float(converted),
        "exchange_rate": float(CurrencyService.get_exchange_rate(
            db, from_currency.upper(), to_currency.upper()
        ))
    }