"""add missing settings columns

Revision ID: add_missing_settings_columns
Revises: 0564db9c49e4
Create Date: 2025-01-09 14:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_missing_settings_columns'
down_revision = '0564db9c49e4'
branch_labels = None
depends_on = None


def upgrade():
    # Add missing notification columns
    op.add_column('settings', sa.Column('sms_enabled', sa.Boolean(), nullable=True, default=False))
    op.add_column('settings', sa.Column('push_notifications_enabled', sa.Boolean(), nullable=True, default=True))
    op.add_column('settings', sa.Column('booking_notifications', sa.Boolean(), nullable=True, default=True))
    op.add_column('settings', sa.Column('payment_notifications', sa.Boolean(), nullable=True, default=True))
    op.add_column('settings', sa.Column('system_notifications', sa.Boolean(), nullable=True, default=True))
    op.add_column('settings', sa.Column('driver_notifications', sa.Boolean(), nullable=True, default=True))
    op.add_column('settings', sa.Column('admin_notifications', sa.Boolean(), nullable=True, default=True))
    op.add_column('settings', sa.Column('notification_frequency', sa.String(50), nullable=True, default='immediate'))
    op.add_column('settings', sa.Column('quiet_hours_start', sa.String(10), nullable=True, default='22:00'))
    op.add_column('settings', sa.Column('quiet_hours_end', sa.String(10), nullable=True, default='08:00'))
    op.add_column('settings', sa.Column('timezone', sa.String(50), nullable=True, default='UTC'))
    
    # Add missing Google Analytics columns
    op.add_column('settings', sa.Column('google_analytics_tracking_id', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('google_analytics_measurement_id', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('google_analytics_api_key', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('google_analytics_enabled', sa.Boolean(), nullable=True, default=False))
    
    # Add missing bank transfer columns
    op.add_column('settings', sa.Column('bank_address', sa.Text(), nullable=True))
    op.add_column('settings', sa.Column('account_type', sa.String(20), nullable=True, default='checking'))
    op.add_column('settings', sa.Column('currency', sa.String(10), nullable=True, default='USD'))
    op.add_column('settings', sa.Column('transfer_fee', sa.String(20), nullable=True, default='0.00'))
    op.add_column('settings', sa.Column('processing_time_hours', sa.String(10), nullable=True, default='24'))
    op.add_column('settings', sa.Column('auto_verification_enabled', sa.Boolean(), nullable=True, default=False))
    op.add_column('settings', sa.Column('require_reference_number', sa.Boolean(), nullable=True, default=True))
    op.add_column('settings', sa.Column('bank_transfer_instructions', sa.Text(), nullable=True))
    
    # Add missing webhook columns
    op.add_column('settings', sa.Column('webhook_secret_stripe', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('webhook_secret_paystack', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('webhook_secret_flutterwave', sa.String(255), nullable=True))
    
    # Add missing feature columns
    op.add_column('settings', sa.Column('car_rental_enabled', sa.Boolean(), nullable=True, default=True))
    op.add_column('settings', sa.Column('hotel_booking_enabled', sa.Boolean(), nullable=True, default=True))
    op.add_column('settings', sa.Column('driver_service_enabled', sa.Boolean(), nullable=True, default=True))
    op.add_column('settings', sa.Column('multi_currency_enabled', sa.Boolean(), nullable=True, default=True))
    op.add_column('settings', sa.Column('reviews_enabled', sa.Boolean(), nullable=True, default=True))
    op.add_column('settings', sa.Column('loyalty_program_enabled', sa.Boolean(), nullable=True, default=False))
    op.add_column('settings', sa.Column('referral_program_enabled', sa.Boolean(), nullable=True, default=False))
    op.add_column('settings', sa.Column('chat_support_enabled', sa.Boolean(), nullable=True, default=True))
    op.add_column('settings', sa.Column('mobile_app_enabled', sa.Boolean(), nullable=True, default=False))
    op.add_column('settings', sa.Column('api_access_enabled', sa.Boolean(), nullable=True, default=False))
    op.add_column('settings', sa.Column('booking_modifications_enabled', sa.Boolean(), nullable=True, default=True))
    op.add_column('settings', sa.Column('cancellation_enabled', sa.Boolean(), nullable=True, default=True))
    op.add_column('settings', sa.Column('partial_payments_enabled', sa.Boolean(), nullable=True, default=False))
    op.add_column('settings', sa.Column('group_bookings_enabled', sa.Boolean(), nullable=True, default=False))
    op.add_column('settings', sa.Column('corporate_accounts_enabled', sa.Boolean(), nullable=True, default=False))
    op.add_column('settings', sa.Column('maintenance_notifications', sa.Boolean(), nullable=True, default=True))
    op.add_column('settings', sa.Column('feature_announcements', sa.Boolean(), nullable=True, default=True))
    op.add_column('settings', sa.Column('beta_features_enabled', sa.Boolean(), nullable=True, default=False))


def downgrade():
    # Remove all added columns
    op.drop_column('settings', 'beta_features_enabled')
    op.drop_column('settings', 'feature_announcements')
    op.drop_column('settings', 'maintenance_notifications')
    op.drop_column('settings', 'corporate_accounts_enabled')
    op.drop_column('settings', 'group_bookings_enabled')
    op.drop_column('settings', 'partial_payments_enabled')
    op.drop_column('settings', 'cancellation_enabled')
    op.drop_column('settings', 'booking_modifications_enabled')
    op.drop_column('settings', 'api_access_enabled')
    op.drop_column('settings', 'mobile_app_enabled')
    op.drop_column('settings', 'chat_support_enabled')
    op.drop_column('settings', 'referral_program_enabled')
    op.drop_column('settings', 'loyalty_program_enabled')
    op.drop_column('settings', 'reviews_enabled')
    op.drop_column('settings', 'multi_currency_enabled')
    op.drop_column('settings', 'driver_service_enabled')
    op.drop_column('settings', 'hotel_booking_enabled')
    op.drop_column('settings', 'car_rental_enabled')
    op.drop_column('settings', 'webhook_secret_flutterwave')
    op.drop_column('settings', 'webhook_secret_paystack')
    op.drop_column('settings', 'webhook_secret_stripe')
    op.drop_column('settings', 'bank_transfer_instructions')
    op.drop_column('settings', 'require_reference_number')
    op.drop_column('settings', 'auto_verification_enabled')
    op.drop_column('settings', 'processing_time_hours')
    op.drop_column('settings', 'transfer_fee')
    op.drop_column('settings', 'currency')
    op.drop_column('settings', 'account_type')
    op.drop_column('settings', 'bank_address')
    op.drop_column('settings', 'google_analytics_enabled')
    op.drop_column('settings', 'google_analytics_api_key')
    op.drop_column('settings', 'google_analytics_measurement_id')
    op.drop_column('settings', 'google_analytics_tracking_id')
    op.drop_column('settings', 'timezone')
    op.drop_column('settings', 'quiet_hours_end')
    op.drop_column('settings', 'quiet_hours_start')
    op.drop_column('settings', 'notification_frequency')
    op.drop_column('settings', 'admin_notifications')
    op.drop_column('settings', 'driver_notifications')
    op.drop_column('settings', 'system_notifications')
    op.drop_column('settings', 'payment_notifications')
    op.drop_column('settings', 'booking_notifications')
    op.drop_column('settings', 'push_notifications_enabled')
    op.drop_column('settings', 'sms_enabled')