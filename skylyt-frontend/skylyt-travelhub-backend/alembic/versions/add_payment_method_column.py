"""Add payment_method column to payments

Revision ID: add_payment_method_column
Revises: add_status_column
Create Date: 2025-09-03 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_payment_method_column'
down_revision = 'add_status_column'
branch_labels = None
depends_on = None

def upgrade():
    # Add payment_method column if it doesn't exist
    op.add_column('payments', sa.Column('payment_method', sa.String(length=20), nullable=False, server_default='stripe'))

def downgrade():
    op.drop_column('payments', 'payment_method')