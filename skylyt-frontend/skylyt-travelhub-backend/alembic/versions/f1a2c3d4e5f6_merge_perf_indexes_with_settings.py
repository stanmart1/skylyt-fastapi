"""merge perf indexes v3 with settings heads

Revision ID: f1a2c3d4e5f6
Revises: add_performance_indexes_v3, b8a2015d4512
Create Date: 2026-06-26

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1a2c3d4e5f6'
down_revision = ('add_performance_indexes_v3', 'b8a2015d4512')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
