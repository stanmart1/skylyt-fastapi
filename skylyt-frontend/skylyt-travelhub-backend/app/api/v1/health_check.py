from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db, engine
import time
import logging

router = APIRouter(prefix="/health", tags=["health"])
logger = logging.getLogger(__name__)

@router.get("/")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "timestamp": time.time()}

@router.get("/db")
async def database_health(db: Session = Depends(get_db)):
    """Database health check with connection recovery"""
    try:
        # Simple query to test connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        # Force pool disposal on health check failure
        engine.dispose()
        raise HTTPException(status_code=503, detail="Database unhealthy")

@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Kubernetes readiness probe"""
    try:
        db.execute("SELECT 1")
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Not ready")

@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive"}