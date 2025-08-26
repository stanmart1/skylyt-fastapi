import logging
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import DisconnectionError, OperationalError

logger = logging.getLogger(__name__)

class DatabaseMonitoringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Log slow requests that might indicate DB issues
            duration = time.time() - start_time
            if duration > 5.0:
                logger.warning(f"Slow request: {request.method} {request.url.path} took {duration:.2f}s")
            
            return response
            
        except (DisconnectionError, OperationalError) as e:
            logger.error(f"Database connection error in {request.method} {request.url.path}: {e}")
            return Response(
                content='{"detail": "Database connection error"}',
                status_code=503,
                media_type="application/json"
            )
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Request failed after {duration:.2f}s: {request.method} {request.url.path} - {e}")
            raise