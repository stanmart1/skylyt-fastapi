#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text
from app.core.config import settings

def create_contact_messages_migration():
    """Create migration for contact messages table"""
    
    # Create Alembic config
    alembic_cfg = Config("alembic.ini")
    
    # Create the migration
    command.revision(
        alembic_cfg, 
        message="create_contact_messages_table",
        autogenerate=True
    )
    
    print("Contact messages migration created successfully!")

if __name__ == "__main__":
    create_contact_messages_migration()