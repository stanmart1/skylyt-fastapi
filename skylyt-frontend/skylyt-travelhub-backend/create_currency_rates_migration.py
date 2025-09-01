#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings

def create_currency_rates_table():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as connection:
        # Create currency_rates table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS currency_rates (
                id SERIAL PRIMARY KEY,
                base_currency VARCHAR(3) NOT NULL DEFAULT 'NGN',
                target_currency VARCHAR(3) NOT NULL,
                rate FLOAT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(base_currency, target_currency)
            )
        """))
        
        # Check if table has data, if not insert default rates
        result = connection.execute(text("SELECT COUNT(*) FROM currency_rates"))
        if result.scalar() == 0:
            connection.execute(text("""
                INSERT INTO currency_rates (base_currency, target_currency, rate) VALUES
                ('NGN', 'USD', 0.0012),
                ('NGN', 'GBP', 0.0010),
                ('NGN', 'EUR', 0.0011)
            """))
        
        connection.commit()
        print("Currency rates table created with default rates")

if __name__ == "__main__":
    create_currency_rates_table()