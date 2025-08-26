"""Fix monetary precision - replace Float with Numeric

Revision ID: fix_monetary_precision
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'fix_monetary_precision'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Update payments table
    op.alter_column('payments', 'amount',
                    existing_type=sa.Float(),
                    type_=sa.Numeric(precision=10, scale=2),
                    existing_nullable=False)
    
    op.alter_column('payments', 'refund_amount',
                    existing_type=sa.Float(),
                    type_=sa.Numeric(precision=10, scale=2),
                    existing_nullable=True)
    
    # Update bookings table
    op.alter_column('bookings', 'total_amount',
                    existing_type=sa.Float(),
                    type_=sa.Numeric(precision=10, scale=2),
                    existing_nullable=False)


def downgrade():
    # Revert bookings table
    op.alter_column('bookings', 'total_amount',
                    existing_type=sa.Numeric(precision=10, scale=2),
                    type_=sa.Float(),
                    existing_nullable=False)
    
    # Revert payments table
    op.alter_column('payments', 'refund_amount',
                    existing_type=sa.Numeric(precision=10, scale=2),
                    type_=sa.Float(),
                    existing_nullable=True)
    
    op.alter_column('payments', 'amount',
                    existing_type=sa.Numeric(precision=10, scale=2),
                    type_=sa.Float(),
                    existing_nullable=False)