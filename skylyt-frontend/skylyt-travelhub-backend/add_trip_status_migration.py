#!/usr/bin/env python3
"""
Migration script to add trip_status column to bookings table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    """Add trip_status column to bookings table"""
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check if column already exists (PostgreSQL syntax)
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name = 'bookings' AND column_name = 'trip_status'
            """))
            
            if result.scalar() == 0:
                # Add trip_status column
                conn.execute(text("""
                    ALTER TABLE bookings 
                    ADD COLUMN trip_status VARCHAR(20) DEFAULT 'PENDING'
                """))
                
                # Update existing car bookings to have trip_status
                conn.execute(text("""
                    UPDATE bookings 
                    SET trip_status = 'PENDING' 
                    WHERE booking_type = 'car' AND driver_id IS NOT NULL
                """))
                
                conn.commit()
                print("✅ Successfully added trip_status column to bookings table")
            else:
                print("✅ trip_status column already exists")
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Running trip_status migration...")
    success = run_migration()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1)