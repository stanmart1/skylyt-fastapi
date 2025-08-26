from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import List, Dict, Optional, Any
from datetime import datetime, date
import uuid
import json

from app.models.booking import Booking
from app.models.user import User
from app.models.hotel import Hotel
from app.models.car import Car
from app.services.email_service import EmailService
from app.core.database import get_db


class BookingService:
    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService()

    def get_bookings_with_filters(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
        payment_status: Optional[str] = None,
        booking_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Get bookings with advanced filtering, search, and pagination"""
        query = self.db.query(Booking)
        
        # Search functionality
        if search:
            search_filter = or_(
                Booking.customer_name.ilike(f"%{search}%"),
                Booking.customer_email.ilike(f"%{search}%"),
                Booking.booking_reference.ilike(f"%{search}%"),
                Booking.hotel_name.ilike(f"%{search}%"),
                Booking.car_name.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Status filters
        if status:
            query = query.filter(Booking.status == status)
        if payment_status:
            query = query.filter(Booking.payment_status == payment_status)
        if booking_type:
            query = query.filter(Booking.booking_type == booking_type)
        
        # Date range filter
        if start_date:
            query = query.filter(Booking.start_date >= start_date)
        if end_date:
            query = query.filter(Booking.end_date <= end_date)
        
        # Sorting
        sort_column = getattr(Booking, sort_by, Booking.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Pagination
        total = query.count()
        offset = (page - 1) * per_page
        bookings = query.offset(offset).limit(per_page).all()
        
        return {
            "bookings": [self._serialize_booking(booking) for booking in bookings],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    def get_booking_details(self, booking_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed booking information with related data"""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return None
        
        booking_data = self._serialize_booking(booking)
        
        # Add related data
        if booking.booking_data:
            try:
                data = booking.booking_data if isinstance(booking.booking_data, dict) else json.loads(booking.booking_data)
                item_id = data.get('item_id')
                
                if booking.booking_type == 'hotel' and item_id:
                    hotel = self.db.query(Hotel).filter(Hotel.id == item_id).first()
                    if hotel:
                        booking_data['hotel_details'] = {
                            'name': hotel.name,
                            'location': hotel.location,
                            'rating': hotel.rating,
                            'amenities': hotel.amenities
                        }
                elif booking.booking_type == 'car' and item_id:
                    car = self.db.query(Car).filter(Car.id == item_id).first()
                    if car:
                        booking_data['car_details'] = {
                            'name': car.name,
                            'category': car.category,
                            'features': car.features
                        }
            except Exception as e:
                print(f"Error processing booking data: {e}")
        
        return booking_data

    def update_booking_status(self, booking_id: int, new_status: str, user_id: int) -> bool:
        """Update booking status with lifecycle management"""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return False
        
        old_status = booking.status
        booking.status = new_status
        
        # Log status change
        self._log_booking_history(booking_id, f"Status changed from {old_status} to {new_status}", user_id)
        
        # Trigger notifications based on status change
        if new_status == "confirmed":
            self.send_confirmation_email(booking_id)
        elif new_status == "cancelled":
            self.send_cancellation_email(booking_id)
        
        self.db.commit()
        return True

    def cancel_booking(self, booking_id: int, reason: str, user_id: int) -> bool:
        """Cancel booking with proper lifecycle management"""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return False
        
        booking.status = "cancelled"
        booking.special_requests = f"{booking.special_requests or ''}\nCancellation reason: {reason}".strip()
        
        self._log_booking_history(booking_id, f"Booking cancelled: {reason}", user_id)
        self.send_cancellation_email(booking_id)
        
        self.db.commit()
        return True

    def send_confirmation_email(self, booking_id: int) -> bool:
        """Send booking confirmation email"""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return False
        
        try:
            self.email_service.send_booking_confirmation(
                to_email=booking.customer_email,
                booking_reference=booking.booking_reference,
                customer_name=booking.customer_name,
                booking_details=self._serialize_booking(booking)
            )
            self._log_booking_history(booking_id, "Confirmation email sent", None)
            return True
        except Exception as e:
            print(f"Failed to send confirmation email: {e}")
            return False

    def send_cancellation_email(self, booking_id: int) -> bool:
        """Send booking cancellation email"""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return False
        
        try:
            self.email_service.send_booking_cancellation(
                to_email=booking.customer_email,
                booking_reference=booking.booking_reference,
                customer_name=booking.customer_name
            )
            self._log_booking_history(booking_id, "Cancellation email sent", None)
            return True
        except Exception as e:
            print(f"Failed to send cancellation email: {e}")
            return False

    def generate_invoice_data(self, booking_id: int) -> Optional[Dict[str, Any]]:
        """Generate invoice data for booking"""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return None
        
        return {
            "invoice_number": f"INV-{booking.booking_reference}",
            "booking_reference": booking.booking_reference,
            "customer_name": booking.customer_name,
            "customer_email": booking.customer_email,
            "booking_type": booking.booking_type,
            "hotel_name": booking.hotel_name,
            "car_name": booking.car_name,
            "check_in_date": booking.start_date.isoformat() if booking.start_date else None,
            "check_out_date": booking.end_date.isoformat() if booking.end_date else None,
            "total_amount": float(booking.total_amount),
            "currency": booking.currency,
            "payment_status": booking.payment_status,
            "created_at": booking.created_at.isoformat(),
            "special_requests": booking.special_requests
        }

    def _serialize_booking(self, booking: Booking) -> Dict[str, Any]:
        """Serialize booking object to dictionary"""
        return {
            "id": booking.id,
            "booking_reference": booking.booking_reference,
            "booking_type": booking.booking_type,
            "status": booking.status,
            "customer_name": booking.customer_name,
            "customer_email": booking.customer_email,
            "hotel_name": booking.hotel_name,
            "car_name": booking.car_name,
            "total_amount": float(booking.total_amount),
            "currency": booking.currency,
            "payment_status": booking.payment_status,
            "created_at": booking.created_at.isoformat(),
            "check_in_date": booking.start_date.isoformat() if booking.start_date else None,
            "check_out_date": booking.end_date.isoformat() if booking.end_date else None,
            "number_of_guests": booking.number_of_guests,
            "special_requests": booking.special_requests,
            "booking_data": booking.booking_data
        }

    def _log_booking_history(self, booking_id: int, action: str, user_id: Optional[int]):
        """Log booking history for audit trail"""
        # This would typically insert into a booking_history table
        # For now, we'll just print the log
        timestamp = datetime.utcnow().isoformat()
        user_info = f"User {user_id}" if user_id else "System"
        print(f"[{timestamp}] Booking {booking_id}: {action} by {user_info}")