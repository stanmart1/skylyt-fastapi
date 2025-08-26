#!/usr/bin/env python3
"""Test database connection."""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.core.database import engine
from sqlalchemy import text

def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            print(f"Database URL: {engine.url}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()