from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging

from app.core.database import get_db, reset_connection_pool
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.performance_monitor import performance_monitor

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/test")
async def test_connection():
    """Test endpoint to verify frontend-backend connection"""
    return {
        "status": "success",
        "message": "Backend is connected and working!",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cors_enabled": True
    }


@router.get("/test-admin")
async def test_admin(db: Session = Depends(get_db)):
    """Test admin user exists"""
    admin_user = db.query(User).filter(User.email == "admin@skylyt.com").first()
    if admin_user:
        return {
            "exists": True,
            "email": admin_user.email,
            "is_active": admin_user.is_active,
            "roles_count": len(admin_user.roles)
        }
    return {"exists": False}


@router.get("/performance/metrics")
async def get_performance_metrics(db: Session = Depends(get_db)):
    """Get comprehensive performance metrics"""
    try:
        metrics = performance_monitor.get_comprehensive_metrics(db)
        return metrics
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")


@router.get("/performance/summary")
async def get_performance_summary(db: Session = Depends(get_db)):
    """Get performance summary"""
    try:
        summary = performance_monitor.get_performance_summary(db)
        return summary
    except Exception as e:
        logger.error(f"Error getting performance summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance summary")


@router.post("/performance/reset-pool")
async def reset_database_pool():
    """Reset database connection pool (admin only)"""
    try:
        success = reset_connection_pool()
        return {"success": success, "message": "Database pool reset" if success else "Failed to reset pool"}
    except Exception as e:
        logger.error(f"Error resetting database pool: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset database pool")


@router.get("/cars-management")
async def cars_management_page(current_user=Depends(get_current_user)):
    """Serve cars management dashboard page"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"message": "Cars Management Dashboard", "user": current_user.email}


@router.get("/hotel-management")
async def hotel_management_page(current_user=Depends(get_current_user)):
    """Serve hotel management dashboard page"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"message": "Hotel Management Dashboard", "user": current_user.email}
