from fastapi import APIRouter, Depends, Response
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from datetime import datetime
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET

router = APIRouter(prefix="/seo", tags=["SEO"])

@router.get("/sitemap.xml", response_class=PlainTextResponse)
async def generate_sitemap(db: Session = Depends(get_db)):
    """Generate XML sitemap for search engines"""
    from app.models.hotel import Hotel
    from app.models.car import Car
    
    # Create root element
    urlset = ET.Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    
    base_url = "https://skylytluxury.com"
    
    # Add main pages
    main_pages = [
        {"url": "/", "priority": "1.0", "changefreq": "daily"},
        {"url": "/hotels", "priority": "0.9", "changefreq": "daily"},
        {"url": "/cars", "priority": "0.9", "changefreq": "daily"},
        {"url": "/about", "priority": "0.5", "changefreq": "monthly"},
        {"url": "/contact", "priority": "0.5", "changefreq": "monthly"}
    ]
    
    for page in main_pages:
        url_elem = ET.SubElement(urlset, "url")
        ET.SubElement(url_elem, "loc").text = f"{base_url}{page['url']}"
        ET.SubElement(url_elem, "lastmod").text = datetime.now().strftime("%Y-%m-%d")
        ET.SubElement(url_elem, "changefreq").text = page["changefreq"]
        ET.SubElement(url_elem, "priority").text = page["priority"]
    
    # Add hotel pages
    hotels = db.query(Hotel).filter(Hotel.is_available == True).all()
    for hotel in hotels:
        url_elem = ET.SubElement(urlset, "url")
        slug = hotel.name.lower().replace(" ", "-").replace("&", "and")
        ET.SubElement(url_elem, "loc").text = f"{base_url}/hotels/{hotel.id}/{slug}"
        ET.SubElement(url_elem, "lastmod").text = hotel.updated_at.strftime("%Y-%m-%d")
        ET.SubElement(url_elem, "changefreq").text = "weekly"
        ET.SubElement(url_elem, "priority").text = "0.8"
    
    # Add car pages
    cars = db.query(Car).filter(Car.is_available == True).all()
    for car in cars:
        url_elem = ET.SubElement(urlset, "url")
        slug = f"{car.make}-{car.model}".lower().replace(" ", "-")
        ET.SubElement(url_elem, "loc").text = f"{base_url}/cars/{car.id}/{slug}"
        ET.SubElement(url_elem, "lastmod").text = car.updated_at.strftime("%Y-%m-%d")
        ET.SubElement(url_elem, "changefreq").text = "weekly"
        ET.SubElement(url_elem, "priority").text = "0.8"
    
    # Convert to string
    xml_str = ET.tostring(urlset, encoding='unicode')
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'

@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    """Generate robots.txt for search engine crawlers"""
    robots_content = """User-agent: *
Allow: /
Allow: /api/v1/hotels/
Allow: /api/v1/cars/
Allow: /uploads/

Disallow: /api/v1/admin/
Disallow: /api/v1/auth/
Disallow: /api/v1/payments/
Disallow: /docs
Disallow: /redoc

Sitemap: https://skylytluxury.com/api/v1/seo/sitemap.xml

# Crawl-delay for respectful crawling
Crawl-delay: 1
"""
    return robots_content

@router.get("/meta-tags/{page_type}")
async def get_meta_tags(
    page_type: str,
    item_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Generate meta tags for different page types"""
    base_meta = {
        "site_name": "Skylyt Luxury",
        "type": "website",
        "locale": "en_US"
    }
    
    if page_type == "home":
        return {
            **base_meta,
            "title": "Skylyt Luxury - Premium Car Rentals & Hotel Bookings",
            "description": "Book luxury cars and premium hotels worldwide. Experience comfort and elegance with Skylyt's curated selection of high-end accommodations and vehicles.",
            "keywords": "luxury car rental, premium hotels, luxury travel, car hire, hotel booking",
            "canonical": "https://skylytluxury.com/",
            "og_image": "https://skylytluxury.com/uploads/general/skylyt-og-image.jpg"
        }
    
    elif page_type == "hotels":
        if item_id:
            hotel = db.query(Hotel).filter(Hotel.id == item_id).first()
            if hotel:
                return {
                    **base_meta,
                    "title": f"{hotel.name} - Luxury Hotel in {hotel.location} | Skylyt",
                    "description": f"Book {hotel.name} in {hotel.location}. {hotel.star_rating}-star luxury hotel with premium amenities. Starting from ${hotel.price_per_night}/night.",
                    "keywords": f"luxury hotel {hotel.location}, {hotel.name}, premium accommodation, {hotel.location} hotels",
                    "canonical": f"https://skylytluxury.com/hotels/{hotel.id}",
                    "og_image": hotel.images[0] if hotel.images else None
                }
        return {
            **base_meta,
            "title": "Luxury Hotels Worldwide - Premium Accommodations | Skylyt",
            "description": "Discover and book luxury hotels worldwide. Premium accommodations with exceptional service and amenities.",
            "keywords": "luxury hotels, premium accommodations, hotel booking, luxury travel",
            "canonical": "https://skylytluxury.com/hotels"
        }
    
    elif page_type == "cars":
        if item_id:
            car = db.query(Car).filter(Car.id == item_id).first()
            if car:
                return {
                    **base_meta,
                    "title": f"{car.make} {car.model} - Luxury Car Rental | Skylyt",
                    "description": f"Rent {car.make} {car.model} - {car.category} luxury car. {car.seats} passengers, {car.transmission} transmission. From ${car.price_per_day}/day.",
                    "keywords": f"luxury car rental, {car.make} {car.model}, {car.category} car rental, premium car hire",
                    "canonical": f"https://skylytluxury.com/cars/{car.id}",
                    "og_image": car.images[0] if car.images else None
                }
        return {
            **base_meta,
            "title": "Luxury Car Rentals - Premium Vehicle Fleet | Skylyt",
            "description": "Rent luxury cars from our premium fleet. Sports cars, SUVs, and exotic vehicles available worldwide.",
            "keywords": "luxury car rental, premium car hire, exotic car rental, sports car rental",
            "canonical": "https://skylytluxury.com/cars"
        }
    
    return base_meta

@router.get("/canonical-url/{page_type}")
async def get_canonical_url(page_type: str, item_id: Optional[str] = None):
    """Generate canonical URLs to prevent duplicate content"""
    base_url = "https://skylytluxury.com"
    
    canonical_urls = {
        "home": f"{base_url}/",
        "hotels": f"{base_url}/hotels" + (f"/{item_id}" if item_id else ""),
        "cars": f"{base_url}/cars" + (f"/{item_id}" if item_id else ""),
        "about": f"{base_url}/about",
        "contact": f"{base_url}/contact"
    }
    
    return {"canonical_url": canonical_urls.get(page_type, base_url)}