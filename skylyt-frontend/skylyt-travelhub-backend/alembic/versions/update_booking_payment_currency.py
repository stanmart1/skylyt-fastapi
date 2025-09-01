"""update booking and payment currency fields

Revision ID: update_booking_payment_currency
Revises: add_currencies_table
Create Date: 2024-01-01 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'update_booking_payment_currency'
down_revision = 'add_currencies_table'
branch_labels = None
depends_on = None


def upgrade():
    # Update bookings table
    op.add_column('bookings', sa.Column('total_amount_ngn', sa.Numeric(precision=15, scale=2), nullable=True))
    op.add_column('bookings', sa.Column('display_currency', sa.String(length=3), nullable=True))
    op.add_column('bookings', sa.Column('display_amount', sa.Numeric(precision=15, scale=2), nullable=True))
    
    # Migrate existing data
    op.execute("UPDATE bookings SET total_amount_ngn = total_amount, display_currency = currency, display_amount = total_amount WHERE total_amount_ngn IS NULL")
    
    # Make total_amount_ngn not nullable
    op.alter_column('bookings', 'total_amount_ngn', nullable=False)
    op.alter_column('bookings', 'display_currency', nullable=False, server_default='NGN')
    
    # Update payments table
    op.add_column('payments', sa.Column('amount_ngn', sa.Numeric(precision=15, scale=2), nullable=True))
    op.add_column('payments', sa.Column('display_currency', sa.String(length=3), nullable=True))
    op.add_column('payments', sa.Column('display_amount', sa.Numeric(precision=15, scale=2), nullable=True))
    
    # Migrate existing data
    op.execute("UPDATE payments SET amount_ngn = amount, display_currency = currency, display_amount = amount WHERE amount_ngn IS NULL")
    
    # Make amount_ngn not nullable
    op.alter_column('payments', 'amount_ngn', nullable=False)
    op.alter_column('payments', 'display_currency', nullable=False, server_default='NGN')


def downgrade():
    # Remove new columns
    op.drop_column('bookings', 'display_amount')
    op.drop_column('bookings', 'display_currency')
    op.drop_column('bookings', 'total_amount_ngn')
    
    op.drop_column('payments', 'display_amount')
    op.drop_column('payments', 'display_currency')
    op.drop_column('payments', 'amount_ngn')