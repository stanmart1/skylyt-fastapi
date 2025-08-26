"""Update hotel model with new fields

Revision ID: update_hotel_model
Revises: add_performance_indexes
Create Date: 2024-01-01 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'update_hotel_model'
down_revision = 'add_performance_indexes'
branch_labels = None
depends_on = None

def upgrade():
    # Rename existing columns
    op.alter_column('hotels', 'rating', new_column_name='star_rating')
    op.alter_column('hotels', 'price', new_column_name='price_per_night')
    
    # Add new columns
    op.add_column('hotels', sa.Column('room_count', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('hotels', sa.Column('images', sa.JSON(), nullable=True))
    op.add_column('hotels', sa.Column('features', sa.JSON(), nullable=True))
    op.add_column('hotels', sa.Column('is_available', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('hotels', sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'))
    
    # Drop old column
    op.drop_column('hotels', 'image_url')

def downgrade():
    # Add back old column
    op.add_column('hotels', sa.Column('image_url', sa.String(), nullable=True))
    
    # Drop new columns
    op.drop_column('hotels', 'is_featured')
    op.drop_column('hotels', 'is_available')
    op.drop_column('hotels', 'features')
    op.drop_column('hotels', 'images')
    op.drop_column('hotels', 'room_count')
    
    # Rename columns back
    op.alter_column('hotels', 'price_per_night', new_column_name='price')
    op.alter_column('hotels', 'star_rating', new_column_name='rating')