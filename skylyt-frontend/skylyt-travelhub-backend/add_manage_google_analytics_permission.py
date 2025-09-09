#!/usr/bin/env python3
"""
Script to add Google Analytics manage permission and assign it to SuperAdmin role
"""
from app.core.database import SessionLocal
from app.models.rbac import Permission, Role

def add_manage_google_analytics_permission():
    """Add Google Analytics manage permission and assign to SuperAdmin"""
    db = SessionLocal()
    try:
        # Check if permission already exists
        existing_permission = db.query(Permission).filter(
            Permission.name == "settings.manage_google_analytics"
        ).first()
        
        if existing_permission:
            print("Google Analytics manage permission already exists")
            permission = existing_permission
        else:
            # Create the permission
            permission = Permission(
                name="settings.manage_google_analytics",
                resource="settings",
                action="manage_google_analytics",
                description="Manage Google Analytics settings"
            )
            db.add(permission)
            db.flush()
            print("Created Google Analytics manage permission")
        
        # Get SuperAdmin role
        superadmin_role = db.query(Role).filter(Role.name == "superadmin").first()
        
        if not superadmin_role:
            print("SuperAdmin role not found")
            return
        
        # Check if permission is already assigned to SuperAdmin
        if permission not in superadmin_role.permissions:
            superadmin_role.permissions.append(permission)
            print("Assigned Google Analytics manage permission to SuperAdmin")
        else:
            print("Google Analytics manage permission already assigned to SuperAdmin")
        
        db.commit()
        print("Successfully updated permissions")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_manage_google_analytics_permission()