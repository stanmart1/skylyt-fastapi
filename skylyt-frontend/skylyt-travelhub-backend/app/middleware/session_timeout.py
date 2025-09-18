import time
import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class SessionTimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, timeout_seconds: int = 300):  # 5 minutes
        super().__init__(app)
        self.timeout_seconds = timeout_seconds
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Check for long-running requests
            duration = time.time() - start_time
            if duration > self.timeout_seconds:
                logger.warning(f"Request timeout: {request.url.path} took {duration:.2f}s")
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            if duration > self.timeout_seconds:
                logger.error(f"Request failed after {duration:.2f}s: {e}")
                raise HTTPException(status_code=408, detail="Request timeout")
            raise