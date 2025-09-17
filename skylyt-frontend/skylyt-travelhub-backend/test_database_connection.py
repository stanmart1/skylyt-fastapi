#!/usr/bin/env python3
"""
Test Database Connection
Verify that the database connection works with the new configuration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from app.core.database import check_database_health, get_pool_status, SessionLocal
from app.core.config import settings
from sqlalchemy import text
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic_connection():
    """Test basic database connectivity"""
    logger.info("Testing basic database connection...")
    
    try:
        health = check_database_health()
        logger.info(f"Database health: {health}")
        
        if health['status'] == 'healthy':
            logger.info(f"✅ Database connection successful ({health['connection_time']}ms)")
            return True
        else:
            logger.error(f"❌ Database connection failed: {health.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False

def test_pool_status():
    """Test connection pool status"""
    logger.info("Testing connection pool status...")
    
    try:
        pool_status = get_pool_status()
        logger.info(f"Pool status: {pool_status}")
        
        if pool_status['total_capacity'] > 0:
            logger.info("✅ Connection pool configured correctly")
            return True
        else:
            logger.error("❌ Connection pool not configured")
            return False
    except Exception as e:
        logger.error(f"❌ Pool status test failed: {e}")
        return False

def test_query_execution():
    """Test query execution with timeout settings"""
    logger.info("Testing query execution...")
    
    try:
        db = SessionLocal()
        start_time = time.time()
        
        # Test basic query
        result = db.execute(text("SELECT 1 as test, NOW() as current_time"))
        row = result.fetchone()
        
        query_time = time.time() - start_time
        
        if row and row[0] == 1:
            logger.info(f"✅ Query execution successful ({query_time:.3f}s)")
            logger.info(f"   Result: {dict(row._mapping)}")
            
            # Test timeout settings
            timeout_result = db.execute(text("SHOW statement_timeout"))
            timeout_row = timeout_result.fetchone()
            logger.info(f"   Statement timeout: {timeout_row[0] if timeout_row else 'Not set'}")
            
            db.close()
            return True
        else:
            logger.error("❌ Query returned unexpected result")
            db.close()
            return False
            
    except Exception as e:
        logger.error(f"❌ Query execution test failed: {e}")
        try:
            db.close()
        except:
            pass
        return False

def test_connection_parameters():
    """Test that connection parameters are set correctly"""
    logger.info("Testing connection parameters...")
    
    try:
        db = SessionLocal()
        
        # Check various timeout settings
        queries = {
            "statement_timeout": "SHOW statement_timeout",
            "lock_timeout": "SHOW lock_timeout", 
            "idle_in_transaction_session_timeout": "SHOW idle_in_transaction_session_timeout",
            "application_name": "SHOW application_name"
        }
        
        for param, query in queries.items():
            try:
                result = db.execute(text(query))
                row = result.fetchone()
                value = row[0] if row else "Not set"
                logger.info(f"   {param}: {value}")
            except Exception as e:
                logger.warning(f"   Could not check {param}: {e}")
        
        db.close()
        logger.info("✅ Connection parameters checked")
        return True
        
    except Exception as e:
        logger.error(f"❌ Connection parameters test failed: {e}")
        try:
            db.close()
        except:
            pass
        return False

def main():
    """Run all database tests"""
    logger.info("🔍 Testing Database Connection Configuration...")
    logger.info(f"Database URL: {settings.DATABASE_URL.split('@')[0]}@***")
    
    tests = [
        ("Basic Connection", test_basic_connection),
        ("Pool Status", test_pool_status),
        ("Query Execution", test_query_execution),
        ("Connection Parameters", test_connection_parameters)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        else:
            logger.error(f"Test '{test_name}' failed")
    
    logger.info(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All database tests passed! The connection is working correctly.")
        return 0
    else:
        logger.error(f"❌ {total - passed} tests failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)