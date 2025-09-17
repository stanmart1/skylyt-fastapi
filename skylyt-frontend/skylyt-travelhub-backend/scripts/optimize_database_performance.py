#!/usr/bin/env python3
"""
Database Performance Optimization Script
Adds indexes and optimizes database configuration for better performance
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_performance_indexes():
    """Create indexes to improve query performance"""
    
    indexes = [
        # User table indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_phone ON users(phone)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_is_active ON users(is_active)",
        
        # Booking table indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_user_id ON bookings(user_id)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_status ON bookings(status)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_booking_type ON bookings(booking_type)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_created_at ON bookings(created_at)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_start_date ON bookings(start_date)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_end_date ON bookings(end_date)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_customer_email ON bookings(customer_email)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_booking_reference ON bookings(booking_reference)",
        
        # Payment table indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_booking_id ON payments(booking_id)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_status ON payments(status)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_payment_method ON payments(payment_method)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_created_at ON payments(created_at)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_transaction_id ON payments(transaction_id)",
        
        # Hotel table indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_hotels_location ON hotels(location)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_hotels_star_rating ON hotels(star_rating)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_hotels_price_per_night ON hotels(price_per_night)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_hotels_is_available ON hotels(is_available)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_hotels_is_featured ON hotels(is_featured)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_hotels_state_id ON hotels(state_id)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_hotels_city_id ON hotels(city_id)",
        
        # Car table indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cars_category ON cars(category)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cars_location ON cars(location)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cars_price_per_day ON cars(price_per_day)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cars_status ON cars(status)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cars_is_available ON cars(is_available)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cars_is_featured ON cars(is_featured)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cars_transmission ON cars(transmission)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cars_fuel_type ON cars(fuel_type)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cars_seats ON cars(seats)",
        
        # Composite indexes for common queries
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_user_status ON bookings(user_id, status)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_type_status ON bookings(booking_type, status)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_booking_status ON payments(booking_id, status)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_hotels_location_available ON hotels(location, is_available)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cars_location_available ON cars(location, is_available)",
        
        # Full-text search indexes (if using PostgreSQL)
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_hotels_name_gin ON hotels USING gin(to_tsvector('english', name))",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cars_name_gin ON cars USING gin(to_tsvector('english', name))",
    ]
    
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        for index_sql in indexes:
            try:
                logger.info(f"Creating index: {index_sql.split('idx_')[1].split(' ')[0] if 'idx_' in index_sql else 'unknown'}")
                conn.execute(text(index_sql))
                conn.commit()
                logger.info("✓ Index created successfully")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("✓ Index already exists")
                else:
                    logger.error(f"✗ Failed to create index: {e}")

def optimize_postgresql_settings():
    """Optimize PostgreSQL settings for better performance"""
    
    optimizations = [
        # Connection and memory settings
        "ALTER SYSTEM SET max_connections = 200",
        "ALTER SYSTEM SET shared_buffers = '256MB'",
        "ALTER SYSTEM SET effective_cache_size = '1GB'",
        "ALTER SYSTEM SET maintenance_work_mem = '64MB'",
        "ALTER SYSTEM SET checkpoint_completion_target = 0.9",
        "ALTER SYSTEM SET wal_buffers = '16MB'",
        "ALTER SYSTEM SET default_statistics_target = 100",
        
        # Timeout settings
        "ALTER SYSTEM SET statement_timeout = '45s'",
        "ALTER SYSTEM SET lock_timeout = '30s'",
        "ALTER SYSTEM SET idle_in_transaction_session_timeout = '60s'",
        
        # Connection keepalive settings
        "ALTER SYSTEM SET tcp_keepalives_idle = 300",
        "ALTER SYSTEM SET tcp_keepalives_interval = 15",
        "ALTER SYSTEM SET tcp_keepalives_count = 5",
        
        # Performance settings
        "ALTER SYSTEM SET random_page_cost = 1.1",
        "ALTER SYSTEM SET effective_io_concurrency = 200",
    ]
    
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        for setting in optimizations:
            try:
                logger.info(f"Applying setting: {setting.split('SET ')[1].split(' =')[0]}")
                conn.execute(text(setting))
                conn.commit()
                logger.info("✓ Setting applied successfully")
            except Exception as e:
                logger.error(f"✗ Failed to apply setting: {e}")
        
        # Reload configuration
        try:
            conn.execute(text("SELECT pg_reload_conf()"))
            conn.commit()
            logger.info("✓ PostgreSQL configuration reloaded")
        except Exception as e:
            logger.error(f"✗ Failed to reload configuration: {e}")

def analyze_tables():
    """Update table statistics for better query planning"""
    
    tables = [
        'users', 'bookings', 'payments', 'hotels', 'cars', 
        'roles', 'permissions', 'user_roles', 'role_permissions'
    ]
    
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        for table in tables:
            try:
                logger.info(f"Analyzing table: {table}")
                conn.execute(text(f"ANALYZE {table}"))
                conn.commit()
                logger.info("✓ Table analyzed successfully")
            except Exception as e:
                logger.error(f"✗ Failed to analyze table {table}: {e}")

def vacuum_tables():
    """Vacuum tables to reclaim space and update statistics"""
    
    tables = [
        'users', 'bookings', 'payments', 'hotels', 'cars'
    ]
    
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        for table in tables:
            try:
                logger.info(f"Vacuuming table: {table}")
                # Use autocommit for VACUUM
                conn.execute(text(f"VACUUM ANALYZE {table}"))
                logger.info("✓ Table vacuumed successfully")
            except Exception as e:
                logger.error(f"✗ Failed to vacuum table {table}: {e}")

def main():
    """Run all database optimizations"""
    logger.info("Starting database performance optimization...")
    
    try:
        logger.info("1. Creating performance indexes...")
        create_performance_indexes()
        
        logger.info("2. Optimizing PostgreSQL settings...")
        optimize_postgresql_settings()
        
        logger.info("3. Analyzing tables...")
        analyze_tables()
        
        logger.info("4. Vacuuming tables...")
        vacuum_tables()
        
        logger.info("✅ Database optimization completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database optimization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()