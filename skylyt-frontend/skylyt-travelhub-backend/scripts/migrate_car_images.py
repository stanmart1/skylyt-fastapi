#!/usr/bin/env python3
"""
Script to migrate existing car JSON images to CarImage table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.car import Car
from app.models.car_image import CarImage

def migrate_car_images():
    """Migrate existing Car.images JSON data to CarImage records"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        cars = db.query(Car).filter(Car.images.isnot(None)).all()
        migrated_count = 0
        
        for car in cars:
            if car.images and isinstance(car.images, list):
                # Check if already migrated
                existing_images = db.query(CarImage).filter(CarImage.car_id == car.id).count()
                if existing_images > 0:
                    print(f"Skipping {car.name} - already has CarImage records")
                    continue
                
                # Create CarImage records from JSON images
                for idx, image_url in enumerate(car.images):
                    car_image = CarImage(
                        car_id=car.id,
                        image_url=image_url,
                        is_cover=(idx == 0),  # First image is cover
                        display_order=idx + 1
                    )
                    db.add(car_image)
                
                migrated_count += 1
                print(f"Migrated {len(car.images)} images for {car.name}")
        
        db.commit()
        print(f"\nSuccessfully migrated images for {migrated_count} cars")
        
    except Exception as e:
        db.rollback()
        print(f"Error migrating car images: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_car_images()