"""add booking reference column

Revision ID: add_booking_reference
Revises: add_database_indexes
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_booking_reference'
down_revision = 'add_indexes_001'
branch_labels = None
depends_on = None

def upgrade():
    # Add booking_reference column to bookings table
    op.add_column('bookings', sa.Column('booking_reference', sa.String(50), nullable=True))
    
    # Update existing records with generated references
    op.execute("""
        UPDATE bookings 
        SET booking_reference = 'BK' || UPPER(SUBSTRING(MD5(RANDOM()::TEXT), 1, 8))
        WHERE booking_reference IS NULL
    """)
    
    # Make column non-nullable and unique
    op.alter_column('bookings', 'booking_reference', nullable=False)
    op.create_unique_constraint('uq_bookings_booking_reference', 'bookings', ['booking_reference'])

def downgrade():
    op.drop_constraint('uq_bookings_booking_reference', 'bookings', type_='unique')
    op.drop_column('bookings', 'booking_reference')