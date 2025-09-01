from typing import Dict, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.currency_rate import CurrencyRate
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
        
        # Manual rates using NGN as base
        if from_currency == 'NGN':
            rate = db.query(CurrencyRate).filter(
                CurrencyRate.base_currency == 'NGN',
                CurrencyRate.target_currency == to_currency
            ).first()
            if rate:
                cache_manager.set(cache_key, float(rate.rate), 300)
                return Decimal(str(rate.rate))
        elif to_currency == 'NGN':
            rate = db.query(CurrencyRate).filter(
                CurrencyRate.base_currency == 'NGN',
                CurrencyRate.target_currency == from_currency
            ).first()
            if rate:
                reverse_rate = 1 / rate.rate
                cache_manager.set(cache_key, float(reverse_rate), 300)
                return Decimal(str(reverse_rate))
        else:
            # Convert via NGN pivot
            from_rate = db.query(CurrencyRate).filter(
                CurrencyRate.base_currency == 'NGN',
                CurrencyRate.target_currency == from_currency
            ).first()
            to_rate = db.query(CurrencyRate).filter(
                CurrencyRate.base_currency == 'NGN',
                CurrencyRate.target_currency == to_currency
            ).first()
            if from_rate and to_rate:
                # from_currency -> NGN -> to_currency
                final_rate = to_rate.rate / from_rate.rate
                cache_manager.set(cache_key, float(final_rate), 300)
                return Decimal(str(final_rate))
        
        return Decimal('1.0')
    
    @staticmethod
    def convert_amount(db: Session, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        if from_currency == to_currency:
            return amount
        
        rate = CurrencyService.get_exchange_rate(db, from_currency, to_currency)
        return amount * rate
    
    @staticmethod
    async def update_exchange_rates(db: Session):
        """Manual rates - no external API needed"""
        # Manual rates are managed through admin interface
        pass
    
    @staticmethod
    def get_currency_symbol(currency_code: str) -> str:
        symbols = {
            'NGN': '₦',
            'USD': '$',
            'GBP': '£',
            'EUR': '€'
        }
        return symbols.get(currency_code, currency_code)