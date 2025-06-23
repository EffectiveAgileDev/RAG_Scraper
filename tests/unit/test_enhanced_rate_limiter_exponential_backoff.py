"""Unit tests for exponential backoff functionality."""
import time
import pytest
from unittest.mock import Mock, patch


class TestExponentialBackoff:
    """Test exponential backoff functionality."""

    def test_create_enhanced_rate_limiter_with_backoff_support(self):
        """Test creation of enhanced rate limiter with exponential backoff support."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(
            default_delay=1.0, 
            exponential_backoff_enabled=True,
            base_backoff_delay=1.0,
            max_backoff_delay=60.0,
            backoff_multiplier=2.0
        )
        
        assert limiter.exponential_backoff_enabled is True
        assert limiter.base_backoff_delay == 1.0
        assert limiter.max_backoff_delay == 60.0
        assert limiter.backoff_multiplier == 2.0
        assert hasattr(limiter, 'domain_retry_counts')
        assert isinstance(limiter.domain_retry_counts, dict)

    def test_exponential_backoff_calculation(self):
        """Test exponential backoff delay calculation."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(
            exponential_backoff_enabled=True,
            base_backoff_delay=1.0,
            backoff_multiplier=2.0
        )
        
        # Test backoff delay calculation for different retry counts
        assert limiter._calculate_backoff_delay(0) == 1.0  # 1.0 * (2^0)
        assert limiter._calculate_backoff_delay(1) == 2.0  # 1.0 * (2^1)
        assert limiter._calculate_backoff_delay(2) == 4.0  # 1.0 * (2^2)
        assert limiter._calculate_backoff_delay(3) == 8.0  # 1.0 * (2^3)
        assert limiter._calculate_backoff_delay(4) == 16.0  # 1.0 * (2^4)

    def test_exponential_backoff_max_delay_cap(self):
        """Test that exponential backoff respects maximum delay cap."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(
            exponential_backoff_enabled=True,
            base_backoff_delay=1.0,
            max_backoff_delay=10.0,
            backoff_multiplier=2.0
        )
        
        # Higher retry counts should be capped at max_backoff_delay
        assert limiter._calculate_backoff_delay(5) == 10.0  # Would be 32.0, but capped
        assert limiter._calculate_backoff_delay(10) == 10.0  # Would be 1024.0, but capped

    def test_apply_exponential_backoff_for_failed_request(self):
        """Test applying exponential backoff for failed requests."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(
            exponential_backoff_enabled=True,
            base_backoff_delay=0.1,  # Small delay for testing
            backoff_multiplier=2.0
        )
        
        domain = 'example.com'
        
        # First failure should use base delay
        start_time = time.time()
        actual_wait = limiter.apply_exponential_backoff(domain)
        elapsed = time.time() - start_time
        
        assert actual_wait >= 0.09  # Should wait ~0.1 seconds
        assert elapsed >= 0.09
        assert limiter.domain_retry_counts[domain] == 1

    def test_exponential_backoff_progression(self):
        """Test that exponential backoff increases delay with each failure."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(
            exponential_backoff_enabled=True,
            base_backoff_delay=0.1,
            backoff_multiplier=2.0
        )
        
        domain = 'failing-site.com'
        
        # First failure: 0.1 seconds
        wait1 = limiter.apply_exponential_backoff(domain)
        assert 0.09 <= wait1 <= 0.11
        
        # Second failure: 0.2 seconds
        wait2 = limiter.apply_exponential_backoff(domain)
        assert 0.19 <= wait2 <= 0.21
        
        # Third failure: 0.4 seconds
        wait3 = limiter.apply_exponential_backoff(domain)
        assert 0.39 <= wait3 <= 0.41
        
        # Verify retry counts are tracked
        assert limiter.domain_retry_counts[domain] == 3

    def test_reset_exponential_backoff_on_success(self):
        """Test that exponential backoff resets on successful request."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(
            exponential_backoff_enabled=True,
            base_backoff_delay=0.1
        )
        
        domain = 'recovery-site.com'
        
        # Simulate several failures
        limiter.apply_exponential_backoff(domain)
        limiter.apply_exponential_backoff(domain)
        limiter.apply_exponential_backoff(domain)
        
        assert limiter.domain_retry_counts[domain] == 3
        
        # Reset on success
        limiter.reset_exponential_backoff(domain)
        
        assert limiter.domain_retry_counts.get(domain, 0) == 0

    def test_exponential_backoff_disabled_behavior(self):
        """Test behavior when exponential backoff is disabled."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(exponential_backoff_enabled=False)
        
        domain = 'example.com'
        
        # Should return 0 when disabled
        wait_time = limiter.apply_exponential_backoff(domain)
        assert wait_time == 0.0
        assert domain not in limiter.domain_retry_counts

    def test_exponential_backoff_per_domain_isolation(self):
        """Test that exponential backoff is isolated per domain."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(
            exponential_backoff_enabled=True,
            base_backoff_delay=0.1
        )
        
        domain1 = 'site1.com'
        domain2 = 'site2.com'
        
        # Apply backoff to domain1 multiple times
        limiter.apply_exponential_backoff(domain1)
        limiter.apply_exponential_backoff(domain1)
        limiter.apply_exponential_backoff(domain1)
        
        # domain1 should have 3 retries
        assert limiter.domain_retry_counts[domain1] == 3
        
        # domain2 should be unaffected (first failure should use base delay)
        wait_time = limiter.apply_exponential_backoff(domain2)
        assert 0.09 <= wait_time <= 0.11
        assert limiter.domain_retry_counts[domain2] == 1

    def test_exponential_backoff_with_custom_multiplier(self):
        """Test exponential backoff with custom multiplier."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(
            exponential_backoff_enabled=True,
            base_backoff_delay=1.0,
            backoff_multiplier=3.0  # Triple each time instead of double
        )
        
        domain = 'custom-multiplier.com'
        
        # Test custom multiplier progression
        assert limiter._calculate_backoff_delay(0) == 1.0  # 1.0 * (3^0)
        assert limiter._calculate_backoff_delay(1) == 3.0  # 1.0 * (3^1)
        assert limiter._calculate_backoff_delay(2) == 9.0  # 1.0 * (3^2)
        assert limiter._calculate_backoff_delay(3) == 27.0  # 1.0 * (3^3)

    def test_exponential_backoff_configuration_validation(self):
        """Test validation of exponential backoff configuration."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        # Valid configuration should work
        limiter = EnhancedRateLimiter(
            exponential_backoff_enabled=True,
            base_backoff_delay=1.0,
            max_backoff_delay=60.0,
            backoff_multiplier=2.0
        )
        
        # Invalid base delay should raise error
        with pytest.raises(ValueError, match="Base backoff delay must be positive"):
            EnhancedRateLimiter(
                exponential_backoff_enabled=True,
                base_backoff_delay=0.0
            )
        
        # Invalid max delay should raise error
        with pytest.raises(ValueError, match="Max backoff delay must be positive"):
            EnhancedRateLimiter(
                exponential_backoff_enabled=True,
                max_backoff_delay=0.0
            )
        
        # Invalid multiplier should raise error
        with pytest.raises(ValueError, match="Backoff multiplier must be greater than 1"):
            EnhancedRateLimiter(
                exponential_backoff_enabled=True,
                backoff_multiplier=1.0
            )

    def test_exponential_backoff_statistics(self):
        """Test statistics tracking for exponential backoff."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(
            exponential_backoff_enabled=True,
            base_backoff_delay=0.1
        )
        
        domain = 'stats-domain.com'
        
        # Apply backoff several times
        limiter.apply_exponential_backoff(domain)
        limiter.apply_exponential_backoff(domain)
        limiter.apply_exponential_backoff(domain)
        
        # Get backoff statistics
        stats = limiter.get_exponential_backoff_statistics(domain)
        
        assert 'total_backoff_applications' in stats
        assert 'current_retry_count' in stats
        assert 'total_backoff_time' in stats
        assert stats['total_backoff_applications'] == 3
        assert stats['current_retry_count'] == 3
        assert stats['total_backoff_time'] >= 0.6  # 0.1 + 0.2 + 0.4

    def test_reset_all_exponential_backoffs(self):
        """Test resetting all exponential backoff states."""
        from src.scraper.rate_limiter import EnhancedRateLimiter
        
        limiter = EnhancedRateLimiter(
            exponential_backoff_enabled=True,
            base_backoff_delay=0.1
        )
        
        # Apply backoff to multiple domains
        limiter.apply_exponential_backoff('domain1.com')
        limiter.apply_exponential_backoff('domain1.com')
        limiter.apply_exponential_backoff('domain2.com')
        
        assert len(limiter.domain_retry_counts) == 2
        
        # Reset all
        limiter.reset_all_exponential_backoffs()
        
        assert len(limiter.domain_retry_counts) == 0