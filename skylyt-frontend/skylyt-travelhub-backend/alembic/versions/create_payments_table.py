"""Create payments table

Revision ID: create_payments_table
Revises: fix_payment_enums
Create Date: 2025-09-03 20:51:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_payments_table'
down_revision = 'fix_payment_enums'
branch_labels = None
depends_on = None

def upgrade():
    # Create payments table
    op.create_table('payments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('payment_method', sa.String(length=20), nullable=False),
        sa.Column('stripe_payment_intent_id', sa.String(length=255), nullable=True),
        sa.Column('transaction_id', sa.String(length=255), nullable=True),
        sa.Column('transfer_reference', sa.String(length=255), nullable=True),
        sa.Column('gateway_response', sa.JSON(), nullable=True),
        sa.Column('proof_of_payment_url', sa.String(length=500), nullable=True),
        sa.Column('refund_status', sa.String(length=20), nullable=False),
        sa.Column('refund_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('refund_date', sa.DateTime(), nullable=True),
        sa.Column('refund_reason', sa.String(length=500), nullable=True),
        sa.Column('payment_reference', sa.String(length=100), nullable=True),
        sa.Column('customer_name', sa.String(length=255), nullable=True),
        sa.Column('customer_email', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_payments_id'), table_name='payments')
    op.drop_table('payments')