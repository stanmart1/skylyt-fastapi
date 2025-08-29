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
        
        # Fallback rates if not in database
        fallback_rates = {
            ('NGN', 'USD'): Decimal('0.0012'),
            ('NGN', 'GBP'): Decimal('0.001'),
            ('NGN', 'EUR'): Decimal('0.0011'),
            ('USD', 'NGN'): Decimal('830.0'),
            ('GBP', 'NGN'): Decimal('1000.0'),
            ('EUR', 'NGN'): Decimal('910.0'),
            ('USD', 'GBP'): Decimal('0.83'),
            ('USD', 'EUR'): Decimal('0.92'),
            ('GBP', 'USD'): Decimal('1.2'),
            ('GBP', 'EUR'): Decimal('1.1'),
            ('EUR', 'USD'): Decimal('1.08'),
            ('EUR', 'GBP'): Decimal('0.91')
        }
        
        return fallback_rates.get((from_currency, to_currency), Decimal('1.0'))
    
    @staticmethod
    def convert_amount(db: Session, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        if from_currency == to_currency:
            return amount
        
        # Convert via NGN if needed
        if from_currency == 'NGN':
            rate = CurrencyService.get_exchange_rate(db, from_currency, to_currency)
            return amount * rate
        elif to_currency == 'NGN':
            rate = CurrencyService.get_exchange_rate(db, from_currency, to_currency)
            return amount * rate
        else:
            # Convert from_currency -> NGN -> to_currency
            to_ngn_rate = CurrencyService.get_exchange_rate(db, from_currency, 'NGN')
            from_ngn_rate = CurrencyService.get_exchange_rate(db, 'NGN', to_currency)
            return amount * to_ngn_rate * from_ngn_rate
    
    @staticmethod
    async def update_exchange_rates(db: Session):
        """Update rates from external API"""
        try:
            async with httpx.AsyncClient() as client:
                # Use the correct API key
                api_key = "74288c9c5ac689c0174bad7a"
                
                # Get NGN rates
                response = await client.get(f"https://v6.exchangerate-api.com/v6/{api_key}/latest/NGN")
                
                data = response.json()
                rates = data.get('conversion_rates', {})
                
                # Store NGN to other currencies
                for currency in CurrencyService.SUPPORTED_CURRENCIES:
                    if currency != 'NGN':
                        rate = rates.get(currency, 1.0)
                        
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
                        
                        # Store reverse rate
                        reverse_rate = 1 / rate if rate > 0 else 1.0
                        existing_reverse = db.query(CurrencyRate).filter(
                            CurrencyRate.from_currency == currency,
                            CurrencyRate.to_currency == 'NGN'
                        ).first()
                        
                        if existing_reverse:
                            existing_reverse.rate = Decimal(str(reverse_rate))
                        else:
                            reverse_new = CurrencyRate(
                                from_currency=currency,
                                to_currency='NGN',
                                rate=Decimal(str(reverse_rate))
                            )
                            db.add(reverse_new)
                
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