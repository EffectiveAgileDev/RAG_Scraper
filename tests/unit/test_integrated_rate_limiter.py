"""Unit tests for IntegratedRateLimiter."""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import the module we're testing
try:
    from src.scraper.integrated_rate_limiter import IntegratedRateLimiter
    from src.scraper.integrated_rate_limiter import DomainRateLimiter
    from src.scraper.integrated_rate_limiter import EthicalComplianceChecker
    from src.scraper.integrated_rate_limiter import RateLimitStatistics
except ImportError:
    IntegratedRateLimiter = None
    DomainRateLimiter = None
    EthicalComplianceChecker = None
    RateLimitStatistics = None


class TestIntegratedRateLimiter:
    """Test cases for IntegratedRateLimiter."""

    def test_integrated_rate_limiter_initialization(self):
        """Test that integrated rate limiter initializes correctly."""
        if IntegratedRateLimiter is None:
            pytest.fail("IntegratedRateLimiter not implemented - TDD RED phase")
        
        limiter = IntegratedRateLimiter()
        assert limiter is not None
        assert limiter.domain_limiters is not None
        assert limiter.ethical_checker is not None
        assert limiter.rate_limit_statistics is not None

    def test_integrated_rate_limiter_initialization_with_config(self):
        """Test integrated rate limiter initialization with custom configuration."""
        if IntegratedRateLimiter is None:
            pytest.skip("IntegratedRateLimiter not implemented yet")
        
        config = {
            'default_delay': 2.0,
            'max_requests_per_minute': 30,
            'respect_robots_txt': True,
            'ethical_compliance': True,
            'per_domain_limits': {
                'example.com': {'delay': 1.0, 'max_requests': 60}
            }
        }
        
        limiter = IntegratedRateLimiter(config=config)
        assert limiter.config == config
        assert limiter.default_delay == 2.0
        assert limiter.max_requests_per_minute == 30
        assert limiter.respect_robots_txt is True

    def test_check_rate_limit_single_domain(self):
        """Test checking rate limit for single domain."""
        if IntegratedRateLimiter is None:
            pytest.skip("IntegratedRateLimiter not implemented yet")
        
        limiter = IntegratedRateLimiter()
        url = "https://test-restaurant.com/menu"
        
        with patch.object(limiter, 'domain_limiters') as mock_limiters:
            mock_domain_limiter = Mock()
            mock_domain_limiter.can_make_request.return_value = True
            mock_limiters.get_limiter.return_value = mock_domain_limiter
            
            result = limiter.check_rate_limit(url)
            
            assert result.can_proceed is True
            assert result.required_delay == 0
            mock_limiters.get_limiter.assert_called_once_with('test-restaurant.com')

    def test_check_rate_limit_with_delay_required(self):
        """Test checking rate limit when delay is required."""
        if IntegratedRateLimiter is None:
            pytest.skip("IntegratedRateLimiter not implemented yet")
        
        limiter = IntegratedRateLimiter()
        url = "https://test-restaurant.com/menu"
        
        with patch.object(limiter, 'domain_limiters') as mock_limiters:
            mock_domain_limiter = Mock()
            mock_domain_limiter.can_make_request.return_value = False
            mock_domain_limiter.get_required_delay.return_value = 3.0
            mock_limiters.get_limiter.return_value = mock_domain_limiter
            
            result = limiter.check_rate_limit(url)
            
            assert result.can_proceed is False
            assert result.required_delay == 3.0
            mock_domain_limiter.get_required_delay.assert_called_once()

    def test_apply_rate_limit_single_page_mode(self):
        """Test applying rate limit in single-page mode."""
        if IntegratedRateLimiter is None:
            pytest.skip("IntegratedRateLimiter not implemented yet")
        
        limiter = IntegratedRateLimiter()
        url = "https://test-restaurant.com"
        
        with patch.object(limiter, 'check_rate_limit') as mock_check:
            mock_check.return_value = Mock(can_proceed=False, required_delay=2.0)
            
            with patch('time.sleep') as mock_sleep:
                result = limiter.apply_rate_limit(url, mode='single_page')
                
                assert result.delay_applied is True
                assert result.delay_duration == 2.0
                mock_sleep.assert_called_once_with(2.0)

    def test_apply_rate_limit_multi_page_mode(self):
        """Test applying rate limit in multi-page mode."""
        if IntegratedRateLimiter is None:
            pytest.skip("IntegratedRateLimiter not implemented yet")
        
        limiter = IntegratedRateLimiter()
        urls = [
            "https://restaurant1.com",
            "https://restaurant2.com",
            "https://restaurant1.com/menu"  # Same domain as first
        ]
        
        with patch.object(limiter, 'check_rate_limit') as mock_check:
            # Different delays for different domains
            mock_check.side_effect = [
                Mock(can_proceed=True, required_delay=0),
                Mock(can_proceed=False, required_delay=2.0),
                Mock(can_proceed=False, required_delay=1.0)  # Same domain, shorter delay
            ]
            
            with patch('time.sleep') as mock_sleep:
                result = limiter.apply_rate_limit_batch(urls, mode='multi_page')
                
                assert result.total_delays == 2
                assert result.total_delay_time == 3.0
                assert mock_sleep.call_count == 2

    def test_check_robots_txt_compliance(self):
        """Test checking robots.txt compliance."""
        if IntegratedRateLimiter is None:
            pytest.skip("IntegratedRateLimiter not implemented yet")
        
        limiter = IntegratedRateLimiter()
        url = "https://test-restaurant.com/menu"
        
        with patch.object(limiter, 'ethical_checker') as mock_checker:
            mock_checker.check_robots_txt.return_value = Mock(
                allowed=True,
                crawl_delay=1.0,
                user_agent_allowed=True
            )
            
            result = limiter.check_robots_txt_compliance(url)
            
            assert result.allowed is True
            assert result.crawl_delay == 1.0
            assert result.user_agent_allowed is True
            mock_checker.check_robots_txt.assert_called_once_with(url)

    def test_check_robots_txt_compliance_disallowed(self):
        """Test checking robots.txt compliance when disallowed."""
        if IntegratedRateLimiter is None:
            pytest.skip("IntegratedRateLimiter not implemented yet")
        
        limiter = IntegratedRateLimiter()
        url = "https://test-restaurant.com/admin"
        
        with patch.object(limiter, 'ethical_checker') as mock_checker:
            mock_checker.check_robots_txt.return_value = Mock(
                allowed=False,
                crawl_delay=None,
                user_agent_allowed=False,
                disallow_reason="Path explicitly disallowed"
            )
            
            result = limiter.check_robots_txt_compliance(url)
            
            assert result.allowed is False
            assert result.user_agent_allowed is False
            assert result.disallow_reason == "Path explicitly disallowed"

    def test_handle_server_rate_limit_response(self):
        """Test handling server rate limit response."""
        if IntegratedRateLimiter is None:
            pytest.skip("IntegratedRateLimiter not implemented yet")
        
        limiter = IntegratedRateLimiter()
        url = "https://test-restaurant.com"
        
        # Mock HTTP 429 response with Retry-After header
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '60'}
        
        result = limiter.handle_server_rate_limit(url, mock_response)
        
        assert result.is_rate_limited is True
        assert result.retry_after == 60
        assert result.should_retry is True

    def test_handle_server_rate_limit_response_no_retry_after(self):
        """Test handling server rate limit response without Retry-After header."""
        if IntegratedRateLimiter is None:
            pytest.skip("IntegratedRateLimiter not implemented yet")
        
        limiter = IntegratedRateLimiter()
        url = "https://test-restaurant.com"
        
        # Mock HTTP 429 response without Retry-After header
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {}
        
        result = limiter.handle_server_rate_limit(url, mock_response)
        
        assert result.is_rate_limited is True
        assert result.retry_after is None
        assert result.should_retry is True
        assert result.default_delay > 0  # Should use default delay

    def test_per_domain_rate_limiting(self):
        """Test per-domain rate limiting."""
        if IntegratedRateLimiter is None:
            pytest.skip("IntegratedRateLimiter not implemented yet")
        
        config = {
            'per_domain_limits': {
                'slow-restaurant.com': {'delay': 5.0, 'max_requests': 10},
                'fast-restaurant.com': {'delay': 1.0, 'max_requests': 60}
            }
        }
        
        limiter = IntegratedRateLimiter(config=config)
        
        slow_url = "https://slow-restaurant.com/menu"
        fast_url = "https://fast-restaurant.com/menu"
        
        # Test slow domain
        with patch.object(limiter, 'domain_limiters') as mock_limiters:
            mock_slow_limiter = Mock()
            mock_slow_limiter.get_required_delay.return_value = 5.0
            mock_limiters.get_limiter.return_value = mock_slow_limiter
            
            result = limiter.check_rate_limit(slow_url)
            
            # Should use slow domain settings
            mock_limiters.get_limiter.assert_called_with('slow-restaurant.com')

    def test_ethical_compliance_integration(self):
        """Test ethical compliance integration."""
        if IntegratedRateLimiter is None:
            pytest.skip("IntegratedRateLimiter not implemented yet")
        
        limiter = IntegratedRateLimiter()
        url = "https://test-restaurant.com"
        
        with patch.object(limiter, 'ethical_checker') as mock_checker:
            mock_checker.check_ethical_compliance.return_value = Mock(
                is_compliant=True,
                user_agent_appropriate=True,
                request_headers_appropriate=True,
                request_frequency_appropriate=True
            )
            
            result = limiter.check_ethical_compliance(url)
            
            assert result.is_compliant is True
            assert result.user_agent_appropriate is True
            assert result.request_headers_appropriate is True
            mock_checker.check_ethical_compliance.assert_called_once_with(url)

    def test_rate_limit_statistics_tracking(self):
        """Test rate limit statistics tracking."""
        if IntegratedRateLimiter is None:
            pytest.skip("IntegratedRateLimiter not implemented yet")
        
        limiter = IntegratedRateLimiter()
        
        # Simulate some rate limiting activity
        limiter.record_request("https://restaurant1.com")
        limiter.record_request("https://restaurant2.com")
        limiter.record_delay("https://restaurant1.com", 2.0)
        limiter.record_robots_txt_check("https://restaurant1.com", allowed=True)
        limiter.record_robots_txt_check("https://restaurant2.com", allowed=False)
        
        stats = limiter.get_rate_limit_statistics()
        
        assert stats.total_requests == 2
        assert stats.total_delays == 1
        assert stats.total_delay_time == 2.0
        assert stats.robots_txt_checks == 2
        assert stats.robots_txt_allowed == 1
        assert stats.robots_txt_disallowed == 1

    def test_adaptive_rate_limiting(self):
        """Test adaptive rate limiting based on server responses."""
        if IntegratedRateLimiter is None:
            pytest.skip("IntegratedRateLimiter not implemented yet")
        
        limiter = IntegratedRateLimiter()
        url = "https://test-restaurant.com"
        
        # Simulate server responses
        limiter.record_server_response(url, 200, response_time=0.5)  # Fast response
        limiter.record_server_response(url, 200, response_time=0.3)  # Fast response
        limiter.record_server_response(url, 429, response_time=None)  # Rate limited
        
        # Rate limiter should adapt based on responses
        adapted_delay = limiter.get_adaptive_delay(url)
        
        assert adapted_delay > limiter.default_delay  # Should increase delay after rate limit

    def test_concurrent_request_handling(self):
        """Test handling concurrent requests to same domain."""
        if IntegratedRateLimiter is None:
            pytest.skip("IntegratedRateLimiter not implemented yet")
        
        limiter = IntegratedRateLimiter()
        urls = [
            "https://restaurant.com/page1",
            "https://restaurant.com/page2",
            "https://restaurant.com/page3"
        ]
        
        with patch.object(limiter, 'domain_limiters') as mock_limiters:
            mock_domain_limiter = Mock()
            mock_domain_limiter.can_make_concurrent_request.return_value = True
            mock_limiters.get_limiter.return_value = mock_domain_limiter
            
            result = limiter.check_concurrent_requests(urls)
            
            assert result.can_proceed is True
            assert result.concurrent_requests_allowed == 3

    def test_rate_limiting_consistency_across_modes(self):
        """Test rate limiting consistency across single-page and multi-page modes."""
        if IntegratedRateLimiter is None:
            pytest.skip("IntegratedRateLimiter not implemented yet")
        
        limiter = IntegratedRateLimiter()
        url = "https://test-restaurant.com"
        
        # Test single-page mode
        with patch.object(limiter, 'check_rate_limit') as mock_check:
            mock_check.return_value = Mock(can_proceed=False, required_delay=2.0)
            
            single_page_result = limiter.apply_rate_limit(url, mode='single_page')
            
            assert single_page_result.delay_applied is True
            assert single_page_result.delay_duration == 2.0
        
        # Test multi-page mode with same URL
        with patch.object(limiter, 'check_rate_limit') as mock_check:
            mock_check.return_value = Mock(can_proceed=False, required_delay=2.0)
            
            multi_page_result = limiter.apply_rate_limit_batch([url], mode='multi_page')
            
            # Should use same delay logic
            assert multi_page_result.total_delays == 1
            assert multi_page_result.total_delay_time == 2.0


