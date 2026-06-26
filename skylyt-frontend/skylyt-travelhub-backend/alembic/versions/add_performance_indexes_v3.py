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
    op.create_index('idx_hotels_featured_available', 'hotels', ['is_featured', 'is_available'], if_not_exists=True)
    op.create_index('idx_hotels_location', 'hotels', ['location'], if_not_exists=True)
    op.create_index('idx_hotels_price', 'hotels', ['price_per_night'], if_not_exists=True)
    op.create_index('idx_hotels_rating', 'hotels', ['star_rating'], if_not_exists=True)

    # Cars indexes
    op.create_index('idx_cars_category_available', 'cars', ['category', 'is_available'], if_not_exists=True)
    op.create_index('idx_cars_location', 'cars', ['location'], if_not_exists=True)
    op.create_index('idx_cars_price', 'cars', ['price_per_day'], if_not_exists=True)
    op.create_index('idx_cars_seats', 'cars', ['seats'], if_not_exists=True)

    # Bookings indexes
    op.create_index('idx_bookings_user_status', 'bookings', ['user_id', 'status'], if_not_exists=True)
    op.create_index('idx_bookings_status_created', 'bookings', ['status', 'created_at'], if_not_exists=True)
    op.create_index('idx_bookings_type_status', 'bookings', ['booking_type', 'status'], if_not_exists=True)

    # Payments indexes
    op.create_index('idx_payments_status', 'payments', ['status'], if_not_exists=True)
    op.create_index('idx_payments_booking', 'payments', ['booking_id'], if_not_exists=True)
    op.create_index('idx_payments_created', 'payments', ['created_at'], if_not_exists=True)

    # States and Cities indexes
    op.create_index('idx_states_slug', 'states', ['slug'], if_not_exists=True)
    op.create_index('idx_states_featured', 'states', ['is_featured', 'popularity_score'], if_not_exists=True)
    op.create_index('idx_cities_state', 'cities', ['state_id'], if_not_exists=True)
    op.create_index('idx_cities_slug', 'cities', ['slug'], if_not_exists=True)
    op.create_index('idx_cities_featured', 'cities', ['is_featured', 'popularity_ranking'], if_not_exists=True)

    # Users indexes
    op.create_index('idx_users_email', 'users', ['email'], if_not_exists=True)
    op.create_index('idx_users_active', 'users', ['is_active', 'is_verified'], if_not_exists=True)

    # Hotel images indexes
    op.create_index('idx_hotel_images_hotel_cover', 'hotel_images', ['hotel_id', 'is_cover'], if_not_exists=True)

    # Car images indexes
    op.create_index('idx_car_images_car_cover', 'car_images', ['car_id', 'is_cover'], if_not_exists=True)


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
    op.drop_index('idx_payments_booking', 'payments')
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