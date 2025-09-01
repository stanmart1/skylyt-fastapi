from sqlalchemy import Column, String, Float, Index
from .base import BaseModel

class CurrencyRate(BaseModel):
    __tablename__ = "currency_rates"
    
    from_currency = Column(String(3), nullable=False, default="NGN")  # Always NGN as base
    to_currency = Column(String(3), nullable=False)  # USD, GBP, EUR
    rate = Column(Float, nullable=False)  # 1 NGN = rate * to_currency
    
    __table_args__ = (
        Index('idx_currency_pair', 'from_currency', 'to_currency', unique=True),
        {"extend_existing": True}
    )