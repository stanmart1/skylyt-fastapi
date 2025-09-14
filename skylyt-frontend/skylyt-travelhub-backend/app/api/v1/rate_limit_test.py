from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.services.rate_limit_service import rate_limit_service

router = APIRouter(prefix="/rate-limit", tags=["Rate Limit"])

@router.get("/status")
def get_rate_limit_status():
    """Get current rate limiting configuration"""
    settings = rate_limit_service.get_rate_limit_settings()
    return {
        "rate_limiting_enabled": settings["enabled"],
        "max_requests_per_window": settings["max_requests"],
        "window_seconds": settings["window_seconds"],
        "redis_available": rate_limit_service.redis_client is not None
    }

@router.get("/test")
def test_rate_limit():
    """Test endpoint for rate limiting"""
    return {
        "message": "Rate limit test successful",
        "timestamp": "2024-01-01T00:00:00Z"
    }