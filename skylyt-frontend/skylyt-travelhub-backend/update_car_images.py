#!/usr/bin/env python3
"""
Script to update all cars in the database with 6 similar images each.
Preserves existing functionality by keeping the first image as the primary one.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.car import Car

# Car image sets - 6 similar images per car type/category
CAR_IMAGES = {
    "luxury": [
        "https://images.unsplash.com/photo-1563720223185-11003d516935?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1571607388263-1044f9ea01dd?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=800&h=600&fit=crop"
    ],
    "economy": [
        "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1605559424843-9e4c228bf1c2?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1494976688153-ca3ce29cd5b8?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1502877338535-766e1452684a?w=800&h=600&fit=crop"
    ],
    "suv": [
        "https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1566473965997-3de9c817e938?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1609521263047-f8f205293f24?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1581540222194-0def2dda95b8?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1617788138017-80ad40651399?w=800&h=600&fit=crop"
    ],
    "compact": [
        "https://images.unsplash.com/photo-1502877338535-766e0107ad1b?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1494976688153-ca3ce29cd5b8?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1605559424843-9e4c228bf1c2?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800&h=600&fit=crop"
    ],
    "midsize": [
        "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1571607388263-1044f9ea01dd?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1563720223185-11003d516935?w=800&h=600&fit=crop"
    ],
    "van": [
        "https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1566473965997-3de9c817e938?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1617788138017-80ad40651399?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1581540222194-0def2dda95b8?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1609521263047-f8f205293f24?w=800&h=600&fit=crop"
    ]
}

def update_car_images():
    """Update all cars with 6 similar images based on their category"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        cars = db.query(Car).all()
        updated_count = 0
        
        for car in cars:
            category = car.category.lower() if car.category else "economy"
            
            # Get images for this category, fallback to economy if category not found
            images = CAR_IMAGES.get(category, CAR_IMAGES["economy"])
            
            # Update car with new images array
            car.images = images
            updated_count += 1
            
            print(f"Updated {car.name} ({category}) with {len(images)} images")
        
        db.commit()
        print(f"\nSuccessfully updated {updated_count} cars with multiple images")
        
    except Exception as e:
        db.rollback()
        print(f"Error updating car images: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_car_images()