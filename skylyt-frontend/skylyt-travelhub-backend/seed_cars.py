#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine
from sqlalchemy import text
import json


def seed_cars():
    """Seed the database with realistic car data"""
    
    cars_data = [
        {
            "name": "Toyota Camry 2024",
            "make": "Toyota",
            "model": "Camry",
            "category": "Sedan",
            "price_per_day": 45.00,
            "seats": 5,
            "transmission": "Automatic",
            "features": ["Air Conditioning", "Bluetooth", "Backup Camera", "USB Ports"],
            "images": ["https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?w=500"],
            "is_available": True,
            "is_featured": False
        },
        {
            "name": "BMW X5 2024",
            "make": "BMW",
            "model": "X5",
            "category": "SUV",
            "price_per_day": 120.00,
            "seats": 7,
            "transmission": "Automatic",
            "features": ["Leather Seats", "Navigation", "Sunroof", "Premium Audio", "All-Wheel Drive"],
            "images": ["https://images.unsplash.com/photo-1555215695-3004980ad54e?w=500"],
            "is_available": True,
            "is_featured": True
        },
        {
            "name": "Tesla Model 3 2024",
            "make": "Tesla",
            "model": "Model 3",
            "category": "Electric",
            "price_per_day": 85.00,
            "seats": 5,
            "transmission": "Automatic",
            "features": ["Autopilot", "Supercharging", "Premium Interior", "Glass Roof"],
            "images": ["https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=500"],
            "is_available": True,
            "is_featured": True
        },
        {
            "name": "Honda Civic 2024",
            "make": "Honda",
            "model": "Civic",
            "category": "Compact",
            "price_per_day": 35.00,
            "seats": 5,
            "transmission": "Manual",
            "features": ["Fuel Efficient", "Apple CarPlay", "Safety Sensing"],
            "images": ["https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=500"],
            "is_available": True,
            "is_featured": False
        },
        {
            "name": "Mercedes-Benz C-Class 2024",
            "make": "Mercedes-Benz",
            "model": "C-Class",
            "category": "Luxury",
            "price_per_day": 95.00,
            "seats": 5,
            "transmission": "Automatic",
            "features": ["Premium Sound", "Heated Seats", "Navigation", "Ambient Lighting"],
            "images": ["https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=500"],
            "is_available": True,
            "is_featured": True
        },
        {
            "name": "Ford F-150 2024",
            "make": "Ford",
            "model": "F-150",
            "category": "Truck",
            "price_per_day": 75.00,
            "seats": 6,
            "transmission": "Automatic",
            "features": ["4WD", "Towing Package", "Bed Liner", "Crew Cab"],
            "images": ["https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=500"],
            "is_available": True,
            "is_featured": False
        },
        {
            "name": "Audi A4 2024",
            "make": "Audi",
            "model": "A4",
            "category": "Luxury",
            "price_per_day": 80.00,
            "seats": 5,
            "transmission": "Automatic",
            "features": ["Quattro AWD", "Virtual Cockpit", "Premium Plus", "Bang & Olufsen Audio"],
            "images": ["https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=500"],
            "is_available": True,
            "is_featured": False
        },
        {
            "name": "Jeep Wrangler 2024",
            "make": "Jeep",
            "model": "Wrangler",
            "category": "SUV",
            "price_per_day": 65.00,
            "seats": 4,
            "transmission": "Manual",
            "features": ["4x4", "Removable Doors", "Off-Road Package", "Rock Rails"],
            "images": ["https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=500"],
            "is_available": True,
            "is_featured": True
        },
        {
            "name": "Nissan Altima 2024",
            "make": "Nissan",
            "model": "Altima",
            "category": "Sedan",
            "price_per_day": 40.00,
            "seats": 5,
            "transmission": "CVT",
            "features": ["ProPILOT Assist", "Bose Audio", "Remote Start"],
            "images": ["https://images.unsplash.com/photo-1502877338535-766e1452684a?w=500"],
            "is_available": True,
            "is_featured": False
        },
        {
            "name": "Porsche 911 2024",
            "make": "Porsche",
            "model": "911",
            "category": "Sports",
            "price_per_day": 200.00,
            "seats": 2,
            "transmission": "Manual",
            "features": ["Sport Chrono", "Premium Leather", "Sport Exhaust", "Performance Tires"],
            "images": ["https://images.unsplash.com/photo-1503736334956-4c8f8e92946d?w=500"],
            "is_available": True,
            "is_featured": True
        }
    ]
    
    with engine.connect() as conn:
        # Clear existing cars
        conn.execute(text("DELETE FROM cars"))
        
        # Insert new cars (let database auto-increment the ID)
        for car_data in cars_data:
            insert_query = text("""
                INSERT INTO cars (
                    name, make, model, category, price_per_day, seats, 
                    transmission, features, images, is_available, is_featured,
                    created_at, updated_at
                ) VALUES (
                    :name, :make, :model, :category, :price_per_day, :seats,
                    :transmission, :features, :images, :is_available, :is_featured,
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute(insert_query, {
                'name': car_data['name'],
                'make': car_data['make'],
                'model': car_data['model'],
                'category': car_data['category'],
                'price_per_day': car_data['price_per_day'],
                'seats': car_data['seats'],
                'transmission': car_data['transmission'],
                'features': json.dumps(car_data['features']),
                'images': json.dumps(car_data['images']),
                'is_available': car_data['is_available'],
                'is_featured': car_data['is_featured']
            })
        
        conn.commit()
        print(f"Successfully seeded {len(cars_data)} cars into the database!")

if __name__ == "__main__":
    seed_cars()