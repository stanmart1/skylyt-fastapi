import logging
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from app.core.config import settings

def setup_logging():
    """Configure application logging"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO if not settings.DEBUG else logging.DEBUG)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for general logs
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Specific loggers
    setup_specific_loggers()

def setup_specific_loggers():
    """Setup specific loggers for different components"""
    
    # Database logger
    db_logger = logging.getLogger("sqlalchemy.engine")
    db_logger.setLevel(logging.WARNING)  # Reduce DB logging noise
    
    # HTTP client logger
    http_logger = logging.getLogger("httpx")
    http_logger.setLevel(logging.WARNING)
    
    # Redis logger
    redis_logger = logging.getLogger("redis")
    redis_logger.setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)

# Application-specific loggers
auth_logger = get_logger("skylyt.auth")
booking_logger = get_logger("skylyt.booking")
payment_logger = get_logger("skylyt.payment")
search_logger = get_logger("skylyt.search")
api_logger = get_logger("skylyt.api")