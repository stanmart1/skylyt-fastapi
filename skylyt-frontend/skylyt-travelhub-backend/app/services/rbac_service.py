from sqlalchemy.orm import Session
from app.models.rbac import Role, Permission
from app.models.user import User
from typing import List, Dict, Any


class RBACService:
    
    @staticmethod
    def create_role(db: Session, name: str, description: str = None) -> Role:
        """Create a new role"""
        role = Role(name=name, description=description)
        db.add(role)
        db.commit()
        db.refresh(role)
        return role
    
    @staticmethod
    def create_permission(db: Session, name: str, resource: str, action: str, description: str = None) -> Permission:
        """Create a new permission"""
        # Get next available ID
        max_id = db.query(Permission).count()
        permission = Permission(
            id=str(max_id + 1),
            name=name,
            resource=resource,
            action=action,
            description=description
        )
        db.add(permission)
        db.commit()
        db.refresh(permission)
        return permission
    
    @staticmethod
    def assign_role_to_user(db: Session, user_id: int, role_name: str) -> bool:
        """Assign role to user"""
        user = db.query(User).filter(User.id == user_id).first()
        role = db.query(Role).filter(Role.name == role_name).first()
        
        if not user or not role:
            return False
        
        if role not in user.roles:
            user.roles.append(role)
            db.commit()
        
        return True
    
    @staticmethod
    def remove_role_from_user(db: Session, user_id: int, role_name: str) -> bool:
        """Remove role from user"""
        user = db.query(User).filter(User.id == user_id).first()
        role = db.query(Role).filter(Role.name == role_name).first()
        
        if not user or not role:
            return False
        
        if role in user.roles:
            user.roles.remove(role)
            db.commit()
        
        return True
    
    @staticmethod
    def assign_permission_to_role(db: Session, role_name: str, permission_name: str) -> bool:
        """Assign permission to role"""
        role = db.query(Role).filter(Role.name == role_name).first()
        permission = db.query(Permission).filter(Permission.name == permission_name).first()
        
        if not role or not permission:
            return False
        
        if permission not in role.permissions:
            role.permissions.append(permission)
            db.commit()
        
        return True
    
    @staticmethod
    def initialize_default_roles_and_permissions(db: Session):
        """Initialize default roles and permissions"""
        # Create default permissions
        permissions = [
            # Admin Dashboard Access
            ("dashboard.view_analytics", "dashboard", "view_analytics", "View analytics in admin dashboard"),
            ("dashboard.view_users", "dashboard", "view_users", "View users in admin dashboard"),
            ("dashboard.view_roles", "dashboard", "view_roles", "View roles in admin dashboard"),
            ("dashboard.view_bookings", "dashboard", "view_bookings", "View bookings in admin dashboard"),
            ("dashboard.view_payments", "dashboard", "view_payments", "View payments in admin dashboard"),
            ("dashboard.view_system", "dashboard", "view_system", "View system health in admin dashboard"),
            ("dashboard.view_settings", "dashboard", "view_settings", "View settings in admin dashboard"),
            ("dashboard.view_cars", "dashboard", "view_cars", "View car management in admin dashboard"),
            ("dashboard.view_hotels", "dashboard", "view_hotels", "View hotel management in admin dashboard"),
            
            # User Management
            ("users.create", "users", "create", "Create new users"),
            ("users.read", "users", "read", "View user profiles and data"),
            ("users.update", "users", "update", "Edit user information"),
            ("users.delete", "users", "delete", "Delete user accounts"),
            ("users.manage_roles", "users", "manage_roles", "Assign/remove roles from users"),
            ("users.view_activity", "users", "view_activity", "View user activity logs"),
            
            # Role & Permission Management
            ("roles.create", "roles", "create", "Create new roles"),
            ("roles.read", "roles", "read", "View roles and permissions"),
            ("roles.update", "roles", "update", "Edit role permissions"),
            ("roles.delete", "roles", "delete", "Delete roles"),
            ("permissions.create", "permissions", "create", "Create new permissions"),
            ("permissions.read", "permissions", "read", "View all permissions"),
            ("permissions.update", "permissions", "update", "Edit permissions"),
            ("permissions.delete", "permissions", "delete", "Delete permissions"),
            
            # Booking Management
            ("bookings.create", "bookings", "create", "Create bookings for customers"),
            ("bookings.read", "bookings", "read", "View all booking details"),
            ("bookings.update", "bookings", "update", "Modify booking information"),
            ("bookings.delete", "bookings", "delete", "Cancel/delete bookings"),
            ("bookings.approve", "bookings", "approve", "Approve pending bookings"),
            ("bookings.export", "bookings", "export", "Export booking reports"),
            
            # Payment Management
            ("payments.create", "payments", "create", "Process new payments"),
            ("payments.read", "payments", "read", "View payment transactions"),
            ("payments.update", "payments", "update", "Update payment status"),
            ("payments.refund", "payments", "refund", "Process refunds"),
            ("payments.verify", "payments", "verify", "Verify payment authenticity"),
            ("payments.export", "payments", "export", "Export payment reports"),
            
            # Content Management
            ("content.manage_cars", "content", "manage_cars", "Add/edit/delete cars"),
            ("content.manage_hotels", "content", "manage_hotels", "Add/edit/delete hotels"),
            ("content.manage_featured", "content", "manage_featured", "Set featured cars/hotels"),
            ("content.upload_media", "content", "upload_media", "Upload images and media files"),
            ("content.manage_pricing", "content", "manage_pricing", "Update pricing information"),
            
            # System Administration
            ("system.view_health", "system", "view_health", "View system health status"),
            ("system.manage_settings", "system", "manage_settings", "Configure system settings"),
            ("system.view_logs", "system", "view_logs", "Access system logs"),
            ("system.backup", "system", "backup", "Create system backups"),
            ("system.maintenance", "system", "maintenance", "Perform system maintenance"),
            
            # Analytics & Reporting
            ("analytics.view_dashboard", "analytics", "view_dashboard", "Access analytics dashboard"),
            ("analytics.view_reports", "analytics", "view_reports", "View detailed reports"),
            ("analytics.export_data", "analytics", "export_data", "Export analytics data"),
            ("analytics.view_revenue", "analytics", "view_revenue", "View revenue analytics"),
            
            # Customer Support
            ("support.view_tickets", "support", "view_tickets", "View customer support tickets"),
            ("support.manage_tickets", "support", "manage_tickets", "Respond to support tickets"),
            ("support.view_feedback", "support", "view_feedback", "View customer feedback"),
            
            # Reviews & Ratings Management
            ("dashboard.view_reviews", "dashboard", "view_reviews", "View reviews management in admin dashboard"),
            ("reviews.read", "reviews", "read", "View customer reviews and ratings"),
            ("reviews.moderate", "reviews", "moderate", "Moderate and approve/reject reviews"),
            ("reviews.respond", "reviews", "respond", "Respond to customer reviews"),
            ("reviews.delete", "reviews", "delete", "Delete inappropriate reviews"),
            
            # Support Ticket System
            ("dashboard.view_support", "dashboard", "view_support", "View support system in admin dashboard"),
            ("tickets.create", "tickets", "create", "Create support tickets"),
            ("tickets.read", "tickets", "read", "View support tickets"),
            ("tickets.update", "tickets", "update", "Update ticket status and responses"),
            ("tickets.assign", "tickets", "assign", "Assign tickets to staff members"),
            ("tickets.close", "tickets", "close", "Close resolved tickets"),
            
            # Notification Center
            ("dashboard.view_notifications", "dashboard", "view_notifications", "View notification center in admin dashboard"),
            ("notifications.create", "notifications", "create", "Create notification templates"),
            ("notifications.read", "notifications", "read", "View notifications and templates"),
            ("notifications.update", "notifications", "update", "Edit notification templates"),
            ("notifications.send", "notifications", "send", "Send notifications to users"),
            ("notifications.manage_settings", "notifications", "manage_settings", "Configure notification settings"),
            
            # Driver Permissions
            ("driver.view_assigned_trips", "driver", "view_assigned_trips", "View only assigned bookings and trips"),
            ("driver.update_trip_status", "driver", "update_trip_status", "Update trip status (Pending → En Route → In Progress → Completed → Cancelled)"),
            ("driver.view_customer_contact", "driver", "view_customer_contact", "View customer contact details for assigned trips only"),
            ("driver.view_trip_details", "driver", "view_trip_details", "Access pickup and drop-off details for assigned trips"),
            ("driver.receive_notifications", "driver", "receive_notifications", "Receive trip assignment notifications via app/email/SMS"),
            ("driver.view_dashboard", "driver", "view_dashboard", "Access driver dashboard interface"),
            
            # Settings Management - Fine-grained permissions
            ("settings.view_general", "settings", "view_general", "View general system settings"),
            ("settings.manage_general", "settings", "manage_general", "Manage general system settings"),
            ("settings.view_payment_gateway", "settings", "view_payment_gateway", "View payment gateway settings"),
            ("settings.manage_payment_gateway", "settings", "manage_payment_gateway", "Manage payment gateway configurations"),
            ("settings.view_bank_transfer", "settings", "view_bank_transfer", "View bank transfer settings"),
            ("settings.manage_bank_transfer", "settings", "manage_bank_transfer", "Manage bank transfer configurations"),
            ("settings.view_currency", "settings", "view_currency", "View currency settings and rates"),
            ("settings.manage_currency", "settings", "manage_currency", "Manage currency rates and settings"),
            ("settings.view_notification_config", "settings", "view_notification_config", "View notification configuration settings"),
            ("settings.manage_notification_config", "settings", "manage_notification_config", "Manage notification configuration settings"),
            ("settings.view_security", "settings", "view_security", "View security and authentication settings"),
            ("settings.manage_security", "settings", "manage_security", "Manage security and authentication settings"),
        ]
        
        for name, resource, action, description in permissions:
            existing = db.query(Permission).filter(Permission.name == name).first()
            if not existing:
                RBACService.create_permission(db, name, resource, action, description)
        
        # Create default roles
        roles = [
            ("superadmin", "Super Administrator with all permissions"),
            ("admin", "Administrator with management permissions"),
            ("accountant", "Accountant with financial permissions"),
            ("driver", "Driver with trip management permissions"),
            ("customer", "Customer with basic permissions"),
        ]
        
        for name, description in roles:
            existing = db.query(Role).filter(Role.name == name).first()
            if not existing:
                RBACService.create_role(db, name, description)
        
        # Assign permissions to roles
        role_permissions = {
            "superadmin": [
                # Full dashboard access
                "dashboard.view_analytics", "dashboard.view_users", "dashboard.view_roles",
                "dashboard.view_bookings", "dashboard.view_payments", "dashboard.view_system",
                "dashboard.view_settings", "dashboard.view_cars", "dashboard.view_hotels",
                "dashboard.view_reviews", "dashboard.view_support", "dashboard.view_notifications",
                # Full user management
                "users.create", "users.read", "users.update", "users.delete", "users.manage_roles", "users.view_activity",
                # Full role management
                "roles.create", "roles.read", "roles.update", "roles.delete",
                "permissions.create", "permissions.read", "permissions.update", "permissions.delete",
                # Full booking management
                "bookings.create", "bookings.read", "bookings.update", "bookings.delete", "bookings.approve", "bookings.export",
                # Full payment management
                "payments.create", "payments.read", "payments.update", "payments.refund", "payments.verify", "payments.export",
                # Full content management
                "content.manage_cars", "content.manage_hotels", "content.manage_featured", "content.upload_media", "content.manage_pricing",
                # Full system access
                "system.view_health", "system.manage_settings", "system.view_logs", "system.backup", "system.maintenance",
                # Full analytics
                "analytics.view_dashboard", "analytics.view_reports", "analytics.export_data", "analytics.view_revenue",
                # Support access
                "support.view_tickets", "support.manage_tickets", "support.view_feedback",
                # Reviews management
                "reviews.read", "reviews.moderate", "reviews.respond", "reviews.delete",
                # Ticket management
                "tickets.create", "tickets.read", "tickets.update", "tickets.assign", "tickets.close",
                # Notification management
                "notifications.create", "notifications.read", "notifications.update", "notifications.send", "notifications.manage_settings",
                # Full settings management
                "settings.view_general", "settings.manage_general", "settings.view_payment_gateway", "settings.manage_payment_gateway",
                "settings.view_bank_transfer", "settings.manage_bank_transfer", "settings.view_currency", "settings.manage_currency",
                "settings.view_notification_config", "settings.manage_notification_config", "settings.view_security", "settings.manage_security"
            ],
            "admin": [
                # Limited dashboard access
                "dashboard.view_analytics", "dashboard.view_users", "dashboard.view_bookings",
                "dashboard.view_payments", "dashboard.view_cars", "dashboard.view_hotels",
                "dashboard.view_reviews", "dashboard.view_support", "dashboard.view_notifications",
                "dashboard.view_settings",
                # User management (no delete)
                "users.read", "users.update", "users.view_activity",
                # Booking management
                "bookings.create", "bookings.read", "bookings.update", "bookings.approve", "bookings.export",
                # Payment management (no refunds)
                "payments.read", "payments.update", "payments.verify",
                # Content management
                "content.manage_cars", "content.manage_hotels", "content.manage_featured", "content.upload_media",
                # Limited analytics
                "analytics.view_dashboard", "analytics.view_reports",
                # Support
                "support.view_tickets", "support.manage_tickets",
                # Reviews management
                "reviews.read", "reviews.moderate", "reviews.respond",
                # Ticket management
                "tickets.read", "tickets.update", "tickets.close",
                # Notification management
                "notifications.read", "notifications.send",
                # Limited settings access (view only for sensitive settings)
                "settings.view_general", "settings.manage_general",
                "settings.view_bank_transfer", "settings.manage_bank_transfer",
                "settings.view_currency", "settings.manage_currency",
                "settings.view_notification_config"
            ],
            "accountant": [
                # Financial dashboard access
                "dashboard.view_analytics", "dashboard.view_bookings", "dashboard.view_payments",
                "dashboard.view_settings",
                # Booking viewing
                "bookings.read", "bookings.export",
                # Full payment management
                "payments.read", "payments.update", "payments.refund", "payments.verify", "payments.export",
                # Financial analytics
                "analytics.view_dashboard", "analytics.view_revenue", "analytics.export_data",
                # Financial settings access
                "settings.view_bank_transfer", "settings.manage_bank_transfer",
                "settings.view_currency", "settings.manage_currency"
            ],
            "driver": [
                # Driver dashboard access
                "driver.view_dashboard",
                # Trip management
                "driver.view_assigned_trips", "driver.update_trip_status", "driver.view_trip_details",
                # Customer interaction
                "driver.view_customer_contact", "driver.receive_notifications",
                # Limited booking access (only assigned trips)
                "bookings.read"
            ],
            "customer": [
                # Basic booking permissions
                "bookings.create", "bookings.read", "bookings.update",
                # Basic payment permissions
                "payments.create", "payments.read"
            ]
        }
        
        for role_name, permission_names in role_permissions.items():
            if role_name == "superadmin":
                # Assign ALL permissions to superadmin
                all_permissions = db.query(Permission).all()
                role = db.query(Role).filter(Role.name == role_name).first()
                if role:
                    for permission in all_permissions:
                        if permission not in role.permissions:
                            role.permissions.append(permission)
                    db.commit()
            else:
                for permission_name in permission_names:
                    RBACService.assign_permission_to_role(db, role_name, permission_name)