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
                # Get rates for all currencies using API key
                api_key = settings.EXCHANGE_RATE_API_KEY
                if api_key:
                    base_url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest"
                else:
                    base_url = "https://api.exchangerate-api.com/v4/latest"
                
                for base_currency in CurrencyService.SUPPORTED_CURRENCIES:
                    response = await client.get(f"{base_url}/{base_currency}")
                    data = response.json()
                    
                    for target_currency in CurrencyService.SUPPORTED_CURRENCIES:
                        if base_currency != target_currency:
                            rate = data['rates'].get(target_currency, 1.0)
                            
                            existing = db.query(CurrencyRate).filter(
                                CurrencyRate.from_currency == base_currency,
                                CurrencyRate.to_currency == target_currency
                            ).first()
                            
                            if existing:
                                existing.rate = Decimal(str(rate))
                            else:
                                new_rate = CurrencyRate(
                                    from_currency=base_currency,
                                    to_currency=target_currency,
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