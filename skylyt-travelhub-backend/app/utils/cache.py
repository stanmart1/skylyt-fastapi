import redis
import json
import pickle
from typing import Any, Optional, Union, Dict
from datetime import timedelta
import hashlib
from app.core.config import settings

class CacheManager:
    def __init__(self, redis_url: str = None):
        self.redis_client = redis.from_url(redis_url or settings.REDIS_URL)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            
            # Try to deserialize as JSON first, then pickle
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return pickle.loads(value)
        except Exception:
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Union[int, timedelta] = None
    ) -> bool:
        """Set value in cache"""
        try:
            # Try to serialize as JSON first, then pickle
            try:
                serialized = json.dumps(value)
            except (TypeError, ValueError):
                serialized = pickle.dumps(value)
            
            if expire:
                if isinstance(expire, timedelta):
                    expire = int(expire.total_seconds())
                return self.redis_client.setex(key, expire, serialized)
            else:
                return self.redis_client.set(key, serialized)
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception:
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return bool(self.redis_client.exists(key))
        except Exception:
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception:
            return 0

class SearchCache:
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.default_ttl = 300  # 5 minutes
    
    def _generate_search_key(self, search_params: Dict) -> str:
        """Generate cache key for search parameters"""
        # Sort parameters for consistent key generation
        sorted_params = json.dumps(search_params, sort_keys=True)
        hash_key = hashlib.md5(sorted_params.encode()).hexdigest()
        return f"search:{hash_key}"
    
    async def get_search_results(self, search_params: Dict) -> Optional[Dict]:
        """Get cached search results"""
        key = self._generate_search_key(search_params)
        return await self.cache.get(key)
    
    async def cache_search_results(
        self, 
        search_params: Dict, 
        results: Dict,
        ttl: int = None
    ) -> bool:
        """Cache search results"""
        key = self._generate_search_key(search_params)
        return await self.cache.set(key, results, ttl or self.default_ttl)
    
    async def invalidate_search_cache(self, search_type: str = None):
        """Invalidate search cache"""
        pattern = f"search:*" if not search_type else f"search:{search_type}:*"
        return await self.cache.clear_pattern(pattern)

class UserSessionCache:
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.session_ttl = 3600  # 1 hour
    
    async def get_user_session(self, user_id: int) -> Optional[Dict]:
        """Get user session data"""
        key = f"session:user:{user_id}"
        return await self.cache.get(key)
    
    async def set_user_session(self, user_id: int, session_data: Dict) -> bool:
        """Set user session data"""
        key = f"session:user:{user_id}"
        return await self.cache.set(key, session_data, self.session_ttl)
    
    async def invalidate_user_session(self, user_id: int) -> bool:
        """Invalidate user session"""
        key = f"session:user:{user_id}"
        return await self.cache.delete(key)

class APIResponseCache:
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.default_ttl = 600  # 10 minutes
    
    def _generate_api_key(self, endpoint: str, params: Dict) -> str:
        """Generate cache key for API response"""
        key_data = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        hash_key = hashlib.md5(key_data.encode()).hexdigest()
        return f"api:{hash_key}"
    
    async def get_cached_response(self, endpoint: str, params: Dict) -> Optional[Any]:
        """Get cached API response"""
        key = self._generate_api_key(endpoint, params)
        return await self.cache.get(key)
    
    async def cache_response(
        self, 
        endpoint: str, 
        params: Dict, 
        response: Any,
        ttl: int = None
    ) -> bool:
        """Cache API response"""
        key = self._generate_api_key(endpoint, params)
        return await self.cache.set(key, response, ttl or self.default_ttl)

# Cache warming functions
class CacheWarmer:
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
    
    async def warm_popular_searches(self):
        """Warm cache with popular search queries"""
        popular_destinations = [
            {"destination": "Lagos", "check_in": "2024-06-01", "check_out": "2024-06-03"},
            {"destination": "Abuja", "check_in": "2024-06-01", "check_out": "2024-06-03"},
            {"destination": "Port Harcourt", "check_in": "2024-06-01", "check_out": "2024-06-03"},
        ]
        
        # This would typically call your search service
        # For now, just cache placeholder data
        for search in popular_destinations:
            key = f"popular_search:{search['destination']}"
            await self.cache.set(key, {"cached": True, "results": []}, 1800)  # 30 min
    
    async def warm_static_data(self):
        """Warm cache with static data like amenities, locations"""
        static_data = {
            "amenities": ["WiFi", "Pool", "Gym", "Spa", "Restaurant"],
            "car_categories": ["Economy", "Compact", "Mid-size", "Full-size", "Luxury"],
            "locations": ["Lagos", "Abuja", "Port Harcourt", "Kano", "Ibadan"]
        }
        
        for key, data in static_data.items():
            await self.cache.set(f"static:{key}", data, 86400)  # 24 hours

# Global cache instances
cache_manager = CacheManager()
search_cache = SearchCache(cache_manager)
session_cache = UserSessionCache(cache_manager)
api_cache = APIResponseCache(cache_manager)
cache_warmer = CacheWarmer(cache_manager)