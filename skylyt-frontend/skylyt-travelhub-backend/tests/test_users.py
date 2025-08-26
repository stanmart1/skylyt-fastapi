import pytest
from fastapi.testclient import TestClient

class TestUsers:
    def test_get_current_user(self, client: TestClient, auth_headers, test_user):
        """Test getting current user profile."""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name

    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test getting current user without authentication."""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401

    def test_update_user_profile(self, client: TestClient, auth_headers, test_user):
        """Test updating user profile."""
        update_data = {
            "full_name": "Updated Name",
            "phone_number": "+9876543210"
        }
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["phone_number"] == "+9876543210"

    def test_get_user_bookings(self, client: TestClient, auth_headers, test_booking):
        """Test getting user bookings."""
        response = client.get("/api/v1/users/me/bookings", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["booking_reference"] == test_booking.booking_reference

    def test_get_user_bookings_empty(self, client: TestClient, auth_headers):
        """Test getting user bookings when none exist."""
        response = client.get("/api/v1/users/me/bookings", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_add_favorite(self, client: TestClient, auth_headers):
        """Test adding item to favorites."""
        favorite_data = {
            "item_type": "hotel",
            "item_id": "hotel123",
            "name": "Test Hotel"
        }
        response = client.post("/api/v1/users/me/favorites", json=favorite_data, headers=auth_headers)
        assert response.status_code == 201

    def test_get_favorites(self, client: TestClient, auth_headers):
        """Test getting user favorites."""
        response = client.get("/api/v1/users/me/favorites", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_delete_user_account(self, client: TestClient, auth_headers):
        """Test deleting user account."""
        response = client.delete("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200

    def test_invalid_token(self, client: TestClient):
        """Test request with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 401