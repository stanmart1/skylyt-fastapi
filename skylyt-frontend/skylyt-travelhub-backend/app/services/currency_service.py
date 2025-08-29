from typing import Dict, Optional
from decimal import Decimal
import httpx
from sqlalchemy.orm import Session
from app.models.currency import CurrencyRate
from app.core.config import settings
from app.utils.cache_manager import cache_manager


class CurrencyService:
    SUPPORTED_CURRENCIES = ['NGN', 'USD', 'GBP', 'EUR']
    DEFAULT_CURRENCY = 'NGN'
    
    @staticmethod
    def get_exchange_rate(db: Session, from_currency: str, to_currency: str) -> Decimal:
        if from_currency == to_currency:
            return Decimal('1.0')
        
        # Check cache first
        cache_key = f"rate_{from_currency}_{to_currency}"
        cached_rate = cache_manager.get(cache_key)
        if cached_rate:
            return Decimal(str(cached_rate))
        
        # Check database
        rate = db.query(CurrencyRate).filter(
            CurrencyRate.from_currency == from_currency,
            CurrencyRate.to_currency == to_currency
        ).first()
        
        if rate:
            cache_manager.set(cache_key, float(rate.rate), 300)  # 5 min cache
            return rate.rate
        
        return Decimal('1.0')  # Fallback
    
    @staticmethod
    def convert_amount(db: Session, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        rate = CurrencyService.get_exchange_rate(db, from_currency, to_currency)
        return amount * rate
    
    @staticmethod
    async def update_exchange_rates(db: Session):
        """Update rates from external API"""
        try:
            async with httpx.AsyncClient() as client:
                # Using exchangerate-api.com (free tier)
                response = await client.get(f"https://api.exchangerate-api.com/v4/latest/NGN")
                data = response.json()
                
                for currency in CurrencyService.SUPPORTED_CURRENCIES:
                    if currency != 'NGN':
                        rate = data['rates'].get(currency, 1.0)
                        
                        # Update or create rate
                        existing = db.query(CurrencyRate).filter(
                            CurrencyRate.from_currency == 'NGN',
                            CurrencyRate.to_currency == currency
                        ).first()
                        
                        if existing:
                            existing.rate = Decimal(str(rate))
                        else:
                            new_rate = CurrencyRate(
                                from_currency='NGN',
                                to_currency=currency,
                                rate=Decimal(str(rate))
                            )
                            db.add(new_rate)
                
                db.commit()
        except Exception as e:
            print(f"Failed to update exchange rates: {e}")
    
    @staticmethod
    def get_currency_symbol(currency_code: str) -> str:
        symbols = {
            'NGN': '₦',
            'USD': '$',
            'GBP': '£',
            'EUR': '€'
        }
        return symbols.get(currency_code, currency_code)