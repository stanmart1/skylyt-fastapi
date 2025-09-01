#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings

def add_room_types_column():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as connection:
        # Check if column exists (PostgreSQL)
        result = connection.execute(text("""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_name = 'hotels' AND column_name = 'room_types'
        """))
        
        if result.scalar() == 0:
            # Add room_types column
            connection.execute(text("""
                ALTER TABLE hotels ADD COLUMN room_types JSONB
            """))
            connection.commit()
            print("Added room_types column to hotels table")
        else:
            print("room_types column already exists")

if __name__ == "__main__":
    add_room_types_column()