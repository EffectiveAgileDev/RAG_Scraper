"""PDF cache manager with expiration policies and storage management."""

import os
import time
import json
import hashlib
import threading
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path


# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a cached PDF entry."""
    cache_key: str
    content: bytes
    expiry_time: float
    metadata: Dict[str, Any]
    checksum: str


@dataclass
class CacheStats:
    """Cache statistics and metrics."""
    cache_hits: int = 0
    cache_misses: int = 0
    total_entries: int = 0
    current_size_mb: float = 0.0
    evictions_performed: int = 0
    expired_entries_cleared: int = 0
    concurrent_write_conflicts: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total_requests = self.cache_hits + self.cache_misses
        if total_requests == 0:
            return 0.0
        return self.cache_hits / total_requests


class PDFCacheManager:
    """Manages PDF caching with expiration policies and storage limits."""
    
    def __init__(self, cache_dir: str, max_cache_size_mb: int = 100, 
                 default_expiry_hours: int = 24):
        """Initialize cache manager.
        
        Args:
            cache_dir: Directory for cache storage
            max_cache_size_mb: Maximum cache size in MB
            default_expiry_hours: Default expiry time in hours
        """
        self.cache_dir = Path(cache_dir)
        self.max_cache_size_mb = max_cache_size_mb
        self.default_expiry_hours = default_expiry_hours
        self.cleanup_on_shutdown = True
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self._stats = CacheStats()
        
        # Create cache directory
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            # Directory exists but we can't write to it
            pass
        
        # Metadata storage
        self._metadata_file = self.cache_dir / "cache_metadata.json"
        try:
            self._metadata = self._load_metadata()
        except PermissionError:
            # Can't read metadata due to permissions
            self._metadata = {}
        
        logger.info(f"Initialized PDFCacheManager with cache_dir={cache_dir}, max_size={max_cache_size_mb}MB")

    def get_cache_key(self, url: str) -> str:
        """Generate cache key from URL.
        
        Args:
            url: URL to generate key for
            
        Returns:
            Cache key string
        """
        # Create deterministic hash of URL
        url_hash = hashlib.sha256(url.encode('utf-8')).hexdigest()
        return f"pdf_{url_hash[:16]}"

    def cache_pdf(self, cache_key: str, content: bytes, expiry_hours: int = None, 
                  metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Cache PDF content.
        
        Args:
            cache_key: Cache key
            content: PDF content
            expiry_hours: Expiry time in hours (uses default if None)
            metadata: Optional metadata
            
        Returns:
            True if cached successfully
        """
        if expiry_hours is None:
            expiry_hours = self.default_expiry_hours
        
        with self._lock:
            try:
                # Check cache size and perform eviction if needed
                self._ensure_cache_space(len(content))
                
                # Calculate expiry time
                expiry_time = time.time() + (expiry_hours * 3600)
                
                # Create checksum
                checksum = hashlib.md5(content).hexdigest()
                
                # Save content to file
                cache_file_path = self._get_cache_file_path(cache_key)
                try:
                    with open(cache_file_path, 'wb') as f:
                        f.write(content)
                except PermissionError:
                    # Re-raise permission errors so they can be caught by callers
                    raise
                
                # Update metadata
                current_time = time.time()
                entry_metadata = metadata or {}
                entry_metadata.update({
                    'cache_time': current_time,
                    'access_time': current_time,  # Initialize access time
                    'expiry_time': expiry_time,
                    'checksum': checksum,
                    'file_size': len(content)
                })
                
                self._metadata[cache_key] = entry_metadata
                self._save_metadata()
                
                # Update statistics
                self._stats.total_entries = len(self._metadata)
                self._update_cache_size()
                
                logger.debug(f"Cached PDF with key {cache_key}, size {len(content)} bytes")
                return True
                
            except Exception as e:
                logger.error(f"Failed to cache PDF {cache_key}: {e}")
                return False

    def is_cached(self, cache_key: str) -> bool:
        """Check if PDF is cached.
        
        Args:
            cache_key: Cache key to check
            
        Returns:
            True if cached
        """
        with self._lock:
            cache_file_path = self._get_cache_file_path(cache_key)
            return cache_file_path.exists() and cache_key in self._metadata

    def is_expired(self, cache_key: str) -> bool:
        """Check if cached PDF is expired.
        
        Args:
            cache_key: Cache key to check
            
        Returns:
            True if expired
        """
        with self._lock:
            if cache_key not in self._metadata:
                return True
            
            expiry_time = self._metadata[cache_key].get('expiry_time', 0)
            return time.time() > expiry_time

    def get_cached_content(self, cache_key: str) -> Optional[bytes]:
        """Get cached PDF content.
        
        Args:
            cache_key: Cache key
            
        Returns:
            PDF content or None if not found/expired
        """
        with self._lock:
            if not self.is_cached(cache_key):
                self._stats.cache_misses += 1
                return None
            
            if self.is_expired(cache_key):
                self._stats.cache_misses += 1
                return None
            
            try:
                cache_file_path = self._get_cache_file_path(cache_key)
                with open(cache_file_path, 'rb') as f:
                    content = f.read()
                
                # Update access time for LRU
                self._metadata[cache_key]['access_time'] = time.time()
                self._save_metadata()
                
                self._stats.cache_hits += 1
                return content
                
            except Exception as e:
                logger.error(f"Failed to read cached PDF {cache_key}: {e}")
                self._stats.cache_misses += 1
                return None

    def get_expiry(self, cache_key: str) -> Optional[float]:
        """Get expiry time for cached PDF.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Expiry timestamp or None
        """
        with self._lock:
            if cache_key not in self._metadata:
                return None
            return self._metadata[cache_key].get('expiry_time')

    def get_cache_metadata(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get metadata for cached PDF.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Metadata dictionary or None
        """
        with self._lock:
            return self._metadata.get(cache_key, {}).copy()

    def clear_expired(self) -> int:
        """Clear expired cache entries.
        
        Returns:
            Number of entries cleared
        """
        with self._lock:
            expired_keys = []
            current_time = time.time()
            
            for cache_key, metadata in self._metadata.items():
                expiry_time = metadata.get('expiry_time', 0)
                if current_time > expiry_time:
                    expired_keys.append(cache_key)
            
            for cache_key in expired_keys:
                self._remove_cache_entry(cache_key)
            
            self._stats.expired_entries_cleared += len(expired_keys)
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")
            
            return len(expired_keys)

    def validate_cache_integrity(self, cache_key: str) -> bool:
        """Validate cache entry integrity.
        
        Args:
            cache_key: Cache key to validate
            
        Returns:
            True if integrity is valid
        """
        with self._lock:
            if not self.is_cached(cache_key):
                return False
            
            try:
                # Get content and stored checksum
                cache_file_path = self._get_cache_file_path(cache_key)
                with open(cache_file_path, 'rb') as f:
                    content = f.read()
                
                stored_checksum = self._metadata[cache_key].get('checksum')
                if not stored_checksum:
                    return False
                
                # Calculate current checksum
                current_checksum = hashlib.md5(content).hexdigest()
                
                return current_checksum == stored_checksum
                
            except Exception as e:
                logger.error(f"Failed to validate cache integrity for {cache_key}: {e}")
                return False

    def get_cache_stats(self) -> CacheStats:
        """Get cache statistics.
        
        Returns:
            CacheStats object
        """
        with self._lock:
            self._update_cache_size()
            return CacheStats(
                cache_hits=self._stats.cache_hits,
                cache_misses=self._stats.cache_misses,
                total_entries=len(self._metadata),
                current_size_mb=self._stats.current_size_mb,
                evictions_performed=self._stats.evictions_performed,
                expired_entries_cleared=self._stats.expired_entries_cleared,
                concurrent_write_conflicts=self._stats.concurrent_write_conflicts
            )

    def shutdown(self):
        """Shutdown cache manager and cleanup if configured."""
        with self._lock:
            if self.cleanup_on_shutdown:
                self.clear_expired()
            
            logger.info("PDFCacheManager shutdown complete")

    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Get file path for cache key.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Path to cache file
        """
        return self.cache_dir / f"{cache_key}.pdf"

    def _ensure_cache_space(self, new_content_size: int):
        """Ensure cache has space for new content.
        
        Args:
            new_content_size: Size of new content in bytes
        """
        # Calculate current cache size
        self._update_cache_size()
        
        new_size_mb = new_content_size / (1024 * 1024)
        
        # Check if adding new content would exceed limit
        # Use a small buffer to ensure eviction happens even with rounding
        while (self._stats.current_size_mb + new_size_mb) > (self.max_cache_size_mb * 0.95) and self._metadata:
            oldest_key = self._find_lru_entry()
            if oldest_key:
                self._remove_cache_entry(oldest_key)
                self._stats.evictions_performed += 1
                self._update_cache_size()
            else:
                break

    def _find_lru_entry(self) -> Optional[str]:
        """Find least recently used cache entry.
        
        Returns:
            Cache key of LRU entry or None
        """
        if not self._metadata:
            return None
        
        oldest_key = None
        oldest_time = float('inf')
        
        for cache_key, metadata in self._metadata.items():
            access_time = metadata.get('access_time', metadata.get('cache_time', 0))
            if access_time < oldest_time:
                oldest_time = access_time
                oldest_key = cache_key
        
        return oldest_key

    def _remove_cache_entry(self, cache_key: str):
        """Remove cache entry.
        
        Args:
            cache_key: Cache key to remove
        """
        try:
            # Remove file
            cache_file_path = self._get_cache_file_path(cache_key)
            if cache_file_path.exists():
                cache_file_path.unlink()
            
            # Remove metadata
            if cache_key in self._metadata:
                del self._metadata[cache_key]
            
            self._save_metadata()
            
        except Exception as e:
            logger.error(f"Failed to remove cache entry {cache_key}: {e}")

    def _update_cache_size(self):
        """Update current cache size statistics."""
        total_size = 0
        
        for cache_key in self._metadata:
            cache_file_path = self._get_cache_file_path(cache_key)
            if cache_file_path.exists():
                total_size += cache_file_path.stat().st_size
        
        self._stats.current_size_mb = total_size / (1024 * 1024)

    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata from file.
        
        Returns:
            Metadata dictionary
        """
        if not self._metadata_file.exists():
            return {}
        
        try:
            with open(self._metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load cache metadata: {e}")
            return {}

    def _save_metadata(self):
        """Save cache metadata to file."""
        try:
            with open(self._metadata_file, 'w') as f:
                json.dump(self._metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache metadata: {e}")

    def _set_expiry(self, cache_key: str, expiry_time: float):
        """Set expiry time for cache entry (for testing).
        
        Args:
            cache_key: Cache key
            expiry_time: Expiry timestamp
        """
        with self._lock:
            if cache_key in self._metadata:
                self._metadata[cache_key]['expiry_time'] = expiry_time
                self._save_metadata()