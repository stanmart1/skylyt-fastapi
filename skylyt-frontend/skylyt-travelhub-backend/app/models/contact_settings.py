from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class ContactSettings(Base):
    __tablename__ = "contact_settings"

    id = Column(Integer, primary_key=True, index=True)
    page_title = Column(String(200), default="Contact Us")
    page_description = Column(Text, default="Get in touch with our team for any inquiries or support.")
    contact_email = Column(String(100), default="support@skylytluxury.com")
    contact_phone = Column(String(50), default="+1 (555) 123-4567")
    contact_address = Column(Text, default="123 Business Ave, Suite 100\nNew York, NY 10001")
    office_hours = Column(Text, default="Monday - Friday: 9:00 AM - 6:00 PM\nSaturday: 10:00 AM - 4:00 PM\nSunday: Closed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())