from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db, engine
import time
import logging

router = APIRouter(prefix="/health", tags=["health"])
logger = logging.getLogger(__name__)

@router.get("/")
def health_check():
    """Basic health check"""
    return {"status": "healthy", "timestamp": time.time()}

@router.get("/db")
def database_health():
    """Database health check with direct connection"""
    try:
        # Use direct engine connection to avoid session issues
        with engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text("SELECT 1 as health_check"))
            result.fetchone()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        # Force pool disposal on health check failure
        try:
            engine.dispose()
        except Exception:
            pass
        raise HTTPException(status_code=503, detail="Database unhealthy")

@router.get("/ready")
def readiness_check():
    """Kubernetes readiness probe"""
    try:
        # Use direct engine connection for readiness check
        with engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text("SELECT 1 as ready_check"))
            result.fetchone()
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Not ready")

@router.get("/live")
def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive"}

@router.get("/logs")
def get_system_logs(lines: int = 50):
    """Get recent system logs"""
    try:
        from app.utils.log_reader import log_reader
        logs = log_reader.get_recent_logs(lines)
        return {"logs": logs}
    except Exception as e:
        logger.error(f"Failed to fetch logs: {e}")
        return {"logs": []}