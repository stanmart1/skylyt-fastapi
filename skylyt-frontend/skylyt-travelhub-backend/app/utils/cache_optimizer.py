import hashlib
import json
from typing import Any, Dict, Optional, List
from functools import wraps
from app.utils.cache import cache_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)

class CacheOptimizer:
    """Advanced caching optimization utilities"""
    
    @staticmethod
    def generate_cache_key(prefix: str, **kwargs) -> str:
        """Generate optimized cache key"""
        key_data = json.dumps(kwargs, sort_keys=True, default=str)
        hash_key = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{hash_key}"
    
    @staticmethod
    def cache_with_tags(tags: List[str], ttl: int = 300):
        """Cache decorator with tag-based invalidation"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = CacheOptimizer.generate_cache_key(
                    f"func:{func.__name__}", 
                    args=args, 
                    kwargs=kwargs
                )
                
                # Try to get from cache
                cached_result = await cache_manager.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_result
                
                # Execute function
                result = await func(*args, **kwargs) if hasattr(func, '__await__') else func(*args, **kwargs)
                
                # Cache result with tags
                await cache_manager.set(cache_key, result, ttl)
                
                # Store tag associations
                for tag in tags:
                    tag_key = f"tag:{tag}"
                    tag_keys = await cache_manager.get(tag_key) or []
                    if cache_key not in tag_keys:
                        tag_keys.append(cache_key)
                        await cache_manager.set(tag_key, tag_keys, ttl * 2)
                
                logger.debug(f"Cache miss for {func.__name__}, result cached")
                return result
            
            return wrapper
        return decorator
    
    @staticmethod
    async def invalidate_by_tag(tag: str):
        """Invalidate all cache entries with specific tag"""
        tag_key = f"tag:{tag}"
        cache_keys = await cache_manager.get(tag_key)
        
        if cache_keys:
            for cache_key in cache_keys:
                await cache_manager.delete(cache_key)
            
            await cache_manager.delete(tag_key)
            logger.info(f"Invalidated {len(cache_keys)} cache entries for tag: {tag}")

class SmartCache:
    """Smart caching with automatic optimization"""
    
    def __init__(self):
        self.hit_counts = {}
        self.miss_counts = {}
    
    async def get_with_stats(self, key: str) -> Optional[Any]:
        """Get from cache and track statistics"""
        result = await cache_manager.get(key)
        
        if result is not None:
            self.hit_counts[key] = self.hit_counts.get(key, 0) + 1
        else:
            self.miss_counts[key] = self.miss_counts.get(key, 0) + 1
        
        return result
    
    async def set_with_optimization(self, key: str, value: Any, base_ttl: int = 300):
        """Set cache with optimized TTL based on usage patterns"""
        hit_rate = self.get_hit_rate(key)
        
        # Adjust TTL based on hit rate
        if hit_rate > 0.8:  # High hit rate
            optimized_ttl = base_ttl * 2
        elif hit_rate > 0.5:  # Medium hit rate
            optimized_ttl = base_ttl
        else:  # Low hit rate
            optimized_ttl = base_ttl // 2
        
        await cache_manager.set(key, value, optimized_ttl)
        logger.debug(f"Cached {key} with optimized TTL: {optimized_ttl}s (hit rate: {hit_rate:.2f})")
    
    def get_hit_rate(self, key: str) -> float:
        """Calculate cache hit rate for a key"""
        hits = self.hit_counts.get(key, 0)
        misses = self.miss_counts.get(key, 0)
        total = hits + misses
        
        return hits / total if total > 0 else 0.0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_hits = sum(self.hit_counts.values())
        total_misses = sum(self.miss_counts.values())
        total_requests = total_hits + total_misses
        
        return {
            "total_requests": total_requests,
            "total_hits": total_hits,
            "total_misses": total_misses,
            "overall_hit_rate": total_hits / total_requests if total_requests > 0 else 0.0,
            "top_keys_by_hits": sorted(self.hit_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        }

# Global smart cache instance
smart_cache = SmartCache()

# Optimized caching decorators
def cache_search_results(ttl: int = 300):
    """Cache search results with automatic optimization"""
    return CacheOptimizer.cache_with_tags(["search"], ttl)

def cache_user_data(ttl: int = 600):
    """Cache user data with invalidation support"""
    return CacheOptimizer.cache_with_tags(["user"], ttl)

def cache_booking_data(ttl: int = 1800):
    """Cache booking data with tag-based invalidation"""
    return CacheOptimizer.cache_with_tags(["booking"], ttl)