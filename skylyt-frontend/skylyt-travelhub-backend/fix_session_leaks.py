#!/usr/bin/env python3
"""
Emergency fix for session leaks
"""

import os
import re

def fix_get_db():
    """Fix the get_db function to prevent session leaks"""
    db_file = "/Users/stanleyayo/Documents/python-projects/skylyt-fastapi/skylyt-frontend/skylyt-travelhub-backend/app/core/database.py"
    
    with open(db_file, 'r') as f:
        content = f.read()
    
    # Replace the problematic get_db function
    old_pattern = r'def get_db\(\):\s*""".*?""".*?try:.*?yield db.*?finally:.*?db\.close\(\)'
    
    new_get_db = '''def get_db():
    """Database session with guaranteed cleanup"""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()'''
    
    content = re.sub(old_pattern, new_get_db, content, flags=re.DOTALL)
    
    with open(db_file, 'w') as f:
        f.write(content)
    
    print("✅ Fixed get_db function")

def add_transaction_timeout():
    """Add transaction timeout to prevent long-running transactions"""
    db_file = "/Users/stanleyayo/Documents/python-projects/skylyt-fastapi/skylyt-frontend/skylyt-travelhub-backend/app/core/database.py"
    
    with open(db_file, 'r') as f:
        content = f.read()
    
    # Add transaction timeout to connection args
    if 'idle_in_transaction_session_timeout=60s' not in content:
        content = content.replace(
            '"options": "-c statement_timeout=45s -c idle_in_transaction_session_timeout=60s -c lock_timeout=30s"',
            '"options": "-c statement_timeout=30s -c idle_in_transaction_session_timeout=30s -c lock_timeout=15s"'
        )
    
    with open(db_file, 'w') as f:
        f.write(content)
    
    print("✅ Reduced transaction timeouts")

def fix_dependencies():
    """Fix dependencies to use simpler session handling"""
    deps_file = "/Users/stanleyayo/Documents/python-projects/skylyt-fastapi/skylyt-frontend/skylyt-travelhub-backend/app/core/dependencies.py"
    
    with open(deps_file, 'r') as f:
        content = f.read()
    
    # Simplify get_current_user to avoid session issues
    new_content = content.replace(
        'try:\n        payload = verify_token(credentials.credentials)',
        'payload = verify_token(credentials.credentials)'
    ).replace(
        'except (ValueError, TypeError, Exception):\n        raise credentials_exception',
        'except (ValueError, TypeError):\n        raise credentials_exception'
    )
    
    with open(deps_file, 'w') as f:
        f.write(new_content)
    
    print("✅ Simplified dependencies")

if __name__ == "__main__":
    print("🔧 Fixing session leaks...")
    fix_get_db()
    add_transaction_timeout()
    fix_dependencies()
    print("✅ Session leak fixes applied")