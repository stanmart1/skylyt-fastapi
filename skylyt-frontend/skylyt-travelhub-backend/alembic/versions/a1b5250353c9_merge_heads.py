"""merge_heads

Revision ID: a1b5250353c9
Revises: add_booking_reference, create_settings, update_booking_model
Create Date: 2025-08-22 19:52:51.523972

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b5250353c9'
down_revision = ('add_booking_reference', 'create_settings', 'update_booking_model')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass