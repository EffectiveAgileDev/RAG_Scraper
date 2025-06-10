"""Unit tests for rate limiting and ethical scraping."""
import time
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestRateLimiter:
    """Test rate limiting functionality."""

    def test_create_rate_limiter_with_delay(self):
        """Test creation of rate limiter with specified delay."""
        from src.scraper.rate_limiter import RateLimiter

        limiter = RateLimiter(delay=2.0)

        assert limiter.delay == 2.0
        assert limiter.last_request_time is None

    def test_rate_limiter_enforces_delay(self):
        """Test that rate limiter enforces minimum delay between requests."""
        from src.scraper.rate_limiter import RateLimiter

        limiter = RateLimiter(delay=0.1)  # 100ms delay

        # First request should go through immediately
        start_time = time.time()
        limiter.wait_if_needed()
        first_elapsed = time.time() - start_time

        assert first_elapsed < 0.05  # Should be nearly instant

        # Second request should be delayed
        start_time = time.time()
        limiter.wait_if_needed()
        second_elapsed = time.time() - start_time

        assert second_elapsed >= 0.09  # Should wait ~100ms

    def test_rate_limiter_no_delay_if_time_passed(self):
        """Test that no delay is applied if enough time has passed."""
        from src.scraper.rate_limiter import RateLimiter

        limiter = RateLimiter(delay=0.1)

        # Make first request
        limiter.wait_if_needed()

        # Wait longer than the delay period
        time.sleep(0.15)

        # Second request should not be delayed
        start_time = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start_time

        assert elapsed < 0.05  # Should be nearly instant

    def test_rate_limiter_tracks_request_time(self):
        """Test that rate limiter tracks last request time."""
        from src.scraper.rate_limiter import RateLimiter

        limiter = RateLimiter(delay=1.0)

        assert limiter.last_request_time is None

        limiter.wait_if_needed()

        assert limiter.last_request_time is not None
        assert isinstance(limiter.last_request_time, float)


