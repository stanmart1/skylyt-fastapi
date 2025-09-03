"""Add payment_pending to booking status

Revision ID: add_payment_pending_status
Revises: add_payment_method_column
Create Date: 2025-09-03 21:05:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_payment_pending_status'
down_revision = 'add_payment_method_column'
branch_labels = None
depends_on = None

def upgrade():
    # Update any existing payment_pending status values to be valid
    op.execute("UPDATE bookings SET status = 'payment_pending' WHERE status = 'payment_pending'")

def downgrade():
    # Convert payment_pending back to pending
    op.execute("UPDATE bookings SET status = 'pending' WHERE status = 'payment_pending'")