import redis
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

# Get Dragonfly connection details from DRAGONFLY_URL
dragonfly_url = os.getenv('DRAGONFLY_URL')
parsed = urlparse(dragonfly_url)

host = parsed.hostname or 'localhost'
port = parsed.port or 6379
password = parsed.password
db = int(parsed.path.lstrip('/')) if parsed.path else 0

try:
    # Connect to Dragonfly
    client = redis.Redis(
        host=host,
        port=port,
        password=password,
        db=db,
        decode_responses=True
    )
    
    # Test connection
    client.ping()
    print(f"✅ Successfully connected to Dragonfly at {host}:{port}")
    
    # Test basic operations
    client.set('test_key', 'test_value')
    value = client.get('test_key')
    print(f"✅ Set/Get test: {value}")
    
    # Clean up
    client.delete('test_key')
    print("✅ Dragonfly connection test completed successfully")
    
except Exception as e:
    print(f"❌ Failed to connect to Dragonfly: {e}")