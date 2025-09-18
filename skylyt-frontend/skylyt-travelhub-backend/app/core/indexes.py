from sqlalchemy import Index, text
from app.core.database import engine
import logging

logger = logging.getLogger(__name__)

def create_performance_indexes():
    """Create database indexes for better query performance"""
    indexes = [
        # Hotel search indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_hotels_location ON hotels USING gin(to_tsvector('english', location))",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_hotels_price_rating ON hotels (price_per_night, star_rating)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_hotels_available ON hotels (is_available) WHERE is_available = true",
        
        # Car search indexes  
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cars_location ON cars USING gin(to_tsvector('english', location))",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cars_price_category ON cars (price_per_day, category)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cars_available ON cars (is_available) WHERE is_available = true",
        
        # Booking indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_user_status ON bookings (user_id, status)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_dates ON bookings (check_in_date, check_out_date)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_created ON bookings (created_at DESC)",
        
        # Payment indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_status ON payments (status)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_created ON payments (created_at DESC)",
        
        # Image indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_hotel_images_hotel_cover ON hotel_images (hotel_id, is_cover)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_car_images_car_cover ON car_images (car_id, is_cover)",
        
        # User indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users (email)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_active ON users (is_active) WHERE is_active = true"
    ]
    
    with engine.connect() as conn:
        for index_sql in indexes:
            try:
                conn.execute(text(index_sql))
                conn.commit()
                logger.info(f"Created index: {index_sql.split('idx_')[1].split(' ')[0] if 'idx_' in index_sql else 'unknown'}")
            except Exception as e:
                logger.warning(f"Index creation failed (may already exist): {e}")