import re
import logging
import html
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal"""
    # Remove path separators and dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = filename.replace('..', '')
    return filename.strip()

def escape_html(text: str) -> str:
    """Escape HTML in user input"""
    return html.escape(text) if text else text

def sanitize_log_input(input_value: Any) -> str:
    """Sanitize input for logging to prevent log injection attacks"""
    if input_value is None:
        return "None"
    
    # Convert to string and remove newlines/carriage returns
    safe_value = re.sub(r'[\r\n]', '', str(input_value))
    
    # Limit length to prevent log flooding
    if len(safe_value) > 500:
        safe_value = safe_value[:500] + "..."
    
    return safe_value

def validate_file_upload(filename: str, content_type: str, file_size: int) -> tuple[bool, str]:
    """Validate file upload parameters"""
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf'}
    ALLOWED_CONTENT_TYPES = {
        'image/jpeg', 'image/png', 'image/gif', 'application/pdf'
    }
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Check file extension
    if not any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        return False, "File extension not allowed"
    
    # Check content type
    if content_type not in ALLOWED_CONTENT_TYPES:
        return False, "File type not allowed"
    
    # Check file size
    if file_size > MAX_FILE_SIZE:
        return False, "File too large"
    
    return True, "Valid"