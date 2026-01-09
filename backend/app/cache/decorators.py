# backend/app/cache/decorators.py
from functools import wraps
from app.cache.redis_cache import get_cache
from app.cache.cache_keys import CacheKeys
import logging
import json

logger = logging.getLogger(__name__)

def cached(key_func, ttl: int = 3600):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Generate cache key
            if callable(key_func):
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = key_func
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached_value
            
            # Cache miss, execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cache SET: {cache_key}")
            
            return result
        
        return wrapper
    return decorator

def invalidate_cache(pattern: str):
    """Decorator to invalidate cache after function execution"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            cache = get_cache()
            cache.delete_pattern(pattern)
            logger.debug(f"Cache INVALIDATED: {pattern}")
            return result
        return wrapper
    return decorator
