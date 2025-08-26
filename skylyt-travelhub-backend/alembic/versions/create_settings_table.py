"""create settings table

Revision ID: create_settings
Revises: add_booking_cols
Create Date: 2024-01-01 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'create_settings'
down_revision = 'add_booking_cols'
branch_labels = None
depends_on = None

def upgrade():
    # Create settings table
    op.create_table('settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('site_name', sa.String(255), nullable=True, default='Skylyt TravelHub'),
        sa.Column('site_description', sa.Text(), nullable=True),
        sa.Column('contact_email', sa.String(255), nullable=True),
        sa.Column('contact_phone', sa.String(50), nullable=True),
        sa.Column('maintenance_mode', sa.Boolean(), nullable=True, default=False),
        sa.Column('stripe_public_key', sa.String(255), nullable=True),
        sa.Column('stripe_secret_key', sa.String(255), nullable=True),
        sa.Column('paystack_public_key', sa.String(255), nullable=True),
        sa.Column('paystack_secret_key', sa.String(255), nullable=True),
        sa.Column('flutterwave_public_key', sa.String(255), nullable=True),
        sa.Column('flutterwave_secret_key', sa.String(255), nullable=True),
        sa.Column('paypal_client_id', sa.String(255), nullable=True),
        sa.Column('paypal_client_secret', sa.String(255), nullable=True),
        sa.Column('paypal_sandbox', sa.Boolean(), nullable=True, default=True),
        sa.Column('password_min_length', sa.String(10), nullable=True, default='8'),
        sa.Column('session_timeout', sa.String(10), nullable=True, default='30'),
        sa.Column('two_factor_enabled', sa.Boolean(), nullable=True, default=False),
        sa.Column('login_attempts_limit', sa.String(10), nullable=True, default='5'),
        sa.Column('additional_settings', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('settings')