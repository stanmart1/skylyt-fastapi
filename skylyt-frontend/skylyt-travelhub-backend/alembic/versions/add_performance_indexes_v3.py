"""Add performance indexes for common query patterns

Revision ID: add_performance_indexes_v3
Revises: update_hotel_model
Create Date: 2026-06-26

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_performance_indexes_v3'
down_revision = 'update_hotel_model'
branch_labels = None
depends_on = None


def upgrade():
    # Hotels indexes
    op.create_index('idx_hotels_featured_available', 'hotels', ['is_featured', 'is_available'])
    op.create_index('idx_hotels_location', 'hotels', ['location'])
    op.create_index('idx_hotels_price', 'hotels', ['price_per_night'])
    op.create_index('idx_hotels_rating', 'hotels', ['star_rating'])
    
    # Cars indexes
    op.create_index('idx_cars_category_available', 'cars', ['category', 'is_available'])
    op.create_index('idx_cars_location', 'cars', ['location'])
    op.create_index('idx_cars_price', 'cars', ['price_per_day'])
    op.create_index('idx_cars_seats', 'cars', ['seats'])
    
    # Bookings indexes
    op.create_index('idx_bookings_user_status', 'bookings', ['user_id', 'status'])
    op.create_index('idx_bookings_status_created', 'bookings', ['status', 'created_at'])
    op.create_index('idx_bookings_type_status', 'bookings', ['booking_type', 'status'])
    
    # Payments indexes
    op.create_index('idx_payments_status', 'payments', ['status'])
    op.create_index('idx_payments_user', 'payments', ['user_id'])
    op.create_index('idx_payments_created', 'payments', ['created_at'])
    
    # States and Cities indexes
    op.create_index('idx_states_slug', 'states', ['slug'])
    op.create_index('idx_states_featured', 'states', ['is_featured', 'popularity_score'])
    op.create_index('idx_cities_state', 'cities', ['state_id'])
    op.create_index('idx_cities_slug', 'cities', ['slug'])
    op.create_index('idx_cities_featured', 'cities', ['is_featured', 'popularity_ranking'])
    
    # Users indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_active', 'users', ['is_active', 'is_verified'])
    
    # Hotel images indexes
    op.create_index('idx_hotel_images_hotel_cover', 'hotel_images', ['hotel_id', 'is_cover'])
    
    # Car images indexes
    op.create_index('idx_car_images_car_cover', 'car_images', ['car_id', 'is_cover'])


def downgrade():
    # Hotels indexes
    op.drop_index('idx_hotels_featured_available', 'hotels')
    op.drop_index('idx_hotels_location', 'hotels')
    op.drop_index('idx_hotels_price', 'hotels')
    op.drop_index('idx_hotels_rating', 'hotels')
    
    # Cars indexes
    op.drop_index('idx_cars_category_available', 'cars')
    op.drop_index('idx_cars_location', 'cars')
    op.drop_index('idx_cars_price', 'cars')
    op.drop_index('idx_cars_seats', 'cars')
    
    # Bookings indexes
    op.drop_index('idx_bookings_user_status', 'bookings')
    op.drop_index('idx_bookings_status_created', 'bookings')
    op.drop_index('idx_bookings_type_status', 'bookings')
    
    # Payments indexes
    op.drop_index('idx_payments_status', 'payments')
    op.drop_index('idx_payments_user', 'payments')
    op.drop_index('idx_payments_created', 'payments')
    
    # States and Cities indexes
    op.drop_index('idx_states_slug', 'states')
    op.drop_index('idx_states_featured', 'states')
    op.drop_index('idx_cities_state', 'cities')
    op.drop_index('idx_cities_slug', 'cities')
    op.drop_index('idx_cities_featured', 'cities')
    
    # Users indexes
    op.drop_index('idx_users_email', 'users')
    op.drop_index('idx_users_active', 'users')
    
    # Hotel images indexes
    op.drop_index('idx_hotel_images_hotel_cover', 'hotel_images')
    
    # Car images indexes
    op.drop_index('idx_car_images_car_cover', 'car_images')