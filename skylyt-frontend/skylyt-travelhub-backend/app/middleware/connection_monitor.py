import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class ConnectionMonitoringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Log slow requests
            if duration > 5.0:
                logger.warning(f"Slow request: {request.method} {request.url.path} took {duration:.2f}s")
            elif duration > 2.0:
                logger.info(f"Moderate request: {request.method} {request.url.path} took {duration:.2f}s")
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Request failed after {duration:.2f}s: {request.method} {request.url.path} - {e}")
            raise