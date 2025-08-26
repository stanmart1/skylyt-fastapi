"""add bank transfer settings

Revision ID: add_bank_transfer_settings
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_bank_transfer_settings'
down_revision = 'a1b5250353c9'
depends_on = None

def upgrade():
    # Add bank transfer columns to settings table
    op.add_column('settings', sa.Column('bank_name', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('account_name', sa.String(255), nullable=True))
    op.add_column('settings', sa.Column('account_number', sa.String(100), nullable=True))
    op.add_column('settings', sa.Column('is_primary_account', sa.Boolean(), default=True))

def downgrade():
    # Remove bank transfer columns
    op.drop_column('settings', 'is_primary_account')
    op.drop_column('settings', 'account_number')
    op.drop_column('settings', 'account_name')
    op.drop_column('settings', 'bank_name')