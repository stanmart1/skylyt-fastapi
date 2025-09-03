"""
Serialization utilities for converting model objects to dictionaries
"""
from typing import Dict, Any
from datetime import datetime


def serialize_booking(booking) -> Dict[str, Any]:
    """Serialize booking object to dictionary"""
    return {
        "id": booking.id,
        "booking_reference": booking.booking_reference,
        "booking_type": booking.booking_type,
        "status": booking.status,
        "customer_name": booking.customer_name,
        "customer_email": booking.customer_email,
        "customer_phone": getattr(booking, 'customer_phone', None),
        "user_id": booking.user_id,
        "driver_id": getattr(booking, 'driver_id', None),
        "driver_name": getattr(booking.driver, 'name', None) if hasattr(booking, 'driver') and booking.driver else None,
        "hotel_name": booking.hotel_name,
        "car_name": booking.car_name,
        "car_id": getattr(booking, 'car_id', None),
        "check_in_date": booking.check_in_date,
        "check_out_date": booking.check_out_date,
        "start_date": booking.start_date,
        "end_date": booking.end_date,
        "number_of_guests": booking.number_of_guests,
        "special_requests": booking.special_requests,
        "total_amount": float(booking.total_amount) if booking.total_amount else 0,
        "currency": booking.currency,
        "payment_status": booking.payment_status,
        "external_booking_id": booking.external_booking_id,
        "confirmation_number": booking.confirmation_number,
        "booking_data": booking.booking_data,
        "created_at": booking.created_at.isoformat() if booking.created_at else None,
        "updated_at": booking.updated_at.isoformat() if booking.updated_at else None
    }


def serialize_payment(payment) -> Dict[str, Any]:
    """Serialize payment object to dictionary"""
    return {
        "id": payment.id,
        "booking_id": payment.booking_id,
        "amount": float(payment.amount),
        "currency": payment.currency,
        "status": payment.status.value,
        "payment_method": payment.payment_method.value,
        "created_at": payment.created_at.isoformat(),
        "transaction_id": payment.transaction_id,
        "transfer_reference": payment.transfer_reference
    }


def parse_date_string(date_str: str) -> datetime.date:
    """Parse ISO date string to date object"""
    from fastapi import HTTPException
    try:
        return datetime.fromisoformat(date_str).date()
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {date_str}")