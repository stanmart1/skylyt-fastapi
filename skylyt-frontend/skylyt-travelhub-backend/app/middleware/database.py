from fastapi import Request, Response
from sqlalchemy.exc import DisconnectionError, OperationalError
import logging

logger = logging.getLogger(__name__)

class DatabaseMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        
        try:
            await self.app(scope, receive, send)
        except (DisconnectionError, OperationalError) as e:
            logger.error(f"Database connection error: {e}")
            # Force connection pool refresh
            from app.core.database import engine
            engine.dispose()
            
            response = Response(
                content='{"detail": "Database connection error. Please try again."}',
                status_code=503,
                media_type="application/json"
            )
            await response(scope, receive, send)