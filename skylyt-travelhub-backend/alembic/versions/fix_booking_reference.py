"""fix booking reference column

Revision ID: fix_booking_ref
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'fix_booking_ref'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add booking_reference column to bookings table if it doesn't exist
    try:
        op.add_column('bookings', sa.Column('booking_reference', sa.String(50), nullable=True))
    except:
        pass  # Column might already exist
    
    # Update existing records with generated references
    op.execute("""
        UPDATE bookings 
        SET booking_reference = 'BK' || UPPER(SUBSTRING(MD5(RANDOM()::TEXT), 1, 8))
        WHERE booking_reference IS NULL OR booking_reference = ''
    """)
    
    # Make column non-nullable and unique
    try:
        op.alter_column('bookings', 'booking_reference', nullable=False)
        op.create_unique_constraint('uq_bookings_booking_reference', 'bookings', ['booking_reference'])
    except:
        pass  # Constraints might already exist

def downgrade():
    try:
        op.drop_constraint('uq_bookings_booking_reference', 'bookings', type_='unique')
        op.drop_column('bookings', 'booking_reference')
    except:
        pass