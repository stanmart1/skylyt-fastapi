from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_optional
from app.schemas.booking import BookingCreate, BookingResponse, BookingUpdate
from app.services.booking_service import BookingService
from app.services.email_service import EmailService

router = APIRouter(prefix="/bookings", tags=["bookings"])
email_service = EmailService()


@router.post("")
def create_booking(
    booking_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Create new booking"""
    try:
        from app.models.booking import Booking
        import uuid
        import json
        
        # Extract guest info from booking_data
        guest_data = booking_data.get('booking_data', {})
        
        # Create booking with user_id if authenticated, otherwise guest booking
        booking = Booking(
            user_id=current_user.id if current_user else None,
            booking_type=booking_data.get('booking_type'),
            booking_data=booking_data.get('booking_data'),
            start_date=booking_data.get('start_date'),
            end_date=booking_data.get('end_date'),
            total_amount=booking_data.get('total_amount'),
            currency=booking_data.get('currency', 'USD'),
            status='pending',
            booking_reference=f"BK{uuid.uuid4().hex[:8].upper()}",
            customer_name=guest_data.get('guest_name', '') if not current_user else f"{current_user.first_name} {current_user.last_name}",
            customer_email=guest_data.get('guest_email', '') if not current_user else current_user.email,
            special_requests=guest_data.get('special_requests', '')
        )
        
        db.add(booking)
        db.commit()
        db.refresh(booking)
        
        # Send confirmation email immediately after booking creation
        try:
            customer_email = guest_data.get('guest_email', '') if not current_user else current_user.email
            customer_name = guest_data.get('guest_name', '') if not current_user else f"{current_user.first_name} {current_user.last_name}"
            
            email_service.send_booking_confirmation(
                customer_email,
                {
                    "user_name": customer_name,
                    "booking_reference": booking.booking_reference,
                    "booking_type": booking.booking_type,
                    "hotel_name": booking.booking_data.get("hotel", {}).get("name") if booking.booking_type == "hotel" else None,
                    "car_name": booking.booking_data.get("car", {}).get("name") if booking.booking_type == "car" else None,
                    "room_type": booking.booking_data.get("hotel", {}).get("room_type", "Standard"),
                    "check_in_date": booking.start_date.strftime("%B %d, %Y") if booking.start_date else "",
                    "check_out_date": booking.end_date.strftime("%B %d, %Y") if booking.end_date else "",
                    "guests": booking.booking_data.get("guests", 1),
                    "total_amount": float(booking.total_amount),
                    "currency": booking.currency
                }
            )
        except Exception as e:
            print(f"Email sending failed: {e}")  # Don't fail booking if email fails
        
        return {
            "id": booking.id,
            "booking_reference": booking.booking_reference,
            "status": booking.status,
            "total_amount": float(booking.total_amount)
        }
        
    except Exception as e:
        import traceback
        print(f"Booking creation error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Booking creation failed: {str(e)}")


@router.get("", response_model=List[BookingResponse])
def list_user_bookings(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user bookings"""
    from app.services.user_service import UserService
    return UserService.get_user_bookings(db, current_user.id)


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking_details(
    booking_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get booking details"""
    from app.models.booking import Booking
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return booking


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int,
    booking_update: BookingUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update booking"""
    update_data = booking_update.dict(exclude_unset=True)
    booking = BookingService.update_booking(db, booking_id, update_data)
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return booking


@router.delete("/{booking_id}")
def cancel_booking(
    booking_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel booking"""
    success = BookingService.cancel_booking(db, booking_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return {"message": "Booking cancelled successfully"}


@router.post("/{booking_id}/resend-confirmation")
def resend_confirmation(
    booking_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resend booking confirmation"""
    from app.models.booking import Booking
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    email_service.send_booking_confirmation(
        current_user.email,
        {
            "confirmation_number": booking.confirmation_number,
            "booking_type": booking.booking_type.value,
            "total_amount": float(booking.total_amount),
            "start_date": booking.start_date.isoformat(),
            "end_date": booking.end_date.isoformat()
        }
    )
    
    return {"message": "Confirmation email sent"}


@router.post("/{booking_id}/complete")
def complete_booking(
    booking_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark booking as completed and send completion email"""
    from app.models.booking import Booking, BookingStatus
    
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status != BookingStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="Booking must be confirmed to complete")
    
    # Update booking status
    booking.status = "completed"
    db.commit()
    
    # Send completion email
    email_service.send_booking_completion(
        current_user.email,
        {
            "user_name": f"{current_user.first_name} {current_user.last_name}",
            "booking_reference": booking.confirmation_number,
            "booking_type": booking.booking_type.value,
            "hotel_name": booking.booking_data.get("hotel", {}).get("name") if booking.booking_type.value == "hotel" else None,
            "car_name": booking.booking_data.get("car", {}).get("name") if booking.booking_type.value == "car" else None,
            "check_in_date": booking.start_date.strftime("%B %d, %Y"),
            "check_out_date": booking.end_date.strftime("%B %d, %Y"),
            "total_amount": float(booking.total_amount),
            "currency": booking.currency
        }
    )
    
    return {"message": "Booking completed successfully"}


@router.post("/{booking_id}/resend-confirmation")
def resend_booking_confirmation(
    booking_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resend booking confirmation email"""
    from app.models.booking import Booking
    
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Send confirmation email
    email_service.send_booking_confirmation(
        current_user.email,
        {
            "user_name": f"{current_user.first_name} {current_user.last_name}",
            "booking_reference": booking.confirmation_number,
            "booking_type": booking.booking_type.value,
            "hotel_name": booking.booking_data.get("hotel", {}).get("name") if booking.booking_type.value == "hotel" else None,
            "car_name": booking.booking_data.get("car", {}).get("name") if booking.booking_type.value == "car" else None,
            "check_in_date": booking.start_date.strftime("%B %d, %Y"),
            "check_out_date": booking.end_date.strftime("%B %d, %Y"),
            "total_amount": float(booking.total_amount),
            "currency": booking.currency
        }
    )
    
    return {"message": "Confirmation email sent successfully"}


@router.put("/{booking_id}/update")
def update_booking_details(
    booking_id: int,
    update_data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update booking details"""
    from app.models.booking import Booking
    
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Update allowed fields
    allowed_fields = ['special_requests', 'customer_name', 'customer_email']
    for field, value in update_data.items():
        if field in allowed_fields and hasattr(booking, field):
            setattr(booking, field, value)
    
    db.commit()
    db.refresh(booking)
    
    return {
        "id": booking.id,
        "booking_reference": booking.booking_reference,
        "message": "Booking updated successfully"
    }


@router.get("/summary/{item_type}/{item_id}")
def get_booking_summary(
    item_type: str,
    item_id: str,
    currency: str = Query("NGN", description="Currency code"),
    db: Session = Depends(get_db)
):
    """Get booking summary for an item with currency conversion"""
    if item_type not in ['car', 'hotel']:
        raise HTTPException(status_code=400, detail="Invalid item type")
    
    try:
        if item_type == 'car':
            from app.models.car import Car
            item = db.query(Car).filter(Car.id == item_id).first()
        else:
            from app.models.hotel import Hotel
            item = db.query(Hotel).filter(Hotel.id == item_id).first()
        
        if not item:
            raise HTTPException(status_code=404, detail=f"{item_type.title()} not found")
        
        from app.services.currency_service import CurrencyService
        
        if item_type == 'car':
            base_price = float(item.price_per_day)
            base_currency = getattr(item, 'base_currency', 'NGN')
            
            converted_price = CurrencyService.convert_currency(
                base_price, base_currency, currency.upper(), db
            )
            
            curr_obj = CurrencyService.get_currency_by_code(currency.upper(), db)
            symbol = curr_obj.symbol if curr_obj else currency.upper()
            
            return {
                "id": str(item.id),
                "name": item.name,
                "price": converted_price,
                "currency": currency.upper(),
                "currency_symbol": symbol,
                "image_url": item.images[0] if item.images else None,
                "rating": 4.5,
                "passengers": item.seats,
                "transmission": item.transmission,
                "features": item.features or []
            }
        else:
            base_price = float(item.price_per_night)
            base_currency = getattr(item, 'base_currency', 'NGN')
            
            converted_price = CurrencyService.convert_currency(
                base_price, base_currency, currency.upper(), db
            )
            
            curr_obj = CurrencyService.get_currency_by_code(currency.upper(), db)
            symbol = curr_obj.symbol if curr_obj else currency.upper()
            
            return {
                "id": str(item.id),
                "name": item.name,
                "price": converted_price,
                "currency": currency.upper(),
                "currency_symbol": symbol,
                "image_url": item.images[0] if item.images else None,
                "rating": float(item.star_rating),
                "location": item.location,
                "amenities": item.amenities or []
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch booking summary")