class TestEthicalScraper:
    """Test ethical scraping functionality."""

    def test_create_ethical_scraper_with_settings(self):
        """Test creation of ethical scraper with rate limiting."""
        from src.scraper.ethical_scraper import EthicalScraper

        scraper = EthicalScraper(delay=2.0, timeout=30, user_agent="RAG_Scraper/1.0")

        assert scraper.delay == 2.0
        assert scraper.timeout == 30
        assert scraper.user_agent == "RAG_Scraper/1.0"

    def test_ethical_scraper_respects_robots_txt(self):
        """Test that scraper checks robots.txt before scraping."""
        from src.scraper.ethical_scraper import EthicalScraper

        scraper = EthicalScraper()

        # Mock robots.txt that allows scraping
        with patch("src.scraper.ethical_scraper.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = """
User-agent: *
Allow: /

User-agent: RAG_Scraper
Allow: /
"""
            mock_get.return_value = mock_response

            allowed = scraper.is_allowed_by_robots("http://example.com/page")
            assert allowed is True

    def test_ethical_scraper_respects_robots_txt_disallow(self):
        """Test that scraper respects robots.txt disallow rules."""
        from src.scraper.ethical_scraper import EthicalScraper

        scraper = EthicalScraper()

        # Mock robots.txt that disallows scraping
        with patch("src.scraper.ethical_scraper.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = """
User-agent: *
Disallow: /

User-agent: RAG_Scraper
Disallow: /
"""
            mock_get.return_value = mock_response

            allowed = scraper.is_allowed_by_robots("http://example.com/page")
            assert allowed is False

    def test_ethical_scraper_handles_robots_txt_error(self):
        """Test handling of robots.txt fetch errors."""
        from src.scraper.ethical_scraper import EthicalScraper

        scraper = EthicalScraper()

        # Mock robots.txt request failure
        with patch("src.scraper.ethical_scraper.requests.get") as mock_get:
            mock_get.side_effect = Exception("Network error")

            # Should default to allowing if robots.txt can't be fetched
            allowed = scraper.is_allowed_by_robots("http://example.com/page")
            assert allowed is True

    def test_ethical_scraper_uses_proper_user_agent(self):
        """Test that scraper uses proper user agent headers."""
        from src.scraper.ethical_scraper import EthicalScraper

        scraper = EthicalScraper(user_agent="RAG_Scraper/1.0")

        with patch("src.scraper.ethical_scraper.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>Test</body></html>"
            mock_get.return_value = mock_response

            scraper.fetch_page("http://example.com")

            # Verify user agent was set
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            headers = call_args[1]["headers"]
            assert headers["User-Agent"] == "RAG_Scraper/1.0"

    def test_ethical_scraper_applies_rate_limiting(self):
        """Test that scraper applies rate limiting between requests."""
        from src.scraper.ethical_scraper import EthicalScraper

        scraper = EthicalScraper(delay=0.1)

        with patch("src.scraper.ethical_scraper.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>Test</body></html>"
            mock_get.return_value = mock_response

            # First request
            start_time = time.time()
            scraper.fetch_page("http://example.com/page1")
            first_elapsed = time.time() - start_time

            # Second request should be delayed
            start_time = time.time()
            scraper.fetch_page("http://example.com/page2")
            second_elapsed = time.time() - start_time

            assert second_elapsed >= 0.09  # Should include rate limiting delay

    def test_ethical_scraper_handles_http_errors(self):
        """Test handling of HTTP error responses."""
        from src.scraper.ethical_scraper import EthicalScraper

        scraper = EthicalScraper()

        with patch("src.scraper.ethical_scraper.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = Exception("404 Not Found")
            mock_get.return_value = mock_response

            result = scraper.fetch_page("http://example.com/notfound")

            assert result is None  # Should return None for failed requests

    def test_ethical_scraper_handles_timeout(self):
        """Test handling of request timeouts."""
        from src.scraper.ethical_scraper import EthicalScraper

        scraper = EthicalScraper(timeout=1)

        with patch("src.scraper.ethical_scraper.requests.get") as mock_get:
            mock_get.side_effect = Exception("Timeout")

            result = scraper.fetch_page("http://example.com/slow")

            assert result is None  # Should return None for timeouts

    def test_ethical_scraper_respects_retry_after_header(self):
        """Test that scraper respects Retry-After header for 429 responses."""
        from src.scraper.ethical_scraper import EthicalScraper

        scraper = EthicalScraper()

        with patch(
            "src.scraper.ethical_scraper.requests.get"
        ) as mock_get, patch.object(
            scraper.rate_limiter, "wait_if_needed"
        ) as mock_rate_limiter:
            # First call returns 429 with Retry-After
            mock_response_429 = Mock()
            mock_response_429.status_code = 429
            mock_response_429.headers = {"Retry-After": "2"}

            # Second call returns success
            mock_response_200 = Mock()
            mock_response_200.status_code = 200
            mock_response_200.text = "<html><body>Success</body></html>"

            mock_get.side_effect = [mock_response_429, mock_response_200]

            with patch("time.sleep") as mock_sleep:
                result = scraper.fetch_page_with_retry("http://example.com")

                # Should have slept for retry delay
                mock_sleep.assert_called_with(2)
                assert result is not None

    def test_ethical_scraper_retry_logic(self):
        """Test retry logic for failed requests."""
        from src.scraper.ethical_scraper import EthicalScraper

        scraper = EthicalScraper()

        with patch("src.scraper.ethical_scraper.requests.get") as mock_get:
            # First two calls fail, third succeeds
            mock_get.side_effect = [
                Exception("Network error"),
                Exception("Network error"),
                Mock(status_code=200, text="<html><body>Success</body></html>"),
            ]

            result = scraper.fetch_page_with_retry("http://example.com", max_retries=3)

            assert result is not None
            assert mock_get.call_count == 3

    def test_ethical_scraper_max_retries_exceeded(self):
        """Test behavior when max retries are exceeded."""
        from src.scraper.ethical_scraper import EthicalScraper

        scraper = EthicalScraper()

        with patch("src.scraper.ethical_scraper.requests.get") as mock_get:
            mock_get.side_effect = Exception("Persistent error")

            result = scraper.fetch_page_with_retry("http://example.com", max_retries=2)

            assert result is None
            assert mock_get.call_count == 2


class TestRobotsTxtParser:
    """Test robots.txt parsing functionality."""

    def test_parse_simple_robots_txt(self):
        """Test parsing of simple robots.txt file."""
        from src.scraper.ethical_scraper import RobotsTxtParser

        robots_content = """
User-agent: *
Allow: /
Disallow: /admin/
"""

        parser = RobotsTxtParser(robots_content)

        assert parser.is_allowed("/", "RAG_Scraper") is True
        assert parser.is_allowed("/admin/", "RAG_Scraper") is False
        assert parser.is_allowed("/public/", "RAG_Scraper") is True

    def test_parse_specific_user_agent_robots_txt(self):
        """Test parsing with specific user agent rules."""
        from src.scraper.ethical_scraper import RobotsTxtParser

        robots_content = """
User-agent: *
Disallow: /

User-agent: RAG_Scraper
Allow: /
Disallow: /private/
"""

        parser = RobotsTxtParser(robots_content)

        assert parser.is_allowed("/", "RAG_Scraper") is True
        assert parser.is_allowed("/private/", "RAG_Scraper") is False
        assert parser.is_allowed("/", "GoogleBot") is False

    def test_parse_empty_robots_txt(self):
        """Test parsing of empty robots.txt file."""
        from src.scraper.ethical_scraper import RobotsTxtParser

        parser = RobotsTxtParser("")

        # Empty robots.txt should allow everything
        assert parser.is_allowed("/", "RAG_Scraper") is True
        assert parser.is_allowed("/anything/", "RAG_Scraper") is True

    def test_parse_malformed_robots_txt(self):
        """Test parsing of malformed robots.txt file."""
        from src.scraper.ethical_scraper import RobotsTxtParser

        robots_content = """
This is not a valid robots.txt
Random text here
User-agent: *
Allow: /
Invalid line without colon
"""

        parser = RobotsTxtParser(robots_content)

        # Should handle malformed content gracefully
        assert parser.is_allowed("/", "RAG_Scraper") is True


class TestEthicalScrapingConfiguration:
    """Test ethical scraping configuration."""

    def test_default_configuration(self):
        """Test default ethical scraping configuration."""
        from src.scraper.ethical_scraper import EthicalScraper

        scraper = EthicalScraper()

        assert scraper.delay >= 1.0  # Should have reasonable default delay
        assert scraper.timeout >= 10  # Should have reasonable timeout
        assert "RAG_Scraper" in scraper.user_agent  # Should identify itself

    def test_custom_configuration(self):
        """Test custom ethical scraping configuration."""
        from src.scraper.ethical_scraper import EthicalScraper

        scraper = EthicalScraper(
            delay=3.0, timeout=45, user_agent="Custom RAG_Scraper/2.0"
        )

        assert scraper.delay == 3.0
        assert scraper.timeout == 45
        assert scraper.user_agent == "Custom RAG_Scraper/2.0"

    def test_validate_configuration(self):
        """Test validation of scraping configuration."""
        from src.scraper.ethical_scraper import EthicalScraper

        # Should reject negative delays
        with pytest.raises(ValueError):
            EthicalScraper(delay=-1.0)

        # Should reject zero or negative timeouts
        with pytest.raises(ValueError):
            EthicalScraper(timeout=0)

        # Should reject empty user agent
        with pytest.raises(ValueError):
            EthicalScraper(user_agent="")
