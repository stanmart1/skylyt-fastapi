#!/usr/bin/env python3
"""
Migration script to add description and rating fields to cars table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import engine

def run_migration():
    """Add description and rating columns to cars table"""
    
    with engine.connect() as connection:
        # Add description column
        try:
            connection.execute(text("ALTER TABLE cars ADD COLUMN description TEXT"))
            print("✓ Added description column to cars table")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print("✓ Description column already exists")
            else:
                print(f"✗ Error adding description column: {e}")
        
        # Add rating column
        try:
            connection.execute(text("ALTER TABLE cars ADD COLUMN rating FLOAT"))
            print("✓ Added rating column to cars table")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print("✓ Rating column already exists")
            else:
                print(f"✗ Error adding rating column: {e}")
        
        connection.commit()
        print("✓ Migration completed successfully")

if __name__ == "__main__":
    run_migration()