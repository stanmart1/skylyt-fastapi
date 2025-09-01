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

def check_cars():
    """Check existing cars in the database"""
    
    with engine.connect() as conn:
        # Get all existing cars
        result = conn.execute(text("SELECT id, name, make, model, category FROM cars ORDER BY created_at"))
        cars = result.fetchall()
        
        if not cars:
            print("No cars found in database")
            return
        
        print(f"Found {len(cars)} cars in database:")
        print("-" * 80)
        for car in cars:
            print(f"ID: {car[0]} | Name: {car[1]} | Make: {car[2]} | Model: {car[3]} | Category: {car[4]}")
        print("-" * 80)
        
        # Check the data type of the ID column
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'cars' AND column_name = 'id'
        """))
        id_info = result.fetchone()
        if id_info:
            print(f"ID column data type: {id_info[1]}")

if __name__ == "__main__":
    check_cars()