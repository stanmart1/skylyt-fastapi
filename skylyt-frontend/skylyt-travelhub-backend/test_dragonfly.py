import redis
import os
from dotenv import load_dotenv

load_dotenv()

# Get Dragonfly connection details from .env
host = os.getenv('DRAGONFLY_HOST')
port = int(os.getenv('DRAGONFLY_PORT'))
password = os.getenv('DRAGONFLY_PASSWORD')
db = int(os.getenv('DRAGONFLY_DB'))

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