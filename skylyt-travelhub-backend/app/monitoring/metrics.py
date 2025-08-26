try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest
except ImportError:
    # Mock prometheus client for development
    class Counter:
        def __init__(self, *args, **kwargs): pass
        def inc(self, *args, **kwargs): pass
    
    class Histogram:
        def __init__(self, *args, **kwargs): pass
        def observe(self, *args, **kwargs): pass
    
    class Gauge:
        def __init__(self, *args, **kwargs): pass
        def set(self, *args, **kwargs): pass
    
    def generate_latest(): return b""
import time
from typing import Dict, Any

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

BOOKING_COUNT = Counter(
    'bookings_total',
    'Total bookings created',
    ['booking_type', 'status']
)

PAYMENT_COUNT = Counter(
    'payments_total',
    'Total payments processed',
    ['gateway', 'status']
)

SEARCH_COUNT = Counter(
    'searches_total',
    'Total searches performed',
    ['search_type']
)

ERROR_COUNT = Counter(
    'errors_total',
    'Total errors',
    ['error_type', 'endpoint']
)

class MetricsCollector:
    def __init__(self):
        self.start_time = time.time()
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_booking(self, booking_type: str, status: str):
        """Record booking metrics"""
        BOOKING_COUNT.labels(
            booking_type=booking_type,
            status=status
        ).inc()
    
    def record_payment(self, gateway: str, status: str):
        """Record payment metrics"""
        PAYMENT_COUNT.labels(
            gateway=gateway,
            status=status
        ).inc()
    
    def record_search(self, search_type: str):
        """Record search metrics"""
        SEARCH_COUNT.labels(search_type=search_type).inc()
    
    def record_error(self, error_type: str, endpoint: str):
        """Record error metrics"""
        ERROR_COUNT.labels(
            error_type=error_type,
            endpoint=endpoint
        ).inc()
    
    def increment_connections(self):
        """Increment active connections"""
        ACTIVE_CONNECTIONS.inc()
    
    def decrement_connections(self):
        """Decrement active connections"""
        ACTIVE_CONNECTIONS.dec()
    
    def get_metrics(self) -> str:
        """Get Prometheus metrics in text format"""
        return generate_latest()
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get basic health metrics"""
        uptime = time.time() - self.start_time
        
        return {
            "uptime_seconds": uptime,
            "active_connections": ACTIVE_CONNECTIONS._value._value,
            "status": "healthy"
        }

# Global metrics collector instance
metrics_collector = MetricsCollector()