"""
Redis caching service for performance optimization.

Provides caching for:
- Workspace metadata and stats
- Vector search results
- Embeddings
- Document lists
"""
import json
import hashlib
from typing import Optional, Any, Callable
from functools import wraps
import redis
from redis.exceptions import RedisError

from src.core.config import settings
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class CacheService:
    """Redis-based caching service"""
    
    def __init__(self):
        """Initialize Redis client"""
        try:
            self.client = redis.Redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.client.ping()
            self.enabled = True
        except (RedisError, Exception) as e:
            logger.warning(f"Redis not available, caching disabled: {e}", exc_info=True)
            self.client = None
            self.enabled = False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except (RedisError, json.JSONDecodeError) as e:
            logger.warning(f"Cache get error for key {key}: {e}", extra={"cache_key": key}, exc_info=True)
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        if not self.enabled:
            return False
        
        try:
            ttl = ttl or settings.cache_default_ttl
            serialized = json.dumps(value, default=str)
            self.client.setex(key, ttl, serialized)
            return True
        except (RedisError, TypeError) as e:
            logger.warning(f"Cache set error for key {key}: {e}", extra={"cache_key": key}, exc_info=True)
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled:
            return False
        
        try:
            self.client.delete(key)
            return True
        except RedisError as e:
            logger.warning(f"Cache delete error for key {key}: {e}", extra={"cache_key": key}, exc_info=True)
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.enabled:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except RedisError as e:
            logger.warning(f"Cache delete_pattern error for pattern {pattern}: {e}", extra={"pattern": pattern}, exc_info=True)
            return 0
    
    def invalidate_pattern(self, pattern: str) -> None:
        """Alias for delete_pattern for consistency with other code"""
        self.delete_pattern(pattern)
    
    def invalidate_workspace(self, workspace_id: str) -> None:
        """Invalidate all workspace-related caches"""
        patterns = [
            f"workspace:{workspace_id}:*",
            f"workspace:{workspace_id}:stats",
            f"workspace:{workspace_id}:documents",
            f"workspace:{workspace_id}:metadata",
            f"vector_search:{workspace_id}:*",
            f"document:*:workspace:{workspace_id}",
        ]
        for pattern in patterns:
            self.delete_pattern(pattern)
    
    def invalidate_document(self, document_id: str, workspace_id: str) -> None:
        """Invalidate document-related caches"""
        patterns = [
            f"document:{document_id}:*",
            f"workspace:{workspace_id}:documents",
            f"workspace:{workspace_id}:stats",
            f"vector_search:{workspace_id}:*",
        ]
        for pattern in patterns:
            self.delete_pattern(pattern)
    
    def get_or_set(
        self,
        key: str,
        func: Callable[[], Any],
        ttl: Optional[int] = None
    ) -> Any:
        """Get from cache or compute and cache result"""
        # Try cache first
        cached = self.get(key)
        if cached is not None:
            return cached
        
        # Compute value
        value = func()
        
        # Cache it
        self.set(key, value, ttl)
        
        return value


# Global cache instance
cache_service = CacheService()


def cache_result(key_prefix: str, ttl: Optional[int] = None):
    """
    Decorator to cache function results.
    
    Args:
        key_prefix: Prefix for cache key (will be combined with function args)
        ttl: Time to live in seconds (defaults to settings.cache_default_ttl)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key from prefix and args
            key_parts = [key_prefix]
            key_parts.extend(str(arg) for arg in args if arg is not None)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()) if v is not None)
            cache_key = ":".join(key_parts)
            
            # Try cache first
            cached = cache_service.get(cache_key)
            if cached is not None:
                return cached
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def hash_text(text: str) -> str:
    """Generate hash for text (for embedding cache keys)"""
    return hashlib.sha256(text.encode()).hexdigest()[:16]

