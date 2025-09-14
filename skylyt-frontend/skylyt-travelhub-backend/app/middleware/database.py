from fastapi import Request, Response
from sqlalchemy.exc import DisconnectionError, OperationalError
import logging

logger = logging.getLogger(__name__)

class DatabaseMiddleware:
    def __init__(self, app):
        self.app = app
        self._last_dispose = 0

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        
        try:
            await self.app(scope, receive, send)
        except (DisconnectionError, OperationalError) as e:
            logger.error(f"Database connection error: {e}")
            # Force immediate pool disposal
            from app.core.database import engine
            engine.dispose()
            
            # Return 503 for database issues
            response = Response(
                content='{"detail": "Database temporarily unavailable. Please try again."}',
                status_code=503,
                media_type="application/json",
                headers={"Retry-After": "5"}
            )
            await response(scope, receive, send)
        except Exception as e:
            # Catch any other exceptions that might cause crashes
            logger.error(f"Unexpected error: {e}")
            response = Response(
                content='{"detail": "Internal server error"}',
                status_code=500,
                media_type="application/json"
            )
            await response(scope, receive, send)