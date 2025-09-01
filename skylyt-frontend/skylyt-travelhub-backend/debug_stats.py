#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.car import Car
from app.models.hotel import Hotel

def debug_stats():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("=== DATABASE DEBUG ===")
        
        # Check cars table
        print("\n--- CARS ---")
        try:
            car_count = db.query(Car).count()
            print(f"Total cars in database: {car_count}")
            
            if car_count > 0:
                cars = db.query(Car).limit(3).all()
                for car in cars:
                    print(f"Car: {car.name}, Available: {car.is_available}")
        except Exception as e:
            print(f"Error querying cars: {e}")
        
        # Check hotels table
        print("\n--- HOTELS ---")
        try:
            hotel_count = db.query(Hotel).count()
            print(f"Total hotels in database: {hotel_count}")
            
            if hotel_count > 0:
                hotels = db.query(Hotel).limit(3).all()
                for hotel in hotels:
                    print(f"Hotel: {hotel.name}, Rooms: {hotel.room_count}")
        except Exception as e:
            print(f"Error querying hotels: {e}")
        
        # Check raw table counts
        print("\n--- RAW TABLE COUNTS ---")
        try:
            result = db.execute(text("SELECT COUNT(*) FROM cars"))
            print(f"Raw cars count: {result.scalar()}")
        except Exception as e:
            print(f"Error with raw cars query: {e}")
            
        try:
            result = db.execute(text("SELECT COUNT(*) FROM hotels"))
            print(f"Raw hotels count: {result.scalar()}")
        except Exception as e:
            print(f"Error with raw hotels query: {e}")
            
    finally:
        db.close()

if __name__ == "__main__":
    debug_stats()