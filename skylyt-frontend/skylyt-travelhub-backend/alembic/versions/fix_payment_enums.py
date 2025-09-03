"""Fix payment enums

Revision ID: fix_payment_enums
Revises: 
Create Date: 2025-09-03 20:44:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fix_payment_enums'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create the enum types if they don't exist
    op.execute("DROP TYPE IF EXISTS paymentstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS paymentmethod CASCADE")
    
    op.execute("CREATE TYPE paymentstatus AS ENUM ('pending', 'processing', 'completed', 'failed', 'refunded')")
    op.execute("CREATE TYPE paymentmethod AS ENUM ('stripe', 'flutterwave', 'paystack', 'paypal', 'bank_transfer')")
    
    # The table will be created with the correct enum types when the app starts

def downgrade():
    # Convert back to text
    op.execute("ALTER TABLE payments ALTER COLUMN status TYPE VARCHAR(20)")
    op.execute("ALTER TABLE payments ALTER COLUMN payment_method TYPE VARCHAR(20)")
    
    # Drop the enum types
    op.execute("DROP TYPE IF EXISTS paymentstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS paymentmethod CASCADE")