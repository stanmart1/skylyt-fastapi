from typing import Optional, Any
import json
import logging
from app.core.redis import cache_set, cache_get, cache_delete

logger = logging.getLogger(__name__)

class CacheService:
    """Service for caching frequently accessed data"""
    
    @staticmethod
    def cache_hotel_search(search_params: dict, results: list, ttl: int = 300) -> bool:
        """Cache hotel search results"""
        try:
            cache_key = f"hotel_search:{hash(str(sorted(search_params.items())))}"
            return cache_set(cache_key, json.dumps(results), ex=ttl)
        except Exception as e:
            logger.warning(f"Failed to cache hotel search: {e}")
            return False
    
    @staticmethod
    def get_cached_hotel_search(search_params: dict) -> Optional[list]:
        """Get cached hotel search results"""
        try:
            cache_key = f"hotel_search:{hash(str(sorted(search_params.items())))}"
            cached = cache_get(cache_key)
            return json.loads(cached) if cached else None
        except Exception as e:
            logger.warning(f"Failed to get cached hotel search: {e}")
            return None
    
    @staticmethod
    def cache_car_search(search_params: dict, results: list, ttl: int = 300) -> bool:
        """Cache car search results"""
        try:
            cache_key = f"car_search:{hash(str(sorted(search_params.items())))}"
            return cache_set(cache_key, json.dumps(results), ex=ttl)
        except Exception as e:
            logger.warning(f"Failed to cache car search: {e}")
            return False
    
    @staticmethod
    def get_cached_car_search(search_params: dict) -> Optional[list]:
        """Get cached car search results"""
        try:
            cache_key = f"car_search:{hash(str(sorted(search_params.items())))}"
            cached = cache_get(cache_key)
            return json.loads(cached) if cached else None
        except Exception as e:
            logger.warning(f"Failed to get cached car search: {e}")
            return None
    
    @staticmethod
    def cache_user_session(user_id: int, session_data: dict, ttl: int = 3600) -> bool:
        """Cache user session data"""
        try:
            cache_key = f"user_session:{user_id}"
            return cache_set(cache_key, json.dumps(session_data), ex=ttl)
        except Exception as e:
            logger.warning(f"Failed to cache user session: {e}")
            return False
    
    @staticmethod
    def get_cached_user_session(user_id: int) -> Optional[dict]:
        """Get cached user session data"""
        try:
            cache_key = f"user_session:{user_id}"
            cached = cache_get(cache_key)
            return json.loads(cached) if cached else None
        except Exception as e:
            logger.warning(f"Failed to get cached user session: {e}")
            return None
    
    @staticmethod
    def invalidate_user_session(user_id: int) -> bool:
        """Invalidate user session cache"""
        try:
            cache_key = f"user_session:{user_id}"
            return cache_delete(cache_key)
        except Exception as e:
            logger.warning(f"Failed to invalidate user session: {e}")
            return False
    
    @staticmethod
    def cache_currency_rates(rates: dict, ttl: int = 3600) -> bool:
        """Cache currency exchange rates"""
        try:
            cache_key = "currency_rates"
            return cache_set(cache_key, json.dumps(rates), ex=ttl)
        except Exception as e:
            logger.warning(f"Failed to cache currency rates: {e}")
            return False
    
    @staticmethod
    def get_cached_currency_rates() -> Optional[dict]:
        """Get cached currency rates"""
        try:
            cache_key = "currency_rates"
            cached = cache_get(cache_key)
            return json.loads(cached) if cached else None
        except Exception as e:
            logger.warning(f"Failed to get cached currency rates: {e}")
            return None