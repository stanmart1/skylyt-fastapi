"""Add comprehensive settings fields

Revision ID: add_comprehensive_settings
Revises: add_comprehensive_notification_settings
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_comprehensive_settings'
down_revision = 'add_comprehensive_notification_settings'
branch_labels = None
depends_on = None

def upgrade():
    # General Settings Extensions
    op.add_column('settings', sa.Column('site_logo', sa.String(500), nullable=True))
    op.add_column('settings', sa.Column('favicon', sa.String(500), nullable=True))
    op.add_column('settings', sa.Column('default_language', sa.String(10), default='en'))
    op.add_column('settings', sa.Column('default_timezone', sa.String(50), default='UTC'))
    op.add_column('settings', sa.Column('site_keywords', sa.Text, nullable=True))
    op.add_column('settings', sa.Column('social_facebook', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('social_twitter', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('social_instagram', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('social_linkedin', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('terms_url', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('privacy_url', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('support_url', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('company_address', sa.Text, nullable=True))
    op.add_column('settings', sa.Column('company_registration', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('vat_number', sa.String(255), nullable=True))
    
    # Security Settings Extensions
    op.add_column('settings', sa.Column('password_require_uppercase', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('password_require_lowercase', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('password_require_numbers', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('password_require_symbols', sa.Boolean(), default=False))
    op.add_column('settings', sa.Column('account_lockout_duration', sa.String(10), default='30'))
    op.add_column('settings', sa.Column('password_expiry_days', sa.String(10), default='90'))
    op.add_column('settings', sa.Column('force_password_change', sa.Boolean(), default=False))
    op.add_column('settings', sa.Column('allow_password_reset', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('captcha_enabled', sa.Boolean(), default=False))
    op.add_column('settings', sa.Column('ip_whitelist_enabled', sa.Boolean(), default=False))
    op.add_column('settings', sa.Column('ip_whitelist', sa.Text, nullable=True))
    op.add_column('settings', sa.Column('ssl_required', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('cookie_secure', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('session_cookie_httponly', sa.Boolean(), default=True))
    
    # Payment Settings Extensions
    op.add_column('settings', sa.Column('payment_currency', sa.String(10), default='USD'))
    op.add_column('settings', sa.Column('minimum_payment_amount', sa.String(20), default='1.00'))
    op.add_column('settings', sa.Column('maximum_payment_amount', sa.String(20), default='10000.00'))
    op.add_column('settings', sa.Column('payment_processing_fee', sa.String(10), default='2.9'))
    op.add_column('settings', sa.Column('auto_capture_payments', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('refund_policy_days', sa.String(10), default='30'))
    op.add_column('settings', sa.Column('partial_refunds_enabled', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('webhook_secret_stripe', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('webhook_secret_paystack', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('webhook_secret_flutterwave', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('payment_retry_attempts', sa.String(10), default='3'))
    op.add_column('settings', sa.Column('payment_timeout_minutes', sa.String(10), default='15'))
    
    # Bank Transfer Extensions
    op.add_column('settings', sa.Column('routing_number', sa.String(50), nullable=True))
    op.add_column('settings', sa.Column('swift_code', sa.String(20), nullable=True))
    op.add_column('settings', sa.Column('iban', sa.String(50), nullable=True))
    op.add_column('settings', sa.Column('bank_address', sa.Text, nullable=True))
    op.add_column('settings', sa.Column('account_type', sa.String(20), default='checking'))
    op.add_column('settings', sa.Column('currency', sa.String(10), default='USD'))
    op.add_column('settings', sa.Column('minimum_transfer_amount', sa.String(20), default='10.00'))
    op.add_column('settings', sa.Column('maximum_transfer_amount', sa.String(20), default='50000.00'))
    op.add_column('settings', sa.Column('transfer_fee', sa.String(20), default='0.00'))
    op.add_column('settings', sa.Column('processing_time_hours', sa.String(10), default='24'))
    op.add_column('settings', sa.Column('auto_verification_enabled', sa.Boolean(), default=False))
    op.add_column('settings', sa.Column('require_reference_number', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('bank_transfer_instructions', sa.Text, nullable=True))
    
    # Feature Settings
    op.add_column('settings', sa.Column('car_rental_enabled', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('hotel_booking_enabled', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('driver_service_enabled', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('multi_currency_enabled', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('reviews_enabled', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('loyalty_program_enabled', sa.Boolean(), default=False))
    op.add_column('settings', sa.Column('referral_program_enabled', sa.Boolean(), default=False))
    op.add_column('settings', sa.Column('chat_support_enabled', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('mobile_app_enabled', sa.Boolean(), default=False))
    op.add_column('settings', sa.Column('api_access_enabled', sa.Boolean(), default=False))
    op.add_column('settings', sa.Column('booking_modifications_enabled', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('cancellation_enabled', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('partial_payments_enabled', sa.Boolean(), default=False))
    op.add_column('settings', sa.Column('group_bookings_enabled', sa.Boolean(), default=False))
    op.add_column('settings', sa.Column('corporate_accounts_enabled', sa.Boolean(), default=False))
    op.add_column('settings', sa.Column('maintenance_notifications', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('feature_announcements', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('beta_features_enabled', sa.Boolean(), default=False))

def downgrade():
    # Remove Feature Settings
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
    
    # Remove Bank Transfer Extensions
    op.drop_column('settings', 'bank_transfer_instructions')
    op.drop_column('settings', 'require_reference_number')
    op.drop_column('settings', 'auto_verification_enabled')
    op.drop_column('settings', 'processing_time_hours')
    op.drop_column('settings', 'transfer_fee')
    op.drop_column('settings', 'maximum_transfer_amount')
    op.drop_column('settings', 'minimum_transfer_amount')
    op.drop_column('settings', 'currency')
    op.drop_column('settings', 'account_type')
    op.drop_column('settings', 'bank_address')
    op.drop_column('settings', 'iban')
    op.drop_column('settings', 'swift_code')
    op.drop_column('settings', 'routing_number')
    
    # Remove Payment Settings Extensions
    op.drop_column('settings', 'payment_timeout_minutes')
    op.drop_column('settings', 'payment_retry_attempts')
    op.drop_column('settings', 'webhook_secret_flutterwave')
    op.drop_column('settings', 'webhook_secret_paystack')
    op.drop_column('settings', 'webhook_secret_stripe')
    op.drop_column('settings', 'partial_refunds_enabled')
    op.drop_column('settings', 'refund_policy_days')
    op.drop_column('settings', 'auto_capture_payments')
    op.drop_column('settings', 'payment_processing_fee')
    op.drop_column('settings', 'maximum_payment_amount')
    op.drop_column('settings', 'minimum_payment_amount')
    op.drop_column('settings', 'payment_currency')
    
    # Remove Security Settings Extensions
    op.drop_column('settings', 'session_cookie_httponly')
    op.drop_column('settings', 'cookie_secure')
    op.drop_column('settings', 'ssl_required')
    op.drop_column('settings', 'ip_whitelist')
    op.drop_column('settings', 'ip_whitelist_enabled')
    op.drop_column('settings', 'captcha_enabled')
    op.drop_column('settings', 'allow_password_reset')
    op.drop_column('settings', 'force_password_change')
    op.drop_column('settings', 'password_expiry_days')
    op.drop_column('settings', 'account_lockout_duration')
    op.drop_column('settings', 'password_require_symbols')
    op.drop_column('settings', 'password_require_numbers')
    op.drop_column('settings', 'password_require_lowercase')
    op.drop_column('settings', 'password_require_uppercase')
    
    # Remove General Settings Extensions
    op.drop_column('settings', 'vat_number')
    op.drop_column('settings', 'company_registration')
    op.drop_column('settings', 'company_address')
    op.drop_column('settings', 'support_url')
    op.drop_column('settings', 'privacy_url')
    op.drop_column('settings', 'terms_url')
    op.drop_column('settings', 'social_linkedin')
    op.drop_column('settings', 'social_instagram')
    op.drop_column('settings', 'social_twitter')
    op.drop_column('settings', 'social_facebook')
    op.drop_column('settings', 'site_keywords')
    op.drop_column('settings', 'default_timezone')
    op.drop_column('settings', 'default_language')
    op.drop_column('settings', 'favicon')
    op.drop_column('settings', 'site_logo')