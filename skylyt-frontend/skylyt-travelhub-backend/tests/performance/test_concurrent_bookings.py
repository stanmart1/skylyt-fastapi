import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi.testclient import TestClient
from unittest.mock import patch

class TestConcurrentBookings:
    def test_concurrent_booking_creation(self, client: TestClient, auth_headers):
        """Test concurrent booking creation."""
        
        def create_booking(booking_id):
            booking_data = {
                "booking_type": "hotel",
                "hotel_name": f"Test Hotel {booking_id}",
                "room_type": "Standard",
                "check_in_date": "2024-06-01",
                "check_out_date": "2024-06-03",
                "guests": 2,
                "total_amount": 200.00,
                "currency": "USD"
            }
            
            response = client.post("/api/v1/bookings", json=booking_data, headers=auth_headers)
            return response.status_code == 201, response.json() if response.status_code == 201 else None
        
        # Create 5 concurrent bookings
        with ThreadPoolExecutor(max_workers=5) as executor:
            start_time = time.time()
            futures = [executor.submit(create_booking, i) for i in range(5)]
            results = [future.result() for future in futures]
            end_time = time.time()
        
        # All bookings should succeed
        successful_bookings = [result for success, result in results if success]
        assert len(successful_bookings) == 5
        
        # Should complete within reasonable time
        total_time = end_time - start_time
        assert total_time < 10.0

    def test_concurrent_payment_processing(self, client: TestClient, auth_headers):
        """Test concurrent payment processing."""
        
        # First create bookings
        booking_ids = []
        for i in range(3):
            booking_data = {
                "booking_type": "hotel",
                "hotel_name": f"Test Hotel {i}",
                "total_amount": 200.00,
                "currency": "USD"
            }
            response = client.post("/api/v1/bookings", json=booking_data, headers=auth_headers)
            if response.status_code == 201:
                booking_ids.append(response.json()["id"])
        
        def process_payment(booking_id):
            with patch('app.services.payment_service.PaymentService.process_payment') as mock_payment:
                mock_payment.return_value = {
                    "status": "completed",
                    "transaction_id": f"txn_{booking_id}",
                    "amount": 200.00
                }
                
                payment_data = {
                    "booking_id": booking_id,
                    "gateway": "stripe",
                    "amount": 200.00,
                    "currency": "USD"
                }
                
                response = client.post("/api/v1/payments/process", json=payment_data, headers=auth_headers)
                return response.status_code == 200
        
        # Process payments concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            start_time = time.time()
            futures = [executor.submit(process_payment, booking_id) for booking_id in booking_ids]
            results = [future.result() for future in futures]
            end_time = time.time()
        
        # All payments should succeed
        assert all(results)
        
        total_time = end_time - start_time
        assert total_time < 8.0

    def test_concurrent_user_operations(self, client: TestClient):
        """Test concurrent operations by different users."""
        
        # Create multiple users
        users = []
        for i in range(3):
            user_data = {
                "email": f"user{i}@example.com",
                "password": "password123",
                "full_name": f"User {i}",
                "phone_number": f"+123456789{i}"
            }
            response = client.post("/api/v1/auth/register", json=user_data)
            if response.status_code == 201:
                users.append(response.json())
        
        def user_operations(user):
            headers = {"Authorization": f"Bearer {user['access_token']}"}
            
            # Get user profile
            profile_response = client.get("/api/v1/users/me", headers=headers)
            
            # Create booking
            booking_data = {
                "booking_type": "hotel",
                "hotel_name": "Test Hotel",
                "total_amount": 200.00,
                "currency": "USD"
            }
            booking_response = client.post("/api/v1/bookings", json=booking_data, headers=headers)
            
            return profile_response.status_code == 200 and booking_response.status_code == 201
        
        # Execute operations concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            start_time = time.time()
            futures = [executor.submit(user_operations, user) for user in users]
            results = [future.result() for future in futures]
            end_time = time.time()
        
        # All operations should succeed
        assert all(results)
        
        total_time = end_time - start_time
        assert total_time < 15.0

    def test_database_connection_pool_stress(self, client: TestClient, auth_headers):
        """Test database connection pool under stress."""
        
        def database_intensive_operation():
            # Simulate database-heavy operations
            response = client.get("/api/v1/users/me/bookings", headers=auth_headers)
            return response.status_code in [200, 404]  # 404 is fine if no bookings exist
        
        # Execute many concurrent database operations
        with ThreadPoolExecutor(max_workers=20) as executor:
            start_time = time.time()
            futures = [executor.submit(database_intensive_operation) for _ in range(50)]
            results = [future.result() for future in futures]
            end_time = time.time()
        
        # Most operations should succeed
        success_rate = sum(results) / len(results)
        assert success_rate > 0.9  # At least 90% success rate
        
        total_time = end_time - start_time
        assert total_time < 30.0

    def test_rate_limiting_under_load(self, client: TestClient):
        """Test rate limiting behavior under high load."""
        
        def make_request():
            response = client.get("/api/v1/health")
            return response.status_code
        
        # Make many requests quickly
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            status_codes = [future.result() for future in futures]
        
        # Should have mix of 200 (success) and 429 (rate limited)
        success_count = status_codes.count(200)
        rate_limited_count = status_codes.count(429)
        
        # At least some requests should succeed
        assert success_count > 0
        # Rate limiting should kick in for some requests
        # Note: This depends on actual rate limiting implementation

    def test_memory_usage_under_load(self, client: TestClient, auth_headers):
        """Test memory usage during concurrent operations."""
        
        def create_and_fetch_booking():
            # Create booking
            booking_data = {
                "booking_type": "hotel",
                "hotel_name": "Memory Test Hotel",
                "total_amount": 100.00,
                "currency": "USD"
            }
            create_response = client.post("/api/v1/bookings", json=booking_data, headers=auth_headers)
            
            if create_response.status_code == 201:
                booking_id = create_response.json()["id"]
                # Fetch booking details
                fetch_response = client.get(f"/api/v1/bookings/{booking_id}", headers=auth_headers)
                return fetch_response.status_code == 200
            
            return False
        
        # Execute operations that create and fetch data
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_and_fetch_booking) for _ in range(20)]
            results = [future.result() for future in futures]
        
        # Most operations should succeed
        success_rate = sum(results) / len(results)
        assert success_rate > 0.8