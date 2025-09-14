from sqlalchemy.orm import Session
from app.models.settings import Settings
from app.core.database import SessionLocal
from app.core.redis import RedisService
from app.middleware.rate_limit import RateLimiter
from fastapi import Request
import logging

logger = logging.getLogger(__name__)

class RateLimitService:
    def __init__(self):
        self.redis_client = None
        self.limiter = None
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis client and rate limiter"""
        try:
            self.redis_client = RedisService.get_client()
            self.limiter = RateLimiter(self.redis_client)
        except Exception as e:
            logger.warning(f"Failed to initialize Redis for rate limiting: {e}")
    
    def get_rate_limit_settings(self) -> dict:
        """Get current rate limit settings from database"""
        db = SessionLocal()
        try:
            settings = db.query(Settings).first()
            if not settings:
                return {
                    "enabled": True,
                    "max_requests": 100,
                    "window_seconds": 60
                }
            
            return {
                "enabled": getattr(settings, 'api_rate_limit_enabled', True),
                "max_requests": int(getattr(settings, 'api_rate_limit_requests', '100')),
                "window_seconds": int(getattr(settings, 'api_rate_limit_window', '60'))
            }
        except Exception as e:
            logger.error(f"Failed to get rate limit settings: {e}")
            return {
                "enabled": True,
                "max_requests": 100,
                "window_seconds": 60
            }
        finally:
            db.close()
    
    async def check_rate_limit(self, request: Request) -> bool:
        """Check if request should be rate limited"""
        if not self.limiter or not self.redis_client:
            return True  # Allow if Redis is not available
        
        settings = self.get_rate_limit_settings()
        
        # If rate limiting is disabled, allow all requests
        if not settings["enabled"]:
            return True
        
        # Apply rate limiting
        return await self.limiter.check_rate_limit(
            request,
            max_requests=settings["max_requests"],
            window_seconds=settings["window_seconds"]
        )

# Global instance
rate_limit_service = RateLimitService()