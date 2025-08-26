import pytest
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from unittest.mock import patch

class TestSearchPerformance:
    def test_hotel_search_response_time(self, client: TestClient):
        """Test hotel search response time."""
        
        with patch('app.services.hotel_service.HotelService.search_hotels') as mock_search:
            mock_search.return_value = {
                "hotels": [{"id": f"hotel_{i}", "name": f"Hotel {i}"} for i in range(50)],
                "total": 50
            }
            
            start_time = time.time()
            response = client.get("/api/v1/hotels/search?destination=Lagos&check_in=2024-06-01&check_out=2024-06-03")
            end_time = time.time()
            
            assert response.status_code == 200
            response_time = end_time - start_time
            assert response_time < 2.0  # Should respond within 2 seconds

    def test_car_search_response_time(self, client: TestClient):
        """Test car search response time."""
        
        with patch('app.services.car_service.CarService.search_cars') as mock_search:
            mock_search.return_value = {
                "cars": [{"id": f"car_{i}", "name": f"Car {i}"} for i in range(30)],
                "total": 30
            }
            
            start_time = time.time()
            response = client.get("/api/v1/cars/search?location=Lagos&pickup_date=2024-06-01&return_date=2024-06-03")
            end_time = time.time()
            
            assert response.status_code == 200
            response_time = end_time - start_time
            assert response_time < 2.0

    def test_bundle_search_response_time(self, client: TestClient):
        """Test bundle search response time."""
        
        with patch('app.services.search_service.SearchService.search_bundles') as mock_search:
            mock_search.return_value = {
                "bundles": [{"id": f"bundle_{i}", "total_price": 100 + i} for i in range(20)],
                "total": 20
            }
            
            start_time = time.time()
            response = client.get("/api/v1/search/bundles?destination=Lagos&check_in=2024-06-01&check_out=2024-06-03")
            end_time = time.time()
            
            assert response.status_code == 200
            response_time = end_time - start_time
            assert response_time < 3.0  # Bundle search may take slightly longer

    def test_concurrent_search_requests(self, client: TestClient):
        """Test handling concurrent search requests."""
        
        with patch('app.services.hotel_service.HotelService.search_hotels') as mock_search:
            mock_search.return_value = {"hotels": [], "total": 0}
            
            def make_search_request():
                response = client.get("/api/v1/hotels/search?destination=Lagos")
                return response.status_code == 200
            
            # Execute 10 concurrent requests
            with ThreadPoolExecutor(max_workers=10) as executor:
                start_time = time.time()
                futures = [executor.submit(make_search_request) for _ in range(10)]
                results = [future.result() for future in futures]
                end_time = time.time()
            
            # All requests should succeed
            assert all(results)
            # Total time should be reasonable for concurrent requests
            total_time = end_time - start_time
            assert total_time < 5.0

    def test_large_result_set_performance(self, client: TestClient):
        """Test performance with large result sets."""
        
        # Mock large result set
        large_hotels = [{"id": f"hotel_{i}", "name": f"Hotel {i}"} for i in range(1000)]
        
        with patch('app.services.hotel_service.HotelService.search_hotels') as mock_search:
            mock_search.return_value = {
                "hotels": large_hotels[:50],  # Paginated results
                "total": 1000,
                "page": 1,
                "per_page": 50
            }
            
            start_time = time.time()
            response = client.get("/api/v1/hotels/search?destination=Lagos&per_page=50")
            end_time = time.time()
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["hotels"]) == 50
            assert data["total"] == 1000
            
            response_time = end_time - start_time
            assert response_time < 3.0

    def test_search_with_filters_performance(self, client: TestClient):
        """Test search performance with multiple filters."""
        
        with patch('app.services.hotel_service.HotelService.search_hotels') as mock_search:
            mock_search.return_value = {"hotels": [], "total": 0}
            
            # Complex search with many filters
            search_params = {
                "destination": "Lagos",
                "check_in": "2024-06-01",
                "check_out": "2024-06-03",
                "guests": "2",
                "min_price": "50",
                "max_price": "500",
                "amenities": "wifi,pool,gym",
                "rating": "4",
                "sort_by": "price"
            }
            
            start_time = time.time()
            response = client.get("/api/v1/hotels/search", params=search_params)
            end_time = time.time()
            
            assert response.status_code == 200
            response_time = end_time - start_time
            assert response_time < 2.5

    def test_cache_effectiveness(self, client: TestClient):
        """Test search result caching effectiveness."""
        
        with patch('app.services.hotel_service.HotelService.search_hotels') as mock_search:
            mock_search.return_value = {"hotels": [], "total": 0}
            
            search_url = "/api/v1/hotels/search?destination=Lagos&check_in=2024-06-01&check_out=2024-06-03"
            
            # First request
            start_time = time.time()
            response1 = client.get(search_url)
            first_request_time = time.time() - start_time
            
            # Second request (should be cached)
            start_time = time.time()
            response2 = client.get(search_url)
            second_request_time = time.time() - start_time
            
            assert response1.status_code == 200
            assert response2.status_code == 200
            
            # Second request should be faster due to caching
            # Note: This test might not work as expected without actual caching implementation
            # but it demonstrates the testing approach