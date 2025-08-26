from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.monitoring.metrics import metrics_collector
from app.monitoring.alerting import health_checker, alert_manager
from app.monitoring.error_tracking import error_tracker
from app.utils.cache import cache_manager
import redis
import time

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """System health check for admin dashboard"""
    import psutil
    
    health_data = {
        "status": "healthy",
        "database": {
            "status": "connected",
            "responseTime": 0,
            "connections": 0
        },
        "redis": {
            "status": "connected", 
            "responseTime": 0
        },

        "system": {
            "cpu_usage": round(psutil.cpu_percent(), 1),
            "memory_usage": round(psutil.virtual_memory().percent, 1),
            "disk_usage": round(psutil.disk_usage('/').percent, 1)
        },
        "uptime": 0  # Will be calculated from database
    }
    
    # Test database
    try:
        from sqlalchemy import text
        start_time = time.time()
        db.execute(text("SELECT 1"))
        health_data["database"]["responseTime"] = round((time.time() - start_time) * 1000, 2)
        # Get actual database connection count
        result = db.execute(text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"))
        health_data["database"]["connections"] = result.scalar() or 0
        
        # Get database uptime
        uptime_result = db.execute(text("SELECT EXTRACT(EPOCH FROM (now() - pg_postmaster_start_time()))"))
        uptime_seconds = uptime_result.scalar() or 0
        health_data["uptime"] = int(uptime_seconds)
    except Exception as e:
        print(f"Database health check failed: {e}")
        health_data["status"] = "warning"
        health_data["database"]["status"] = "error"
    
    # Redis check disabled
    health_data["redis"]["status"] = "disabled"
    health_data["redis"]["responseTime"] = 0
    
    return health_data

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with dependency status"""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "skylyt-travelhub-backend",
        "checks": {}
    }
    
    # Database check
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "unhealthy"
    
    # Redis check disabled
    health_status["checks"]["redis"] = {"status": "disabled"}
    
    return health_status

@router.get("/metrics")
async def get_metrics():
    """Get application metrics"""
    return metrics_collector.get_health_metrics()

@router.get("/metrics/prometheus")
async def get_prometheus_metrics():
    """Get Prometheus metrics"""
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(
        content=metrics_collector.get_metrics(),
        media_type="text/plain"
    )

@router.get("/health/comprehensive")
async def comprehensive_health_check():
    """Comprehensive health check with all systems"""
    health_results = await health_checker.run_health_checks()
    
    # Add error tracking summary
    error_summary = error_tracker.get_error_summary()
    health_results["error_tracking"] = error_summary
    
    # Add performance metrics
    performance_metrics = metrics_collector.get_health_metrics()
    health_results["performance"] = performance_metrics
    
    return health_results

@router.get("/errors/summary")
async def get_error_summary():
    """Get error tracking summary"""
    return error_tracker.get_error_summary()

@router.post("/alerts/test")
async def test_alert_system():
    """Test alert system functionality"""
    test_metrics = {
        "avg_response_time": 3.0,
        "error_rate": 0.1
    }
    
    await alert_manager.check_performance_alerts(test_metrics)
    return {"message": "Test alerts sent"}