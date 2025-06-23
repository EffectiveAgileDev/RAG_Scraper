"""Unit tests for multi-page scraper concurrent fetching functionality."""
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import asyncio
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.scraper.multi_page_scraper import MultiPageScraper, MultiPageScrapingResult


class TestMultiPageScraperConcurrentFetching:
    """Test concurrent fetching functionality for multi-page scraping."""

    def test_concurrent_fetch_multiple_pages(self):
        """Test that multiple pages can be fetched concurrently."""
        scraper = MultiPageScraper(max_pages=5)
        
        with patch.object(scraper, '_fetch_page') as mock_fetch, \
             patch.object(scraper, '_fetch_and_process_page') as mock_process:
            
            # Mock responses with delays to test concurrency
            def mock_fetch_side_effect(url):
                time.sleep(0.1)  # Simulate network delay
                return f"<html>Content for {url}</html>"
            
            mock_fetch.side_effect = mock_fetch_side_effect
            mock_process.return_value = {"page_type": "menu", "data": Mock()}
            
            pages = [
                "http://example.com/menu",
                "http://example.com/contact", 
                "http://example.com/about",
                "http://example.com/hours"
            ]
            
            # Test concurrent fetching
            start_time = time.time()
            results = scraper._fetch_pages_concurrently(pages, max_workers=2)
            end_time = time.time()
            
            # Should complete faster than sequential (4 * 0.1s = 0.4s)
            # With 2 workers: should be around 0.2s
            assert end_time - start_time < 0.35
            assert len(results) == 4
            assert all(result is not None for result in results)

    def test_concurrent_fetch_respects_max_workers(self):
        """Test that concurrent fetching respects max workers limit."""
        scraper = MultiPageScraper()
        
        with patch.object(scraper, '_fetch_page') as mock_fetch:
            mock_fetch.return_value = "<html>Content</html>"
            
            pages = [f"http://example.com/page{i}" for i in range(5)]
            
            # Test with different worker limits
            results_2_workers = scraper._fetch_pages_concurrently(pages, max_workers=2)
            results_4_workers = scraper._fetch_pages_concurrently(pages, max_workers=4)
            
            # Both should return same number of results
            assert len(results_2_workers) == len(results_4_workers) == 5

    def test_concurrent_fetch_handles_throttling(self):
        """Test that concurrent fetching includes rate limiting/throttling."""
        scraper = MultiPageScraper()
        
        with patch.object(scraper, '_fetch_page') as mock_fetch:
            mock_fetch.return_value = "<html>Content</html>"
            
            pages = [f"http://example.com/page{i}" for i in range(3)]
            
            # Test with throttling enabled
            start_time = time.time()
            results = scraper._fetch_pages_concurrently(
                pages, max_workers=2, throttle_delay=0.1
            )
            end_time = time.time()
            
            # Should have some delay due to throttling
            assert end_time - start_time >= 0.1
            assert len(results) == 3

    def test_concurrent_fetch_error_handling(self):
        """Test concurrent fetching handles errors gracefully."""
        scraper = MultiPageScraper()
        
        with patch.object(scraper, '_fetch_page') as mock_fetch:
            
            def mock_fetch_side_effect(url):
                if "error" in url:
                    raise Exception("Network error")
                return "<html>Content</html>"
            
            mock_fetch.side_effect = mock_fetch_side_effect
            
            pages = [
                "http://example.com/good1",
                "http://example.com/error",
                "http://example.com/good2"
            ]
            
            results = scraper._fetch_pages_concurrently(pages, max_workers=2)
            
            # Should handle errors and continue with other pages
            assert len(results) == 3
            assert results[0] is not None  # good1
            assert results[1] is None      # error
            assert results[2] is not None  # good2

    def test_concurrent_fetch_timeout_handling(self):
        """Test that concurrent fetching handles timeouts."""
        scraper = MultiPageScraper()
        
        with patch.object(scraper, '_fetch_page') as mock_fetch:
            
            def mock_fetch_side_effect(url):
                if "slow" in url:
                    time.sleep(1.0)  # Simulate slow response
                return "<html>Content</html>"
            
            mock_fetch.side_effect = mock_fetch_side_effect
            
            pages = [
                "http://example.com/fast",
                "http://example.com/slow",
                "http://example.com/fast2"
            ]
            
            # Test with short timeout
            results = scraper._fetch_pages_concurrently(
                pages, max_workers=2, timeout=0.5
            )
            
            # Fast pages should succeed, slow should timeout
            assert len(results) == 3
            assert results[0] is not None  # fast
            assert results[1] is None      # slow (timeout)
            assert results[2] is not None  # fast2

    def test_concurrent_processing_integration(self):
        """Test integration of concurrent fetching with page processing."""
        scraper = MultiPageScraper(max_pages=3)
        
        with patch.object(scraper, '_fetch_page') as mock_fetch, \
             patch.object(scraper, '_fetch_and_process_page') as mock_process:
            
            mock_fetch.return_value = "<html>Content</html>"
            mock_process.return_value = {"page_type": "menu", "data": Mock()}
            
            pages = [
                "http://example.com/menu",
                "http://example.com/contact",
                "http://example.com/about"
            ]
            
            # Test concurrent processing
            results = scraper._process_pages_concurrently(pages, max_workers=2)
            
            assert len(results) == 3
            assert all(result["page_type"] == "menu" for result in results if result)

    def test_concurrent_fetch_preserves_order(self):
        """Test that concurrent fetching preserves input order in results."""
        scraper = MultiPageScraper()
        
        with patch.object(scraper, '_fetch_page') as mock_fetch:
            
            def mock_fetch_side_effect(url):
                # Add different delays to test ordering
                if "page1" in url:
                    time.sleep(0.2)
                elif "page2" in url:
                    time.sleep(0.1)
                return f"<html>Content for {url}</html>"
            
            mock_fetch.side_effect = mock_fetch_side_effect
            
            pages = [
                "http://example.com/page1",  # Slower
                "http://example.com/page2",  # Faster
                "http://example.com/page3"   # Normal
            ]
            
            results = scraper._fetch_pages_concurrently(pages, max_workers=3)
            
            # Results should maintain input order despite different completion times
            assert len(results) == 3
            assert "page1" in results[0] if results[0] else False
            assert "page2" in results[1] if results[1] else False
            assert "page3" in results[2] if results[2] else False

    def test_concurrent_fetch_progress_tracking(self):
        """Test that concurrent fetching supports progress tracking."""
        scraper = MultiPageScraper()
        progress_updates = []
        
        def mock_progress_callback(message):
            progress_updates.append(message)
        
        with patch.object(scraper, '_fetch_page') as mock_fetch:
            mock_fetch.return_value = "<html>Content</html>"
            
            pages = [f"http://example.com/page{i}" for i in range(3)]
            
            results = scraper._fetch_pages_concurrently(
                pages, max_workers=2, progress_callback=mock_progress_callback
            )
            
            # Should have progress updates
            assert len(progress_updates) > 0
            assert len(results) == 3

    def test_concurrent_fetch_statistics(self):
        """Test that concurrent fetching provides statistics."""
        scraper = MultiPageScraper()
        
        with patch.object(scraper, '_fetch_page') as mock_fetch:
            
            def mock_fetch_side_effect(url):
                if "error" in url:
                    raise Exception("Error")
                return "<html>Content</html>"
            
            mock_fetch.side_effect = mock_fetch_side_effect
            
            pages = [
                "http://example.com/good1",
                "http://example.com/error",
                "http://example.com/good2"
            ]
            
            results = scraper._fetch_pages_concurrently(pages, max_workers=2)
            stats = scraper._get_concurrent_fetch_stats()
            
            # Should track successful and failed fetches
            assert "successful_fetches" in stats
            assert "failed_fetches" in stats
            assert "total_time" in stats
            assert stats["successful_fetches"] == 2
            assert stats["failed_fetches"] == 1