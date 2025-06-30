"""Database query optimization layer for industry knowledge databases."""

import threading
import time
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict, OrderedDict
from functools import wraps
import hashlib
import logging

logger = logging.getLogger(__name__)


class QueryCache:
    """Thread-safe LRU cache with TTL support for database queries."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """Initialize query cache.
        
        Args:
            max_size: Maximum number of cached entries
            ttl_seconds: Time-to-live for cache entries in seconds
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache = OrderedDict()
        self._access_times = {}
        self._lock = threading.RLock()
        self._hit_count = 0
        self._miss_count = 0
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = f"{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with TTL check."""
        with self._lock:
            if key not in self._cache:
                self._miss_count += 1
                return None
            
            # Check TTL
            access_time = self._access_times.get(key, 0)
            if time.time() - access_time > self.ttl_seconds:
                self._remove_entry(key)
                self._miss_count += 1
                return None
            
            # Move to end (most recently used)
            value = self._cache.pop(key)
            self._cache[key] = value
            self._access_times[key] = time.time()
            self._hit_count += 1
            return value
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache with LRU eviction."""
        with self._lock:
            if key in self._cache:
                # Update existing entry
                self._cache.pop(key)
            elif len(self._cache) >= self.max_size:
                # Remove least recently used entry
                oldest_key = next(iter(self._cache))
                self._remove_entry(oldest_key)
            
            self._cache[key] = value
            self._access_times[key] = time.time()
    
    def _remove_entry(self, key: str) -> None:
        """Remove entry from cache and access times."""
        self._cache.pop(key, None)
        self._access_times.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
            self._hit_count = 0
            self._miss_count = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hit_count + self._miss_count
            hit_rate = self._hit_count / total_requests if total_requests > 0 else 0.0
            
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hit_count": self._hit_count,
                "miss_count": self._miss_count,
                "hit_rate": hit_rate,
                "ttl_seconds": self.ttl_seconds
            }


class QueryBatcher:
    """Batches multiple queries to reduce database access overhead."""
    
    def __init__(self, batch_size: int = 10, flush_interval: float = 0.1):
        """Initialize query batcher.
        
        Args:
            batch_size: Maximum batch size before auto-flush
            flush_interval: Time interval for auto-flush in seconds
        """
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self._pending_queries = []
        self._lock = threading.Lock()
        self._last_flush = time.time()
    
    def add_query(self, query_func, *args, **kwargs) -> Any:
        """Add query to batch or execute immediately if batch is full."""
        with self._lock:
            self._pending_queries.append((query_func, args, kwargs))
            
            # Check if we should flush
            should_flush = (
                len(self._pending_queries) >= self.batch_size or
                time.time() - self._last_flush > self.flush_interval
            )
            
            if should_flush:
                return self._flush_batch()
            
            return None
    
    def _flush_batch(self) -> List[Any]:
        """Execute all pending queries in batch."""
        if not self._pending_queries:
            return []
        
        results = []
        for query_func, args, kwargs in self._pending_queries:
            try:
                result = query_func(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                results.append(None)
        
        self._pending_queries.clear()
        self._last_flush = time.time()
        return results
    
    def flush(self) -> List[Any]:
        """Manually flush all pending queries."""
        with self._lock:
            return self._flush_batch()


class QueryOptimizer:
    """Optimizes database queries with caching, batching, and indexing."""
    
    def __init__(self, cache_size: int = 1000, cache_ttl: int = 3600):
        """Initialize query optimizer.
        
        Args:
            cache_size: Maximum cache size
            cache_ttl: Cache TTL in seconds
        """
        self.cache = QueryCache(max_size=cache_size, ttl_seconds=cache_ttl)
        self.batcher = QueryBatcher()
        self._indexes = defaultdict(dict)
        self._lock = threading.RLock()
    
    def cached_query(self, cache_key: Optional[str] = None):
        """Decorator for caching query results."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                if cache_key:
                    key = f"{func.__name__}:{cache_key}"
                else:
                    key = self.cache._generate_key(func.__name__, *args, **kwargs)
                
                # Check cache first
                cached_result = self.cache.get(key)
                if cached_result is not None:
                    return cached_result
                
                # Execute query and cache result
                result = func(*args, **kwargs)
                self.cache.set(key, result)
                return result
            
            return wrapper
        return decorator
    
    def build_index(self, data: Dict[str, Any], index_fields: List[str]) -> None:
        """Build indexes for faster lookups."""
        with self._lock:
            for field in index_fields:
                index = defaultdict(list)
                
                # Build index based on data structure
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, dict) and field in value:
                            index[value[field]].append(key)
                        elif isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict) and field in item:
                                    index[item[field]].append(key)
                
                self._indexes[field] = dict(index)
                logger.debug(f"Built index for field '{field}' with {len(index)} entries")
    
    def indexed_lookup(self, field: str, value: Any) -> List[str]:
        """Perform indexed lookup for faster queries."""
        with self._lock:
            if field in self._indexes:
                return self._indexes[field].get(value, [])
            return []
    
    def rebuild_indexes(self, data: Dict[str, Any]) -> None:
        """Rebuild all indexes with new data."""
        with self._lock:
            fields = list(self._indexes.keys())
            self._indexes.clear()
            if fields:
                self.build_index(data, fields)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_stats()
    
    def clear_cache(self) -> None:
        """Clear query cache."""
        self.cache.clear()
    
    def optimize_query_batch(self, queries: List[Tuple]) -> List[Any]:
        """Optimize a batch of queries."""
        results = []
        cached_results = {}
        
        # First pass: check cache for all queries
        for i, (func, args, kwargs) in enumerate(queries):
            key = self.cache._generate_key(func.__name__, *args, **kwargs)
            cached_result = self.cache.get(key)
            if cached_result is not None:
                cached_results[i] = cached_result
            else:
                results.append((i, func, args, kwargs, key))
        
        # Second pass: execute uncached queries
        final_results = [None] * len(queries)
        
        # Add cached results
        for i, result in cached_results.items():
            final_results[i] = result
        
        # Execute remaining queries
        for i, func, args, kwargs, key in results:
            try:
                result = func(*args, **kwargs)
                self.cache.set(key, result)
                final_results[i] = result
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                final_results[i] = None
        
        return final_results


# Global query optimizer instance
_query_optimizer = QueryOptimizer()


def get_query_optimizer() -> QueryOptimizer:
    """Get the global query optimizer instance."""
    return _query_optimizer


def reset_query_optimizer():
    """Reset the global query optimizer (for testing)."""
    global _query_optimizer
    _query_optimizer = QueryOptimizer()