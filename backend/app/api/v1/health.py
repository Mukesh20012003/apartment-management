# e.g. app/api/v1/health.py
from fastapi import APIRouter
from app.cache.redis_cache import get_cache  # or wherever

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/redis")
def health_redis():
    cache = get_cache()               # sync helper returning RedisCache
    cache.set("ping", "pong", ttl=60) # include ttl argument
    val = cache.get("ping")
    return {"ok": val == "pong"}
