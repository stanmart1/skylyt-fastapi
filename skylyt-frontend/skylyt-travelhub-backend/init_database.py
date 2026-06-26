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
            # Dashboard permissions
            {"name": "dashboard.view_users", "resource": "dashboard", "action": "view", "description": "View users section"},
            {"name": "dashboard.view_roles", "resource": "dashboard", "action": "view", "description": "View roles section"},
            {"name": "dashboard.view_system", "resource": "dashboard", "action": "view", "description": "View system section"},
            {"name": "dashboard.view_cars", "resource": "dashboard", "action": "view", "description": "View cars section"},
            {"name": "dashboard.view_hotels", "resource": "dashboard", "action": "view", "description": "View hotels section"},
            {"name": "dashboard.view_bookings", "resource": "dashboard", "action": "view", "description": "View bookings section"},
            {"name": "dashboard.view_payments", "resource": "dashboard", "action": "view", "description": "View payments section"},
            {"name": "dashboard.view_reviews", "resource": "dashboard", "action": "view", "description": "View reviews section"},
            {"name": "dashboard.view_support", "resource": "dashboard", "action": "view", "description": "View support section"},
            {"name": "dashboard.view_notifications", "resource": "dashboard", "action": "view", "description": "View notifications section"},
            {"name": "dashboard.view_settings", "resource": "dashboard", "action": "view", "description": "View settings section"},

            # Settings permissions
            {"name": "settings.view_general", "resource": "settings", "action": "view", "description": "View general settings"},
            {"name": "settings.manage_general", "resource": "settings", "action": "manage", "description": "Manage general settings"},
            {"name": "settings.view_payment_gateway", "resource": "settings", "action": "view", "description": "View payment gateway settings"},
            {"name": "settings.manage_payment_gateway", "resource": "settings", "action": "manage", "description": "Manage payment gateway settings"},
            {"name": "settings.view_bank_transfer", "resource": "settings", "action": "view", "description": "View bank transfer settings"},
            {"name": "settings.manage_bank_transfer", "resource": "settings", "action": "manage", "description": "Manage bank transfer settings"},
            {"name": "settings.view_currency", "resource": "settings", "action": "view", "description": "View currency settings"},
            {"name": "settings.manage_currency", "resource": "settings", "action": "manage", "description": "Manage currency settings"},
            {"name": "settings.view_notification_config", "resource": "settings", "action": "view", "description": "View notification settings"},
            {"name": "settings.manage_notification_config", "resource": "settings", "action": "manage", "description": "Manage notification settings"},
            {"name": "settings.view_security", "resource": "settings", "action": "view", "description": "View security settings"},
            {"name": "settings.manage_security", "resource": "settings", "action": "manage", "description": "Manage security settings"},
            {"name": "settings.view_google_analytics", "resource": "settings", "action": "view", "description": "View Google Analytics settings"},
            {"name": "settings.manage_google_analytics", "resource": "settings", "action": "manage", "description": "Manage Google Analytics settings"},
            {"name": "settings.view_features", "resource": "settings", "action": "view", "description": "View feature settings"},
            {"name": "settings.manage_features", "resource": "settings", "action": "manage", "description": "Manage feature settings"},

            # Content permissions
            {"name": "content.manage_hotels", "resource": "content", "action": "manage", "description": "Manage hotels"},
            {"name": "content.manage_cars", "resource": "content", "action": "manage", "description": "Manage cars"},
            {"name": "content.manage_drivers", "resource": "content", "action": "manage", "description": "Manage drivers"},

            # User permissions
            {"name": "users.create", "resource": "users", "action": "create", "description": "Create users"},
            {"name": "users.manage_roles", "resource": "users", "action": "manage", "description": "Manage user roles"},
            {"name": "users.update", "resource": "users", "action": "update", "description": "Update users"},
            {"name": "users.delete", "resource": "users", "action": "delete", "description": "Delete users"},

            # Booking permissions
            {"name": "bookings.create", "resource": "bookings", "action": "create", "description": "Create bookings"},
            {"name": "bookings.update", "resource": "bookings", "action": "update", "description": "Update bookings"},
            {"name": "bookings.delete", "resource": "bookings", "action": "delete", "description": "Cancel bookings"},

            # Payment permissions
            {"name": "payments.create", "resource": "payments", "action": "create", "description": "Process payments"},
            {"name": "payments.update", "resource": "payments", "action": "update", "description": "Update payments"},
            {"name": "payments.verify", "resource": "payments", "action": "verify", "description": "Verify payments"},
            {"name": "payments.delete", "resource": "payments", "action": "delete", "description": "Delete payments"},

            # Support permissions
            {"name": "support.assign", "resource": "support", "action": "assign", "description": "Assign support tickets"},
            {"name": "support.update", "resource": "support", "action": "update", "description": "Update support tickets"},
            {"name": "support.respond", "resource": "support", "action": "respond", "description": "Respond to support tickets"},

            # Review permissions
            {"name": "reviews.respond", "resource": "reviews", "action": "respond", "description": "Respond to reviews"},
            {"name": "reviews.moderate", "resource": "reviews", "action": "moderate", "description": "Moderate reviews"},

            # Notification permissions
            {"name": "notifications.create", "resource": "notifications", "action": "create", "description": "Create notifications"},
            {"name": "notifications.test", "resource": "notifications", "action": "test", "description": "Send test notifications"},
            {"name": "notifications.update", "resource": "notifications", "action": "update", "description": "Update notifications"},
            {"name": "notifications.delete", "resource": "notifications", "action": "delete", "description": "Delete notifications"},

            # System permissions
            {"name": "system.manage_settings", "resource": "system", "action": "manage", "description": "Manage system settings"},
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
            Permission.name.in_(["bookings.create", "bookings.update", "payments.create"])
        ).all()
        customer_role.permissions = customer_permissions

        # Accountant role permissions
        accountant_permissions = db.query(Permission).filter(
            Permission.name.in_(["dashboard.view_bookings", "dashboard.view_payments", "payments.verify", "payments.update"])
        ).all()
        accountant_role.permissions = accountant_permissions

        # Admin role permissions - all dashboard, content, users, bookings, payments, reviews, support, notifications
        admin_permissions = db.query(Permission).filter(
            Permission.resource.in_(["dashboard", "content", "users", "bookings", "payments", "reviews", "support", "notifications", "system"])
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