"""Unit tests for PageQueueManager class."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from collections import deque
import threading
import time
from typing import List, Dict, Any, Tuple, Optional, Callable

# Import PageQueueManager (to be created)
try:
    from src.scraper.page_queue_manager import PageQueueManager
except ImportError:
    # Will fail initially - this is expected in TDD
    PageQueueManager = None


class TestPageQueueManagerInitialization:
    """Test PageQueueManager initialization."""

    def test_default_initialization(self):
        """Test default initialization of PageQueueManager."""
        if PageQueueManager is None:
            pytest.skip("PageQueueManager not implemented yet")
        
        manager = PageQueueManager()
        
        assert manager.max_pages == 10  # Default max pages
        assert manager.get_traversal_strategy() == "BFS"  # Default strategy
        assert not manager.has_pending_pages()

    def test_initialization_with_max_pages(self):
        """Test initialization with custom max pages."""
        if PageQueueManager is None:
            pytest.skip("PageQueueManager not implemented yet")
        
        manager = PageQueueManager(max_pages=5)
        
        assert manager.max_pages == 5
        assert not manager.has_pending_pages()

    def test_initialization_with_strategy(self):
        """Test initialization with custom strategy."""
        if PageQueueManager is None:
            pytest.skip("PageQueueManager not implemented yet")
        
        manager = PageQueueManager(default_strategy="DFS")
        
        assert manager.get_traversal_strategy() == "DFS"


class TestPageQueueManagerBasicOperations:
    """Test basic queue operations."""

    @pytest.fixture
    def queue_manager(self):
        """Create a PageQueueManager for testing."""
        if PageQueueManager is None:
            pytest.skip("PageQueueManager not implemented yet")
        return PageQueueManager(max_pages=5)

    def test_initialize_page_queue(self, queue_manager):
        """Test initializing the page queue."""
        queue_manager.initialize_page_queue()
        
        assert not queue_manager.has_pending_pages()
        stats = queue_manager.get_queue_stats()
        assert stats["pending"] == 0
        assert stats["visited"] == 0

    def test_add_pages_to_queue_bfs(self, queue_manager):
        """Test adding pages with BFS strategy."""
        queue_manager.initialize_page_queue()
        pages = ["http://example.com/", "http://example.com/menu", "http://example.com/contact"]
        
        queue_manager.add_pages_to_queue(pages, "BFS")
        
        assert queue_manager.has_pending_pages()
        stats = queue_manager.get_queue_stats()
        assert stats["pending"] == 3
        
        # Check FIFO order
        assert queue_manager.get_next_page() == "http://example.com/"
        assert queue_manager.get_next_page() == "http://example.com/menu"
        assert queue_manager.get_next_page() == "http://example.com/contact"

    def test_add_pages_to_queue_dfs(self, queue_manager):
        """Test adding pages with DFS strategy."""
        queue_manager.initialize_page_queue()
        pages = ["http://example.com/", "http://example.com/menu", "http://example.com/contact"]
        
        queue_manager.add_pages_to_queue(pages, "DFS")
        
        assert queue_manager.has_pending_pages()
        stats = queue_manager.get_queue_stats()
        assert stats["pending"] == 3
        
        # Check LIFO order (reverse of input)
        assert queue_manager.get_next_page() == "http://example.com/contact"
        assert queue_manager.get_next_page() == "http://example.com/menu"
        assert queue_manager.get_next_page() == "http://example.com/"

    def test_add_pages_to_queue_with_priority(self, queue_manager):
        """Test adding pages with priority."""
        queue_manager.initialize_page_queue()
        pages_with_priority = [
            ("http://example.com/about", 1),
            ("http://example.com/menu", 10),
            ("http://example.com/contact", 5),
        ]
        
        queue_manager.add_pages_to_queue_with_priority(pages_with_priority)
        
        # Should return highest priority first
        assert queue_manager.get_next_page() == "http://example.com/menu"
        assert queue_manager.get_next_page() == "http://example.com/contact"
        assert queue_manager.get_next_page() == "http://example.com/about"

    def test_get_next_page_empty_queue(self, queue_manager):
        """Test getting next page from empty queue."""
        queue_manager.initialize_page_queue()
        
        assert queue_manager.get_next_page() is None

    def test_has_pending_pages(self, queue_manager):
        """Test checking if queue has pending pages."""
        queue_manager.initialize_page_queue()
        
        # Initially empty
        assert not queue_manager.has_pending_pages()
        
        # Add pages
        queue_manager.add_pages_to_queue(["http://example.com/menu"])
        assert queue_manager.has_pending_pages()
        
        # Remove page
        queue_manager.get_next_page()
        assert not queue_manager.has_pending_pages()

    def test_clear_page_queue(self, queue_manager):
        """Test clearing the page queue."""
        queue_manager.initialize_page_queue()
        pages = ["http://example.com/menu", "http://example.com/contact"]
        queue_manager.add_pages_to_queue(pages)
        
        assert queue_manager.has_pending_pages()
        
        queue_manager.clear_page_queue()
        
        assert not queue_manager.has_pending_pages()
        stats = queue_manager.get_queue_stats()
        assert stats["pending"] == 0


class TestPageQueueManagerDuplicatePrevention:
    """Test duplicate prevention functionality."""

    @pytest.fixture
    def queue_manager(self):
        """Create a PageQueueManager for testing."""
        if PageQueueManager is None:
            pytest.skip("PageQueueManager not implemented yet")
        return PageQueueManager()

    def test_prevents_duplicate_pages(self, queue_manager):
        """Test that queue prevents adding duplicate pages."""
        queue_manager.initialize_page_queue()
        pages = [
            "http://example.com/menu",
            "http://example.com/menu",  # Duplicate
            "http://example.com/contact",
        ]
        
        queue_manager.add_pages_to_queue(pages)
        
        stats = queue_manager.get_queue_stats()
        assert stats["pending"] == 2  # Only 2 unique pages
        
        # Verify both unique pages are present
        retrieved_pages = set()
        while queue_manager.has_pending_pages():
            page = queue_manager.get_next_page()
            retrieved_pages.add(page)
        
        assert "http://example.com/menu" in retrieved_pages
        assert "http://example.com/contact" in retrieved_pages
        assert len(retrieved_pages) == 2

    def test_prevents_duplicate_across_queue_types(self, queue_manager):
        """Test preventing duplicates across regular and priority queues."""
        queue_manager.initialize_page_queue()
        
        # Add to regular queue
        queue_manager.add_pages_to_queue(["http://example.com/menu"])
        
        # Try to add same page to priority queue
        queue_manager.add_pages_to_queue_with_priority([("http://example.com/menu", 10)])
        
        # Should only have one page total
        pages_retrieved = []
        while queue_manager.has_pending_pages():
            pages_retrieved.append(queue_manager.get_next_page())
        
        assert len(pages_retrieved) == 1
        assert pages_retrieved[0] == "http://example.com/menu"

    def test_prevents_adding_visited_pages(self, queue_manager):
        """Test that visited pages are not added again."""
        queue_manager.initialize_page_queue()
        
        # Add and retrieve a page
        queue_manager.add_pages_to_queue(["http://example.com/menu"])
        visited_page = queue_manager.get_next_page()
        
        # Try to add the same page again
        queue_manager.add_pages_to_queue([visited_page])
        
        # Should not be added to queue
        assert not queue_manager.has_pending_pages()


class TestPageQueueManagerLimits:
    """Test queue limits and constraints."""

    @pytest.fixture
    def limited_queue_manager(self):
        """Create a PageQueueManager with limited pages."""
        if PageQueueManager is None:
            pytest.skip("PageQueueManager not implemented yet")
        return PageQueueManager(max_pages=3)

    def test_respects_max_pages_limit(self, limited_queue_manager):
        """Test that queue respects maximum pages limit."""
        limited_queue_manager.initialize_page_queue()
        
        # Try to add more pages than limit
        pages = [f"http://example.com/page{i}" for i in range(5)]
        limited_queue_manager.add_pages_to_queue(pages)
        
        stats = limited_queue_manager.get_queue_stats()
        assert stats["pending"] <= 3

    def test_max_pages_includes_visited_pages(self, limited_queue_manager):
        """Test that max pages limit includes visited pages."""
        limited_queue_manager.initialize_page_queue()
        
        # Add and process some pages
        pages = ["http://example.com/page1", "http://example.com/page2"]
        limited_queue_manager.add_pages_to_queue(pages)
        
        # Process one page
        limited_queue_manager.get_next_page()
        
        # Try to add more pages
        new_pages = ["http://example.com/page3", "http://example.com/page4"]
        limited_queue_manager.add_pages_to_queue(new_pages)
        
        stats = limited_queue_manager.get_queue_stats()
        total_pages = stats["pending"] + stats["visited"]
        assert total_pages <= 3


class TestPageQueueManagerTraversalStrategies:
    """Test traversal strategy functionality."""

    @pytest.fixture
    def queue_manager(self):
        """Create a PageQueueManager for testing."""
        if PageQueueManager is None:
            pytest.skip("PageQueueManager not implemented yet")
        return PageQueueManager()

    def test_get_traversal_strategy(self, queue_manager):
        """Test getting current traversal strategy."""
        strategy = queue_manager.get_traversal_strategy()
        assert strategy in ["BFS", "DFS"]

    def test_set_traversal_strategy(self, queue_manager):
        """Test setting traversal strategy."""
        queue_manager.set_traversal_strategy("BFS")
        assert queue_manager.get_traversal_strategy() == "BFS"
        
        queue_manager.set_traversal_strategy("DFS")
        assert queue_manager.get_traversal_strategy() == "DFS"

    def test_set_invalid_traversal_strategy(self, queue_manager):
        """Test setting invalid traversal strategy raises error."""
        with pytest.raises(ValueError):
            queue_manager.set_traversal_strategy("INVALID")

    def test_breadth_first_traversal(self, queue_manager):
        """Test breadth-first traversal functionality."""
        def mock_page_fetcher(url):
            # Mock hierarchical structure
            if url == "http://example.com/":
                return ["http://example.com/level1-a", "http://example.com/level1-b"]
            elif url == "http://example.com/level1-a":
                return ["http://example.com/level2-a"]
            elif url == "http://example.com/level1-b":
                return ["http://example.com/level2-b"]
            return []
        
        visited_order = queue_manager.breadth_first_traversal(
            "http://example.com/", page_fetcher=mock_page_fetcher
        )
        
        # Should visit level 1 pages before level 2 pages
        level1_indices = [i for i, url in enumerate(visited_order) if "level1" in url]
        level2_indices = [i for i, url in enumerate(visited_order) if "level2" in url]
        
        if level1_indices and level2_indices:
            assert max(level1_indices) < min(level2_indices)

    def test_depth_first_traversal(self, queue_manager):
        """Test depth-first traversal functionality."""
        def mock_page_fetcher(url):
            # Mock hierarchical structure
            if url == "http://example.com/":
                return ["http://example.com/branch1", "http://example.com/branch2"]
            elif url == "http://example.com/branch1":
                return ["http://example.com/branch1/deep"]
            elif url == "http://example.com/branch2":
                return ["http://example.com/branch2/deep"]
            return []
        
        visited_order = queue_manager.depth_first_traversal(
            "http://example.com/", page_fetcher=mock_page_fetcher
        )
        
        # Should explore one branch completely before the other
        branch1_indices = [i for i, url in enumerate(visited_order) if "branch1" in url]
        branch2_indices = [i for i, url in enumerate(visited_order) if "branch2" in url]
        
        if branch1_indices and branch2_indices:
            # Either all branch1 comes before branch2, or vice versa
            branch1_complete_first = max(branch1_indices) < min(branch2_indices)
            branch2_complete_first = max(branch2_indices) < min(branch1_indices)
            assert branch1_complete_first or branch2_complete_first

    def test_priority_traversal(self, queue_manager):
        """Test priority-based traversal functionality."""
        def mock_page_fetcher(url):
            if url == "http://example.com/":
                return ["http://example.com/menu", "http://example.com/blog", "http://example.com/contact"]
            return []
        
        def mock_prioritizer(pages):
            # Mock priority: menu=10, contact=5, blog=1
            priority_map = {
                "http://example.com/menu": 10,
                "http://example.com/contact": 5,
                "http://example.com/blog": 1
            }
            return [(url, priority_map.get(url, 1)) for url in pages]
        
        visited_order = queue_manager.priority_traversal(
            "http://example.com/", 
            page_fetcher=mock_page_fetcher,
            prioritizer=mock_prioritizer
        )
        
        # High priority pages should come before low priority
        menu_index = next((i for i, url in enumerate(visited_order) if "menu" in url), -1)
        blog_index = next((i for i, url in enumerate(visited_order) if "blog" in url), -1)
        
        if menu_index >= 0 and blog_index >= 0:
            assert menu_index < blog_index

    def test_traversal_respects_max_depth(self, queue_manager):
        """Test that traversal respects maximum depth limit."""
        def mock_page_fetcher(url):
            if url == "http://example.com/":
                return ["http://example.com/level1"]
            elif url == "http://example.com/level1":
                return ["http://example.com/level2"]
            elif url == "http://example.com/level2":
                return ["http://example.com/level3"]
            elif url == "http://example.com/level3":
                return ["http://example.com/level4"]
            return []
        
        visited_order = queue_manager.breadth_first_traversal(
            "http://example.com/", page_fetcher=mock_page_fetcher, max_depth=2
        )
        
        # Should not go beyond depth 2
        assert not any("level3" in url or "level4" in url for url in visited_order)

    def test_traversal_handles_cycles(self, queue_manager):
        """Test that traversal handles circular references."""
        def mock_page_fetcher(url):
            if url == "http://example.com/":
                return ["http://example.com/page-a"]
            elif url == "http://example.com/page-a":
                return ["http://example.com/page-b"]
            elif url == "http://example.com/page-b":
                return ["http://example.com/page-a"]  # Circular reference
            return []
        
        visited_order = queue_manager.breadth_first_traversal(
            "http://example.com/", page_fetcher=mock_page_fetcher
        )
        
        # Should visit each page only once despite cycles
        unique_pages = set(visited_order)
        assert len(visited_order) == len(unique_pages)


class TestPageQueueManagerStatistics:
    """Test queue statistics functionality."""

    @pytest.fixture
    def queue_manager(self):
        """Create a PageQueueManager for testing."""
        if PageQueueManager is None:
            pytest.skip("PageQueueManager not implemented yet")
        return PageQueueManager()

    def test_get_queue_stats(self, queue_manager):
        """Test getting queue statistics."""
        queue_manager.initialize_page_queue()
        
        # Add pages
        pages = ["http://example.com/page1", "http://example.com/page2", "http://example.com/page3"]
        queue_manager.add_pages_to_queue(pages)
        
        # Process one page
        queue_manager.get_next_page()
        
        stats = queue_manager.get_queue_stats()
        
        assert "pending" in stats
        assert "visited" in stats
        assert "strategy" in stats
        assert "total_queued" in stats
        
        assert stats["pending"] == 2
        assert stats["visited"] == 1
        assert stats["total_queued"] == 2  # Currently pending

    def test_queue_stats_with_priority_queue(self, queue_manager):
        """Test queue statistics include priority queue."""
        queue_manager.initialize_page_queue()
        
        # Add regular pages
        queue_manager.add_pages_to_queue(["http://example.com/page1"])
        
        # Add priority pages
        queue_manager.add_pages_to_queue_with_priority([("http://example.com/priority", 10)])
        
        stats = queue_manager.get_queue_stats()
        assert stats["pending"] == 2
        assert stats["total_queued"] == 2


class TestPageQueueManagerThreadSafety:
    """Test thread safety of queue operations."""

    @pytest.fixture
    def queue_manager(self):
        """Create a PageQueueManager for testing."""
        if PageQueueManager is None:
            pytest.skip("PageQueueManager not implemented yet")
        return PageQueueManager()

    def test_concurrent_add_and_get_operations(self, queue_manager):
        """Test concurrent add and get operations are thread-safe."""
        queue_manager.initialize_page_queue()
        
        results = []
        errors = []
        
        def add_pages():
            try:
                for i in range(5):
                    pages = [f"http://example.com/thread1-{i}"]
                    queue_manager.add_pages_to_queue(pages)
                    time.sleep(0.001)  # Small delay to increase contention
            except Exception as e:
                errors.append(e)
        
        def get_pages():
            try:
                local_results = []
                for _ in range(3):
                    if queue_manager.has_pending_pages():
                        page = queue_manager.get_next_page()
                        if page:
                            local_results.append(page)
                    time.sleep(0.001)
                results.extend(local_results)
            except Exception as e:
                errors.append(e)
        
        # Run operations concurrently
        threads = []
        for _ in range(2):
            thread = threading.Thread(target=add_pages)
            threads.append(thread)
            thread.start()
        
        for _ in range(2):
            thread = threading.Thread(target=get_pages)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        assert len(errors) == 0
        
        # Verify results are unique (no duplicates due to race conditions)
        assert len(set(results)) == len(results)

    def test_queue_statistics_thread_safety(self, queue_manager):
        """Test that queue statistics are thread-safe."""
        queue_manager.initialize_page_queue()
        
        stats_results = []
        
        def get_stats():
            for _ in range(10):
                stats = queue_manager.get_queue_stats()
                stats_results.append(stats)
                time.sleep(0.001)
        
        def modify_queue():
            for i in range(5):
                queue_manager.add_pages_to_queue([f"http://example.com/page{i}"])
                time.sleep(0.001)
        
        # Run operations concurrently
        threads = []
        for _ in range(2):
            thread = threading.Thread(target=get_stats)
            threads.append(thread)
            thread.start()
        
        thread = threading.Thread(target=modify_queue)
        threads.append(thread)
        thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify we got some stats
        assert len(stats_results) > 0
        
        # Verify all stats have required fields
        for stats in stats_results:
            assert "pending" in stats
            assert "visited" in stats
            assert stats["pending"] >= 0
            assert stats["visited"] >= 0


class TestPageQueueManagerErrorHandling:
    """Test error handling in PageQueueManager."""

    @pytest.fixture
    def queue_manager(self):
        """Create a PageQueueManager for testing."""
        if PageQueueManager is None:
            pytest.skip("PageQueueManager not implemented yet")
        return PageQueueManager()

    def test_invalid_strategy_raises_error(self, queue_manager):
        """Test that invalid traversal strategy raises ValueError."""
        with pytest.raises(ValueError):
            queue_manager.set_traversal_strategy("INVALID_STRATEGY")

    def test_add_pages_with_invalid_strategy(self, queue_manager):
        """Test adding pages with invalid strategy."""
        queue_manager.initialize_page_queue()
        
        with pytest.raises(ValueError):
            queue_manager.add_pages_to_queue(["http://example.com/"], "INVALID")

    def test_operations_before_initialization(self, queue_manager):
        """Test operations before queue initialization."""
        # These should either work with auto-initialization or raise appropriate errors
        try:
            queue_manager.add_pages_to_queue(["http://example.com/"])
            # If no error, verify queue is initialized
            assert queue_manager.has_pending_pages()
        except RuntimeError:
            # If error is raised, it should be appropriate
            pass

    def test_traversal_with_failing_page_fetcher(self, queue_manager):
        """Test traversal continues when page fetcher fails."""
        def failing_page_fetcher(url):
            if "bad" in url:
                raise Exception("Fetch failed")
            elif url == "http://example.com/":
                return ["http://example.com/good", "http://example.com/bad"]
            return []
        
        visited_order = queue_manager.breadth_first_traversal(
            "http://example.com/", page_fetcher=failing_page_fetcher
        )
        
        # Should still visit the good pages
        assert "http://example.com/" in visited_order
        assert any("good" in url for url in visited_order)
        # Bad page might not be in visited order due to failure

    def test_empty_pages_list(self, queue_manager):
        """Test adding empty pages list."""
        queue_manager.initialize_page_queue()
        
        queue_manager.add_pages_to_queue([])
        assert not queue_manager.has_pending_pages()

    def test_none_in_pages_list(self, queue_manager):
        """Test adding pages list with None values."""
        queue_manager.initialize_page_queue()
        
        pages = ["http://example.com/good", None, "http://example.com/also-good"]
        queue_manager.add_pages_to_queue(pages)
        
        # Should filter out None values
        retrieved_pages = []
        while queue_manager.has_pending_pages():
            page = queue_manager.get_next_page()
            retrieved_pages.append(page)
        
        assert None not in retrieved_pages
        assert len(retrieved_pages) == 2


class TestPageQueueManagerIntegration:
    """Integration tests for PageQueueManager."""

    @pytest.fixture
    def queue_manager(self):
        """Create a PageQueueManager for testing."""
        if PageQueueManager is None:
            pytest.skip("PageQueueManager not implemented yet")
        return PageQueueManager(max_pages=10)

    def test_mixed_queue_and_priority_operations(self, queue_manager):
        """Test mixing regular queue and priority queue operations."""
        queue_manager.initialize_page_queue()
        
        # Add regular pages
        queue_manager.add_pages_to_queue(["http://example.com/normal1", "http://example.com/normal2"])
        
        # Add priority pages
        queue_manager.add_pages_to_queue_with_priority([
            ("http://example.com/high", 10),
            ("http://example.com/medium", 5)
        ])
        
        # Priority pages should come first
        assert queue_manager.get_next_page() == "http://example.com/high"
        assert queue_manager.get_next_page() == "http://example.com/medium"
        
        # Then regular pages
        assert queue_manager.get_next_page() == "http://example.com/normal1"
        assert queue_manager.get_next_page() == "http://example.com/normal2"

    def test_strategy_change_during_processing(self, queue_manager):
        """Test changing strategy while queue has pages."""
        queue_manager.initialize_page_queue()
        
        # Start with BFS
        queue_manager.set_traversal_strategy("BFS")
        queue_manager.add_pages_to_queue(["http://example.com/page1"], "BFS")
        
        # Change to DFS
        queue_manager.set_traversal_strategy("DFS")
        queue_manager.add_pages_to_queue(["http://example.com/page2"], "DFS")
        
        # Should still process existing pages correctly
        assert queue_manager.has_pending_pages()
        page1 = queue_manager.get_next_page()
        page2 = queue_manager.get_next_page()
        
        assert page1 is not None
        assert page2 is not None