"""Update dropoff_location to destination in booking_data

Revision ID: b2c3d4e5f6g7
Revises: f1a2c3d4e5f6
Create Date: 2024-07-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'f1a2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # Update booking_data JSON to rename dropoff_location to destination
    op.execute("""
        UPDATE bookings 
        SET booking_data = jsonb_set(
            booking_data, 
            '{destination}', 
            COALESCE(booking_data->'dropoff_location', booking_data->'destination')
        )
        WHERE booking_data ? 'dropoff_location'
    """)
    
    # Remove the old dropoff_location key from booking_data
    op.execute("""
        UPDATE bookings 
        SET booking_data = booking_data - 'dropoff_location'
        WHERE booking_data ? 'dropoff_location'
    """)


def downgrade():
    # Revert the change by renaming destination back to dropoff_location
    op.execute("""
        UPDATE bookings 
        SET booking_data = jsonb_set(
            booking_data, 
            '{dropoff_location}', 
            COALESCE(booking_data->'destination', booking_data->'dropoff_location')
        )
        WHERE booking_data ? 'destination'
    """)
    
    # Remove the destination key from booking_data
    op.execute("""
        UPDATE bookings 
        SET booking_data = booking_data - 'destination'
        WHERE booking_data ? 'destination'
    """)
