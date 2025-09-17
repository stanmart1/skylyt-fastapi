import redis
import os
from typing import Optional
import logging
import time
from redis.connection import ConnectionPool
from redis.retry import Retry
from redis.backoff import ExponentialBackoff

logger = logging.getLogger(__name__)

class RedisService:
    _instance: Optional[redis.Redis] = None
    _pool: Optional[ConnectionPool] = None
    
    @classmethod
    def get_connection_pool(cls) -> ConnectionPool:
        """Get Redis connection pool with enhanced timeout handling"""
        if cls._pool is None:
            try:
                cls._pool = ConnectionPool(
                    host=os.getenv('DRAGONFLY_HOST', 'localhost'),
                    port=int(os.getenv('DRAGONFLY_PORT', 6379)),
                    password=os.getenv('DRAGONFLY_PASSWORD'),
                    db=int(os.getenv('DRAGONFLY_DB', 0)),
                    decode_responses=True,
                    socket_connect_timeout=10,  # Increased from 5
                    socket_timeout=15,  # Increased from 5
                    socket_keepalive=True,
                    socket_keepalive_options={},
                    health_check_interval=30,  # Health check every 30 seconds
                    max_connections=50,  # Increased pool size
                    retry_on_timeout=True,
                    retry_on_error=[ConnectionError, TimeoutError],
                )
                logger.info("Redis connection pool created successfully")
            except Exception as e:
                logger.error(f"Failed to create Redis connection pool: {e}")
                cls._pool = None
        
        return cls._pool
    
    @classmethod
    def get_client(cls) -> redis.Redis:
        """Get Redis/Dragonfly client instance with enhanced error handling"""
        if cls._instance is None:
            try:
                pool = cls.get_connection_pool()
                if pool is None:
                    return None
                
                # Create Redis client with retry logic
                retry = Retry(ExponentialBackoff(), retries=3)
                
                cls._instance = redis.Redis(
                    connection_pool=pool,
                    retry=retry,
                    retry_on_timeout=True,
                    retry_on_error=[ConnectionError, TimeoutError, redis.BusyLoadingError]
                )
                
                # Test connection with timeout
                start_time = time.time()
                cls._instance.ping()
                connection_time = time.time() - start_time
                
                logger.info(f"Successfully connected to Dragonfly in {connection_time:.3f}s")
                
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
    """Set cache value with expiration and timeout handling"""
    max_retries = 3
    retry_delay = 0.1
    
    for attempt in range(max_retries):
        try:
            client = get_redis()
            if client:
                # Use pipeline for better performance
                pipe = client.pipeline()
                pipe.set(key, value, ex=ex)
                pipe.execute()
                return True
        except (redis.TimeoutError, redis.ConnectionError) as e:
            if attempt < max_retries - 1:
                logger.warning(f"Cache set timeout (attempt {attempt + 1}), retrying: {e}")
                time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                continue
            else:
                logger.error(f"Cache set failed after {max_retries} attempts: {e}")
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
            break
    return False

def cache_get(key: str) -> Optional[str]:
    """Get cache value with timeout handling"""
    max_retries = 2
    retry_delay = 0.05
    
    for attempt in range(max_retries):
        try:
            client = get_redis()
            if client:
                return client.get(key)
        except (redis.TimeoutError, redis.ConnectionError) as e:
            if attempt < max_retries - 1:
                logger.warning(f"Cache get timeout (attempt {attempt + 1}), retrying: {e}")
                time.sleep(retry_delay * (2 ** attempt))
                continue
            else:
                logger.error(f"Cache get failed after {max_retries} attempts: {e}")
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
            break
    return None

def cache_delete(key: str) -> bool:
    """Delete cache key with timeout handling"""
    try:
        client = get_redis()
        if client:
            client.delete(key)
            return True
    except (redis.TimeoutError, redis.ConnectionError) as e:
        logger.warning(f"Cache delete timeout: {e}")
    except Exception as e:
        logger.warning(f"Cache delete failed: {e}")
    return False

def cache_mget(keys: list) -> dict:
    """Get multiple cache values efficiently"""
    try:
        client = get_redis()
        if client and keys:
            values = client.mget(keys)
            return dict(zip(keys, values))
    except Exception as e:
        logger.warning(f"Cache mget failed: {e}")
    return {}

def cache_mset(mapping: dict, ex: int = 3600) -> bool:
    """Set multiple cache values efficiently"""
    try:
        client = get_redis()
        if client and mapping:
            pipe = client.pipeline()
            for key, value in mapping.items():
                pipe.set(key, value, ex=ex)
            pipe.execute()
            return True
    except Exception as e:
        logger.warning(f"Cache mset failed: {e}")
    return False

def get_cache_stats() -> dict:
    """Get cache performance statistics"""
    try:
        client = get_redis()
        if client:
            info = client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": round(
                    info.get("keyspace_hits", 0) / 
                    max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1) * 100, 2
                )
            }
    except Exception as e:
        logger.warning(f"Failed to get cache stats: {e}")
    return {"status": "unavailable"}