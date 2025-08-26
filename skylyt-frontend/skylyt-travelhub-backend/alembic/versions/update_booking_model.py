"""Update booking model with customer details

Revision ID: update_booking_model
Revises: update_hotel_model
Create Date: 2024-01-01 00:00:02.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'update_booking_model'
down_revision = 'update_hotel_model'
branch_labels = None
depends_on = None

def upgrade():
    # Add customer details
    op.add_column('bookings', sa.Column('customer_name', sa.String(255), nullable=False, server_default='Unknown'))
    op.add_column('bookings', sa.Column('customer_email', sa.String(255), nullable=False, server_default='unknown@example.com'))
    
    # Add booking details
    op.add_column('bookings', sa.Column('number_of_guests', sa.Integer(), nullable=True))
    op.add_column('bookings', sa.Column('special_requests', sa.String(1000), nullable=True))
    op.add_column('bookings', sa.Column('payment_status', sa.String(20), nullable=False, server_default='pending'))

def downgrade():
    # Remove added columns
    op.drop_column('bookings', 'payment_status')
    op.drop_column('bookings', 'special_requests')
    op.drop_column('bookings', 'number_of_guests')
    op.drop_column('bookings', 'customer_email')
    op.drop_column('bookings', 'customer_name')