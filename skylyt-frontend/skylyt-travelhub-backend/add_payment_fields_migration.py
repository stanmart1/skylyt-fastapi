#!/usr/bin/env python3
"""
Migration script to add payment tracking fields
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import engine

def run_migration():
    """Add payment tracking fields to payments table"""
    
    with engine.connect() as connection:
        # Add proof of payment URL
        try:
            connection.execute(text("ALTER TABLE payments ADD COLUMN proof_of_payment_url VARCHAR(500)"))
            print("✓ Added proof_of_payment_url column")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("✓ proof_of_payment_url column already exists")
            else:
                print(f"✗ Error adding proof_of_payment_url: {e}")
        
        # Add refund tracking fields
        fields_to_add = [
            ("refund_status", "VARCHAR(20) DEFAULT 'none'"),
            ("refund_amount", "FLOAT"),
            ("refund_date", "TIMESTAMP"),
            ("refund_reason", "VARCHAR(500)"),
            ("payment_reference", "VARCHAR(100)"),
            ("customer_name", "VARCHAR(255)"),
            ("customer_email", "VARCHAR(255)")
        ]
        
        for field_name, field_type in fields_to_add:
            try:
                connection.execute(text(f"ALTER TABLE payments ADD COLUMN {field_name} {field_type}"))
                print(f"✓ Added {field_name} column")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"✓ {field_name} column already exists")
                else:
                    print(f"✗ Error adding {field_name}: {e}")
        
        connection.commit()
        print("✓ Payment fields migration completed")

if __name__ == "__main__":
    run_migration()