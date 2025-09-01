from pydantic import BaseModel, validator
from typing import Optional
from decimal import Decimal


class CurrencyBase(BaseModel):
    code: str
    name: str
    symbol: str
    rate_to_ngn: float
    is_active: bool = True
    
    @validator('code')
    def validate_code(cls, v):
        return v.upper()
    
    @validator('rate_to_ngn')
    def validate_rate(cls, v):
        if v <= 0:
            raise ValueError('Exchange rate must be positive')
        return v


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyUpdate(BaseModel):
    name: Optional[str] = None
    symbol: Optional[str] = None
    rate_to_ngn: Optional[float] = None
    is_active: Optional[bool] = None
    
    @validator('rate_to_ngn')
    def validate_rate(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Exchange rate must be positive')
        return v


class CurrencyResponse(CurrencyBase):
    id: int
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class CurrencyConversionRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str


class CurrencyConversionResponse(BaseModel):
    original_amount: float
    converted_amount: float
    from_currency: str
    to_currency: str
    exchange_rate: float


class BulkRateUpdate(BaseModel):
    updates: dict  # {currency_code: new_rate}