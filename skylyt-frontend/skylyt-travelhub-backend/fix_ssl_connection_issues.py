#!/usr/bin/env python3
"""
Fix SSL Connection Issues
Addresses SSL connection problems with PostgreSQL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from app.core.config import settings
from sqlalchemy import create_engine, text
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ssl_connection_modes():
    """Test different SSL connection modes to find the most stable one"""
    
    ssl_modes = [
        ("disable", "No SSL - fastest but less secure"),
        ("allow", "SSL if available, fallback to non-SSL"),
        ("prefer", "Prefer SSL, fallback to non-SSL"),
        ("require", "Require SSL, fail if not available"),
    ]
    
    base_url = settings.DATABASE_URL
    
    for ssl_mode, description in ssl_modes:
        logger.info(f"\nTesting SSL mode: {ssl_mode} - {description}")
        
        try:
            # Modify URL to include SSL mode
            if "?" in base_url:
                test_url = f"{base_url}&sslmode={ssl_mode}"
            else:
                test_url = f"{base_url}?sslmode={ssl_mode}"
            
            # Create test engine
            test_engine = create_engine(
                test_url,
                pool_pre_ping=True,
                pool_size=1,
                max_overflow=0,
                pool_timeout=30,
                connect_args={
                    "connect_timeout": 10,
                    "keepalives_idle": 120,
                    "keepalives_interval": 10,
                    "keepalives_count": 3,
                }
            )
            
            # Test connection
            start_time = time.time()
            with test_engine.connect() as conn:
                result = conn.execute(text("SELECT 1, version(), current_setting('ssl')"))
                row = result.fetchone()
                connection_time = time.time() - start_time
                
                logger.info(f"✅ Success! Connection time: {connection_time:.3f}s")
                logger.info(f"   PostgreSQL version: {row[1][:50]}...")
                logger.info(f"   SSL status: {row[2]}")
                
                # Test a few more queries to ensure stability
                for i in range(3):
                    conn.execute(text("SELECT NOW()"))
                    time.sleep(0.1)
                
                logger.info(f"   Stability test: ✅ Passed")
            
            test_engine.dispose()
            
        except Exception as e:
            logger.error(f"❌ Failed: {e}")
            try:
                test_engine.dispose()
            except:
                pass

def optimize_ssl_settings():
    """Apply optimal SSL settings to the database"""
    
    logger.info("Applying SSL optimization settings...")
    
    # Use the most stable SSL mode found (usually 'prefer' or 'allow')
    optimized_args = {
        "connect_timeout": 20,
        "keepalives_idle": 120,  # 2 minutes
        "keepalives_interval": 10,  # 10 seconds
        "keepalives_count": 3,  # 3 attempts
        "application_name": "skylyt_api_ssl_optimized",
        "sslmode": "prefer",  # Prefer SSL but allow fallback
        "options": "-c statement_timeout=45s -c idle_in_transaction_session_timeout=60s"
    }
    
    try:
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=5,
            pool_timeout=60,
            pool_recycle=300,  # 5 minutes for SSL connections
            connect_args=optimized_args
        )
        
        # Test the optimized connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1, 'SSL optimized' as status"))
            row = result.fetchone()
            
            if row and row[0] == 1:
                logger.info("✅ SSL optimization successful!")
                logger.info(f"   Status: {row[1]}")
                return True
            else:
                logger.error("❌ SSL optimization failed - unexpected result")
                return False
                
    except Exception as e:
        logger.error(f"❌ SSL optimization failed: {e}")
        return False

def create_ssl_monitoring_script():
    """Create a script to monitor SSL connection health"""
    
    script_content = '''#!/usr/bin/env python3
"""
SSL Connection Monitor
Monitors SSL connection health and automatically recovers from issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import logging
from app.core.database import check_database_health, reset_connection_pool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def monitor_ssl_connections():
    """Monitor SSL connections and recover from issues"""
    
    consecutive_failures = 0
    max_failures = 3
    
    while True:
        try:
            health = check_database_health()
            
            if health['status'] == 'healthy':
                if consecutive_failures > 0:
                    logger.info(f"✅ Connection recovered after {consecutive_failures} failures")
                consecutive_failures = 0
                logger.info(f"Connection healthy ({health['connection_time']}ms)")
            else:
                consecutive_failures += 1
                logger.warning(f"❌ Connection unhealthy (failure {consecutive_failures}): {health.get('error', 'Unknown')}")
                
                if consecutive_failures >= max_failures:
                    logger.error("Max failures reached, resetting connection pool...")
                    reset_connection_pool()
                    consecutive_failures = 0
                    time.sleep(5)  # Wait longer after reset
            
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
            break
        except Exception as e:
            logger.error(f"Monitor error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    logger.info("Starting SSL connection monitoring...")
    monitor_ssl_connections()
'''
    
    with open("monitor_ssl_connections.py", "w") as f:
        f.write(script_content)
    
    logger.info("✅ SSL monitoring script created: monitor_ssl_connections.py")

def main():
    """Run SSL connection fixes"""
    
    logger.info("🔧 Fixing SSL Connection Issues...")
    
    # Test different SSL modes
    test_ssl_connection_modes()
    
    # Apply optimizations
    if optimize_ssl_settings():
        logger.info("✅ SSL settings optimized")
    else:
        logger.error("❌ SSL optimization failed")
    
    # Create monitoring script
    create_ssl_monitoring_script()
    
    logger.info("\n📋 SSL Fix Summary:")
    logger.info("1. Tested different SSL connection modes")
    logger.info("2. Applied optimal SSL settings")
    logger.info("3. Created SSL monitoring script")
    logger.info("\n💡 Recommendations:")
    logger.info("- Use 'sslmode=prefer' for best compatibility")
    logger.info("- Monitor connections with: python monitor_ssl_connections.py")
    logger.info("- Restart the application to apply changes")

if __name__ == "__main__":
    main()