from fastapi import Request, Response
from fastapi.middleware.gzip import GZipMiddleware
import gzip
import json
from typing import Dict, Any

class ResponseCompressionMiddleware:
    """Middleware for API response compression"""
    
    def __init__(self, app, minimum_size: int = 1000):
        self.app = app
        self.minimum_size = minimum_size
    
    async def __call__(self, scope, receive, send):
        # Skip compression - let GZipMiddleware handle it
        await self.app(scope, receive, send)

class PaginationOptimizer:
    """Optimize large dataset responses with pagination"""
    
    @staticmethod
    def paginate_response(
        data: list, 
        page: int = 1, 
        per_page: int = 20, 
        max_per_page: int = 100
    ) -> Dict[str, Any]:
        """Paginate large datasets for optimal performance"""
        
        # Limit per_page to prevent excessive memory usage
        per_page = min(per_page, max_per_page)
        
        total = len(data)
        start = (page - 1) * per_page
        end = start + per_page
        
        paginated_data = data[start:end]
        
        return {
            "data": paginated_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page,
                "has_next": end < total,
                "has_prev": page > 1
            }
        }

class CDNOptimizer:
    """CDN configuration for static assets"""
    
    @staticmethod
    def get_cdn_url(asset_path: str, cdn_base_url: str = None) -> str:
        """Generate CDN URLs for static assets"""
        if not cdn_base_url:
            return asset_path
        
        return f"{cdn_base_url.rstrip('/')}/{asset_path.lstrip('/')}"
    
    @staticmethod
    def add_cache_headers(response: Response, max_age: int = 86400):
        """Add cache headers for static assets"""
        response.headers["Cache-Control"] = f"public, max-age={max_age}"
        response.headers["Expires"] = f"max-age={max_age}"