#!/usr/bin/env python3
"""
Database Timeout Fix Script
Fixes common database timeout issues and optimizes connection handling
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_database_timeouts():
    """Apply database timeout fixes"""
    
    timeout_fixes = [
        # Connection timeout settings
        "ALTER SYSTEM SET statement_timeout = '45s'",
        "ALTER SYSTEM SET lock_timeout = '30s'", 
        "ALTER SYSTEM SET idle_in_transaction_session_timeout = '60s'",
        
        # Connection keepalive settings
        "ALTER SYSTEM SET tcp_keepalives_idle = 300",
        "ALTER SYSTEM SET tcp_keepalives_interval = 15",
        "ALTER SYSTEM SET tcp_keepalives_count = 5",
        
        # Connection limits
        "ALTER SYSTEM SET max_connections = 200",
        "ALTER SYSTEM SET superuser_reserved_connections = 3",
        
        # Memory and performance
        "ALTER SYSTEM SET shared_buffers = '256MB'",
        "ALTER SYSTEM SET effective_cache_size = '1GB'",
        "ALTER SYSTEM SET maintenance_work_mem = '64MB'",
        "ALTER SYSTEM SET work_mem = '4MB'",
        
        # WAL and checkpoint settings
        "ALTER SYSTEM SET checkpoint_timeout = '5min'",
        "ALTER SYSTEM SET checkpoint_completion_target = 0.9",
        "ALTER SYSTEM SET wal_buffers = '16MB'",
        
        # Query optimization
        "ALTER SYSTEM SET random_page_cost = 1.1",
        "ALTER SYSTEM SET effective_io_concurrency = 200",
        "ALTER SYSTEM SET default_statistics_target = 100"
    ]
    
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_timeout=180,
        connect_args={
            "connect_timeout": 15,
            "options": "-c statement_timeout=45s -c lock_timeout=30s"
        }
    )
    
    logger.info("Applying database timeout fixes...")
    
    with engine.connect() as conn:
        for fix in timeout_fixes:
            try:
                setting_name = fix.split('SET ')[1].split(' =')[0]
                logger.info(f"Applying: {setting_name}")
                conn.execute(text(fix))
                conn.commit()
                logger.info("✓ Applied successfully")
            except Exception as e:
                logger.error(f"✗ Failed to apply {setting_name}: {e}")
        
        # Reload configuration
        try:
            logger.info("Reloading PostgreSQL configuration...")
            conn.execute(text("SELECT pg_reload_conf()"))
            conn.commit()
            logger.info("✓ Configuration reloaded")
        except Exception as e:
            logger.error(f"✗ Failed to reload configuration: {e}")

if __name__ == "__main__":
    fix_database_timeouts()
    logger.info("✅ Database timeout fixes completed!")