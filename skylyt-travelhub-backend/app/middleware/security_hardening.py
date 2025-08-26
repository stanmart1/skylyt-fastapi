from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
import re
from typing import List, Pattern
from app.utils.logger import get_logger

logger = get_logger(__name__)

class SQLInjectionProtection:
    """SQL injection protection middleware"""
    
    # Common SQL injection patterns
    SQL_INJECTION_PATTERNS: List[Pattern] = [
        re.compile(r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)", re.IGNORECASE),
        re.compile(r"(\b(OR|AND)\s+\d+\s*=\s*\d+)", re.IGNORECASE),
        re.compile(r"('|(\\')|(;)|(\\;)|(\-\-)|(\#))", re.IGNORECASE),
        re.compile(r"(\b(SCRIPT|JAVASCRIPT|VBSCRIPT)\b)", re.IGNORECASE)
    ]
    
    @classmethod
    def validate_input(cls, value: str) -> bool:
        """Validate input for SQL injection patterns"""
        if not isinstance(value, str):
            return True
        
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if pattern.search(value):
                logger.warning(f"Potential SQL injection detected: {value[:100]}")
                return False
        
        return True
    
    @classmethod
    def sanitize_input(cls, value: str) -> str:
        """Sanitize input by removing dangerous characters"""
        if not isinstance(value, str):
            return value
        
        # Remove dangerous characters
        sanitized = re.sub(r"[';\"\\#\-\-]", "", value)
        return sanitized.strip()

class RequestValidationMiddleware:
    """Enhanced request validation middleware"""
    
    def __init__(self, app):
        self.app = app
        self.max_request_size = 10 * 1024 * 1024  # 10MB
        self.blocked_user_agents = [
            "sqlmap", "nikto", "nmap", "masscan", "zap"
        ]
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Validate request size
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.max_request_size:
                response = HTTPException(413, "Request too large")
                await response(scope, receive, send)
                return
            
            # Check user agent
            user_agent = request.headers.get("user-agent", "").lower()
            if any(blocked in user_agent for blocked in self.blocked_user_agents):
                logger.warning(f"Blocked suspicious user agent: {user_agent}")
                response = HTTPException(403, "Forbidden")
                await response(scope, receive, send)
                return
            
            # Validate query parameters
            for key, value in request.query_params.items():
                if not SQLInjectionProtection.validate_input(value):
                    logger.warning(f"Blocked malicious query parameter: {key}={value}")
                    response = HTTPException(400, "Invalid request parameters")
                    await response(scope, receive, send)
                    return
        
        await self.app(scope, receive, send)

class HTTPSRedirectMiddleware:
    """Force HTTPS in production"""
    
    def __init__(self, app, force_https: bool = True):
        self.app = app
        self.force_https = force_https
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and self.force_https:
            headers = dict(scope.get("headers", []))
            
            # Check if request is HTTP
            scheme = scope.get("scheme", "http")
            if scheme == "http":
                # Redirect to HTTPS
                host = headers.get(b"host", b"localhost").decode()
                path = scope.get("path", "/")
                query_string = scope.get("query_string", b"").decode()
                
                redirect_url = f"https://{host}{path}"
                if query_string:
                    redirect_url += f"?{query_string}"
                
                response = {
                    "type": "http.response.start",
                    "status": 301,
                    "headers": [
                        [b"location", redirect_url.encode()],
                        [b"content-length", b"0"]
                    ]
                }
                
                await send(response)
                await send({"type": "http.response.body", "body": b""})
                return
        
        await self.app(scope, receive, send)

class SecurityHeadersMiddleware:
    """Enhanced security headers middleware"""
    
    def __init__(self, app):
        self.app = app
        self.security_headers = {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=()",
            "Cross-Origin-Embedder-Policy": "require-corp",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "same-origin"
        }
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = dict(message.get("headers", []))
                    
                    # Add security headers
                    for header, value in self.security_headers.items():
                        headers[header.encode()] = value.encode()
                    
                    message["headers"] = list(headers.items())
                
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)