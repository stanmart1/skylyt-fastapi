#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine
from sqlalchemy import text

def fix_car_ids():
    """Fix existing cars by converting UUID IDs to integer IDs"""
    
    with engine.connect() as conn:
        # Get all existing cars with their data
        result = conn.execute(text("SELECT * FROM cars ORDER BY created_at"))
        existing_cars = result.fetchall()
        
        if not existing_cars:
            print("No cars found in database")
            return
        
        print(f"Found {len(existing_cars)} cars with UUID IDs")
        
        # Create a temporary table to store the data
        conn.execute(text("""
            CREATE TEMPORARY TABLE cars_temp AS 
            SELECT name, make, model, category, price_per_day, seats, transmission, 
                   features, images, is_available, is_featured, created_at, updated_at
            FROM cars
        """))
        
        # Clear the original table
        conn.execute(text("DELETE FROM cars"))
        
        # Reset the auto-increment counter
        conn.execute(text("ALTER TABLE cars AUTO_INCREMENT = 1"))
        
        # Insert data back with auto-incremented integer IDs
        conn.execute(text("""
            INSERT INTO cars (name, make, model, category, price_per_day, seats, transmission, 
                             features, images, is_available, is_featured, created_at, updated_at)
            SELECT name, make, model, category, price_per_day, seats, transmission, 
                   features, images, is_available, is_featured, created_at, updated_at
            FROM cars_temp
        """))
        
        conn.commit()
        
        # Verify the fix
        result = conn.execute(text("SELECT id, name FROM cars ORDER BY id"))
        fixed_cars = result.fetchall()
        
        print(f"Successfully fixed {len(fixed_cars)} cars:")
        for car in fixed_cars:
            print(f"  ID: {car[0]} - {car[1]}")

if __name__ == "__main__":
    fix_car_ids()