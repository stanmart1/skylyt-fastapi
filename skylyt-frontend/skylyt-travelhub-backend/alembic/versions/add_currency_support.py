"""Add currency support

Revision ID: add_currency_support
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_currency_support'
down_revision = None  # Replace with actual previous revision
branch_labels = None
depends_on = None

def upgrade():
    # Create currency_rates table
    op.create_table('currency_rates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('from_currency', sa.String(length=3), nullable=False),
        sa.Column('to_currency', sa.String(length=3), nullable=False),
        sa.Column('rate', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('from_currency', 'to_currency')
    )
    
    # Create countries table
    op.create_table('countries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=2), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('currency_code', sa.String(length=3), nullable=False),
        sa.Column('is_supported', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Add currency fields to existing tables
    op.add_column('bookings', sa.Column('currency_code', sa.String(length=3), nullable=True, default='NGN'))
    op.add_column('bookings', sa.Column('exchange_rate', sa.Numeric(precision=10, scale=4), nullable=True, default=1.0))
    op.add_column('hotels', sa.Column('base_currency', sa.String(length=3), nullable=True, default='NGN'))
    op.add_column('cars', sa.Column('base_currency', sa.String(length=3), nullable=True, default='NGN'))
    
    # Insert supported countries
    op.execute("""
        INSERT INTO countries (code, name, currency_code, is_supported) VALUES
        ('NG', 'Nigeria', 'NGN', true),
        ('US', 'United States', 'USD', true),
        ('GB', 'United Kingdom', 'GBP', true),
        ('CA', 'Canada', 'USD', true),
        ('DE', 'Germany', 'EUR', true),
        ('FR', 'France', 'EUR', true)
    """)
    
    # Insert initial exchange rates (placeholder values)
    op.execute("""
        INSERT INTO currency_rates (from_currency, to_currency, rate) VALUES
        ('NGN', 'USD', 0.0012),
        ('NGN', 'GBP', 0.001),
        ('NGN', 'EUR', 0.0011),
        ('USD', 'NGN', 830.0),
        ('GBP', 'NGN', 1000.0),
        ('EUR', 'NGN', 910.0)
    """)

def downgrade():
    op.drop_column('cars', 'base_currency')
    op.drop_column('hotels', 'base_currency')
    op.drop_column('bookings', 'exchange_rate')
    op.drop_column('bookings', 'currency_code')
    op.drop_table('countries')
    op.drop_table('currency_rates')