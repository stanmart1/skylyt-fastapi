from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.settings import Settings


class MaintenanceMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Skip maintenance check for admin and settings endpoints
            if (request.url.path.startswith("/api/v1/auth") or 
                request.url.path.startswith("/api/v1/settings") or
                request.url.path.startswith("/docs") or
                request.url.path.startswith("/redoc") or
                request.url.path == "/"):
                await self.app(scope, receive, send)
                return
            
            # Check maintenance mode
            try:
                db = next(get_db())
                settings = db.query(Settings).first()
                if settings and settings.maintenance_mode:
                    response = JSONResponse(
                        status_code=503,
                        content={
                            "detail": "System is currently under maintenance. Please try again later.",
                            "maintenance_mode": True
                        }
                    )
                    await response(scope, receive, send)
                    return
            except:
                pass  # Continue if settings check fails
        
        await self.app(scope, receive, send)