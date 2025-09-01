from sqlalchemy import Column, String, Numeric, Boolean, Index
from .base import BaseModel


class Currency(BaseModel):
    __tablename__ = "currencies"
    
    code = Column(String(3), unique=True, nullable=False, index=True)  # USD, EUR, GBP, etc.
    name = Column(String(100), nullable=False)  # US Dollar, Euro, etc.
    symbol = Column(String(10), nullable=False)  # $, €, £, etc.
    rate_to_ngn = Column(Numeric(15, 6), nullable=False)  # Exchange rate to NGN
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('idx_currency_code_active', 'code', 'is_active'),
    )