class TestDomainRateLimiter:
    """Test cases for DomainRateLimiter."""

    def test_domain_rate_limiter_initialization(self):
        """Test domain rate limiter initialization."""
        if DomainRateLimiter is None:
            pytest.skip("DomainRateLimiter not implemented yet")
        
        limiter = DomainRateLimiter(
            domain='test-restaurant.com',
            delay=2.0,
            max_requests_per_minute=30
        )
        
        assert limiter.domain == 'test-restaurant.com'
        assert limiter.delay == 2.0
        assert limiter.max_requests_per_minute == 30

    def test_domain_rate_limiter_request_tracking(self):
        """Test domain rate limiter request tracking."""
        if DomainRateLimiter is None:
            pytest.skip("DomainRateLimiter not implemented yet")
        
        limiter = DomainRateLimiter(
            domain='test-restaurant.com',
            delay=1.0,
            max_requests_per_minute=60
        )
        
        # Make some requests
        limiter.record_request()
        limiter.record_request()
        limiter.record_request()
        
        assert limiter.get_request_count() == 3
        assert limiter.get_requests_in_last_minute() == 3

    def test_domain_rate_limiter_can_make_request(self):
        """Test domain rate limiter can make request check."""
        if DomainRateLimiter is None:
            pytest.skip("DomainRateLimiter not implemented yet")
        
        limiter = DomainRateLimiter(
            domain='test-restaurant.com',
            delay=1.0,
            max_requests_per_minute=60
        )
        
        # Should be able to make first request
        assert limiter.can_make_request() is True
        
        # Record request
        limiter.record_request()
        
        # Should need to wait for delay
        assert limiter.can_make_request() is False
        
        # Wait for delay
        time.sleep(1.1)
        
        # Should be able to make request again
        assert limiter.can_make_request() is True

    def test_domain_rate_limiter_required_delay(self):
        """Test domain rate limiter required delay calculation."""
        if DomainRateLimiter is None:
            pytest.skip("DomainRateLimiter not implemented yet")
        
        limiter = DomainRateLimiter(
            domain='test-restaurant.com',
            delay=2.0,
            max_requests_per_minute=60
        )
        
        # Record request
        limiter.record_request()
        
        # Should require delay
        required_delay = limiter.get_required_delay()
        assert required_delay > 0
        assert required_delay <= 2.0

    def test_domain_rate_limiter_exponential_backoff(self):
        """Test domain rate limiter exponential backoff."""
        if DomainRateLimiter is None:
            pytest.skip("DomainRateLimiter not implemented yet")
        
        limiter = DomainRateLimiter(
            domain='test-restaurant.com',
            delay=1.0,
            max_requests_per_minute=60,
            use_exponential_backoff=True
        )
        
        # Record multiple failures
        limiter.record_failure()
        limiter.record_failure()
        limiter.record_failure()
        
        # Delay should increase exponentially
        delay_after_3_failures = limiter.get_required_delay()
        assert delay_after_3_failures > 1.0  # Should be more than base delay


