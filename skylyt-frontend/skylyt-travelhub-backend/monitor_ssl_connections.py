#!/usr/bin/env python3
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
