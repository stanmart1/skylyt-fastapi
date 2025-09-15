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
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Storage directory ready: {path}")
        except Exception as e:
            logger.error(f"Failed to create storage directory {path}: {e}")
            raise
    
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

# Initialize all storage directories on import
try:
    StorageManager.ensure_directory(StorageManager.BASE_STORAGE_PATH)
    for category in ["hotels", "cars", "general", "payment_proofs", "documents"]:
        StorageManager.ensure_directory(StorageManager.get_storage_path(category))
except Exception as e:
    logger.warning(f"Storage initialization failed: {e}")