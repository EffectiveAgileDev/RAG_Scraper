"""Unit tests for PDF cache manager with expiration policies and storage management."""

import pytest
import tempfile
import time
import os
import hashlib
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

# Import the module we'll be testing (will be created)
try:
    from src.pdf_processing.pdf_cache_manager import PDFCacheManager, CacheEntry, CacheStats
except ImportError:
    # Module doesn't exist yet - this is expected in TDD RED phase
    PDFCacheManager = None
    CacheEntry = None
    CacheStats = None


class TestPDFCacheManager:
    """Test PDF cache manager with expiration policies and storage limits."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def pdf_cache_manager(self, temp_cache_dir):
        """Create PDF cache manager instance for testing."""
        if PDFCacheManager is None:
            pytest.fail("PDFCacheManager not implemented yet - TDD RED phase")
        
        return PDFCacheManager(
            cache_dir=temp_cache_dir,
            max_cache_size_mb=10,  # Small for testing
            default_expiry_hours=24
        )

    @pytest.fixture
    def mock_pdf_content(self):
        """Mock valid PDF content."""
        return b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\nxref\n0 2\n0000000000 65535 f \n0000000010 00000 n \ntrailer\n<<\n/Size 2\n/Root 1 0 R\n>>\nstartxref\n79\n%%EOF'

    def test_cache_manager_initialization(self, temp_cache_dir):
        """Test cache manager can be initialized with configuration."""
        if PDFCacheManager is None:
            pytest.fail("PDFCacheManager not implemented yet - TDD RED phase")

        cache_manager = PDFCacheManager(
            cache_dir=temp_cache_dir,
            max_cache_size_mb=50,
            default_expiry_hours=48
        )
        
        assert str(cache_manager.cache_dir) == temp_cache_dir
        assert cache_manager.max_cache_size_mb == 50
        assert cache_manager.default_expiry_hours == 48
        assert os.path.exists(temp_cache_dir)

    def test_cache_pdf_successfully(self, pdf_cache_manager, mock_pdf_content):
        """Test successfully caching a PDF with metadata."""
        if PDFCacheManager is None:
            pytest.fail("PDFCacheManager not implemented yet - TDD RED phase")

        url = "https://mobimag.co/wteg/portland/restaurant_guide.pdf"
        cache_key = pdf_cache_manager.get_cache_key(url)
        
        result = pdf_cache_manager.cache_pdf(cache_key, mock_pdf_content, expiry_hours=24)
        
        assert result is True
        assert pdf_cache_manager.is_cached(cache_key) is True
        assert pdf_cache_manager.get_cached_content(cache_key) == mock_pdf_content
        assert pdf_cache_manager.get_expiry(cache_key) > time.time()

    def test_get_cache_key_from_url(self, pdf_cache_manager):
        """Test cache key generation from URL."""
        if PDFCacheManager is None:
            pytest.fail("PDFCacheManager not implemented yet - TDD RED phase")

        url = "https://mobimag.co/wteg/portland/restaurant_guide.pdf"
        cache_key = pdf_cache_manager.get_cache_key(url)
        
        # Cache key should be deterministic and safe for filesystem
        assert cache_key is not None
        assert len(cache_key) > 0
        assert cache_key == pdf_cache_manager.get_cache_key(url)  # Deterministic
        assert "/" not in cache_key  # Safe for filesystem
        assert "?" not in cache_key  # URL parameters handled

    def test_retrieve_cached_pdf(self, pdf_cache_manager, mock_pdf_content):
        """Test retrieving cached PDF content."""
        if PDFCacheManager is None:
            pytest.fail("PDFCacheManager not implemented yet - TDD RED phase")

        url = "https://mobimag.co/wteg/portland/restaurant_guide.pdf"
        cache_key = pdf_cache_manager.get_cache_key(url)
        
        # Cache the PDF
        pdf_cache_manager.cache_pdf(cache_key, mock_pdf_content, expiry_hours=24)
        
        # Retrieve it
        retrieved_content = pdf_cache_manager.get_cached_content(cache_key)
        
        assert retrieved_content == mock_pdf_content
        assert pdf_cache_manager.is_cached(cache_key) is True

    def test_cache_expiration_check(self, pdf_cache_manager, mock_pdf_content):
        """Test cache expiration checking."""
        if PDFCacheManager is None:
            pytest.fail("PDFCacheManager not implemented yet - TDD RED phase")

        url = "https://mobimag.co/wteg/portland/restaurant_guide.pdf"
        cache_key = pdf_cache_manager.get_cache_key(url)
        
        # Cache with past expiry time (negative hours)
        pdf_cache_manager.cache_pdf(cache_key, mock_pdf_content, expiry_hours=-1)
        
        assert pdf_cache_manager.is_cached(cache_key) is True  # File exists
        assert pdf_cache_manager.is_expired(cache_key) is True  # But expired
        
        # Should return None for expired content
        retrieved_content = pdf_cache_manager.get_cached_content(cache_key)
        assert retrieved_content is None

    def test_clear_expired_cache(self, pdf_cache_manager, mock_pdf_content):
        """Test clearing expired cache entries."""
        if PDFCacheManager is None:
            pytest.fail("PDFCacheManager not implemented yet - TDD RED phase")

        url = "https://mobimag.co/wteg/portland/restaurant_guide.pdf"
        cache_key = pdf_cache_manager.get_cache_key(url)
        
        # Cache with past expiry time
        pdf_cache_manager.cache_pdf(cache_key, mock_pdf_content, expiry_hours=-1)
        assert pdf_cache_manager.is_cached(cache_key) is True
        
        # Clear expired entries
        cleared_count = pdf_cache_manager.clear_expired()
        
        assert cleared_count == 1
        assert pdf_cache_manager.is_cached(cache_key) is False

    def test_cache_size_management(self, pdf_cache_manager, mock_pdf_content):
        """Test cache size limits and eviction."""
        if PDFCacheManager is None:
            pytest.fail("PDFCacheManager not implemented yet - TDD RED phase")

        # Create multiple large cache entries to exceed limit
        large_content = mock_pdf_content * 1000  # Make it larger
        
        # Cache multiple files
        for i in range(5):
            url = f"https://mobimag.co/wteg/portland/guide_{i}.pdf"
            cache_key = pdf_cache_manager.get_cache_key(url)
            pdf_cache_manager.cache_pdf(cache_key, large_content, expiry_hours=24)
        
        # Check that cache size is managed
        stats = pdf_cache_manager.get_cache_stats()
        assert stats.current_size_mb <= pdf_cache_manager.max_cache_size_mb
        assert stats.evictions_performed > 0

    def test_lru_eviction_policy(self, pdf_cache_manager, mock_pdf_content):
        """Test LRU (Least Recently Used) eviction policy."""
        if PDFCacheManager is None:
            pytest.fail("PDFCacheManager not implemented yet - TDD RED phase")

        # Cache three files
        urls = [
            "https://mobimag.co/wteg/portland/guide_1.pdf",
            "https://mobimag.co/wteg/portland/guide_2.pdf", 
            "https://mobimag.co/wteg/portland/guide_3.pdf"
        ]
        
        cache_keys = []
        for url in urls:
            cache_key = pdf_cache_manager.get_cache_key(url)
            cache_keys.append(cache_key)
            pdf_cache_manager.cache_pdf(cache_key, mock_pdf_content, expiry_hours=24)
        
        # Access first file to make it recently used
        pdf_cache_manager.get_cached_content(cache_keys[0])
        
        # Force eviction by adding large file
        large_content = mock_pdf_content * 2000
        new_url = "https://mobimag.co/wteg/portland/large_guide.pdf"
        new_cache_key = pdf_cache_manager.get_cache_key(new_url)
        pdf_cache_manager.cache_pdf(new_cache_key, large_content, expiry_hours=24)
        
        # First file should still be cached (recently accessed)
        # Second file should be evicted (least recently used)
        assert pdf_cache_manager.is_cached(cache_keys[0]) is True
        assert pdf_cache_manager.is_cached(cache_keys[1]) is False

    def test_cache_stats_tracking(self, pdf_cache_manager, mock_pdf_content):
        """Test cache statistics tracking."""
        if PDFCacheManager is None:
            pytest.fail("PDFCacheManager not implemented yet - TDD RED phase")

        # Perform various cache operations
        url = "https://mobimag.co/wteg/portland/restaurant_guide.pdf"
        cache_key = pdf_cache_manager.get_cache_key(url)
        
        # Cache hit/miss tracking
        pdf_cache_manager.get_cached_content(cache_key)  # Miss
        pdf_cache_manager.cache_pdf(cache_key, mock_pdf_content, expiry_hours=24)
        pdf_cache_manager.get_cached_content(cache_key)  # Hit
        
        stats = pdf_cache_manager.get_cache_stats()
        
        assert isinstance(stats, CacheStats)
        assert stats.cache_hits >= 1
        assert stats.cache_misses >= 1
        assert stats.total_entries >= 1
        assert stats.current_size_mb > 0

    def test_concurrent_cache_operations(self, pdf_cache_manager, mock_pdf_content):
        """Test thread-safe concurrent cache operations."""
        if PDFCacheManager is None:
            pytest.fail("PDFCacheManager not implemented yet - TDD RED phase")

        import threading
        import time
        
        results = []
        errors = []
        
        def cache_operation(thread_id):
            try:
                url = f"https://mobimag.co/wteg/portland/guide_{thread_id}.pdf"
                cache_key = pdf_cache_manager.get_cache_key(url)
                
                # Cache PDF
                success = pdf_cache_manager.cache_pdf(cache_key, mock_pdf_content, expiry_hours=24)
                
                # Retrieve PDF
                content = pdf_cache_manager.get_cached_content(cache_key)
                
                results.append({
                    'thread_id': thread_id,
                    'cache_success': success,
                    'retrieve_success': content == mock_pdf_content
                })
            except Exception as e:
                errors.append({'thread_id': thread_id, 'error': str(e)})
        
        # Run concurrent operations
        threads = []
        for i in range(5):
            thread = threading.Thread(target=cache_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify no errors and all operations succeeded
        assert len(errors) == 0
        assert len(results) == 5
        for result in results:
            assert result['cache_success'] is True
            assert result['retrieve_success'] is True

    def test_cache_integrity_validation(self, pdf_cache_manager, mock_pdf_content):
        """Test cache integrity validation."""
        if PDFCacheManager is None:
            pytest.fail("PDFCacheManager not implemented yet - TDD RED phase")

        url = "https://mobimag.co/wteg/portland/restaurant_guide.pdf"
        cache_key = pdf_cache_manager.get_cache_key(url)
        
        # Cache PDF with checksum
        pdf_cache_manager.cache_pdf(cache_key, mock_pdf_content, expiry_hours=24)
        
        # Verify integrity
        is_valid = pdf_cache_manager.validate_cache_integrity(cache_key)
        assert is_valid is True
        
        # Simulate corruption by modifying cached file
        cache_file_path = pdf_cache_manager._get_cache_file_path(cache_key)
        with open(cache_file_path, 'wb') as f:
            f.write(b'corrupted data')
        
        # Integrity check should fail
        is_valid = pdf_cache_manager.validate_cache_integrity(cache_key)
        assert is_valid is False

    def test_cache_metadata_storage(self, pdf_cache_manager, mock_pdf_content):
        """Test cache metadata storage and retrieval."""
        if PDFCacheManager is None:
            pytest.fail("PDFCacheManager not implemented yet - TDD RED phase")

        url = "https://mobimag.co/wteg/portland/restaurant_guide.pdf"
        cache_key = pdf_cache_manager.get_cache_key(url)
        
        # Cache with metadata
        metadata = {
            'source_url': url,
            'content_type': 'application/pdf',
            'download_timestamp': time.time(),
            'file_size': len(mock_pdf_content)
        }
        
        pdf_cache_manager.cache_pdf(cache_key, mock_pdf_content, expiry_hours=24, metadata=metadata)
        
        # Retrieve metadata
        retrieved_metadata = pdf_cache_manager.get_cache_metadata(cache_key)
        
        assert retrieved_metadata['source_url'] == url
        assert retrieved_metadata['content_type'] == 'application/pdf'
        assert retrieved_metadata['file_size'] == len(mock_pdf_content)

    def test_cache_cleanup_on_shutdown(self, pdf_cache_manager, mock_pdf_content):
        """Test cache cleanup when manager is shut down."""
        if PDFCacheManager is None:
            pytest.fail("PDFCacheManager not implemented yet - TDD RED phase")

        # Cache some files
        for i in range(3):
            url = f"https://mobimag.co/wteg/portland/guide_{i}.pdf"
            cache_key = pdf_cache_manager.get_cache_key(url)
            pdf_cache_manager.cache_pdf(cache_key, mock_pdf_content, expiry_hours=24)
        
        # Set to clean up expired files on shutdown
        pdf_cache_manager.cleanup_on_shutdown = True
        
        # Expire one file
        expired_url = "https://mobimag.co/wteg/portland/guide_0.pdf"
        expired_key = pdf_cache_manager.get_cache_key(expired_url)
        pdf_cache_manager._set_expiry(expired_key, time.time() - 3600)  # 1 hour ago
        
        # Trigger shutdown cleanup
        pdf_cache_manager.shutdown()
        
        # Expired file should be cleaned up
        assert pdf_cache_manager.is_cached(expired_key) is False

    def test_cache_directory_permissions(self, temp_cache_dir):
        """Test cache directory permissions and access."""
        if PDFCacheManager is None:
            pytest.fail("PDFCacheManager not implemented yet - TDD RED phase")

        # Test with read-only directory (should fail gracefully)
        readonly_dir = os.path.join(temp_cache_dir, "readonly")
        os.makedirs(readonly_dir)
        os.chmod(readonly_dir, 0o444)  # Read-only
        
        try:
            cache_manager = PDFCacheManager(
                cache_dir=readonly_dir,
                max_cache_size_mb=10,
                default_expiry_hours=24
            )
            
            # Should handle permission error gracefully
            with pytest.raises(PermissionError):
                cache_key = cache_manager.get_cache_key("https://example.com/test.pdf")
                cache_manager.cache_pdf(cache_key, b'test', expiry_hours=1)
        
        finally:
            # Restore permissions for cleanup
            os.chmod(readonly_dir, 0o755)

    def test_cache_entry_creation(self, mock_pdf_content):
        """Test CacheEntry creation and attributes."""
        if CacheEntry is None:
            pytest.fail("CacheEntry not implemented yet - TDD RED phase")

        entry = CacheEntry(
            cache_key="test_key",
            content=mock_pdf_content,
            expiry_time=time.time() + 3600,
            metadata={'source_url': 'https://example.com/test.pdf'},
            checksum=hashlib.md5(mock_pdf_content).hexdigest()
        )
        
        assert entry.cache_key == "test_key"
        assert entry.content == mock_pdf_content
        assert entry.expiry_time > time.time()
        assert entry.metadata['source_url'] == 'https://example.com/test.pdf'
        assert entry.checksum == hashlib.md5(mock_pdf_content).hexdigest()

    def test_cache_stats_creation(self):
        """Test CacheStats creation and attributes."""
        if CacheStats is None:
            pytest.fail("CacheStats not implemented yet - TDD RED phase")

        stats = CacheStats(
            cache_hits=10,
            cache_misses=5,
            total_entries=8,
            current_size_mb=25.5,
            evictions_performed=2,
            expired_entries_cleared=3
        )
        
        assert stats.cache_hits == 10
        assert stats.cache_misses == 5
        assert stats.total_entries == 8
        assert stats.current_size_mb == 25.5
        assert stats.evictions_performed == 2
        assert stats.expired_entries_cleared == 3
        assert stats.hit_rate == 10 / (10 + 5)  # 0.667

    def test_cache_key_collision_handling(self, pdf_cache_manager, mock_pdf_content):
        """Test handling of cache key collisions."""
        if PDFCacheManager is None:
            pytest.fail("PDFCacheManager not implemented yet - TDD RED phase")

        # URLs that might generate similar cache keys
        url1 = "https://mobimag.co/wteg/portland/guide.pdf"
        url2 = "https://mobimag.co/wteg/portland/guide.pdf?version=2"
        
        cache_key1 = pdf_cache_manager.get_cache_key(url1)
        cache_key2 = pdf_cache_manager.get_cache_key(url2)
        
        # Cache keys should be different to avoid collisions
        assert cache_key1 != cache_key2
        
        # Both should be cacheable independently
        pdf_cache_manager.cache_pdf(cache_key1, mock_pdf_content, expiry_hours=24)
        pdf_cache_manager.cache_pdf(cache_key2, mock_pdf_content + b'_v2', expiry_hours=24)
        
        content1 = pdf_cache_manager.get_cached_content(cache_key1)
        content2 = pdf_cache_manager.get_cached_content(cache_key2)
        
        assert content1 == mock_pdf_content
        assert content2 == mock_pdf_content + b'_v2'