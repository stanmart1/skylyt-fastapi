"""Add contact and about settings tables

Revision ID: add_contact_about_settings
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_contact_about_settings'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create contact_settings table
    op.create_table('contact_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('page_title', sa.String(length=200), nullable=True),
        sa.Column('page_description', sa.Text(), nullable=True),
        sa.Column('contact_email', sa.String(length=100), nullable=True),
        sa.Column('contact_phone', sa.String(length=50), nullable=True),
        sa.Column('contact_address', sa.Text(), nullable=True),
        sa.Column('office_hours', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contact_settings_id'), 'contact_settings', ['id'], unique=False)

    # Create about_settings table
    op.create_table('about_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('page_title', sa.String(length=200), nullable=True),
        sa.Column('page_description', sa.Text(), nullable=True),
        sa.Column('company_story', sa.Text(), nullable=True),
        sa.Column('mission_statement', sa.Text(), nullable=True),
        sa.Column('vision_statement', sa.Text(), nullable=True),
        sa.Column('core_values', sa.JSON(), nullable=True),
        sa.Column('team_description', sa.Text(), nullable=True),
        sa.Column('achievements', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_about_settings_id'), 'about_settings', ['id'], unique=False)

    # Insert default contact settings
    op.execute("""
        INSERT INTO contact_settings (page_title, page_description, contact_email, contact_phone, contact_address, office_hours)
        VALUES (
            'Contact Us',
            'Get in touch with our team for any inquiries or support.',
            'support@skylytluxury.com',
            '+1 (555) 123-4567',
            '123 Business Ave, Suite 100\nNew York, NY 10001',
            'Monday - Friday: 9:00 AM - 6:00 PM\nSaturday: 10:00 AM - 4:00 PM\nSunday: Closed'
        )
    """)

    # Insert default about settings
    op.execute("""
        INSERT INTO about_settings (
            page_title, page_description, company_story, mission_statement, vision_statement, 
            core_values, team_description, achievements
        )
        VALUES (
            'About Skylyt Luxury',
            'Your trusted partner in luxury travel experiences.',
            'Founded with a passion for exceptional travel experiences, Skylyt Luxury has been connecting travelers with premium accommodations and luxury vehicles since our inception. We believe that every journey should be memorable, comfortable, and tailored to your unique preferences.',
            'To provide unparalleled luxury travel experiences through premium accommodations and exceptional service, making every journey extraordinary.',
            'To be the world''s leading platform for luxury travel, setting new standards in hospitality and customer satisfaction.',
            '["Excellence", "Integrity", "Innovation", "Customer Focus", "Sustainability"]',
            'Our dedicated team of travel experts works around the clock to ensure your experience exceeds expectations. From our customer service representatives to our partner network, everyone is committed to delivering excellence.',
            '[
                {"title": "10,000+ Happy Customers", "description": "Served customers across multiple countries", "icon": "users"},
                {"title": "500+ Premium Hotels", "description": "Curated selection of luxury accommodations", "icon": "hotel"},
                {"title": "200+ Luxury Vehicles", "description": "Fleet of premium cars and chauffeur services", "icon": "car"},
                {"title": "24/7 Support", "description": "Round-the-clock customer assistance", "icon": "clock"}
            ]'
        )
    """)


def downgrade():
    op.drop_index(op.f('ix_about_settings_id'), table_name='about_settings')
    op.drop_table('about_settings')
    op.drop_index(op.f('ix_contact_settings_id'), table_name='contact_settings')
    op.drop_table('contact_settings')