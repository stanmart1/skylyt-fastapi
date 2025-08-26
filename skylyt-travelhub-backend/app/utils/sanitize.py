"""
Input sanitization utilities to prevent log injection and other attacks
"""
import re
from typing import Any


def sanitize_for_logging(value: Any) -> str:
    """
    Sanitize input for safe logging by removing newlines and control characters
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Remove newlines, carriage returns, and other control characters
    sanitized = re.sub(r'[\r\n\t\x00-\x1f\x7f-\x9f]', '', value)
    
    # Limit length to prevent log flooding
    if len(sanitized) > 200:
        sanitized = sanitized[:200] + '...'
    
    return sanitized


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal
    """
    if not isinstance(filename, str):
        return ''
    
    # Remove path separators and dangerous characters
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', filename)
    
    # Remove dots at the beginning to prevent hidden files
    sanitized = sanitized.lstrip('.')
    
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    
    return sanitized