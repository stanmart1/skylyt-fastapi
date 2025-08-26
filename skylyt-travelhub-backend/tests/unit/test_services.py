import pytest
from unittest.mock import Mock, patch
from app.services.user_service import UserService
from app.services.booking_service import BookingService
from app.services.payment_service import PaymentService
from app.models.user import User
from app.models.booking import Booking

class TestUserService:
    def test_create_user(self, db_session):
        """Test user creation."""
        user_service = UserService(db_session)
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User",
            "phone_number": "+1234567890"
        }
        
        user = user_service.create_user(user_data)
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.check_password("password123")

    def test_get_user_by_email(self, db_session, test_user):
        """Test getting user by email."""
        user_service = UserService(db_session)
        found_user = user_service.get_user_by_email(test_user.email)
        assert found_user is not None
        assert found_user.id == test_user.id

    def test_update_user(self, db_session, test_user):
        """Test updating user."""
        user_service = UserService(db_session)
        update_data = {"full_name": "Updated Name"}
        
        updated_user = user_service.update_user(test_user.id, update_data)
        assert updated_user.full_name == "Updated Name"

class TestBookingService:
    def test_create_booking(self, db_session, test_user):
        """Test booking creation."""
        booking_service = BookingService(db_session)
        booking_data = {
            "user_id": test_user.id,
            "booking_type": "hotel",
            "hotel_name": "Test Hotel",
            "total_amount": 200.00,
            "currency": "USD"
        }
        
        booking = booking_service.create_booking(booking_data)
        assert booking.user_id == test_user.id
        assert booking.hotel_name == "Test Hotel"
        assert booking.status == "pending"

    def test_get_user_bookings(self, db_session, test_booking):
        """Test getting user bookings."""
        booking_service = BookingService(db_session)
        bookings = booking_service.get_user_bookings(test_booking.user_id)
        assert len(bookings) >= 1
        assert any(b.id == test_booking.id for b in bookings)

    def test_cancel_booking(self, db_session, test_booking):
        """Test booking cancellation."""
        booking_service = BookingService(db_session)
        cancelled_booking = booking_service.cancel_booking(test_booking.id, "User request")
        assert cancelled_booking.status == "cancelled"
        assert cancelled_booking.cancellation_reason == "User request"

class TestPaymentService:
    def test_create_payment_record(self, db_session, test_booking):
        """Test payment record creation."""
        payment_service = PaymentService(db_session)
        payment_data = {
            "booking_id": test_booking.id,
            "gateway": "stripe",
            "amount": 200.00,
            "currency": "USD",
            "transaction_id": "txn_123"
        }
        
        payment = payment_service.create_payment_record(payment_data)
        assert payment.booking_id == test_booking.id
        assert payment.gateway == "stripe"
        assert payment.amount == 200.00

    @patch('app.external.payment.stripe_client.StripeClient.create_payment_intent')
    def test_process_stripe_payment(self, mock_stripe, db_session, test_booking):
        """Test Stripe payment processing."""
        mock_stripe.return_value = {
            "id": "pi_test123",
            "status": "succeeded",
            "amount": 20000
        }
        
        payment_service = PaymentService(db_session)
        result = payment_service.process_payment({
            "booking_id": test_booking.id,
            "gateway": "stripe",
            "amount": 200.00,
            "currency": "USD"
        })
        
        assert result["status"] == "completed"
        mock_stripe.assert_called_once()

    def test_validate_payment_amount(self, db_session, test_booking):
        """Test payment amount validation."""
        payment_service = PaymentService(db_session)
        
        # Valid amount
        assert payment_service.validate_payment_amount(test_booking.id, test_booking.total_amount)
        
        # Invalid amount
        assert not payment_service.validate_payment_amount(test_booking.id, 100.00)