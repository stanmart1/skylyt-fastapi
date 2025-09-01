"""add plate_number to cars

Revision ID: add_car_plate_number
Revises: update_booking_payment_currency
Create Date: 2024-01-01 00:00:02.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_car_plate_number'
down_revision = 'update_booking_payment_currency'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('cars', sa.Column('plate_number', sa.String(), nullable=True))

def downgrade():
    op.drop_column('cars', 'plate_number')
