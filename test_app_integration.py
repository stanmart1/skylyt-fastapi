#!/usr/bin/env python3
import sys
import os
sys.path.append('/Users/stanleyayo/Documents/python-projects/skylyt-fastapi/skylyt-frontend/skylyt-travelhub-backend')

from app.core.redis import RedisService, cache_set, cache_get, cache_delete
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/stanleyayo/Documents/python-projects/skylyt-fastapi/skylyt-frontend/skylyt-travelhub-backend/.env')

print("🔍 Testing DragonflyDB Integration with Application...")

# Test 1: Redis Service Connection
print("\n1. Testing RedisService connection...")
try:
    client = RedisService.get_client()
    if client:
        print("✅ RedisService.get_client() successful")
        is_available = RedisService.is_available()
        print(f"✅ RedisService.is_available(): {is_available}")
    else:
        print("❌ RedisService.get_client() returned None")
except Exception as e:
    print(f"❌ RedisService connection failed: {e}")

# Test 2: Cache Operations
print("\n2. Testing cache operations...")
try:
    # Test cache_set
    result = cache_set("test_app_key", "test_app_value", ex=60)
    print(f"✅ cache_set result: {result}")
    
    # Test cache_get
    value = cache_get("test_app_key")
    print(f"✅ cache_get result: {value}")
    
    # Test cache_delete
    delete_result = cache_delete("test_app_key")
    print(f"✅ cache_delete result: {delete_result}")
    
    # Verify deletion
    deleted_value = cache_get("test_app_key")
    print(f"✅ Verification after delete: {deleted_value}")
    
except Exception as e:
    print(f"❌ Cache operations failed: {e}")

# Test 3: Health Check Integration
print("\n3. Testing health check integration...")
try:
    from app.api.v1.health import get_system_health
    from app.core.database import get_db
    
    # Mock database session
    class MockDB:
        def execute(self, query):
            return type('Result', (), {'scalar': lambda: 1})()
    
    health_status = get_system_health(db=MockDB())
    print(f"✅ Health check response: {health_status}")
    
except Exception as e:
    print(f"❌ Health check integration failed: {e}")

print("\n🎉 Integration test completed!")