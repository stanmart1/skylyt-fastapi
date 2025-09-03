"""Add status column to payments

Revision ID: add_status_column
Revises: fix_payment_enums
Create Date: 2025-09-03 20:52:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_status_column'
down_revision = 'fix_payment_enums'
branch_labels = None
depends_on = None

def upgrade():
    # Add status column if it doesn't exist
    op.add_column('payments', sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'))

def downgrade():
    op.drop_column('payments', 'status')