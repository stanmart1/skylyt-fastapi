"""Add comprehensive notification settings

Revision ID: add_comprehensive_notification_settings
Revises: add_notification_settings
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_comprehensive_notification_settings'
down_revision = 'add_notification_settings'
branch_labels = None
depends_on = None

def upgrade():
    # Add new notification settings columns
    op.add_column('settings', sa.Column('sms_enabled', sa.Boolean(), default=False))
    op.add_column('settings', sa.Column('push_notifications_enabled', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('booking_notifications', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('payment_notifications', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('system_notifications', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('driver_notifications', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('admin_notifications', sa.Boolean(), default=True))
    op.add_column('settings', sa.Column('notification_frequency', sa.String(50), default='immediate'))
    op.add_column('settings', sa.Column('quiet_hours_start', sa.String(10), default='22:00'))
    op.add_column('settings', sa.Column('quiet_hours_end', sa.String(10), default='08:00'))
    op.add_column('settings', sa.Column('timezone', sa.String(50), default='UTC'))

def downgrade():
    # Remove the added columns
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