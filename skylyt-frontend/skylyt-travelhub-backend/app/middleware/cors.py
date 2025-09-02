from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

def setup_cors(app):
    """Configure CORS middleware for the FastAPI application"""
    
    # Development origins
    dev_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ]
    
    # Production origins (add your production domains)
    prod_origins = [
        "https://skylyt.com",
        "https://www.skylyt.com",
        "https://app.skylyt.com",
        "https://skylyt.scaleitpro.com",
    ]
    
    # Combine origins based on environment
    allowed_origins = dev_origins if settings.DEBUG else prod_origins
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRF-Token",
        ],
        expose_headers=["X-Total-Count", "X-Page-Count"],
        max_age=86400,  # 24 hours
    )