"""add notification settings

Revision ID: add_notification_settings
Revises: 
Create Date: 2024-12-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_notification_settings'
down_revision = None
depends_on = None

def upgrade():
    # Add notification settings columns to settings table
    op.add_column('settings', sa.Column('smtp_server', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('smtp_port', sa.Integer(), nullable=True, default=587))
    op.add_column('settings', sa.Column('smtp_username', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('smtp_password', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('from_email', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('resend_api_key', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('onesignal_app_id', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('onesignal_api_key', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('email_notifications_enabled', sa.Boolean(), nullable=True, default=True))
    op.add_column('settings', sa.Column('push_notifications_enabled', sa.Boolean(), nullable=True, default=True))

def downgrade():
    # Remove notification settings columns
    op.drop_column('settings', 'push_notifications_enabled')
    op.drop_column('settings', 'email_notifications_enabled')
    op.drop_column('settings', 'onesignal_api_key')
    op.drop_column('settings', 'onesignal_app_id')
    op.drop_column('settings', 'resend_api_key')
    op.drop_column('settings', 'from_email')
    op.drop_column('settings', 'smtp_password')
    op.drop_column('settings', 'smtp_username')
    op.drop_column('settings', 'smtp_port')
    op.drop_column('settings', 'smtp_server')