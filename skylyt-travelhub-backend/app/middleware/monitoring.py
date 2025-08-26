from fastapi import Request, Response
import time
import json
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class MonitoringMiddleware:
    def __init__(self, app):
        self.app = app
        self.metrics: Dict[str, Any] = {
            "requests_total": 0,
            "requests_by_method": {},
            "requests_by_status": {},
            "response_times": [],
            "errors": []
        }
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            start_time = time.time()
            
            # Increment total requests
            self.metrics["requests_total"] += 1
            
            # Track method
            method = request.method
            self.metrics["requests_by_method"][method] = \
                self.metrics["requests_by_method"].get(method, 0) + 1
            
            response_data = {}
            
            async def send_wrapper(message):
                nonlocal response_data
                if message["type"] == "http.response.start":
                    response_data["status_code"] = message["status"]
                    response_data["headers"] = dict(message.get("headers", []))
                elif message["type"] == "http.response.body":
                    # Calculate response time
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    # Track metrics
                    status_code = response_data.get("status_code", 500)
                    self.metrics["requests_by_status"][str(status_code)] = \
                        self.metrics["requests_by_status"].get(str(status_code), 0) + 1
                    
                    self.metrics["response_times"].append(response_time)
                    
                    # Keep only last 1000 response times
                    if len(self.metrics["response_times"]) > 1000:
                        self.metrics["response_times"] = self.metrics["response_times"][-1000:]
                    
                    # Log request details
                    self._log_request(request, status_code, response_time)
                    
                    # Track errors
                    if status_code >= 400:
                        self._track_error(request, status_code, response_time)
                
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)
    
    def _log_request(self, request: Request, status_code: int, response_time: float):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "status_code": status_code,
            "response_time": response_time,
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("User-Agent", ""),
        }
        
        if status_code >= 400:
            logger.error(f"HTTP Error: {json.dumps(log_data)}")
        else:
            logger.info(f"HTTP Request: {json.dumps(log_data)}")
    
    def _track_error(self, request: Request, status_code: int, response_time: float):
        error_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "status_code": status_code,
            "response_time": response_time,
            "client_ip": self._get_client_ip(request),
        }
        
        self.metrics["errors"].append(error_data)
        
        # Keep only last 100 errors
        if len(self.metrics["errors"]) > 100:
            self.metrics["errors"] = self.metrics["errors"][-100:]
    
    def _get_client_ip(self, request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
            
        return request.client.host if request.client else "unknown"
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        avg_response_time = 0
        if self.metrics["response_times"]:
            avg_response_time = sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
        
        return {
            **self.metrics,
            "avg_response_time": avg_response_time,
            "error_rate": len(self.metrics["errors"]) / max(self.metrics["requests_total"], 1)
        }
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = {
            "requests_total": 0,
            "requests_by_method": {},
            "requests_by_status": {},
            "response_times": [],
            "errors": []
        }