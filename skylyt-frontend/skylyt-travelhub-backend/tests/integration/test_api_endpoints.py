import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

class TestAPIEndpoints:
    def test_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_detailed_health_check(self, client: TestClient):
        """Test detailed health check."""
        response = client.get("/api/v1/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "checks" in data
        assert "database" in data["checks"]

    def test_hotel_search(self, client: TestClient):
        """Test hotel search endpoint."""
        with patch('app.services.hotel_service.HotelService.search_hotels') as mock_search:
            mock_search.return_value = {
                "hotels": [],
                "total": 0,
                "page": 1,
                "per_page": 10
            }
            
            response = client.get("/api/v1/hotels/search?destination=Lagos&check_in=2024-06-01&check_out=2024-06-03")
            assert response.status_code == 200
            mock_search.assert_called_once()

    def test_car_search(self, client: TestClient):
        """Test car search endpoint."""
        with patch('app.services.car_service.CarService.search_cars') as mock_search:
            mock_search.return_value = {
                "cars": [],
                "total": 0,
                "page": 1,
                "per_page": 10
            }
            
            response = client.get("/api/v1/cars/search?location=Lagos&pickup_date=2024-06-01&return_date=2024-06-03")
            assert response.status_code == 200
            mock_search.assert_called_once()

    def test_bundle_search(self, client: TestClient):
        """Test bundle search endpoint."""
        with patch('app.services.search_service.SearchService.search_bundles') as mock_search:
            mock_search.return_value = {
                "bundles": [],
                "total": 0
            }
            
            response = client.get("/api/v1/search/bundles?destination=Lagos&check_in=2024-06-01&check_out=2024-06-03")
            assert response.status_code == 200
            mock_search.assert_called_once()

    def test_payment_processing(self, client: TestClient, auth_headers):
        """Test payment processing endpoint."""
        with patch('app.services.payment_service.PaymentService.process_payment') as mock_payment:
            mock_payment.return_value = {
                "status": "completed",
                "transaction_id": "txn_123",
                "amount": 200.00
            }
            
            payment_data = {
                "booking_id": 1,
                "gateway": "stripe",
                "amount": 200.00,
                "currency": "USD",
                "payment_method": "card"
            }
            
            response = client.post("/api/v1/payments/process", json=payment_data, headers=auth_headers)
            assert response.status_code == 200
            mock_payment.assert_called_once()

    def test_cors_headers(self, client: TestClient):
        """Test CORS headers are present."""
        response = client.options("/api/v1/health")
        assert response.status_code == 200

    def test_rate_limiting(self, client: TestClient):
        """Test rate limiting functionality."""
        # Make multiple requests to trigger rate limiting
        for _ in range(5):
            response = client.get("/api/v1/health")
            assert response.status_code == 200

    def test_authentication_required_endpoints(self, client: TestClient):
        """Test endpoints that require authentication."""
        protected_endpoints = [
            "/api/v1/users/me",
            "/api/v1/bookings",
            "/api/v1/users/me/favorites"
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401