import traceback
import json
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ErrorTracker:
    """Error tracking and reporting system"""
    
    def __init__(self):
        self.error_counts = {}
        self.recent_errors = []
        self.max_recent_errors = 100
    
    def track_error(
        self, 
        error: Exception, 
        request: Optional[Request] = None,
        user_id: Optional[int] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ):
        """Track and log application errors"""
        
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "user_id": user_id,
            "request_data": self._extract_request_data(request) if request else None,
            "additional_context": additional_context or {}
        }
        
        # Count error occurrences
        error_key = f"{error_data['error_type']}:{error_data['error_message']}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Store recent errors
        self.recent_errors.append(error_data)
        if len(self.recent_errors) > self.max_recent_errors:
            self.recent_errors.pop(0)
        
        # Log error
        logger.error(f"Error tracked: {error_data['error_type']} - {error_data['error_message']}")
        
        # Send to external error tracking service (e.g., Sentry)
        self._send_to_external_service(error_data)
    
    def _extract_request_data(self, request: Request) -> Dict[str, Any]:
        """Extract relevant request data for error context"""
        return {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent")
        }
    
    def _send_to_external_service(self, error_data: Dict[str, Any]):
        """Send error data to external tracking service"""
        # This would integrate with Sentry, Rollbar, etc.
        # For now, just log to file
        try:
            with open("logs/errors.json", "a") as f:
                json.dump(error_data, f)
                f.write("\n")
        except Exception as e:
            logger.error(f"Failed to write error to file: {e}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics"""
        total_errors = sum(self.error_counts.values())
        
        # Top errors by frequency
        top_errors = sorted(
            self.error_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        return {
            "total_errors": total_errors,
            "unique_errors": len(self.error_counts),
            "top_errors": [
                {"error": error, "count": count} 
                for error, count in top_errors
            ],
            "recent_errors_count": len(self.recent_errors)
        }

class ErrorHandlingMiddleware:
    """Global error handling middleware"""
    
    def __init__(self, app, error_tracker: ErrorTracker):
        self.app = app
        self.error_tracker = error_tracker
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            try:
                await self.app(scope, receive, send)
            except Exception as e:
                # Track the error
                self.error_tracker.track_error(e, request)
                
                # Re-raise all exceptions to let FastAPI handle them
                raise e
        else:
            await self.app(scope, receive, send)

# Global error tracker instance
error_tracker = ErrorTracker()