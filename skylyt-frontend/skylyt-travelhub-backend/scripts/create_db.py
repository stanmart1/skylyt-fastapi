#!/usr/bin/env python3
"""Database creation and initialization script."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import engine, Base
from app.models import user, booking, search_history, payment, favorite


def create_database():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    create_database()