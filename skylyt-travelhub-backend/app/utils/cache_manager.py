import redis
import json
import pickle
from typing import Any, Optional, Union
from functools import wraps
from app.core.config import settings

class CacheManager:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.default_ttl = 300  # 5 minutes
    
    def get(self, key: str) -> Optional[Any]:
        try:
            data = self.redis_client.get(key)
            return pickle.loads(data) if data else None
        except:
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        try:
            ttl = ttl or self.default_ttl
            self.redis_client.setex(key, ttl, pickle.dumps(value))
            return True
        except:
            return False
    
    def delete(self, key: str) -> bool:
        try:
            self.redis_client.delete(key)
            return True
        except:
            return False
    
    def clear_pattern(self, pattern: str) -> bool:
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except:
            return False

cache_manager = CacheManager()

def cache_result(key_prefix: str, ttl: int = 300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator