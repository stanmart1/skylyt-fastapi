import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

class TestBookings:
    def test_create_booking(self, client: TestClient, auth_headers):
        """Test creating a new booking."""
        booking_data = {
            "booking_type": "hotel",
            "hotel_name": "Test Hotel",
            "room_type": "Standard",
            "check_in_date": "2024-06-01",
            "check_out_date": "2024-06-03",
            "guests": 2,
            "total_amount": 200.00,
            "currency": "USD"
        }
        response = client.post("/api/v1/bookings", json=booking_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["booking_type"] == "hotel"
        assert "booking_reference" in data

    def test_get_booking_details(self, client: TestClient, auth_headers, test_booking):
        """Test getting booking details."""
        response = client.get(f"/api/v1/bookings/{test_booking.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_booking.id
        assert data["booking_reference"] == test_booking.booking_reference

    def test_get_nonexistent_booking(self, client: TestClient, auth_headers):
        """Test getting nonexistent booking."""
        response = client.get("/api/v1/bookings/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_update_booking(self, client: TestClient, auth_headers, test_booking):
        """Test updating booking."""
        update_data = {
            "guests": 3,
            "room_type": "Deluxe"
        }
        response = client.put(f"/api/v1/bookings/{test_booking.id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["guests"] == 3
        assert data["room_type"] == "Deluxe"

    def test_cancel_booking(self, client: TestClient, auth_headers, test_booking):
        """Test cancelling booking."""
        response = client.delete(f"/api/v1/bookings/{test_booking.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

    def test_list_user_bookings(self, client: TestClient, auth_headers, test_booking):
        """Test listing user bookings."""
        response = client.get("/api/v1/bookings", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(b["id"] == test_booking.id for b in data)

    def test_resend_confirmation(self, client: TestClient, auth_headers, test_booking):
        """Test resending booking confirmation."""
        with patch('app.tasks.email_tasks.send_booking_confirmation_email.delay') as mock_email:
            response = client.post(f"/api/v1/bookings/{test_booking.id}/resend-confirmation", headers=auth_headers)
            assert response.status_code == 200
            mock_email.assert_called_once()

    def test_create_booking_invalid_dates(self, client: TestClient, auth_headers):
        """Test creating booking with invalid dates."""
        booking_data = {
            "booking_type": "hotel",
            "hotel_name": "Test Hotel",
            "check_in_date": "2024-06-03",
            "check_out_date": "2024-06-01",  # Check-out before check-in
            "guests": 2,
            "total_amount": 200.00,
            "currency": "USD"
        }
        response = client.post("/api/v1/bookings", json=booking_data, headers=auth_headers)
        assert response.status_code == 400

    def test_unauthorized_booking_access(self, client: TestClient, test_booking):
        """Test accessing booking without authentication."""
        response = client.get(f"/api/v1/bookings/{test_booking.id}")
        assert response.status_code == 401