"""add booking columns

Revision ID: add_booking_cols
Revises: add_updated_at
Create Date: 2024-01-01 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_booking_cols'
down_revision = 'add_updated_at'
branch_labels = None
depends_on = None

def upgrade():
    # Add missing columns to bookings table
    try:
        op.add_column('bookings', sa.Column('hotel_name', sa.String(255), nullable=True))
    except:
        pass
    try:
        op.add_column('bookings', sa.Column('car_name', sa.String(255), nullable=True))
    except:
        pass
    try:
        op.add_column('bookings', sa.Column('check_in_date', sa.DateTime(), nullable=True))
    except:
        pass
    try:
        op.add_column('bookings', sa.Column('check_out_date', sa.DateTime(), nullable=True))
    except:
        pass
    try:
        op.add_column('bookings', sa.Column('total_amount', sa.Float(), nullable=True))
    except:
        pass
    try:
        op.add_column('bookings', sa.Column('currency', sa.String(3), nullable=True))
    except:
        pass
    try:
        op.add_column('bookings', sa.Column('booking_data', sa.JSON(), nullable=True))
    except:
        pass
    try:
        op.add_column('bookings', sa.Column('updated_at', sa.DateTime(), nullable=True))
    except:
        pass
    
    # Update existing records
    op.execute("UPDATE bookings SET updated_at = created_at WHERE updated_at IS NULL")
    op.execute("UPDATE bookings SET currency = 'USD' WHERE currency IS NULL")
    op.execute("UPDATE bookings SET total_amount = 0 WHERE total_amount IS NULL")

def downgrade():
    op.drop_column('bookings', 'booking_data')
    op.drop_column('bookings', 'currency')
    op.drop_column('bookings', 'total_amount')
    op.drop_column('bookings', 'check_out_date')
    op.drop_column('bookings', 'check_in_date')
    op.drop_column('bookings', 'car_name')
    op.drop_column('bookings', 'hotel_name')
    op.drop_column('bookings', 'updated_at')