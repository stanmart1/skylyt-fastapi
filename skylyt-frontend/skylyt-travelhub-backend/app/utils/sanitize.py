import re
import html


def sanitize_for_logging(text: str) -> str:
    """Sanitize text for safe logging by removing newlines and control characters"""
    if not text:
        return ""
    
    # Remove newlines and carriage returns
    sanitized = re.sub(r'[\r\n]', '', str(text))
    
    # Remove other control characters except tab
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
    
    # Truncate if too long
    if len(sanitized) > 100:
        sanitized = sanitized[:97] + "..."
    
    return sanitized


def sanitize_html(text: str) -> str:
    """Sanitize HTML content"""
    if not text:
        return ""
    
    return html.escape(str(text))