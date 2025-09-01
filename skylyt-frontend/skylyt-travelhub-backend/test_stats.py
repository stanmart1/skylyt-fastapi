#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.car import Car
from app.models.hotel import Hotel

def test_stats():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("=== TESTING STATS QUERIES ===")
        
        # Test car queries
        print("\n--- CAR STATS ---")
        total_cars = db.query(Car).count()
        print(f"Total cars: {total_cars}")
        
        available_cars = db.query(Car).filter(Car.is_available == True).count()
        print(f"Available cars: {available_cars}")
        
        # Test hotel queries  
        print("\n--- HOTEL STATS ---")
        total_hotels = db.query(Hotel).count()
        print(f"Total hotels: {total_hotels}")
        
        from sqlalchemy import func
        total_rooms = db.query(func.sum(Hotel.room_count)).scalar() or 0
        print(f"Total rooms: {total_rooms}")
        
        # Test the exact queries from the endpoints
        print("\n--- ENDPOINT SIMULATION ---")
        
        # Car stats endpoint simulation
        try:
            car_stats = {
                "total_cars": db.query(Car).count(),
                "available": db.query(Car).filter(Car.is_available == True).count(),
                "booked": 0,  # No active bookings yet
                "maintenance": 0,
                "revenue_today": 0.0,
                "utilization_rate": 0.0
            }
            print(f"Car stats: {car_stats}")
        except Exception as e:
            print(f"Car stats error: {e}")
            
        # Hotel stats endpoint simulation
        try:
            hotel_stats = {
                "totalHotels": db.query(Hotel).count(),
                "totalRooms": int(db.query(func.sum(Hotel.room_count)).scalar() or 0),
                "activeBookings": 0,
                "totalRevenue": 0.0,
                "revenueChange": 0.0,
                "occupancyRate": 0.0
            }
            print(f"Hotel stats: {hotel_stats}")
        except Exception as e:
            print(f"Hotel stats error: {e}")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_stats()