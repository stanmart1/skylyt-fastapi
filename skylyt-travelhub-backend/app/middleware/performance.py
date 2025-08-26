from fastapi import Request, Response
import time
from app.utils.logger import get_logger
from app.monitoring.metrics import metrics_collector

logger = get_logger(__name__)

class PerformanceMiddleware:
    """Middleware to monitor and optimize performance"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            start_time = time.time()
            
            # Track database connections
            metrics_collector.increment_connections()
            
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    # Calculate response time
                    response_time = time.time() - start_time
                    
                    # Log slow requests
                    if response_time > 2.0:  # 2 second threshold
                        logger.warning(f"Slow request: {request.method} {request.url.path} - {response_time:.2f}s")
                    
                    # Record metrics
                    status_code = message["status"]
                    metrics_collector.record_request(
                        method=request.method,
                        endpoint=request.url.path,
                        status_code=status_code,
                        duration=response_time
                    )
                    
                    # Add performance headers
                    headers = dict(message.get("headers", []))
                    headers[b"X-Response-Time"] = f"{response_time:.3f}".encode()
                    message["headers"] = list(headers.items())
                
                await send(message)
            
            try:
                await self.app(scope, receive, send_wrapper)
            finally:
                metrics_collector.decrement_connections()
        else:
            await self.app(scope, receive, send)

class DatabasePerformanceMiddleware:
    """Middleware to monitor database performance"""
    
    def __init__(self, app):
        self.app = app
        self.query_count = 0
        self.query_time = 0.0
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Reset counters for each request
            self.query_count = 0
            self.query_time = 0.0
            
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    # Add database performance headers
                    headers = dict(message.get("headers", []))
                    headers[b"X-DB-Query-Count"] = str(self.query_count).encode()
                    headers[b"X-DB-Query-Time"] = f"{self.query_time:.3f}".encode()
                    message["headers"] = list(headers.items())
                    
                    # Log excessive database usage
                    if self.query_count > 10:
                        logger.warning(f"High DB query count: {self.query_count} queries for {request.url.path}")
                    
                    if self.query_time > 1.0:
                        logger.warning(f"High DB query time: {self.query_time:.3f}s for {request.url.path}")
                
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)