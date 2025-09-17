from app.utils.cache import cache_manager, search_cache, api_cache, session_cache
import logging

logger = logging.getLogger(__name__)

class CacheInvalidationService:
    """Service to handle cache invalidation when data changes"""
    
    @staticmethod
    async def invalidate_hotel_cache(hotel_id: str = None):
        """Invalidate hotel-related cache"""
        try:
            # Clear hotel search cache
            await search_cache.invalidate_search_cache("hotel")
            
            # Clear API cache for hotels
            await api_cache.cache.clear_pattern("api:*hotels*")
            
            # Clear featured hotels cache
            await api_cache.cache.clear_pattern("api:*featured_hotels*")
            
            if hotel_id:
                # Clear specific hotel cache
                await api_cache.cache.delete(f"hotel_details_{hotel_id}")
            
            logger.info(f"Hotel cache invalidated for hotel_id: {hotel_id}")
        except Exception as e:
            logger.error(f"Failed to invalidate hotel cache: {e}")
    
    @staticmethod
    async def invalidate_car_cache(car_id: str = None):
        """Invalidate car-related cache"""
        try:
            # Clear car search cache
            await search_cache.invalidate_search_cache("car")
            
            # Clear API cache for cars
            await api_cache.cache.clear_pattern("api:*cars*")
            
            # Clear featured cars cache
            await api_cache.cache.clear_pattern("api:*featured_cars*")
            
            if car_id:
                # Clear specific car cache
                await api_cache.cache.delete(f"car_details_{car_id}")
            
            logger.info(f"Car cache invalidated for car_id: {car_id}")
        except Exception as e:
            logger.error(f"Failed to invalidate car cache: {e}")
    
    @staticmethod
    async def invalidate_user_cache(user_id: int):
        """Invalidate user-related cache"""
        try:
            # Clear user session cache
            await session_cache.invalidate_user_session(user_id)
            
            # Clear user bookings cache
            await api_cache.cache.delete(f"api:*user_bookings*{user_id}*")
            
            logger.info(f"User cache invalidated for user_id: {user_id}")
        except Exception as e:
            logger.error(f"Failed to invalidate user cache: {e}")
    
    @staticmethod
    async def invalidate_booking_cache(user_id: int = None):
        """Invalidate booking-related cache"""
        try:
            if user_id:
                # Clear specific user's booking cache
                await api_cache.cache.clear_pattern(f"api:*user_bookings*{user_id}*")
            else:
                # Clear all booking cache
                await api_cache.cache.clear_pattern("api:*bookings*")
            
            logger.info(f"Booking cache invalidated for user_id: {user_id}")
        except Exception as e:
            logger.error(f"Failed to invalidate booking cache: {e}")
    
    @staticmethod
    async def warm_popular_cache():
        """Warm cache with popular data"""
        try:
            from app.utils.cache import cache_warmer
            
            # Warm popular searches
            await cache_warmer.warm_popular_searches()
            
            # Warm static data
            await cache_warmer.warm_static_data()
            
            logger.info("Cache warming completed")
        except Exception as e:
            logger.error(f"Failed to warm cache: {e}")