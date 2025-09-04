#!/usr/bin/env python3
"""
Script to update hotels with multiple unique images that match their names
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.hotel import Hotel
from app.models.hotel_image import HotelImage

# Hotel-specific image sets - 5 unique images per hotel
HOTEL_IMAGES = {
    "Eko Hotel & Suites": [
        "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&h=600&fit=crop", 
        "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&h=600&fit=crop"
    ],
    "The Wheatbaker Hotel": [
        "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=800&h=600&fit=crop"
    ],
    "Radisson Blu Anchorage Hotel": [
        "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1587985064135-0366536eab42?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800&h=600&fit=crop"
    ],
    "Four Points by Sheraton Lagos": [
        "https://images.unsplash.com/photo-1549294413-26f195200c16?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1561501900-3701fa6a0864?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1568495248636-6432b97bd949?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1576013551627-0cc20b96c2a7?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&h=600&fit=crop"
    ],
    "Nicon Luxury Hotel": [
        "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1584132915807-fd1f5fbc078f?w=800&h=600&fit=crop"
    ],
    "Lagos Continental Hotel": [
        "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800&h=600&fit=crop"
    ],
    "The George Hotel": [
        "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1587985064135-0366536eab42?w=800&h=600&fit=crop"
    ],
    "BON Hotel Ikeja": [
        "https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1549294413-26f195200c16?w=800&h=600&fit=crop"
    ],
    "Protea Hotel Ikeja": [
        "https://images.unsplash.com/photo-1561501900-3701fa6a0864?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1568495248636-6432b97bd949?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1576013551627-0cc20b96c2a7?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?w=800&h=600&fit=crop"
    ],
    "Transcorp Hilton Abuja": [
        "https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1584132915807-fd1f5fbc078f?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800&h=600&fit=crop"
    ],
    "Kano Grand Hotel": [
        "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&h=600&fit=crop"
    ],
    "Chelsea Hotel Abuja": [
        "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1587985064135-0366536eab42?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=800&h=600&fit=crop"
    ]
}

def update_hotel_images():
    """Update hotels with multiple unique images"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        hotels = db.query(Hotel).all()
        updated_count = 0
        
        for hotel in hotels:
            # Get images for this hotel
            images = HOTEL_IMAGES.get(hotel.name, [])
            if not images:
                print(f"No images defined for {hotel.name}")
                continue
            
            # Check if already has images
            existing_images = db.query(HotelImage).filter(HotelImage.hotel_id == hotel.id).count()
            if existing_images > 0:
                print(f"Skipping {hotel.name} - already has {existing_images} images")
                continue
            
            # Create HotelImage records
            for idx, image_url in enumerate(images):
                hotel_image = HotelImage(
                    hotel_id=hotel.id,
                    image_url=image_url,
                    is_cover=(idx == 0),  # First image is cover
                    display_order=idx + 1
                )
                db.add(hotel_image)
            
            updated_count += 1
            print(f"Added {len(images)} images for {hotel.name}")
        
        db.commit()
        print(f"\nSuccessfully updated {updated_count} hotels with images")
        
    except Exception as e:
        db.rollback()
        print(f"Error updating hotel images: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_hotel_images()