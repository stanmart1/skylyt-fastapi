from sqlalchemy import Column, String, Numeric, DateTime, Boolean
from sqlalchemy.sql import func
from .base import BaseModel


class CurrencyRate(BaseModel):
    __tablename__ = "currency_rates"
    
    from_currency = Column(String(3), nullable=False)
    to_currency = Column(String(3), nullable=False)
    rate = Column(Numeric(10, 4), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Country(BaseModel):
    __tablename__ = "countries"
    
    code = Column(String(2), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    currency_code = Column(String(3), nullable=False)
    is_supported = Column(Boolean, default=False)