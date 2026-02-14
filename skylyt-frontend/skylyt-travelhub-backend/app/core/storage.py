"""
Centralized storage management for all file uploads
"""
from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)

class StorageManager:
    """Centralized storage manager"""
    
    BASE_STORAGE_PATH = Path("/app/storage")
    
    @classmethod
    def get_storage_path(cls, category: str = "") -> Path:
        """Get storage path for category"""
        if category:
            return cls.BASE_STORAGE_PATH / category
        return cls.BASE_STORAGE_PATH
    
    @classmethod
    def ensure_directory(cls, path: Path) -> None:
        """Ensure directory exists with proper permissions"""
        try:
            # Check if directory exists and is writable
            if path.exists():
                if os.access(path, os.W_OK):
                    logger.info(f"Storage directory ready: {path}")
                    return
                else:
                    logger.warning(f"Storage directory exists but not writable: {path}")
                    return
            
            # Try to create directory
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Storage directory created: {path}")
        except PermissionError:
            # Directory might exist but we don't have permission to check/create
            # If it exists and is writable, that's fine
            if path.exists() and os.access(path, os.W_OK):
                logger.info(f"Storage directory ready: {path}")
            else:
                logger.warning(f"Cannot create/access storage directory {path}, continuing anyway")
        except Exception as e:
            logger.warning(f"Storage directory check failed for {path}: {e}, continuing anyway")
    
    @classmethod
    def get_upload_path(cls, category: str, filename: str) -> Path:
        """Get full upload path for file"""
        from app.utils.security import sanitize_filename
        # Sanitize filename to prevent path traversal
        safe_filename = sanitize_filename(filename)
        storage_dir = cls.get_storage_path(category)
        cls.ensure_directory(storage_dir)
        return storage_dir / safe_filename
    
    @classmethod
    def get_serve_url(cls, category: str, filename: str) -> str:
        """Get URL for serving file"""
        return f"/uploads/{category}/{filename}"
