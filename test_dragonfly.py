#!/usr/bin/env python3
import redis
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/stanleyayo/Documents/python-projects/skylyt-fastapi/skylyt-frontend/skylyt-travelhub-backend/.env')

# Get DragonflyDB connection details
host = os.getenv('DRAGONFLY_HOST', '149.102.159.118')
port = int(os.getenv('DRAGONFLY_PORT', '6379'))
password = os.getenv('DRAGONFLY_PASSWORD', '1rcRAINEt6a4hjtjbMFif078xjKAE0c9aqS8SYETh6idLCilSrTfs8tW9i5bKXJo')
db = int(os.getenv('DRAGONFLY_DB', '0'))

print(f"Connecting to DragonflyDB at {host}:{port}")

try:
    # Create Redis connection
    r = redis.Redis(
        host=host,
        port=port,
        password=password,
        db=db,
        decode_responses=True,
        socket_timeout=10,
        socket_connect_timeout=10
    )
    
    # Test connection
    response = r.ping()
    print(f"✅ Connection successful! PING response: {response}")
    
    # Test basic operations
    r.set('test_key', 'test_value')
    value = r.get('test_key')
    print(f"✅ Set/Get test successful: {value}")
    
    # Get server info
    info = r.info('server')
    print(f"✅ Server info: {info.get('redis_version', 'Unknown version')}")
    
    # Clean up
    r.delete('test_key')
    print("✅ Test completed successfully")
    
except redis.ConnectionError as e:
    print(f"❌ Connection failed: {e}")
except redis.TimeoutError as e:
    print(f"❌ Connection timeout: {e}")
except Exception as e:
    print(f"❌ Error: {e}")