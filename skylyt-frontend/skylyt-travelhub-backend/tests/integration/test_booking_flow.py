import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

class TestBookingFlow:
    def test_complete_booking_flow(self, client: TestClient, auth_headers):
        """Test complete booking flow from search to confirmation."""
        
        # Step 1: Search for hotels
        with patch('app.services.hotel_service.HotelService.search_hotels') as mock_search:
            mock_search.return_value = {
                "hotels": [{
                    "id": "hotel_123",
                    "name": "Test Hotel",
                    "price": 100.00,
                    "available": True
                }],
                "total": 1
            }
            
            search_response = client.get("/api/v1/hotels/search?destination=Lagos&check_in=2024-06-01&check_out=2024-06-03")
            assert search_response.status_code == 200
            hotels = search_response.json()["hotels"]
            assert len(hotels) == 1

        # Step 2: Check availability
        with patch('app.services.hotel_service.HotelService.check_availability') as mock_availability:
            mock_availability.return_value = {"available": True, "price": 200.00}
            
            availability_response = client.post("/api/v1/hotels/hotel_123/check-availability", json={
                "check_in_date": "2024-06-01",
                "check_out_date": "2024-06-03",
                "guests": 2
            })
            assert availability_response.status_code == 200
            assert availability_response.json()["available"] is True

        # Step 3: Create booking
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
        
        booking_response = client.post("/api/v1/bookings", json=booking_data, headers=auth_headers)
        assert booking_response.status_code == 201
        booking = booking_response.json()
        booking_id = booking["id"]

        # Step 4: Process payment
        with patch('app.services.payment_service.PaymentService.process_payment') as mock_payment:
            mock_payment.return_value = {
                "status": "completed",
                "transaction_id": "txn_123",
                "amount": 200.00
            }
            
            payment_data = {
                "booking_id": booking_id,
                "gateway": "stripe",
                "amount": 200.00,
                "currency": "USD",
                "payment_method": "card"
            }
            
            payment_response = client.post("/api/v1/payments/process", json=payment_data, headers=auth_headers)
            assert payment_response.status_code == 200
            assert payment_response.json()["status"] == "completed"

        # Step 5: Verify booking confirmation
        booking_details = client.get(f"/api/v1/bookings/{booking_id}", headers=auth_headers)
        assert booking_details.status_code == 200

    def test_booking_cancellation_flow(self, client: TestClient, auth_headers, test_booking):
        """Test booking cancellation flow."""
        
        # Cancel booking
        cancel_response = client.delete(f"/api/v1/bookings/{test_booking.id}", headers=auth_headers)
        assert cancel_response.status_code == 200
        assert cancel_response.json()["status"] == "cancelled"

        # Verify booking is cancelled
        booking_details = client.get(f"/api/v1/bookings/{test_booking.id}", headers=auth_headers)
        assert booking_details.status_code == 200
        assert booking_details.json()["status"] == "cancelled"

    def test_bundle_booking_flow(self, client: TestClient, auth_headers):
        """Test hotel + car bundle booking flow."""
        
        # Search for bundles
        with patch('app.services.search_service.SearchService.search_bundles') as mock_search:
            mock_search.return_value = {
                "bundles": [{
                    "hotel": {"id": "hotel_123", "name": "Test Hotel", "price": 150.00},
                    "car": {"id": "car_123", "name": "Test Car", "price": 50.00},
                    "total_price": 180.00,  # Discounted bundle price
                    "savings": 20.00
                }]
            }
            
            bundle_response = client.get("/api/v1/search/bundles?destination=Lagos&check_in=2024-06-01&check_out=2024-06-03")
            assert bundle_response.status_code == 200
            bundles = bundle_response.json()["bundles"]
            assert len(bundles) == 1
            assert bundles[0]["savings"] == 20.00

        # Create bundle booking
        bundle_booking_data = {
            "booking_type": "bundle",
            "hotel_name": "Test Hotel",
            "car_name": "Test Car",
            "check_in_date": "2024-06-01",
            "check_out_date": "2024-06-03",
            "total_amount": 180.00,
            "currency": "USD"
        }
        
        booking_response = client.post("/api/v1/bookings", json=bundle_booking_data, headers=auth_headers)
        assert booking_response.status_code == 201
        assert booking_response.json()["booking_type"] == "bundle"

    def test_failed_payment_flow(self, client: TestClient, auth_headers):
        """Test booking flow with failed payment."""
        
        # Create booking
        booking_data = {
            "booking_type": "hotel",
            "hotel_name": "Test Hotel",
            "total_amount": 200.00,
            "currency": "USD"
        }
        
        booking_response = client.post("/api/v1/bookings", json=booking_data, headers=auth_headers)
        booking_id = booking_response.json()["id"]

        # Attempt payment with failure
        with patch('app.services.payment_service.PaymentService.process_payment') as mock_payment:
            mock_payment.return_value = {
                "status": "failed",
                "error": "Card declined"
            }
            
            payment_data = {
                "booking_id": booking_id,
                "gateway": "stripe",
                "amount": 200.00,
                "currency": "USD"
            }
            
            payment_response = client.post("/api/v1/payments/process", json=payment_data, headers=auth_headers)
            assert payment_response.status_code == 400
            assert "failed" in payment_response.json()["detail"].lower()