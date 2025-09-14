from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.services.rate_limit_service import rate_limit_service
import logging

logger = logging.getLogger(__name__)

class DynamicRateLimitMiddleware:
    """Rate limiting middleware that uses database settings"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Skip rate limiting for certain paths
            if self._should_skip_rate_limit(request.url.path):
                await self.app(scope, receive, send)
                return
            
            # Check rate limit
            try:
                if not await rate_limit_service.check_rate_limit(request):
                    response = JSONResponse(
                        status_code=429,
                        content={
                            "detail": "Rate limit exceeded. Please try again later.",
                            "error": "too_many_requests"
                        },
                        headers={
                            "Retry-After": "60",
                            "X-RateLimit-Limit": str(rate_limit_service.get_rate_limit_settings()["max_requests"]),
                            "X-RateLimit-Window": str(rate_limit_service.get_rate_limit_settings()["window_seconds"])
                        }
                    )
                    await response(scope, receive, send)
                    return
            except Exception as e:
                logger.error(f"Rate limiting error: {e}")
                # Continue if rate limiting fails
        
        await self.app(scope, receive, send)
    
    def _should_skip_rate_limit(self, path: str) -> bool:
        """Determine if rate limiting should be skipped for this path"""
        skip_paths = [
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/uploads/",
            "/robots.txt",
            "/sitemap.xml",
            "/api/v1/health",
            "/api/v1/test"
        ]
        
        return any(path.startswith(skip_path) for skip_path in skip_paths)