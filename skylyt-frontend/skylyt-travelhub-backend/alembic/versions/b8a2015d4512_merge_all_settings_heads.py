"""merge_all_settings_heads

Revision ID: b8a2015d4512
Revises: add_comprehensive_settings, add_contact_about_settings, add_missing_settings_columns, add_payment_pending_status, add_performance_indexes_v2, footer_settings_001, create_payments_table, fix_hotel_image_hotel_id
Create Date: 2025-09-09 15:22:37.136332

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8a2015d4512'
down_revision = ('add_comprehensive_settings', 'add_contact_about_settings', 'add_missing_settings_columns', 'add_payment_pending_status', 'add_performance_indexes_v2', 'footer_settings_001', 'create_payments_table', 'fix_hotel_image_hotel_id')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass