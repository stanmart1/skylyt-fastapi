from PIL import Image
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class ImageService:
    """Service for image optimization and metadata"""
    
    @staticmethod
    def optimize_image(image_path: Path, max_width: int = 1200, quality: int = 85) -> bool:
        """Optimize image for web delivery"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if too large
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                
                # Save optimized version
                img.save(image_path, 'JPEG', quality=quality, optimize=True)
                return True
        except Exception as e:
            logger.error(f"Failed to optimize image {image_path}: {e}")
            return False
    
    @staticmethod
    def get_image_dimensions(image_path: Path) -> Optional[Tuple[int, int]]:
        """Get image dimensions"""
        try:
            with Image.open(image_path) as img:
                return img.size
        except Exception as e:
            logger.error(f"Failed to get image dimensions {image_path}: {e}")
            return None
    
    @staticmethod
    def generate_alt_text(item_type: str, item_name: str, context: str = "") -> str:
        """Generate SEO-friendly alt text for images"""
        if item_type == "hotel":
            return f"{item_name} - Luxury hotel {context}".strip()
        elif item_type == "car":
            return f"{item_name} - Luxury car rental {context}".strip()
        else:
            return f"{item_name} {context}".strip()
    
    @staticmethod
    def create_webp_version(image_path: Path) -> bool:
        """Create WebP version of image for better performance"""
        try:
            webp_path = image_path.with_suffix('.webp')
            with Image.open(image_path) as img:
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                img.save(webp_path, 'WEBP', quality=85, optimize=True)
                return True
        except Exception as e:
            logger.error(f"Failed to create WebP version {image_path}: {e}")
            return False