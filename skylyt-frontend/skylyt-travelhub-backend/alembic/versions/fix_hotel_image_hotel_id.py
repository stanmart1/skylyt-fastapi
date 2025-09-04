"""fix_hotel_image_hotel_id

Revision ID: fix_hotel_image_hotel_id
Revises: add_car_images_table
Create Date: 2024-01-01 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fix_hotel_image_hotel_id'
down_revision = 'add_car_images_table'
branch_labels = None
depends_on = None


def upgrade():
    # Change hotel_id column from Integer to String
    op.alter_column('hotel_images', 'hotel_id',
                    existing_type=sa.Integer(),
                    type_=sa.String(),
                    existing_nullable=False)


def downgrade():
    # Change hotel_id column from String back to Integer
    op.alter_column('hotel_images', 'hotel_id',
                    existing_type=sa.String(),
                    type_=sa.Integer(),
                    existing_nullable=False)