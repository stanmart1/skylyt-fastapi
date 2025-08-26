import pytest
from fastapi.testclient import TestClient
from app.services.auth_service import AuthService

class TestAuth:
    def test_register_user(self, client: TestClient):
        """Test user registration."""
        response = client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User",
            "phone_number": "+1234567890"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "access_token" in data

    def test_register_duplicate_email(self, client: TestClient, test_user):
        """Test registration with duplicate email."""
        response = client.post("/api/v1/auth/register", json={
            "email": test_user.email,
            "password": "password123",
            "full_name": "Another User",
            "phone_number": "+1234567891"
        })
        assert response.status_code == 400

    def test_login_valid_credentials(self, client: TestClient, test_user):
        """Test login with valid credentials."""
        response = client.post("/api/v1/auth/login", data={
            "username": test_user.email,
            "password": "testpassword123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client: TestClient, test_user):
        """Test login with invalid credentials."""
        response = client.post("/api/v1/auth/login", data={
            "username": test_user.email,
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with nonexistent user."""
        response = client.post("/api/v1/auth/login", data={
            "username": "nonexistent@example.com",
            "password": "password123"
        })
        assert response.status_code == 401

    def test_forgot_password(self, client: TestClient, test_user):
        """Test password reset request."""
        response = client.post("/api/v1/auth/forgot-password", json={
            "email": test_user.email
        })
        assert response.status_code == 200

    def test_forgot_password_nonexistent_email(self, client: TestClient):
        """Test password reset with nonexistent email."""
        response = client.post("/api/v1/auth/forgot-password", json={
            "email": "nonexistent@example.com"
        })
        assert response.status_code == 404

class TestAuthService:
    def test_create_access_token(self, db_session, test_user):
        """Test access token creation."""
        auth_service = AuthService(db_session)
        token = auth_service.create_access_token(data={"sub": str(test_user.id)})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_password(self, db_session, test_user):
        """Test password verification."""
        auth_service = AuthService(db_session)
        assert auth_service.verify_password("testpassword123", test_user.hashed_password)
        assert not auth_service.verify_password("wrongpassword", test_user.hashed_password)

    def test_authenticate_user(self, db_session, test_user):
        """Test user authentication."""
        auth_service = AuthService(db_session)
        user = auth_service.authenticate_user(test_user.email, "testpassword123")
        assert user is not None
        assert user.id == test_user.id
        
        user = auth_service.authenticate_user(test_user.email, "wrongpassword")
        assert user is None