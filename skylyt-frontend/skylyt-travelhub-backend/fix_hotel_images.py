#!/usr/bin/env python3
"""
Fix hotel image display by synchronizing Hotel.images with HotelImage table
"""

from app.core.database import SessionLocal
from app.models.hotel import Hotel
from app.models.hotel_image import HotelImage

def fix_hotel_images():
    db = SessionLocal()
    try:
        # Get the Test hotel
        hotel = db.query(Hotel).filter(Hotel.name == 'Test').first()
        if not hotel:
            print("Hotel 'Test' not found")
            return
        
        print(f"Found hotel: {hotel.name} (ID: {hotel.id})")
        print(f"Current hotel.images: {hotel.images}")
        
        # Clear existing hotel_images records for this hotel
        existing_images = db.query(HotelImage).filter(HotelImage.hotel_id == hotel.id).all()
        for img in existing_images:
            db.delete(img)
        
        # If hotel.images has valid URLs, create HotelImage records
        if hotel.images:
            for i, image_url in enumerate(hotel.images):
                # Check if image file exists
                import os
                from pathlib import Path
                
                if image_url.startswith('/uploads/'):
                    file_path = Path(image_url[1:])  # Remove leading slash
                    if file_path.exists():
                        hotel_image = HotelImage(
                            hotel_id=hotel.id,
                            image_url=image_url,
                            is_cover=(i == 0),  # First image is cover
                            display_order=i + 1
                        )
                        db.add(hotel_image)
                        print(f"Added HotelImage record: {image_url}")
                    else:
                        print(f"File not found: {file_path}")
        
        # If no valid images, use placeholder
        if not hotel.images or not any(Path(url[1:]).exists() for url in hotel.images if url.startswith('/uploads/')):
            # Use existing hotel image as placeholder
            placeholder_url = '/uploads/hotels/a96b9e40-530d-471b-9727-b152e5b86760.png'
            
            hotel_image = HotelImage(
                hotel_id=hotel.id,
                image_url=placeholder_url,
                is_cover=True,
                display_order=1
            )
            db.add(hotel_image)
            
            # Update hotel.images to match
            hotel.images = [placeholder_url]
            print(f"Added placeholder image: {placeholder_url}")
        
        db.commit()
        
        # Verify the fix
        hotel_images = db.query(HotelImage).filter(HotelImage.hotel_id == hotel.id).all()
        print(f"\nFixed! Hotel now has {len(hotel_images)} image records:")
        for img in hotel_images:
            print(f"  - {img.image_url} (cover: {img.is_cover})")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_hotel_images()