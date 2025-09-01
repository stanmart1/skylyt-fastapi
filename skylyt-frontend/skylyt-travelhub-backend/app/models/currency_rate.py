from sqlalchemy import Column, String, Float, Index
from .base import BaseModel

class CurrencyRate(BaseModel):
    __tablename__ = "currency_rates"
    
    base_currency = Column(String(3), nullable=False, default="NGN")  # Always NGN as base
    target_currency = Column(String(3), nullable=False)  # USD, GBP, EUR
    rate = Column(Float, nullable=False)  # 1 NGN = rate * target_currency
    
    __table_args__ = (
        Index('idx_currency_pair', 'base_currency', 'target_currency', unique=True),
        {"extend_existing": True}
    )