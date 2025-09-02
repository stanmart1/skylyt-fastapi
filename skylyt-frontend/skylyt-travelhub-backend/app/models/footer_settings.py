from sqlalchemy import Column, String, Text
from .base import BaseModel


class FooterSettings(BaseModel):
    __tablename__ = "footer_settings"
    
    # Company Info
    company_name = Column(String(255), nullable=False, default="Skylyt Luxury")
    company_description = Column(Text, nullable=False, default="Your perfect journey awaits. Rent premium cars and book luxurious hotels with confidence.")
    
    # Social Media Links
    twitter_url = Column(String(500), nullable=True)
    instagram_url = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    
    # Contact Info
    contact_address = Column(Text, nullable=False, default="123 Business Ave, Suite 100\nNew York, NY 10001")
    contact_phone = Column(String(50), nullable=False, default="+1 (555) 123-4567")
    contact_email = Column(String(255), nullable=False, default="support@skylytluxury.com")