"""add phone column back

Revision ID: add_phone_back
Revises: remove_phone
Create Date: 2025-01-01 20:52:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_phone_back'
down_revision = 'remove_phone'
branch_labels = None
depends_on = None

def upgrade():
    # Add phone column back to users table
    try:
        op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))
    except Exception as e:
        print(f"Column might already exist: {e}")

def downgrade():
    # Remove phone column
    try:
        op.drop_column('users', 'phone')
    except Exception as e:
        print(f"Column might not exist: {e}")