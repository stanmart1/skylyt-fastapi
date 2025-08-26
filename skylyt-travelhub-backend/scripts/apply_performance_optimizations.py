#!/usr/bin/env python3
"""
Apply performance optimizations to the database
Run this script to add indexes and optimize database performance
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine
from app.utils.cache_manager import cache_manager

def apply_indexes():
    """Apply performance indexes to the database"""
    indexes = [
        # Cars table indexes
        "CREATE INDEX IF NOT EXISTS idx_cars_category ON cars(category);",
        "CREATE INDEX IF NOT EXISTS idx_cars_price_per_day ON cars(price_per_day);",
        "CREATE INDEX IF NOT EXISTS idx_cars_is_featured ON cars(is_featured);",
        "CREATE INDEX IF NOT EXISTS idx_cars_is_available ON cars(is_available);",
        "CREATE INDEX IF NOT EXISTS idx_cars_location ON cars(location);",
        "CREATE INDEX IF NOT EXISTS idx_cars_make_model ON cars(make, model);",
        "CREATE INDEX IF NOT EXISTS idx_cars_created_at ON cars(created_at);",
        
        # Hotels table indexes
        "CREATE INDEX IF NOT EXISTS idx_hotels_location ON hotels(location);",
        "CREATE INDEX IF NOT EXISTS idx_hotels_rating ON hotels(rating);",
        "CREATE INDEX IF NOT EXISTS idx_hotels_price ON hotels(price);",
        "CREATE INDEX IF NOT EXISTS idx_hotels_created_at ON hotels(created_at);",
        
        # Bookings table indexes
        "CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);",
        "CREATE INDEX IF NOT EXISTS idx_bookings_type ON bookings(booking_type);",
        "CREATE INDEX IF NOT EXISTS idx_bookings_reference ON bookings(booking_reference);",
        "CREATE INDEX IF NOT EXISTS idx_bookings_dates ON bookings(check_in_date, check_out_date);",
        "CREATE INDEX IF NOT EXISTS idx_bookings_created_at ON bookings(created_at);",
        
        # Users table indexes
        "CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);",
        "CREATE INDEX IF NOT EXISTS idx_users_verified ON users(is_verified);",
        "CREATE INDEX IF NOT EXISTS idx_users_name ON users(first_name, last_name);",
        "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);",
    ]
    
    with engine.connect() as conn:
        for index_sql in indexes:
            try:
                conn.execute(text(index_sql))
                print(f"✓ Applied: {index_sql}")
            except Exception as e:
                print(f"✗ Failed: {index_sql} - {e}")
        conn.commit()

def clear_cache():
    """Clear all cached data to ensure fresh performance"""
    try:
        cache_manager.clear_pattern("*")
        print("✓ Cache cleared successfully")
    except Exception as e:
        print(f"✗ Cache clear failed: {e}")

def main():
    print("🚀 Applying performance optimizations...")
    
    print("\n📊 Adding database indexes...")
    apply_indexes()
    
    print("\n🧹 Clearing cache...")
    clear_cache()
    
    print("\n✅ Performance optimizations applied successfully!")
    print("📈 Your application should now be significantly faster!")

if __name__ == "__main__":
    main()