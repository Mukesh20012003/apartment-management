# backend/app/cache/decorators.py
from functools import wraps
import inspect
import logging

from app.cache.redis_cache import get_cache

logger = logging.getLogger(__name__)


def cached(key_func, ttl: int = 3600):
    """Decorator for caching function results (sync + async safe)."""
    def decorator(func):
        is_coroutine = inspect.iscoroutinefunction(func)

        if is_coroutine:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                cache = get_cache()
                cache_key = key_func(*args, **kwargs) if callable(key_func) else key_func

                cached_value = cache.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache HIT: {cache_key}")
                    return cached_value

                result = await func(*args, **kwargs)

                cache.set(cache_key, result, ttl)
                logger.debug(f"Cache SET: {cache_key}")
                return result

            return async_wrapper

        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                cache = get_cache()
                cache_key = key_func(*args, **kwargs) if callable(key_func) else key_func

                cached_value = cache.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache HIT: {cache_key}")
                    return cached_value

                result = func(*args, **kwargs)

                cache.set(cache_key, result, ttl)
                logger.debug(f"Cache SET: {cache_key}")
                return result

            return sync_wrapper

    return decorator


def invalidate_cache(pattern: str):
    """Decorator to invalidate cache after function execution (sync + async)."""
    def decorator(func):
        is_coroutine = inspect.iscoroutinefunction(func)

        if is_coroutine:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)
                cache = get_cache()
                cache.delete_pattern(pattern)
                logger.debug(f"Cache INVALIDATED: {pattern}")
                return result

            return async_wrapper

        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                cache = get_cache()
                cache.delete_pattern(pattern)
                logger.debug(f"Cache INVALIDATED: {pattern}")
                return result

            return sync_wrapper

    return decorator
