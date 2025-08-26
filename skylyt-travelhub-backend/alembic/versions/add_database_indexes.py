"""Add database indexes for performance optimization

Revision ID: add_indexes_001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_indexes_001'
down_revision = None
depends_on = None

def upgrade():
    # User table indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_phone', 'users', ['phone_number'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    
    # Booking table indexes
    op.create_index('idx_bookings_user_id', 'bookings', ['user_id'])
    op.create_index('idx_bookings_status', 'bookings', ['status'])
    op.create_index('idx_bookings_reference', 'bookings', ['booking_reference'])
    op.create_index('idx_bookings_created_at', 'bookings', ['created_at'])
    op.create_index('idx_bookings_check_in', 'bookings', ['check_in_date'])
    op.create_index('idx_bookings_type_status', 'bookings', ['booking_type', 'status'])
    
    # Payment table indexes
    op.create_index('idx_payments_booking_id', 'payments', ['booking_id'])
    op.create_index('idx_payments_status', 'payments', ['status'])
    op.create_index('idx_payments_gateway', 'payments', ['gateway'])
    op.create_index('idx_payments_transaction_id', 'payments', ['transaction_id'])
    op.create_index('idx_payments_created_at', 'payments', ['created_at'])
    
    # Role and Permission indexes
    op.create_index('idx_roles_name', 'roles', ['name'])
    op.create_index('idx_permissions_name', 'permissions', ['name'])
    
    # User roles association indexes
    op.create_index('idx_user_roles_user_id', 'user_roles', ['user_id'])
    op.create_index('idx_user_roles_role_id', 'user_roles', ['role_id'])

def downgrade():
    # Drop indexes in reverse order
    op.drop_index('idx_user_roles_role_id')
    op.drop_index('idx_user_roles_user_id')
    op.drop_index('idx_permissions_name')
    op.drop_index('idx_roles_name')
    op.drop_index('idx_payments_created_at')
    op.drop_index('idx_payments_transaction_id')
    op.drop_index('idx_payments_gateway')
    op.drop_index('idx_payments_status')
    op.drop_index('idx_payments_booking_id')
    op.drop_index('idx_bookings_type_status')
    op.drop_index('idx_bookings_check_in')
    op.drop_index('idx_bookings_created_at')
    op.drop_index('idx_bookings_reference')
    op.drop_index('idx_bookings_status')
    op.drop_index('idx_bookings_user_id')
    op.drop_index('idx_users_created_at')
    op.drop_index('idx_users_phone')
    op.drop_index('idx_users_email')