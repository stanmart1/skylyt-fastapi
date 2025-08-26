#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine
from sqlalchemy import text
import json
import uuid

def seed_hotels():
    """Seed the database with realistic Nigerian hotel data"""
    
    hotels_data = [
        {
            "name": "Eko Hotel & Suites",
            "location": "Victoria Island, Lagos",
            "star_rating": 5.0,
            "price_per_night": 85000.00,
            "amenities": ["Swimming Pool", "Spa", "Fitness Center", "Business Center", "WiFi", "Restaurant", "Bar"],
            "description": "Luxury waterfront hotel in the heart of Lagos with stunning views of the Atlantic Ocean. Features world-class amenities and exceptional service.",
            "images": ["https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500"],
            "is_available": True,
            "is_featured": True,
            "room_count": 450
        },
        {
            "name": "Transcorp Hilton Abuja",
            "location": "Central Business District, Abuja",
            "star_rating": 5.0,
            "price_per_night": 75000.00,
            "amenities": ["Swimming Pool", "Spa", "Golf Course", "Conference Rooms", "WiFi", "Multiple Restaurants"],
            "description": "Premier luxury hotel in Nigeria's capital city, offering exceptional hospitality and modern amenities for business and leisure travelers.",
            "images": ["https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=500"],
            "is_available": True,
            "is_featured": True,
            "room_count": 670
        },
        {
            "name": "The Wheatbaker Hotel",
            "location": "Ikoyi, Lagos",
            "star_rating": 5.0,
            "price_per_night": 95000.00,
            "amenities": ["Rooftop Pool", "Spa", "Fine Dining", "Concierge", "WiFi", "Valet Parking"],
            "description": "Boutique luxury hotel offering personalized service and elegant accommodations in the prestigious Ikoyi district.",
            "images": ["https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=500"],
            "is_available": True,
            "is_featured": True,
            "room_count": 240
        },
        {
            "name": "Radisson Blu Anchorage Hotel",
            "location": "Victoria Island, Lagos",
            "star_rating": 4.0,
            "price_per_night": 65000.00,
            "amenities": ["Swimming Pool", "Fitness Center", "Business Center", "WiFi", "Restaurant", "Meeting Rooms"],
            "description": "Contemporary hotel with modern amenities and excellent location for business travelers visiting Lagos.",
            "images": ["https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=500"],
            "is_available": True,
            "is_featured": False,
            "room_count": 170
        },
        {
            "name": "Four Points by Sheraton Lagos",
            "location": "Victoria Island, Lagos",
            "star_rating": 4.0,
            "price_per_night": 55000.00,
            "amenities": ["Swimming Pool", "Fitness Center", "WiFi", "Restaurant", "Bar", "Airport Shuttle"],
            "description": "Modern hotel offering comfortable accommodations and reliable service in the heart of Lagos business district.",
            "images": ["https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=500"],
            "is_available": True,
            "is_featured": False,
            "room_count": 198
        },
        {
            "name": "Nicon Luxury Hotel",
            "location": "Central Area, Abuja",
            "star_rating": 4.0,
            "price_per_night": 45000.00,
            "amenities": ["Swimming Pool", "Spa", "Business Center", "WiFi", "Multiple Restaurants", "Conference Facilities"],
            "description": "Established luxury hotel in Abuja offering comprehensive facilities for both business and leisure guests.",
            "images": ["https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=500"],
            "is_available": True,
            "is_featured": False,
            "room_count": 365
        },
        {
            "name": "Lagos Continental Hotel",
            "location": "Victoria Island, Lagos",
            "star_rating": 4.0,
            "price_per_night": 50000.00,
            "amenities": ["Swimming Pool", "Fitness Center", "Business Center", "WiFi", "Restaurant", "Laundry Service"],
            "description": "Well-established hotel providing quality accommodation and services in the commercial heart of Lagos.",
            "images": ["https://images.unsplash.com/photo-1590490360182-c33d57733427?w=500"],
            "is_available": True,
            "is_featured": False,
            "room_count": 358
        },
        {
            "name": "The George Hotel",
            "location": "Ikoyi, Lagos",
            "star_rating": 5.0,
            "price_per_night": 80000.00,
            "amenities": ["Rooftop Bar", "Spa", "Fine Dining", "WiFi", "Concierge", "Valet Parking"],
            "description": "Sophisticated boutique hotel offering luxury accommodations and exceptional dining experiences in upscale Ikoyi.",
            "images": ["https://images.unsplash.com/photo-1549294413-26f195200c16?w=500"],
            "is_available": True,
            "is_featured": True,
            "room_count": 100
        },
        {
            "name": "BON Hotel Ikeja",
            "location": "Ikeja, Lagos",
            "star_rating": 3.0,
            "price_per_night": 35000.00,
            "amenities": ["Swimming Pool", "Restaurant", "WiFi", "Airport Shuttle", "Meeting Rooms"],
            "description": "Comfortable mid-range hotel conveniently located near Murtala Muhammed Airport with modern amenities.",
            "images": ["https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=500"],
            "is_available": True,
            "is_featured": False,
            "room_count": 142
        },
        {
            "name": "Chelsea Hotel Abuja",
            "location": "Garki, Abuja",
            "star_rating": 4.0,
            "price_per_night": 40000.00,
            "amenities": ["Swimming Pool", "Fitness Center", "Restaurant", "WiFi", "Business Center", "Spa"],
            "description": "Contemporary hotel in Abuja offering modern comfort and convenience for discerning travelers.",
            "images": ["https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=500"],
            "is_available": True,
            "is_featured": False,
            "room_count": 95
        },
        {
            "name": "Protea Hotel Ikeja",
            "location": "Ikeja, Lagos",
            "star_rating": 4.0,
            "price_per_night": 48000.00,
            "amenities": ["Swimming Pool", "Fitness Center", "Restaurant", "WiFi", "Business Center", "Airport Shuttle"],
            "description": "International standard hotel offering reliable service and modern amenities near Lagos airport.",
            "images": ["https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=500"],
            "is_available": True,
            "is_featured": False,
            "room_count": 188
        },
        {
            "name": "Kano Grand Hotel",
            "location": "Kano City, Kano",
            "star_rating": 3.0,
            "price_per_night": 25000.00,
            "amenities": ["Restaurant", "WiFi", "Conference Rooms", "Laundry Service", "Airport Transfer"],
            "description": "Comfortable accommodation in the commercial center of Northern Nigeria with traditional hospitality.",
            "images": ["https://images.unsplash.com/photo-1587985064135-0366536eab42?w=500"],
            "is_available": True,
            "is_featured": False,
            "room_count": 120
        }
    ]
    
    with engine.connect() as conn:
        # Clear existing hotels
        conn.execute(text("DELETE FROM hotels"))
        
        # Insert new hotels
        for hotel_data in hotels_data:
            hotel_id = str(uuid.uuid4())
            
            insert_query = text("""
                INSERT INTO hotels (
                    id, name, location, star_rating, price_per_night, amenities, 
                    description, images, is_available, is_featured, room_count,
                    created_at, updated_at
                ) VALUES (
                    :id, :name, :location, :star_rating, :price_per_night, :amenities,
                    :description, :images, :is_available, :is_featured, :room_count,
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute(insert_query, {
                'id': hotel_id,
                'name': hotel_data['name'],
                'location': hotel_data['location'],
                'star_rating': hotel_data['star_rating'],
                'price_per_night': hotel_data['price_per_night'],
                'amenities': json.dumps(hotel_data['amenities']),
                'description': hotel_data['description'],
                'images': json.dumps(hotel_data['images']),
                'is_available': hotel_data['is_available'],
                'is_featured': hotel_data['is_featured'],
                'room_count': hotel_data['room_count']
            })
        
        conn.commit()
        print(f"Successfully seeded {len(hotels_data)} hotels into the database!")

if __name__ == "__main__":
    seed_hotels()