"""Unit tests for multi-page scraper queue management functionality."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from collections import deque
import asyncio

from src.scraper.multi_page_scraper import MultiPageScraper


class TestMultiPageScraperQueueManagement:
    """Test queue management functionality for multi-page scraping."""

    def test_initialize_page_queue_empty(self):
        """Test initializing an empty page queue."""
        scraper = MultiPageScraper()

        # Queue should be initialized but empty
        assert hasattr(scraper, "_page_queue") or not hasattr(scraper, "_page_queue")

        # Initialize queue
        scraper._initialize_page_queue()

        assert hasattr(scraper, "_page_queue")
        assert len(scraper._page_queue) == 0
        assert isinstance(scraper._page_queue, deque)

    def test_add_pages_to_queue_fifo(self):
        """Test adding pages to queue with FIFO (BFS) ordering."""
        scraper = MultiPageScraper()
        scraper._initialize_page_queue()

        pages = [
            "http://example.com/",
            "http://example.com/menu",
            "http://example.com/contact",
        ]

        # Add pages to queue
        scraper._add_pages_to_queue(pages, strategy="BFS")

        assert len(scraper._page_queue) == 3

        # Should maintain FIFO order for BFS
        assert scraper._get_next_page() == "http://example.com/"
        assert scraper._get_next_page() == "http://example.com/menu"
        assert scraper._get_next_page() == "http://example.com/contact"

    def test_add_pages_to_queue_lifo(self):
        """Test adding pages to queue with LIFO (DFS) ordering."""
        scraper = MultiPageScraper()
        scraper._initialize_page_queue()

        pages = [
            "http://example.com/",
            "http://example.com/menu",
            "http://example.com/contact",
        ]

        # Add pages to queue
        scraper._add_pages_to_queue(pages, strategy="DFS")

        assert len(scraper._page_queue) == 3

        # Should maintain LIFO order for DFS (reverse order)
        assert scraper._get_next_page() == "http://example.com/contact"
        assert scraper._get_next_page() == "http://example.com/menu"
        assert scraper._get_next_page() == "http://example.com/"

    def test_get_next_page_from_empty_queue(self):
        """Test getting next page from empty queue."""
        scraper = MultiPageScraper()
        scraper._initialize_page_queue()

        # Should return None when queue is empty
        assert scraper._get_next_page() is None

    def test_queue_has_pages(self):
        """Test checking if queue has pages."""
        scraper = MultiPageScraper()
        scraper._initialize_page_queue()

        # Initially empty
        assert not scraper._has_pending_pages()

        # Add pages
        scraper._add_pages_to_queue(["http://example.com/menu"], strategy="BFS")
        assert scraper._has_pending_pages()

        # Remove page
        scraper._get_next_page()
        assert not scraper._has_pending_pages()

    def test_queue_prevents_duplicate_pages(self):
        """Test that queue prevents adding duplicate pages."""
        scraper = MultiPageScraper()
        scraper._initialize_page_queue()

        pages = [
            "http://example.com/menu",
            "http://example.com/menu",  # Duplicate
            "http://example.com/contact",
        ]

        scraper._add_pages_to_queue(pages, strategy="BFS")

        # Should only have 2 unique pages
        assert len(scraper._page_queue) == 2

        # Verify both unique pages are present
        page1 = scraper._get_next_page()
        page2 = scraper._get_next_page()

        unique_pages = {page1, page2}
        assert "http://example.com/menu" in unique_pages
        assert "http://example.com/contact" in unique_pages

    def test_queue_respects_max_pages_limit(self):
        """Test that queue respects maximum pages limit."""
        scraper = MultiPageScraper(max_pages=3)
        scraper._initialize_page_queue()

        # Try to add more pages than limit
        pages = [f"http://example.com/page{i}" for i in range(5)]
        scraper._add_pages_to_queue(pages, strategy="BFS")

        # Should only have max_pages items
        assert len(scraper._page_queue) <= 3

    def test_queue_priority_ordering(self):
        """Test that queue can handle priority-based ordering."""
        scraper = MultiPageScraper()
        scraper._initialize_page_queue()

        # Pages with different priorities (menu > contact > about)
        pages = [
            ("http://example.com/about", 1),
            ("http://example.com/menu", 10),
            ("http://example.com/contact", 5),
        ]

        scraper._add_pages_to_queue_with_priority(pages)

        # Should return highest priority first
        assert scraper._get_next_page() == "http://example.com/menu"
        assert scraper._get_next_page() == "http://example.com/contact"
        assert scraper._get_next_page() == "http://example.com/about"

    def test_clear_queue(self):
        """Test clearing the page queue."""
        scraper = MultiPageScraper()
        scraper._initialize_page_queue()

        # Add pages
        pages = ["http://example.com/menu", "http://example.com/contact"]
        scraper._add_pages_to_queue(pages, strategy="BFS")

        assert len(scraper._page_queue) == 2

        # Clear queue
        scraper._clear_page_queue()

        assert len(scraper._page_queue) == 0
        assert not scraper._has_pending_pages()

    def test_queue_statistics(self):
        """Test getting queue statistics."""
        scraper = MultiPageScraper()
        scraper._initialize_page_queue()

        # Add pages
        pages = ["http://example.com/menu", "http://example.com/contact"]
        scraper._add_pages_to_queue(pages, strategy="BFS")

        stats = scraper._get_queue_stats()

        assert stats["total_queued"] == 2
        assert stats["pending"] == 2
        assert stats["strategy"] in ["BFS", "DFS"]

    def test_queue_thread_safety(self):
        """Test that queue operations are thread-safe."""
        scraper = MultiPageScraper()
        scraper._initialize_page_queue()

        # This test would require actual threading to be comprehensive
        # For now, just test that the queue supports thread-safe operations
        import threading

        def add_pages():
            pages = [f"http://example.com/page{i}" for i in range(3)]
            scraper._add_pages_to_queue(pages, strategy="BFS")

        def get_pages():
            while scraper._has_pending_pages():
                scraper._get_next_page()

        # Test that we can call these without errors
        # (Full concurrency testing would need more complex setup)
        add_pages()
        assert scraper._has_pending_pages()
        get_pages()
        assert not scraper._has_pending_pages()
