"""Unit tests for per-domain rate limiting functionality."""
import time
import pytest
from unittest.mock import Mock, patch
from urllib.parse import urlparse


class TestPerDomainRateLimiting:
    """Test per-domain rate limiting functionality."""

    def test_create_enhanced_rate_limiter_with_domain_support(self):
        """Test creation of enhanced rate limiter with per-domain support."""
        from src.scraper.rate_limiter import EnhancedRateLimiter

        limiter = EnhancedRateLimiter(default_delay=2.0, per_domain_enabled=True)

        assert limiter.default_delay == 2.0
        assert limiter.per_domain_enabled is True
        assert hasattr(limiter, "domain_limiters")
        assert isinstance(limiter.domain_limiters, dict)

    def test_per_domain_rate_limiting_different_domains(self):
        """Test that different domains are rate limited independently."""
        from src.scraper.rate_limiter import EnhancedRateLimiter

        limiter = EnhancedRateLimiter(default_delay=1.0, per_domain_enabled=True)

        # Configure different delays for different domains
        limiter.configure_domain_delay("fast-domain.com", 0.1)
        limiter.configure_domain_delay("slow-domain.com", 2.0)

        # First request to fast domain should be immediate
        start_time = time.time()
        wait_time = limiter.wait_if_needed("http://fast-domain.com/page1")
        first_elapsed = time.time() - start_time

        assert wait_time == 0.0
        assert first_elapsed < 0.05

        # First request to slow domain should also be immediate
        start_time = time.time()
        wait_time = limiter.wait_if_needed("http://slow-domain.com/page1")
        first_elapsed = time.time() - start_time

        assert wait_time == 0.0
        assert first_elapsed < 0.05

        # Second request to fast domain should wait 0.1 seconds
        start_time = time.time()
        wait_time = limiter.wait_if_needed("http://fast-domain.com/page2")
        second_elapsed = time.time() - start_time

        assert wait_time >= 0.09
        assert second_elapsed >= 0.09

        # Second request to slow domain should wait 2.0 seconds
        start_time = time.time()
        wait_time = limiter.wait_if_needed("http://slow-domain.com/page2")
        third_elapsed = time.time() - start_time

        assert wait_time >= 1.8
        assert third_elapsed >= 1.8

    def test_extract_domain_from_url(self):
        """Test domain extraction from URLs."""
        from src.scraper.rate_limiter import EnhancedRateLimiter

        limiter = EnhancedRateLimiter()

        assert limiter._extract_domain("http://example.com/path") == "example.com"
        assert (
            limiter._extract_domain("https://sub.example.com/path") == "sub.example.com"
        )
        assert limiter._extract_domain("https://example.com:8080/path") == "example.com"
        assert (
            limiter._extract_domain("ftp://files.example.com/file")
            == "files.example.com"
        )

    def test_configure_domain_delay(self):
        """Test configuring domain-specific delays."""
        from src.scraper.rate_limiter import EnhancedRateLimiter

        limiter = EnhancedRateLimiter(per_domain_enabled=True)

        # Configure delays for specific domains
        limiter.configure_domain_delay("fast.com", 0.5)
        limiter.configure_domain_delay("slow.com", 3.0)

        # Verify domain configurations are stored
        assert "fast.com" in limiter.domain_configs
        assert "slow.com" in limiter.domain_configs
        assert limiter.domain_configs["fast.com"]["delay"] == 0.5
        assert limiter.domain_configs["slow.com"]["delay"] == 3.0

    def test_get_domain_limiter(self):
        """Test getting domain-specific rate limiter."""
        from src.scraper.rate_limiter import EnhancedRateLimiter

        limiter = EnhancedRateLimiter(per_domain_enabled=True)
        limiter.configure_domain_delay("example.com", 1.5)

        # Get domain limiter
        domain_limiter = limiter._get_domain_limiter("example.com")

        # Should return a RateLimiter with configured delay
        assert domain_limiter.delay == 1.5

        # Same domain should return same limiter instance
        same_limiter = limiter._get_domain_limiter("example.com")
        assert domain_limiter is same_limiter

    def test_default_delay_for_unconfigured_domain(self):
        """Test that unconfigured domains use default delay."""
        from src.scraper.rate_limiter import EnhancedRateLimiter

        limiter = EnhancedRateLimiter(default_delay=2.0, per_domain_enabled=True)

        # Get limiter for unconfigured domain
        domain_limiter = limiter._get_domain_limiter("unknown.com")

        # Should use default delay
        assert domain_limiter.delay == 2.0

    def test_per_domain_disabled_uses_single_limiter(self):
        """Test that when per-domain is disabled, single limiter is used."""
        from src.scraper.rate_limiter import EnhancedRateLimiter

        limiter = EnhancedRateLimiter(default_delay=1.0, per_domain_enabled=False)

        # First request to any domain
        start_time = time.time()
        limiter.wait_if_needed("http://domain1.com/page")
        first_elapsed = time.time() - start_time

        # Second request to different domain should still be rate limited
        start_time = time.time()
        limiter.wait_if_needed("http://domain2.com/page")
        second_elapsed = time.time() - start_time

        assert first_elapsed < 0.05  # First request immediate
        assert second_elapsed >= 0.9  # Second request delayed

    def test_domain_limiter_isolation(self):
        """Test that domain limiters are isolated from each other."""
        from src.scraper.rate_limiter import EnhancedRateLimiter

        limiter = EnhancedRateLimiter(per_domain_enabled=True)
        limiter.configure_domain_delay("domain1.com", 0.1)
        limiter.configure_domain_delay("domain2.com", 0.1)

        # Make requests to domain1
        limiter.wait_if_needed("http://domain1.com/page1")
        time.sleep(0.05)  # Wait half the delay period

        # Request to domain2 should be immediate (not affected by domain1)
        start_time = time.time()
        wait_time = limiter.wait_if_needed("http://domain2.com/page1")
        elapsed = time.time() - start_time

        assert wait_time == 0.0
        assert elapsed < 0.05

    def test_reset_domain_limiter(self):
        """Test resetting specific domain limiter."""
        from src.scraper.rate_limiter import EnhancedRateLimiter

        limiter = EnhancedRateLimiter(per_domain_enabled=True)
        limiter.configure_domain_delay("example.com", 1.0)

        # Make a request to establish timing
        limiter.wait_if_needed("http://example.com/page1")

        # Reset the domain limiter
        limiter.reset_domain("example.com")

        # Next request should be immediate
        start_time = time.time()
        wait_time = limiter.wait_if_needed("http://example.com/page2")
        elapsed = time.time() - start_time

        assert wait_time == 0.0
        assert elapsed < 0.05

    def test_reset_all_domain_limiters(self):
        """Test resetting all domain limiters."""
        from src.scraper.rate_limiter import EnhancedRateLimiter

        limiter = EnhancedRateLimiter(per_domain_enabled=True)
        limiter.configure_domain_delay("domain1.com", 0.1)
        limiter.configure_domain_delay("domain2.com", 0.1)

        # Make requests to both domains
        limiter.wait_if_needed("http://domain1.com/page1")
        limiter.wait_if_needed("http://domain2.com/page1")

        # Reset all limiters
        limiter.reset()

        # Next requests to both domains should be immediate
        start_time = time.time()
        wait_time1 = limiter.wait_if_needed("http://domain1.com/page2")
        wait_time2 = limiter.wait_if_needed("http://domain2.com/page2")
        elapsed = time.time() - start_time

        assert wait_time1 == 0.0
        assert wait_time2 == 0.0
        assert elapsed < 0.05

    def test_domain_configuration_validation(self):
        """Test validation of domain configuration."""
        from src.scraper.rate_limiter import EnhancedRateLimiter

        limiter = EnhancedRateLimiter(per_domain_enabled=True)

        # Valid configuration should work
        limiter.configure_domain_delay("example.com", 1.0)

        # Invalid delay should raise error
        with pytest.raises(ValueError, match="Delay must be non-negative"):
            limiter.configure_domain_delay("example.com", -1.0)

        # Empty domain should raise error
        with pytest.raises(ValueError, match="Domain cannot be empty"):
            limiter.configure_domain_delay("", 1.0)

    def test_get_domain_statistics(self):
        """Test getting statistics for domain rate limiting."""
        from src.scraper.rate_limiter import EnhancedRateLimiter

        limiter = EnhancedRateLimiter(per_domain_enabled=True)
        limiter.configure_domain_delay("example.com", 0.1)

        # Make some requests
        limiter.wait_if_needed("http://example.com/page1")
        limiter.wait_if_needed("http://example.com/page2")
        limiter.wait_if_needed("http://example.com/page3")

        # Get statistics
        stats = limiter.get_domain_statistics("example.com")

        assert "total_requests" in stats
        assert "total_wait_time" in stats
        assert "average_wait_time" in stats
        assert stats["total_requests"] == 3
        assert stats["total_wait_time"] >= 0.19  # At least two delays of ~0.1s each
