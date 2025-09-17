#!/usr/bin/env python3
"""
Run All Performance Fixes
Executes database optimizations and performance improvements
"""

import sys
import os
import subprocess
import logging

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_script(script_path, description):
    """Run a Python script and handle errors"""
    try:
        logger.info(f"Running {description}...")
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, check=True)
        logger.info(f"✅ {description} completed successfully")
        if result.stdout:
            logger.info(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed: {e}")
        if e.stdout:
            logger.error(f"Stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"Stderr: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"❌ Error running {description}: {e}")
        return False

def main():
    """Run all performance optimization scripts"""
    logger.info("🚀 Starting Skylyt Luxury Performance Optimization...")
    
    scripts = [
        ("fix_ssl_connection_issues.py", "SSL Connection Fixes"),
        ("fix_database_timeouts.py", "Database Timeout Fixes"),
        ("scripts/optimize_database_performance.py", "Database Performance Optimization"),
    ]
    
    success_count = 0
    total_count = len(scripts)
    
    for script_path, description in scripts:
        full_path = os.path.join(os.path.dirname(__file__), script_path)
        if os.path.exists(full_path):
            if run_script(full_path, description):
                success_count += 1
        else:
            logger.warning(f"⚠️  Script not found: {full_path}")
    
    # Test database connection after optimizations
    try:
        logger.info("Testing database connection...")
        from app.core.database import check_database_health
        health = check_database_health()
        if health['status'] == 'healthy':
            logger.info(f"✅ Database connection healthy ({health['connection_time']}ms)")
        else:
            logger.warning(f"⚠️  Database health check: {health}")
    except Exception as e:
        logger.error(f"❌ Database health check failed: {e}")
    
    # Test Redis connection
    try:
        logger.info("Testing Redis connection...")
        from app.core.redis import RedisService
        redis_client = RedisService.get_client()
        if redis_client and RedisService.is_available():
            logger.info("✅ Redis connection healthy")
        else:
            logger.warning("⚠️  Redis connection unavailable")
    except Exception as e:
        logger.error(f"❌ Redis connection test failed: {e}")
    
    # Summary
    logger.info(f"\n📊 Performance Optimization Summary:")
    logger.info(f"   Completed: {success_count}/{total_count} scripts")
    
    if success_count == total_count:
        logger.info("🎉 All performance optimizations completed successfully!")
        logger.info("\n📋 Next Steps:")
        logger.info("   1. Restart the application to apply all changes")
        logger.info("   2. Monitor performance metrics at /api/v1/performance/summary")
        logger.info("   3. Check database connection pool status")
        logger.info("   4. Verify Redis cache performance")
        return 0
    else:
        logger.warning(f"⚠️  {total_count - success_count} optimizations failed")
        logger.info("   Please check the logs above and fix any issues")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)