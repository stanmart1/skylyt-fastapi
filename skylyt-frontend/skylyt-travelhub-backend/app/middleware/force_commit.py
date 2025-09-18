import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class ForceCommitMiddleware(BaseHTTPMiddleware):
    """Force commit/rollback on all database sessions"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        finally:
            # Force cleanup any lingering sessions
            from app.core.database import engine
            try:
                # Dispose any idle connections
                if hasattr(engine.pool, 'dispose'):
                    # Only dispose if we have too many connections
                    if engine.pool.checkedout() > engine.pool.size() * 0.8:
                        logger.warning("High connection usage, disposing idle connections")
                        engine.dispose()
            except Exception as e:
                logger.error(f"Error in force commit middleware: {e}")