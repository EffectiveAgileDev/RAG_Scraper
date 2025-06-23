"""Unit tests for retry-after headers support functionality."""
import time
import pytest
from unittest.mock import Mock, patch


class TestRetryAfterSupport:
    """Test retry-after headers support functionality."""

    def test_create_enhanced_rate_limiter_with_retry_after_support(self):
        """Test creation of enhanced rate limiter with retry-after support."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(
            default_delay=1.0,
            retry_after_enabled=True
        )
        
        assert limiter.retry_after_enabled is True
        assert hasattr(limiter, 'domain_retry_after_delays')
        assert isinstance(limiter.domain_retry_after_delays, dict)

    def test_parse_retry_after_header_seconds(self):
        """Test parsing retry-after header with seconds value."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(retry_after_enabled=True)
        
        # Test parsing seconds value
        delay = limiter._parse_retry_after_header("10")
        assert delay == 10.0
        
        delay = limiter._parse_retry_after_header("120")
        assert delay == 120.0

    def test_parse_retry_after_header_http_date(self):
        """Test parsing retry-after header with HTTP date value."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(retry_after_enabled=True)
        
        # Mock current time for consistent testing
        with patch('time.time') as mock_time:
            mock_time.return_value = 1640000000.0  # Fixed timestamp
            
            # HTTP date format: "Wed, 21 Oct 2015 07:28:00 GMT"
            # This should calculate the difference from current time
            future_date = "Wed, 20 Dec 2024 10:00:00 GMT"
            delay = limiter._parse_retry_after_header(future_date)
            
            # Should return a positive delay (exact value depends on date parsing)
            assert isinstance(delay, float)
            assert delay >= 0

    def test_parse_retry_after_header_invalid(self):
        """Test parsing invalid retry-after header values."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(retry_after_enabled=True)
        
        # Invalid values should return None
        assert limiter._parse_retry_after_header("invalid") is None
        assert limiter._parse_retry_after_header("") is None
        assert limiter._parse_retry_after_header("-10") is None

    def test_apply_retry_after_delay(self):
        """Test applying retry-after delay for a domain."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(retry_after_enabled=True)
        
        domain = 'example.com'
        retry_after_delay = 0.1  # Small delay for testing
        
        # Apply retry-after delay
        start_time = time.time()
        actual_wait = limiter.apply_retry_after_delay(domain, retry_after_delay)
        elapsed = time.time() - start_time
        
        assert actual_wait >= 0.09
        assert elapsed >= 0.09
        assert limiter.domain_retry_after_delays[domain] == retry_after_delay

    def test_retry_after_overrides_normal_rate_limiting(self):
        """Test that retry-after delay overrides normal rate limiting."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(
            default_delay=2.0,  # Normal delay
            retry_after_enabled=True
        )
        
        domain = 'example.com'
        url = f'http://{domain}/page'
        
        # First request - normal rate limiting
        limiter.wait_if_needed(url)
        
        # Apply retry-after delay (shorter than normal delay)
        retry_after_delay = 0.1
        limiter.apply_retry_after_delay(domain, retry_after_delay)
        
        # Next request should use retry-after delay instead of normal delay
        start_time = time.time()
        wait_time = limiter.wait_if_needed_with_retry_after(url)
        elapsed = time.time() - start_time
        
        # Should use retry-after delay (~0.1s) not normal delay (~2.0s)
        assert wait_time >= 0.09
        assert wait_time <= 0.2
        assert elapsed >= 0.09
        assert elapsed <= 0.2

    def test_retry_after_clears_after_use(self):
        """Test that retry-after delay is cleared after use."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(
            default_delay=0.1,
            retry_after_enabled=True
        )
        
        domain = 'example.com'
        url = f'http://{domain}/page'
        
        # Apply retry-after delay
        limiter.apply_retry_after_delay(domain, 0.2)
        assert domain in limiter.domain_retry_after_delays
        
        # Use retry-after delay
        limiter.wait_if_needed_with_retry_after(url)
        
        # Should be cleared after use
        assert domain not in limiter.domain_retry_after_delays

    def test_retry_after_disabled_behavior(self):
        """Test behavior when retry-after support is disabled."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(retry_after_enabled=False)
        
        domain = 'example.com'
        
        # Should return 0 when disabled
        wait_time = limiter.apply_retry_after_delay(domain, 10.0)
        assert wait_time == 0.0
        assert domain not in limiter.domain_retry_after_delays

    def test_retry_after_per_domain_isolation(self):
        """Test that retry-after delays are isolated per domain."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(
            default_delay=0.1,
            retry_after_enabled=True
        )
        
        domain1 = 'site1.com'
        domain2 = 'site2.com'
        
        # Apply different retry-after delays to different domains
        limiter.apply_retry_after_delay(domain1, 0.2)
        limiter.apply_retry_after_delay(domain2, 0.3)
        
        assert limiter.domain_retry_after_delays[domain1] == 0.2
        assert limiter.domain_retry_after_delays[domain2] == 0.3
        
        # Use retry-after for domain1
        url1 = f'http://{domain1}/page'
        start_time = time.time()
        limiter.wait_if_needed_with_retry_after(url1)
        elapsed1 = time.time() - start_time
        
        # domain1 should be cleared, domain2 should remain
        assert domain1 not in limiter.domain_retry_after_delays
        assert limiter.domain_retry_after_delays[domain2] == 0.3
        assert 0.19 <= elapsed1 <= 0.21

    def test_retry_after_max_delay_cap(self):
        """Test that retry-after delays respect maximum delay cap."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(
            retry_after_enabled=True,
            max_retry_after_delay=5.0  # Cap at 5 seconds
        )
        
        domain = 'example.com'
        
        # Try to apply a very large retry-after delay
        actual_wait = limiter.apply_retry_after_delay(domain, 3600.0)  # 1 hour
        
        # Should be capped at max_retry_after_delay
        assert actual_wait <= 5.1  # Allow small timing variance
        assert limiter.domain_retry_after_delays[domain] <= 5.0

    def test_wait_if_needed_with_retry_after_fallback(self):
        """Test fallback to normal rate limiting when no retry-after is set."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(
            default_delay=0.1,
            retry_after_enabled=True
        )
        
        domain = 'example.com'
        url = f'http://{domain}/page'
        
        # First request - no retry-after delay set
        start_time = time.time()
        limiter.wait_if_needed_with_retry_after(url)
        first_elapsed = time.time() - start_time
        
        # Second request - should use normal rate limiting
        start_time = time.time()
        wait_time = limiter.wait_if_needed_with_retry_after(url)
        elapsed = time.time() - start_time
        
        assert first_elapsed < 0.05  # First request immediate
        assert wait_time >= 0.09  # Second request uses normal delay
        assert elapsed >= 0.09

    def test_get_retry_after_statistics(self):
        """Test getting retry-after statistics for a domain."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(retry_after_enabled=True)
        
        domain = 'stats-domain.com'
        
        # Apply retry-after delays multiple times
        limiter.apply_retry_after_delay(domain, 1.0)
        limiter.apply_retry_after_delay(domain, 2.0)
        limiter.apply_retry_after_delay(domain, 3.0)
        
        # Get statistics
        stats = limiter.get_retry_after_statistics(domain)
        
        assert 'total_retry_after_applications' in stats
        assert 'total_retry_after_time' in stats
        assert 'current_retry_after_delay' in stats
        assert stats['total_retry_after_applications'] == 3
        assert stats['total_retry_after_time'] >= 5.9  # 1.0 + 2.0 + 3.0
        assert stats['current_retry_after_delay'] == 3.0

    def test_reset_retry_after_delay(self):
        """Test resetting retry-after delay for a domain."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(retry_after_enabled=True)
        
        domain = 'example.com'
        
        # Apply retry-after delay
        limiter.apply_retry_after_delay(domain, 10.0)
        assert domain in limiter.domain_retry_after_delays
        
        # Reset retry-after delay
        limiter.reset_retry_after_delay(domain)
        assert domain not in limiter.domain_retry_after_delays

    def test_reset_all_retry_after_delays(self):
        """Test resetting all retry-after delays."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(retry_after_enabled=True)
        
        # Apply retry-after delays to multiple domains
        limiter.apply_retry_after_delay('domain1.com', 1.0)
        limiter.apply_retry_after_delay('domain2.com', 2.0)
        limiter.apply_retry_after_delay('domain3.com', 3.0)
        
        assert len(limiter.domain_retry_after_delays) == 3
        
        # Reset all
        limiter.reset_all_retry_after_delays()
        
        assert len(limiter.domain_retry_after_delays) == 0

    def test_retry_after_configuration_validation(self):
        """Test validation of retry-after configuration."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        # Valid configuration should work
        limiter = EnhancedRateLimiter(
            retry_after_enabled=True,
            max_retry_after_delay=300.0
        )
        
        # Invalid max delay should raise error
        with pytest.raises(ValueError, match="Max retry-after delay must be positive"):
            EnhancedRateLimiter(
                retry_after_enabled=True,
                max_retry_after_delay=0.0
            )