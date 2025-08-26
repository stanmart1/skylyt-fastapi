#!/usr/bin/env python3
"""
Migration script to add bank_transfer to payment method enum
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import engine

def run_migration():
    """Add bank_transfer to payment method enum"""
    
    with engine.connect() as connection:
        try:
            # Add bank_transfer to the enum
            connection.execute(text("ALTER TYPE paymentmethod ADD VALUE 'bank_transfer'"))
            connection.commit()
            print("✓ Added 'bank_transfer' to paymentmethod enum")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("✓ 'bank_transfer' already exists in paymentmethod enum")
            else:
                print(f"✗ Error adding bank_transfer to enum: {e}")
                # If enum doesn't exist, let's check the current column type
                try:
                    result = connection.execute(text("""
                        SELECT column_name, data_type, udt_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'payments' AND column_name = 'payment_method'
                    """))
                    row = result.fetchone()
                    if row:
                        print(f"Current payment_method column: {row}")
                        
                        # If it's a varchar, we can just update it directly
                        if 'varchar' in str(row[1]).lower() or 'character' in str(row[1]).lower():
                            print("✓ payment_method is already a string column, no enum constraint")
                        else:
                            print("Need to investigate column type further")
                except Exception as e2:
                    print(f"Error checking column type: {e2}")

if __name__ == "__main__":
    run_migration()