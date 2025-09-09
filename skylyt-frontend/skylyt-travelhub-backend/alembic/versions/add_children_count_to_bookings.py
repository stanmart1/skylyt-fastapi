"""add children count to bookings

Revision ID: add_children_count
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_children_count'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add children_count column to bookings table
    op.add_column('bookings', sa.Column('children_count', sa.Integer(), nullable=True, default=0))


def downgrade():
    # Remove children_count column from bookings table
    op.drop_column('bookings', 'children_count')