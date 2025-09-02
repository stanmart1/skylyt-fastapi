#!/usr/bin/env python3
"""Initialize RBAC system with default roles and permissions."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.services.rbac_service import RBACService
from app.services.auth_service import AuthService
from app.schemas.auth import UserCreate


def init_rbac():
    """Initialize RBAC system"""
    db = SessionLocal()
    
    try:
        print("Initializing RBAC system...")
        
        # Initialize roles and permissions
        RBACService.initialize_default_roles_and_permissions(db)
        print("✅ Default roles and permissions created")
        
        # Delete existing superadmin user if exists
        superadmin_email = "superadmin@skylyt.com"
        existing_superadmin = db.query(User).filter(User.email == superadmin_email).first()
        
        if existing_superadmin:
            db.delete(existing_superadmin)
            db.commit()
            print(f"✅ Deleted existing superadmin user: {superadmin_email}")
        else:
            print(f"✅ No existing superadmin user found to delete")
        
        print("🎉 RBAC initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing RBAC: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    from app.models.user import User
    init_rbac()