"""merge bank transfer settings

Revision ID: e22b0c72d0bf
Revises: a1b5250353c9, add_bank_transfer_settings
Create Date: 2025-08-22 21:47:17.167260

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e22b0c72d0bf'
down_revision = ('a1b5250353c9', 'add_bank_transfer_settings')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass