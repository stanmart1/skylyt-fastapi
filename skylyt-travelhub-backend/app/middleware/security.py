from fastapi import Request, Response
from fastapi.responses import JSONResponse
import time
from typing import List, Optional

class SecurityMiddleware:
    def __init__(self, app):
        self.app = app
        self.blocked_ips: List[str] = []
        self.allowed_ips: Optional[List[str]] = None
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # IP filtering
            client_ip = self._get_client_ip(request)
            if not self._is_ip_allowed(client_ip):
                response = JSONResponse(
                    status_code=403,
                    content={"detail": "Access forbidden"}
                )
                await response(scope, receive, send)
                return
            
            # Add security headers to response
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = dict(message.get("headers", []))
                    
                    # Security headers
                    security_headers = {
                        b"X-Content-Type-Options": b"nosniff",
                        b"X-Frame-Options": b"DENY",
                        b"X-XSS-Protection": b"1; mode=block",
                        b"Strict-Transport-Security": b"max-age=31536000; includeSubDomains",
                        b"Content-Security-Policy": b"default-src 'self'",
                        b"Referrer-Policy": b"strict-origin-when-cross-origin",
                        b"Permissions-Policy": b"geolocation=(), microphone=(), camera=()"
                    }
                    
                    headers.update(security_headers)
                    message["headers"] = list(headers.items())
                
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)
    
    def _get_client_ip(self, request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
            
        return request.client.host if request.client else "unknown"
    
    def _is_ip_allowed(self, ip: str) -> bool:
        # Check if IP is blocked
        if ip in self.blocked_ips:
            return False
        
        # Check whitelist if configured
        if self.allowed_ips and ip not in self.allowed_ips:
            return False
        
        return True
    
    def block_ip(self, ip: str):
        if ip not in self.blocked_ips:
            self.blocked_ips.append(ip)
    
    def unblock_ip(self, ip: str):
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
    
    def set_ip_whitelist(self, ips: List[str]):
        self.allowed_ips = ips

# Request logging middleware
class RequestLoggingMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            start_time = time.time()
            
            # Log request
            print(f"Request: {request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}")
            
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    process_time = time.time() - start_time
                    status_code = message["status"]
                    print(f"Response: {status_code} in {process_time:.4f}s")
                
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)