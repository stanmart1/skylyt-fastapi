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
        
        # Create superadmin user if not exists
        superadmin_email = "superadmin@skylyt.com"
        existing_superadmin = db.query(User).filter(User.email == superadmin_email).first()
        
        if not existing_superadmin:
            superadmin_data = UserCreate(
                email=superadmin_email,
                password="SuperAdmin123!",
                first_name="Super",
                last_name="Admin",
                phone="+1234567890"
            )
            
            superadmin = AuthService.register_user(db, superadmin_data)
            
            # Assign superadmin role
            RBACService.assign_role_to_user(db, superadmin.id, "superadmin")
            print(f"✅ Superadmin user created: {superadmin_email}")
        else:
            print(f"✅ Superadmin user already exists: {superadmin_email}")
        
        print("🎉 RBAC initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing RBAC: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    from app.models.user import User
    init_rbac()