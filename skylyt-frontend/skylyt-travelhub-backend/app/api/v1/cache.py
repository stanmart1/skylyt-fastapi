from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user
from app.core.redis import RedisService
import logging

router = APIRouter(prefix="/cache", tags=["Cache"])
logger = logging.getLogger(__name__)

@router.post("/clear")
def clear_cache(current_user = Depends(get_current_user)):
    """Clear all DragonflyDB cache"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        redis_client = RedisService.get_client()
        redis_client.flushall()
        logger.info(f"Cache cleared by user: {current_user.email}")
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")