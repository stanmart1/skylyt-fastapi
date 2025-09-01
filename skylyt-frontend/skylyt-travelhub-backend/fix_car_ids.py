#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create PostgreSQL connection
db_user = os.getenv('DATABASE_USER', 'postgres')
db_password = os.getenv('DATABASE_PASSWORD')
db_name = os.getenv('DATABASE_NAME', 'postgres')
db_port = os.getenv('DATABASE_PORT', '5321')
db_host = os.getenv('DATABASE_HOST')

DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(DATABASE_URL)

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
        
        # Store car data in memory
        cars_data = []
        for row in existing_cars:
            cars_data.append({
                'name': row[1],
                'make': row[2], 
                'model': row[3],
                'category': row[4],
                'price_per_day': row[5],
                'seats': row[6],
                'transmission': row[7],
                'features': row[8],
                'images': row[9],
                'is_available': row[10],
                'is_featured': row[11],
                'created_at': row[12],
                'updated_at': row[13]
            })
        
        # Drop and recreate the table with proper integer ID
        conn.execute(text("DROP TABLE cars"))
        conn.execute(text("""
            CREATE TABLE cars (
                id SERIAL PRIMARY KEY,
                name VARCHAR NOT NULL,
                make VARCHAR NOT NULL,
                model VARCHAR NOT NULL,
                category VARCHAR NOT NULL,
                price_per_day FLOAT NOT NULL,
                seats INTEGER NOT NULL,
                transmission VARCHAR NOT NULL,
                features JSON,
                images JSON,
                is_available BOOLEAN DEFAULT TRUE,
                is_featured BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Insert data back with auto-incremented integer IDs
        for car in cars_data:
            conn.execute(text("""
                INSERT INTO cars (name, make, model, category, price_per_day, seats, transmission, 
                                 features, images, is_available, is_featured, created_at, updated_at)
                VALUES (:name, :make, :model, :category, :price_per_day, :seats, :transmission,
                        :features, :images, :is_available, :is_featured, :created_at, :updated_at)
            """), car)
        
        conn.commit()
        
        # Verify the fix
        result = conn.execute(text("SELECT id, name FROM cars ORDER BY id"))
        fixed_cars = result.fetchall()
        
        print(f"Successfully fixed {len(fixed_cars)} cars:")
        for car in fixed_cars:
            print(f"  ID: {car[0]} - {car[1]}")

if __name__ == "__main__":
    fix_car_ids()