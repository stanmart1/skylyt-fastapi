from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.orm import Session
from app.models.currency import Currency
from typing import Optional, Dict, List


class CurrencyService:
    BASE_CURRENCY = "NGN"
    
    @staticmethod
    def convert_currency(amount: float, from_currency: str, to_currency: str, db: Session) -> float:
        """Convert amount between currencies through NGN base currency
        
        Exchange rate logic:
        - rate_to_ngn represents: 1 foreign currency = X NGN
        - From foreign to NGN: multiply by rate_to_ngn
        - From NGN to foreign: divide by rate_to_ngn
        """
        if from_currency == to_currency:
            return round(float(amount), 2)
        
        amount_decimal = Decimal(str(amount))
        
        # Convert to NGN first if not already
        if from_currency != CurrencyService.BASE_CURRENCY:
            from_rate = db.query(Currency).filter(
                Currency.code == from_currency, 
                Currency.is_active == True
            ).first()
            if not from_rate:
                raise ValueError(f"Currency {from_currency} not found or inactive")
            # Foreign to NGN: multiply by rate (1 USD = 1600 NGN, so 5 USD = 5 * 1600 NGN)
            amount_decimal = amount_decimal * from_rate.rate_to_ngn
        
        # Convert from NGN to target currency
        if to_currency != CurrencyService.BASE_CURRENCY:
            to_rate = db.query(Currency).filter(
                Currency.code == to_currency, 
                Currency.is_active == True
            ).first()
            if not to_rate:
                raise ValueError(f"Currency {to_currency} not found or inactive")
            # NGN to foreign: divide by rate (8000 NGN = 8000 / 1600 USD = 5 USD)
            amount_decimal = amount_decimal / to_rate.rate_to_ngn
        
        return float(amount_decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    @staticmethod
    def get_active_currencies(db: Session) -> List[Currency]:
        """Get all active currencies"""
        return db.query(Currency).filter(Currency.is_active == True).all()
    
    @staticmethod
    def get_currency_by_code(code: str, db: Session) -> Optional[Currency]:
        """Get currency by code"""
        return db.query(Currency).filter(
            Currency.code == code, 
            Currency.is_active == True
        ).first()
    
    @staticmethod
    def seed_default_currencies(db: Session):
        """Seed default currencies"""
        default_currencies = [
            {"code": "NGN", "name": "Nigerian Naira", "symbol": "₦", "rate_to_ngn": 1.0},
            {"code": "USD", "name": "US Dollar", "symbol": "$", "rate_to_ngn": 1600.0},
            {"code": "EUR", "name": "Euro", "symbol": "€", "rate_to_ngn": 1800.0},
            {"code": "GBP", "name": "British Pound", "symbol": "£", "rate_to_ngn": 2100.0},
        ]
        
        for curr_data in default_currencies:
            existing = db.query(Currency).filter(Currency.code == curr_data["code"]).first()
            if not existing:
                currency = Currency(**curr_data)
                db.add(currency)
        
        db.commit()