from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base

class AboutSettings(Base):
    __tablename__ = "about_settings"

    id = Column(Integer, primary_key=True, index=True)
    page_title = Column(String(200), default="About Skylyt Luxury")
    page_description = Column(Text, default="Your trusted partner in luxury travel experiences.")
    company_story = Column(Text, default="Founded with a passion for exceptional travel experiences...")
    mission_statement = Column(Text, default="To provide unparalleled luxury travel experiences...")
    vision_statement = Column(Text, default="To be the world's leading platform for luxury travel...")
    core_values = Column(JSON, default=["Excellence", "Integrity", "Innovation", "Customer Focus", "Sustainability"])
    team_description = Column(Text, default="Our dedicated team of travel experts works around the clock...")
    achievements = Column(JSON, default=[
        {"title": "10,000+ Happy Customers", "description": "Served customers across multiple countries", "icon": "users"},
        {"title": "500+ Premium Hotels", "description": "Curated selection of luxury accommodations", "icon": "hotel"},
        {"title": "200+ Luxury Vehicles", "description": "Fleet of premium cars and chauffeur services", "icon": "car"},
        {"title": "24/7 Support", "description": "Round-the-clock customer assistance", "icon": "clock"}
    ])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())