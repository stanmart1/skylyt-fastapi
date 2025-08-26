"""remove phone column

Revision ID: remove_phone
Revises: fix_booking_ref
Create Date: 2024-01-01 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'remove_phone'
down_revision = 'fix_booking_ref'
branch_labels = None
depends_on = None

def upgrade():
    # Remove phone column from users table
    try:
        op.drop_column('users', 'phone')
    except:
        pass  # Column might not exist

def downgrade():
    # Add phone column back
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))