class TestEthicalComplianceChecker:
    """Test cases for EthicalComplianceChecker."""

    def test_ethical_compliance_checker_initialization(self):
        """Test ethical compliance checker initialization."""
        if EthicalComplianceChecker is None:
            pytest.skip("EthicalComplianceChecker not implemented yet")
        
        checker = EthicalComplianceChecker()
        assert checker.robots_txt_cache is not None
        assert checker.user_agent is not None

    def test_ethical_compliance_checker_robots_txt_parsing(self):
        """Test ethical compliance checker robots.txt parsing."""
        if EthicalComplianceChecker is None:
            pytest.skip("EthicalComplianceChecker not implemented yet")
        
        checker = EthicalComplianceChecker()
        
        robots_txt_content = """
        User-agent: *
        Disallow: /admin/
        Disallow: /private/
        Crawl-delay: 1
        
        User-agent: *
        Allow: /menu
        """
        
        with patch.object(checker, 'fetch_robots_txt') as mock_fetch:
            mock_fetch.return_value = robots_txt_content
            
            result = checker.check_robots_txt("https://test-restaurant.com/menu")
            
            assert result.allowed is True
            assert result.crawl_delay == 1
            mock_fetch.assert_called_once()

    def test_ethical_compliance_checker_robots_txt_disallow(self):
        """Test ethical compliance checker robots.txt disallow."""
        if EthicalComplianceChecker is None:
            pytest.skip("EthicalComplianceChecker not implemented yet")
        
        checker = EthicalComplianceChecker()
        
        robots_txt_content = """
        User-agent: *
        Disallow: /admin/
        Disallow: /private/
        """
        
        with patch.object(checker, 'fetch_robots_txt') as mock_fetch:
            mock_fetch.return_value = robots_txt_content
            
            result = checker.check_robots_txt("https://test-restaurant.com/admin/users")
            
            assert result.allowed is False
            assert result.disallow_reason == "Path explicitly disallowed"

    def test_ethical_compliance_checker_user_agent_validation(self):
        """Test ethical compliance checker user agent validation."""
        if EthicalComplianceChecker is None:
            pytest.skip("EthicalComplianceChecker not implemented yet")
        
        checker = EthicalComplianceChecker()
        
        # Test appropriate user agent
        appropriate_ua = "RAGScraper/1.0 (+https://example.com/bot-info)"
        assert checker.is_user_agent_appropriate(appropriate_ua) is True
        
        # Test inappropriate user agent
        inappropriate_ua = "Mozilla/5.0 (fake browser)"
        assert checker.is_user_agent_appropriate(inappropriate_ua) is False

    def test_ethical_compliance_checker_request_headers_validation(self):
        """Test ethical compliance checker request headers validation."""
        if EthicalComplianceChecker is None:
            pytest.skip("EthicalComplianceChecker not implemented yet")
        
        checker = EthicalComplianceChecker()
        
        # Test appropriate headers
        appropriate_headers = {
            'User-Agent': 'RAGScraper/1.0 (+https://example.com/bot-info)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        assert checker.are_request_headers_appropriate(appropriate_headers) is True
        
        # Test inappropriate headers (missing user agent)
        inappropriate_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        assert checker.are_request_headers_appropriate(inappropriate_headers) is False

    def test_ethical_compliance_checker_request_frequency_validation(self):
        """Test ethical compliance checker request frequency validation."""
        if EthicalComplianceChecker is None:
            pytest.skip("EthicalComplianceChecker not implemented yet")
        
        checker = EthicalComplianceChecker()
        
        # Test appropriate frequency (1 request per 2 seconds)
        checker.record_request("https://test-restaurant.com", time.time() - 3)
        assert checker.is_request_frequency_appropriate("https://test-restaurant.com", 2.0) is True
        
        # Test inappropriate frequency (too frequent)
        checker.record_request("https://test-restaurant.com", time.time() - 0.5)
        assert checker.is_request_frequency_appropriate("https://test-restaurant.com", 2.0) is False


class TestRateLimitStatistics:
    """Test cases for RateLimitStatistics."""

    def test_rate_limit_statistics_initialization(self):
        """Test rate limit statistics initialization."""
        if RateLimitStatistics is None:
            pytest.skip("RateLimitStatistics not implemented yet")
        
        stats = RateLimitStatistics()
        assert stats.total_requests == 0
        assert stats.total_delays == 0
        assert stats.total_delay_time == 0.0
        assert stats.robots_txt_checks == 0

    def test_rate_limit_statistics_request_tracking(self):
        """Test rate limit statistics request tracking."""
        if RateLimitStatistics is None:
            pytest.skip("RateLimitStatistics not implemented yet")
        
        stats = RateLimitStatistics()
        
        # Record some requests
        stats.record_request("https://restaurant1.com")
        stats.record_request("https://restaurant2.com")
        stats.record_request("https://restaurant1.com")
        
        assert stats.total_requests == 3
        assert stats.unique_domains == 2
        assert stats.requests_per_domain["restaurant1.com"] == 2
        assert stats.requests_per_domain["restaurant2.com"] == 1

    def test_rate_limit_statistics_delay_tracking(self):
        """Test rate limit statistics delay tracking."""
        if RateLimitStatistics is None:
            pytest.skip("RateLimitStatistics not implemented yet")
        
        stats = RateLimitStatistics()
        
        # Record some delays
        stats.record_delay("https://restaurant1.com", 2.0)
        stats.record_delay("https://restaurant2.com", 1.5)
        stats.record_delay("https://restaurant1.com", 3.0)
        
        assert stats.total_delays == 3
        assert stats.total_delay_time == 6.5
        assert stats.average_delay_time == 2.17  # 6.5 / 3

    def test_rate_limit_statistics_robots_txt_tracking(self):
        """Test rate limit statistics robots.txt tracking."""
        if RateLimitStatistics is None:
            pytest.skip("RateLimitStatistics not implemented yet")
        
        stats = RateLimitStatistics()
        
        # Record robots.txt checks
        stats.record_robots_txt_check("https://restaurant1.com", allowed=True)
        stats.record_robots_txt_check("https://restaurant2.com", allowed=False)
        stats.record_robots_txt_check("https://restaurant3.com", allowed=True)
        
        assert stats.robots_txt_checks == 3
        assert stats.robots_txt_allowed == 2
        assert stats.robots_txt_disallowed == 1
        assert stats.robots_txt_compliance_rate == 0.67  # 2/3

    def test_rate_limit_statistics_performance_metrics(self):
        """Test rate limit statistics performance metrics."""
        if RateLimitStatistics is None:
            pytest.skip("RateLimitStatistics not implemented yet")
        
        stats = RateLimitStatistics()
        
        # Record performance data
        stats.record_performance_metric("average_response_time", 0.5)
        stats.record_performance_metric("success_rate", 0.95)
        stats.record_performance_metric("throughput", 25.0)
        
        performance_metrics = stats.get_performance_metrics()
        
        assert performance_metrics["average_response_time"] == 0.5
        assert performance_metrics["success_rate"] == 0.95
        assert performance_metrics["throughput"] == 25.0

    def test_rate_limit_statistics_json_export(self):
        """Test rate limit statistics JSON export."""
        if RateLimitStatistics is None:
            pytest.skip("RateLimitStatistics not implemented yet")
        
        stats = RateLimitStatistics()
        
        # Add some data
        stats.record_request("https://restaurant1.com")
        stats.record_delay("https://restaurant1.com", 2.0)
        stats.record_robots_txt_check("https://restaurant1.com", allowed=True)
        
        json_data = stats.to_json()
        
        assert json_data["total_requests"] == 1
        assert json_data["total_delays"] == 1
        assert json_data["total_delay_time"] == 2.0
        assert json_data["robots_txt_checks"] == 1
        assert json_data["robots_txt_allowed"] == 1