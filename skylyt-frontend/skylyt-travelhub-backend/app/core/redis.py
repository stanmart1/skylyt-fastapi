import redis
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class RedisService:
    _instance: Optional[redis.Redis] = None
    
    @classmethod
    def get_client(cls) -> redis.Redis:
        """Get Redis/Dragonfly client instance"""
        if cls._instance is None:
            try:
                cls._instance = redis.Redis(
                    host=os.getenv('DRAGONFLY_HOST', 'localhost'),
                    port=int(os.getenv('DRAGONFLY_PORT', 6379)),
                    password=os.getenv('DRAGONFLY_PASSWORD'),
                    db=int(os.getenv('DRAGONFLY_DB', 0)),
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                # Test connection
                cls._instance.ping()
                logger.info("Successfully connected to Dragonfly")
            except Exception as e:
                logger.error(f"Failed to connect to Dragonfly: {e}")
                # Fallback to None - application will work without cache
                cls._instance = None
        
        return cls._instance
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if Redis/Dragonfly is available"""
        try:
            client = cls.get_client()
            return client is not None and client.ping()
        except:
            return False

# Convenience functions
def get_redis() -> Optional[redis.Redis]:
    """Get Redis client or None if unavailable"""
    return RedisService.get_client()

def cache_set(key: str, value: str, ex: int = 3600) -> bool:
    """Set cache value with expiration"""
    try:
        client = get_redis()
        if client:
            client.set(key, value, ex=ex)
            return True
    except Exception as e:
        logger.warning(f"Cache set failed: {e}")
    return False

def cache_get(key: str) -> Optional[str]:
    """Get cache value"""
    try:
        client = get_redis()
        if client:
            return client.get(key)
    except Exception as e:
        logger.warning(f"Cache get failed: {e}")
    return None

def cache_delete(key: str) -> bool:
    """Delete cache key"""
    try:
        client = get_redis()
        if client:
            client.delete(key)
            return True
    except Exception as e:
        logger.warning(f"Cache delete failed: {e}")
    return False