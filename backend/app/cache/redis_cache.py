# backend/app/cache/redis_cache.py
import json
import logging
from typing import Optional, Any

from pydantic import BaseModel
import redis

from app.config import settings

logger = logging.getLogger(__name__)


def _to_serializable(value):
    # If it's a Pydantic model
    if isinstance(value, BaseModel):
        return value.model_dump()

    # If it's a SQLAlchemy model-like object
    if hasattr(value, "__dict__") and not isinstance(
        value, (dict, list, str, int, float, bool, type(None))
    ):
        data = {
            k: v
            for k, v in value.__dict__.items()
            if not k.startswith("_")
        }
        return data

    # Already JSON‑serializable
    return value


class RedisCache:
    """Redis caching service"""

    def __init__(self):
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            print("CACHE GET:", key, "->", value)
            if value:
                try:
                    return json.loads(value)
                except Exception:
                    return value
            return None
        except Exception as e:
            logger.error(f"Cache GET error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int) -> None:
        """Set value in cache with TTL"""
        try:
            serializable = _to_serializable(value)
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(serializable, default=str),
            )
            print("CACHE SET:", key)
            logger.debug(f"Cache SET: {key}")
        except Exception as e:
            logger.error(f"Cache SET error: {e}")

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache DELETE error: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache DELETE_PATTERN error: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache EXISTS error: {e}")
            return False

    def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter"""
        try:
            return self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache INCREMENT error: {e}")
            return 0

    def get_ttl(self, key: str) -> int:
        """Get TTL of key"""
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL error: {e}")
            return -1


# Global cache instance
cache_service: Optional[RedisCache] = None


def get_cache() -> RedisCache:
    """Get cache instance"""
    global cache_service
    if cache_service is None:
        cache_service = RedisCache()
    return cache_service
