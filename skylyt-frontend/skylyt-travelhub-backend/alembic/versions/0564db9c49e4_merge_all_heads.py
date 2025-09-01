"""merge_all_heads

Revision ID: 0564db9c49e4
Revises: add_car_plate_number, add_currency_support, add_phone_back, create_hotel_images, e22b0c72d0bf, fix_monetary_precision
Create Date: 2025-09-01 21:55:12.333045

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0564db9c49e4'
down_revision = ('add_car_plate_number', 'add_currency_support', 'add_phone_back', 'create_hotel_images', 'e22b0c72d0bf', 'fix_monetary_precision')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass