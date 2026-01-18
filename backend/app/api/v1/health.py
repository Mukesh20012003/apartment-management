from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.cache.redis_cache import get_cache  # your Redis cache
import redis # pyright: ignore[reportMissingImports]
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/health", tags=["Health"])

@router.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    """Basic liveness probe"""
    return {
        "status": "healthy",
        "service": "apartment-management-api",
        "timestamp": "2026-01-17T19:00:00Z",  # replace with datetime.utcnow()
        "version": "1.0.0"
    }

@router.get("/detailed", status_code=status.HTTP_200_OK)
async def detailed_health_check(
    db: Session = Depends(get_db)
):
    """Readiness probe with full dependency check"""
    health_status = {
        "status": "healthy",
        "services": {},
        "timestamp": "2026-01-17T19:00:00Z"
    }
    
    # 1. Database check
    try:
        db.execute("SELECT 1")
        db.commit()
        health_status["services"]["database"] = {
            "status": "healthy",
            "message": "PostgreSQL connection OK"
        }
    except Exception as e:
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
        logger.error(f"DB health check failed: {e}")
    
    # 2. Redis check (YOUR style + Phase 13)
    try:
        cache = get_cache()
        # Phase 13: ping
        cache.redis_client.ping()
        # YOUR style: real test
        cache.set("health-ping", "pong", ttl=60)
        result = cache.get("health-ping")
        if result == "pong":
            health_status["services"]["redis"] = {
                "status": "healthy",
                "test": "ping/pong passed",
                "cache_ttl_test": True
            }
        else:
            raise redis.RedisError("Cache test failed")
    except (redis.ConnectionError, redis.RedisError) as e:
        health_status["services"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
        logger.error(f"Redis health check failed: {e}")
    
    # 3. Cache invalidation test (bonus)
    try:
        cache = get_cache()
        cache.set("health-invalidate", "test", ttl=1)
        cache.delete("health-invalidate")
        health_status["services"]["cache_ops"] = "healthy"
    except:
        health_status["services"]["cache_ops"] = "degraded"
    
    return health_status

@router.get("/redis", status_code=status.HTTP_200_OK)
def health_redis_only():
    """Redis-specific check (your original)"""
    try:
        cache = get_cache()
        cache.set("ping", "pong", ttl=60)
        val = cache.get("ping")
        return {
            "redis": "healthy",
            "ping_pong": val == "pong",
            "cache_test": True
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis unhealthy: {str(e)}")
