from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import redis
from typing import Dict, Optional
import json
from app.core.config import settings

class RateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
    async def check_rate_limit(
        self, 
        request: Request, 
        max_requests: int = 100, 
        window_seconds: int = 3600,
        identifier: Optional[str] = None
    ) -> bool:
        # Use provided identifier or fall back to IP
        key = identifier or self._get_client_ip(request)
        rate_key = f"rate_limit:{key}:{window_seconds}"
        
        try:
            current = self.redis.get(rate_key)
            if current is None:
                # First request in window
                self.redis.setex(rate_key, window_seconds, 1)
                return True
            
            current_count = int(current)
            if current_count >= max_requests:
                return False
            
            # Increment counter
            self.redis.incr(rate_key)
            return True
            
        except Exception:
            # If Redis fails, allow request
            return True
    
    def _get_client_ip(self, request: Request) -> str:
        # Check for forwarded IP first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
            
        return request.client.host if request.client else "unknown"

# Rate limiting decorator
def rate_limit(max_requests: int = 100, window_seconds: int = 3600):
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            redis_client = redis.from_url(settings.REDIS_URL)
            limiter = RateLimiter(redis_client)
            
            if not await limiter.check_rate_limit(request, max_requests, window_seconds):
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later."
                )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

# Middleware class
class RateLimitMiddleware:
    def __init__(self, app, redis_client: redis.Redis):
        self.app = app
        self.limiter = RateLimiter(redis_client)
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Apply different limits based on endpoint
            limits = self._get_endpoint_limits(request.url.path)
            
            if limits and not await self.limiter.check_rate_limit(
                request, limits["max_requests"], limits["window_seconds"]
            ):
                response = JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"}
                )
                await response(scope, receive, send)
                return
        
        await self.app(scope, receive, send)
    
    def _get_endpoint_limits(self, path: str) -> Optional[Dict]:
        # Define different limits for different endpoints
        if path.startswith("/auth/"):
            return {"max_requests": 10, "window_seconds": 300}  # 10 per 5 min
        elif path.startswith("/search/"):
            return {"max_requests": 50, "window_seconds": 300}  # 50 per 5 min
        elif path.startswith("/bookings/"):
            return {"max_requests": 20, "window_seconds": 300}  # 20 per 5 min
        return None