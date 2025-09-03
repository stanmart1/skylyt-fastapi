"""
Validation utilities for business logic validation
"""
from fastapi import HTTPException

# Constants
VALID_BOOKING_STATUSES = ["pending", "confirmed", "cancelled", "payment_pending"]
VALID_CURRENCIES = ["USD", "EUR", "GBP", "NGN", "CAD", "AUD"]


def validate_financial_data(amount: float, currency: str) -> None:
    """Validate financial data"""
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    if currency not in VALID_CURRENCIES:
        raise HTTPException(status_code=400, detail=f"Invalid currency. Must be one of: {', '.join(VALID_CURRENCIES)}")


def validate_booking_status(status: str) -> None:
    """Validate booking status"""
    if status not in VALID_BOOKING_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(VALID_BOOKING_STATUSES)}")