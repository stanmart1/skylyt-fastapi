#!/usr/bin/env python3
"""
Database initialization script for Skylyt TravelHub
Creates all tables and adds initial data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import engine, SessionLocal
from app.models import Base, User, Role, Permission
from app.models.rbac import user_roles, role_permissions
from app.models.notification import Notification
from app.models.car import Car
from app.models.hotel import Hotel
from app.models.booking import Booking
from app.models.payment import Payment
from app.core.security import get_password_hash

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")

def create_initial_permissions():
    """Create initial permissions"""
    db = SessionLocal()
    try:
        permissions_data = [
            # User permissions
            {"name": "users:read", "resource": "users", "action": "read", "description": "View users"},
            {"name": "users:create", "resource": "users", "action": "create", "description": "Create users"},
            {"name": "users:update", "resource": "users", "action": "update", "description": "Update users"},
            {"name": "users:delete", "resource": "users", "action": "delete", "description": "Delete users"},
            
            # Booking permissions
            {"name": "bookings:read", "resource": "bookings", "action": "read", "description": "View bookings"},
            {"name": "bookings:create", "resource": "bookings", "action": "create", "description": "Create bookings"},
            {"name": "bookings:update", "resource": "bookings", "action": "update", "description": "Update bookings"},
            {"name": "bookings:delete", "resource": "bookings", "action": "delete", "description": "Cancel bookings"},
            
            # Payment permissions
            {"name": "payments:read", "resource": "payments", "action": "read", "description": "View payments"},
            {"name": "payments:create", "resource": "payments", "action": "create", "description": "Process payments"},
            {"name": "payments:verify", "resource": "payments", "action": "verify", "description": "Verify payments"},
            
            # Admin permissions
            {"name": "admin:dashboard", "resource": "admin", "action": "read", "description": "Access admin dashboard"},
            {"name": "admin:analytics", "resource": "admin", "action": "read", "description": "View analytics"},
        ]
        
        for perm_data in permissions_data:
            existing = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
            if not existing:
                permission = Permission(**perm_data)
                db.add(permission)
        
        db.commit()
        print("✅ Initial permissions created")
    except Exception as e:
        print(f"❌ Error creating permissions: {e}")
        db.rollback()
    finally:
        db.close()

def create_initial_roles():
    """Create initial roles"""
    db = SessionLocal()
    try:
        # Create roles
        roles_data = [
            {"name": "customer", "description": "Customer with basic permissions"},
            {"name": "accountant", "description": "Accountant with financial permissions"},
            {"name": "admin", "description": "Administrator with elevated permissions"},
            {"name": "superadmin", "description": "Super administrator with all permissions"},
        ]
        
        for role_data in roles_data:
            existing = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing:
                role = Role(**role_data)
                db.add(role)
        
        db.commit()
        
        # Assign permissions to roles
        customer_role = db.query(Role).filter(Role.name == "customer").first()
        accountant_role = db.query(Role).filter(Role.name == "accountant").first()
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        superadmin_role = db.query(Role).filter(Role.name == "superadmin").first()
        
        # Customer role permissions
        customer_permissions = db.query(Permission).filter(
            Permission.name.in_(["bookings:read", "bookings:create", "bookings:update", "payments:create"])
        ).all()
        customer_role.permissions = customer_permissions
        
        # Accountant role permissions
        accountant_permissions = db.query(Permission).filter(
            Permission.name.in_(["bookings:read", "payments:read", "payments:verify"])
        ).all()
        accountant_role.permissions = accountant_permissions
        
        # Admin role permissions
        admin_permissions = db.query(Permission).filter(
            Permission.resource.in_(["bookings", "payments", "users"])
        ).all()
        admin_role.permissions = admin_permissions
        
        # Superadmin gets all permissions
        all_permissions = db.query(Permission).all()
        superadmin_role.permissions = all_permissions
        
        db.commit()
        print("✅ Initial roles and permissions assigned")
    except Exception as e:
        print(f"❌ Error creating roles: {e}")
        db.rollback()
    finally:
        db.close()

def create_admin_user():
    """Create initial admin user"""
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin_user = db.query(User).filter(User.email == "admin@skylyt.com").first()
        if not admin_user:
            admin_user = User(
                email="admin@skylyt.com",
                hashed_password=get_password_hash("admin123"),
                first_name="Admin",
                last_name="User",
                is_active=True,
                is_verified=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            # Assign superadmin role
            superadmin_role = db.query(Role).filter(Role.name == "superadmin").first()
            if superadmin_role:
                admin_user.roles.append(superadmin_role)
                db.commit()
            
            print("✅ Admin user created: admin@skylyt.com / admin123")
        else:
            print("ℹ️ Admin user already exists")
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

def test_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Initializing Skylyt TravelHub Database...")
    
    if not test_connection():
        print("❌ Cannot connect to database. Check your .env configuration.")
        sys.exit(1)
    
    create_tables()
    create_initial_permissions()
    create_initial_roles()
    create_admin_user()
    
    print("✅ Database initialization complete!")
    print("🔑 Admin login: admin@skylyt.com / admin123")