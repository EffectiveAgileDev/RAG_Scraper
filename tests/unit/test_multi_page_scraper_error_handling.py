"""Unit tests for multi-page scraper error handling functionality."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import time
import threading

from src.scraper.multi_page_scraper import MultiPageScraper
from src.scraper.multi_page_result_handler import MultiPageScrapingResult


class TestMultiPageScraperErrorHandling:
    """Test error handling functionality for multi-page scraping."""

    def test_handle_network_failure(self):
        """Test handling of network failures during page fetching."""
        scraper = MultiPageScraper()

        with patch.object(scraper, "_fetch_page") as mock_fetch:
            # Simulate network failure
            mock_fetch.side_effect = ConnectionError("Network unreachable")

            # Test error handling
            result = scraper._handle_page_error(
                "http://example.com/", "ConnectionError", "Network unreachable"
            )

            assert result is not None
            assert result["error_type"] == "ConnectionError"
            assert result["error_message"] == "Network unreachable"
            assert result["url"] == "http://example.com/"
            assert result["retry_attempted"] is False

    def test_handle_timeout_error(self):
        """Test handling of timeout errors during page fetching."""
        scraper = MultiPageScraper()

        with patch.object(scraper, "_fetch_page") as mock_fetch:
            # Simulate timeout
            mock_fetch.side_effect = TimeoutError("Request timeout")

            # Test timeout handling
            result = scraper._handle_page_error(
                "http://example.com/slow", "TimeoutError", "Request timeout"
            )

            assert result["error_type"] == "TimeoutError"
            assert result["should_retry"] is True

    def test_handle_http_error_codes(self):
        """Test handling of HTTP error codes (404, 500, etc.)."""
        scraper = MultiPageScraper()

        # Test different HTTP error codes
        error_codes = [404, 500, 503, 429]

        for code in error_codes:
            result = scraper._handle_http_error("http://example.com/", code)

            assert result["status_code"] == code
            assert result["error_type"] == "HTTPError"

            # 429 (rate limit) should be retryable
            if code == 429:
                assert result["should_retry"] is True
                assert result["retry_delay"] > 0
            # 500, 503 should be retryable
            elif code in [500, 503]:
                assert result["should_retry"] is True
            # 404 should not be retryable
            elif code == 404:
                assert result["should_retry"] is False

    def test_retry_failed_pages(self):
        """Test retry mechanism for failed pages."""
        scraper = MultiPageScraper()

        with patch.object(scraper, "_fetch_page") as mock_fetch:
            # First call fails, second succeeds
            mock_fetch.side_effect = [
                ConnectionError("Network error"),
                "<html>Success</html>",
            ]

            # Test retry functionality
            result = scraper._retry_failed_page("http://example.com/", max_retries=1)

            assert result is not None
            assert "Success" in result
            assert mock_fetch.call_count == 2

    def test_retry_with_exponential_backoff(self):
        """Test retry mechanism with exponential backoff."""
        scraper = MultiPageScraper()

        with patch.object(scraper, "_fetch_page") as mock_fetch, patch(
            "time.sleep"
        ) as mock_sleep:
            # Fail twice, then succeed
            mock_fetch.side_effect = [
                ConnectionError("Error 1"),
                ConnectionError("Error 2"),
                "<html>Success</html>",
            ]

            start_time = time.time()
            result = scraper._retry_failed_page(
                "http://example.com/", max_retries=2, use_exponential_backoff=True
            )
            end_time = time.time()

            assert result is not None
            assert mock_fetch.call_count == 3

            # Should have called sleep for backoff
            assert mock_sleep.call_count == 2
            # First sleep should be shorter than second
            assert (
                mock_sleep.call_args_list[0][0][0] < mock_sleep.call_args_list[1][0][0]
            )

    def test_handle_malformed_html(self):
        """Test handling of malformed HTML content."""
        scraper = MultiPageScraper()

        with patch.object(scraper, "_fetch_page") as mock_fetch, patch.object(
            scraper, "_fetch_and_process_page"
        ) as mock_process:
            # Return malformed HTML
            mock_fetch.return_value = "<html><div><p>Unclosed tags"
            mock_process.side_effect = Exception("HTML parsing error")

            # Test handling malformed content
            result = scraper._handle_processing_error(
                "http://example.com/bad", "HTMLParsingError", "HTML parsing error"
            )

            assert result["error_type"] == "HTMLParsingError"
            assert result["should_skip"] is True

    def test_handle_missing_dependencies(self):
        """Test handling of missing data extraction dependencies."""
        scraper = MultiPageScraper()

        with patch.object(scraper, "_fetch_and_process_page") as mock_process:
            # Simulate missing extractor
            mock_process.side_effect = ImportError("Missing beautifulsoup4")

            # Test dependency error handling
            result = scraper._handle_dependency_error(
                "ImportError", "Missing beautifulsoup4"
            )

            assert result["error_type"] == "ImportError"
            assert result["is_critical"] is True
            assert result["should_abort"] is True

    def test_error_aggregation_and_reporting(self):
        """Test aggregation and reporting of multiple errors."""
        scraper = MultiPageScraper()

        # Simulate various errors
        errors = [
            {"url": "http://example.com/1", "error_type": "TimeoutError"},
            {
                "url": "http://example.com/2",
                "error_type": "HTTPError",
                "status_code": 404,
            },
            {"url": "http://example.com/3", "error_type": "ConnectionError"},
            {
                "url": "http://example.com/4",
                "error_type": "HTTPError",
                "status_code": 500,
            },
        ]

        # Add errors to scraper
        for error in errors:
            scraper._add_error_to_log(error)

        # Get error summary
        error_summary = scraper._get_error_summary()

        assert error_summary["total_errors"] == 4
        assert error_summary["error_types"]["TimeoutError"] == 1
        assert error_summary["error_types"]["HTTPError"] == 2
        assert error_summary["error_types"]["ConnectionError"] == 1
        assert error_summary["retryable_errors"] == 3  # Timeout, 500, Connection
        assert error_summary["non_retryable_errors"] == 1  # 404

    def test_error_recovery_strategies(self):
        """Test different error recovery strategies."""
        scraper = MultiPageScraper()

        # Test skip strategy
        result_skip = scraper._apply_error_recovery_strategy(
            "http://example.com/",
            {"error_type": "HTTPError", "status_code": 404},
            strategy="skip",
        )
        assert result_skip["action"] == "skip"

        # Test retry strategy
        result_retry = scraper._apply_error_recovery_strategy(
            "http://example.com/", {"error_type": "TimeoutError"}, strategy="retry"
        )
        assert result_retry["action"] == "retry"

        # Test fallback strategy
        result_fallback = scraper._apply_error_recovery_strategy(
            "http://example.com/",
            {"error_type": "HTMLParsingError"},
            strategy="fallback",
        )
        assert result_fallback["action"] == "fallback"

    def test_critical_error_handling(self):
        """Test handling of critical errors that should stop processing."""
        scraper = MultiPageScraper()

        critical_errors = [
            {"error_type": "MemoryError", "message": "Out of memory"},
            {"error_type": "PermissionError", "message": "Access denied"},
            {"error_type": "ImportError", "message": "Missing required module"},
        ]

        for error in critical_errors:
            is_critical = scraper._is_critical_error(error)
            assert is_critical is True

    def test_error_logging_and_persistence(self):
        """Test error logging and persistence functionality."""
        scraper = MultiPageScraper()

        # Test error logging
        error_info = {
            "url": "http://example.com/error",
            "error_type": "ConnectionError",
            "message": "Network error",
            "timestamp": time.time(),
        }

        scraper._log_error(error_info)

        # Verify error was logged
        logged_errors = scraper._get_logged_errors()
        assert len(logged_errors) == 1
        assert logged_errors[0]["url"] == "http://example.com/error"

    def test_partial_failure_recovery(self):
        """Test recovery from partial failures in multi-page scraping."""
        scraper = MultiPageScraper()

        with patch.object(scraper, "_fetch_and_process_page") as mock_process:
            # Mix of successful and failed pages
            def mock_process_side_effect(url):
                if "fail" in url:
                    return None
                return {"page_type": "menu", "data": Mock()}

            mock_process.side_effect = mock_process_side_effect

            pages = [
                "http://example.com/success1",
                "http://example.com/fail1",
                "http://example.com/success2",
                "http://example.com/fail2",
            ]

            # Test partial failure handling
            result = scraper._handle_partial_failures(pages)

            assert len(result["successful_pages"]) == 2
            assert len(result["failed_pages"]) == 2
            assert result["success_rate"] == 0.5
            assert result["should_continue"] is True  # 50% success rate should continue

    def test_error_rate_monitoring(self):
        """Test monitoring of error rates and circuit breaker functionality."""
        scraper = MultiPageScraper()

        # Simulate high error rate
        for i in range(10):
            error = {
                "url": f"http://example.com/{i}",
                "error_type": "ConnectionError",
                "timestamp": time.time(),
            }
            scraper._add_error_to_log(error)

        # Check if circuit breaker should trigger
        error_rate = scraper._calculate_error_rate(window_seconds=60)
        should_stop = scraper._should_trigger_circuit_breaker(error_rate, threshold=0.8)

        assert error_rate > 0.8
        assert should_stop is True

    def test_error_context_preservation(self):
        """Test preservation of error context for debugging."""
        scraper = MultiPageScraper()

        context = {
            "restaurant_name": "Test Restaurant",
            "page_number": 3,
            "total_pages": 5,
            "scraping_strategy": "BFS",
        }

        error_info = {
            "url": "http://example.com/menu",
            "error_type": "HTTPError",
            "status_code": 500,
            "context": context,
        }

        # Test context preservation
        scraper._log_error_with_context(error_info)

        logged_errors = scraper._get_logged_errors()
        assert logged_errors[0]["context"]["restaurant_name"] == "Test Restaurant"
        assert logged_errors[0]["context"]["page_number"] == 3
