# backend/app/cache/redis_cache.py
import redis
from app.config import settings
from typing import Optional, Any, List
import json
import logging

logger = logging.getLogger(__name__)

class RedisCache:
    """Redis caching service"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache GET error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache"""
        try:
            self.redis_client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Cache SET error: {e}")
            return False
    
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
