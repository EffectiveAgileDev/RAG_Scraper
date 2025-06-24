"""Page queue management and traversal strategies for multi-page scraping.

This module provides a dedicated PageQueueManager class that handles all queue
management and traversal strategies for multi-page website scraping. It supports
various traversal algorithms including breadth-first search (BFS), depth-first 
search (DFS), and priority-based traversal.

Key Features:
- Thread-safe queue operations
- Multiple traversal strategies (BFS, DFS, Priority)
- Duplicate page prevention
- Configurable page limits
- Comprehensive statistics tracking
- Error handling and recovery

Example:
    manager = PageQueueManager(max_pages=20)
    manager.add_pages_to_queue(['http://example.com/menu'], 'BFS')
    
    def page_fetcher(url):
        # Fetch and return list of linked pages
        return fetch_page_links(url)
    
    visited = manager.breadth_first_traversal('http://example.com', page_fetcher)
"""
from collections import deque
from typing import List, Dict, Any, Optional, Callable, Tuple, Set
import threading
import heapq
import time


class PageQueueManager:
    """Manages page queues and traversal strategies for multi-page scraping."""

    def __init__(self, max_pages: int = 10, default_strategy: str = "BFS"):
        """Initialize PageQueueManager.

        Args:
            max_pages: Maximum number of pages to process
            default_strategy: Default traversal strategy ("BFS" or "DFS")
        """
        self.max_pages = max_pages
        self._default_strategy = default_strategy

        # Queue management
        self._page_queue: Optional[deque] = None
        self._visited_pages: Set[str] = set()
        self._queue_strategy = default_strategy
        self._queue_lock = threading.Lock()
        self._priority_queue: List[Tuple[int, str]] = []  # For priority-based ordering

        # Initialize queue automatically
        self.initialize_page_queue()

    def initialize_page_queue(self):
        """Initialize the page queue for processing."""
        with self._queue_lock:
            self._page_queue = deque()
            self._visited_pages.clear()
            self._priority_queue.clear()

    def add_pages_to_queue(self, pages: List[str], strategy: str = None):
        """Add pages to the processing queue.

        Args:
            pages: List of page URLs to add
            strategy: Queue strategy ("BFS" for breadth-first, "DFS" for depth-first)
                     If None, uses current strategy
        """
        if strategy is None:
            strategy = self._queue_strategy

        if strategy not in ["BFS", "DFS"]:
            raise ValueError(f"Invalid strategy: {strategy}. Must be 'BFS' or 'DFS'")

        with self._queue_lock:
            self._queue_strategy = strategy

            # Filter out None values and duplicates
            filtered_pages = [page for page in pages if page is not None]

            # Remove duplicates and already visited pages
            unique_pages = []
            existing_in_queue = set(self._page_queue) if self._page_queue else set()
            for page in filtered_pages:
                if (
                    page not in self._visited_pages
                    and page not in existing_in_queue
                    and page not in unique_pages
                ):
                    unique_pages.append(page)

            # Respect max pages limit
            current_total = len(self._page_queue) + len(self._visited_pages)
            available_slots = max(0, self.max_pages - current_total)
            unique_pages = unique_pages[:available_slots]

            if strategy == "BFS":
                # Add to the right (FIFO)
                self._page_queue.extend(unique_pages)
            elif strategy == "DFS":
                # Add to the left (LIFO) - last added will be first out
                for page in unique_pages:
                    self._page_queue.appendleft(page)

    def add_pages_to_queue_with_priority(self, pages_with_priority: List[Tuple[str, int]]):
        """Add pages to queue with priority ordering.

        Args:
            pages_with_priority: List of (url, priority) tuples
        """
        with self._queue_lock:
            # Get existing URLs from regular queue to prevent duplicates
            existing_in_queue = set(self._page_queue) if self._page_queue else set()
            existing_in_priority = {url for _, url in self._priority_queue}
            
            for url, priority in pages_with_priority:
                if (url not in self._visited_pages and 
                    url is not None and 
                    url not in existing_in_queue and 
                    url not in existing_in_priority):
                    # Use negative priority for max-heap behavior
                    heapq.heappush(self._priority_queue, (-priority, url))

    def get_next_page(self) -> Optional[str]:
        """Get the next page from the queue.

        Returns:
            Next page URL or None if queue is empty
        """
        with self._queue_lock:
            # Check priority queue first
            if self._priority_queue:
                _, url = heapq.heappop(self._priority_queue)
                self._visited_pages.add(url)
                return url

            # Then check regular queue
            if self._page_queue:
                url = self._page_queue.popleft()
                self._visited_pages.add(url)
                return url

            return None

    def has_pending_pages(self) -> bool:
        """Check if there are pending pages in the queue.

        Returns:
            True if there are pages to process
        """
        with self._queue_lock:
            queue_len = len(self._page_queue) if self._page_queue else 0
            return queue_len > 0 or len(self._priority_queue) > 0

    def clear_page_queue(self):
        """Clear all pages from the queue."""
        with self._queue_lock:
            if self._page_queue:
                self._page_queue.clear()
            self._priority_queue.clear()

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics.

        Returns:
            Dictionary with queue statistics
        """
        with self._queue_lock:
            queue_len = len(self._page_queue) if self._page_queue else 0
            priority_len = len(self._priority_queue)
            total_queued = queue_len + priority_len

            return {
                "total_queued": total_queued,
                "pending": total_queued,
                "visited": len(self._visited_pages),
                "strategy": self._queue_strategy,
            }

    # Traversal Strategy Methods

    def get_traversal_strategy(self) -> str:
        """Get the current traversal strategy.

        Returns:
            Current traversal strategy ("BFS" or "DFS")
        """
        return self._queue_strategy

    def set_traversal_strategy(self, strategy: str):
        """Set the traversal strategy.

        Args:
            strategy: Traversal strategy ("BFS" or "DFS")
        """
        if strategy not in ["BFS", "DFS"]:
            raise ValueError(f"Invalid traversal strategy: {strategy}")
        self._queue_strategy = strategy

    def breadth_first_traversal(
        self, 
        start_url: str, 
        page_fetcher: Callable[[str], List[str]],
        max_depth: Optional[int] = None
    ) -> List[str]:
        """Perform breadth-first traversal of website pages.

        Args:
            start_url: Starting URL for traversal
            page_fetcher: Function that fetches links from a page
            max_depth: Maximum depth to traverse (optional)

        Returns:
            List of visited URLs in BFS order
        """
        visited_order = []
        self.initialize_page_queue()
        self.add_pages_to_queue([start_url], strategy="BFS")

        current_depth = 0
        pages_at_current_depth = 1
        pages_at_next_depth = 0

        while self.has_pending_pages():
            if max_depth is not None and current_depth >= max_depth:
                break

            if pages_at_current_depth == 0:
                # Move to next depth level
                current_depth += 1
                pages_at_current_depth = pages_at_next_depth
                pages_at_next_depth = 0
                continue

            current_url = self.get_next_page()
            if current_url is None:
                break

            visited_order.append(current_url)
            pages_at_current_depth -= 1

            # Fetch page and discover new links
            try:
                new_links = page_fetcher(current_url)
                if new_links:
                    # Add new links to queue for next depth level
                    self.add_pages_to_queue(new_links, strategy="BFS")
                    pages_at_next_depth += len(
                        [p for p in new_links if p not in self._visited_pages and p is not None]
                    )
            except Exception:
                # Continue traversal even if individual pages fail
                continue

        return visited_order

    def depth_first_traversal(
        self, 
        start_url: str, 
        page_fetcher: Callable[[str], List[str]],
        max_depth: Optional[int] = None
    ) -> List[str]:
        """Perform depth-first traversal of website pages.

        Args:
            start_url: Starting URL for traversal
            page_fetcher: Function that fetches links from a page
            max_depth: Maximum depth to traverse (optional)

        Returns:
            List of visited URLs in DFS order
        """
        visited_order = []
        self.initialize_page_queue()

        def _dfs_recursive(url: str, current_depth: int = 0):
            if max_depth is not None and current_depth >= max_depth:
                return
            if url in self._visited_pages:
                return
            if len(visited_order) >= self.max_pages:
                return

            # Visit current page
            self._visited_pages.add(url)
            visited_order.append(url)

            try:
                # Fetch page and discover new links
                new_links = page_fetcher(url)
                if new_links:
                    # Recursively visit each new link (depth-first)
                    for link in new_links:
                        if link not in self._visited_pages and link is not None:
                            _dfs_recursive(link, current_depth + 1)
            except Exception:
                # Continue traversal even if individual pages fail
                pass

        _dfs_recursive(start_url)
        return visited_order

    def priority_traversal(
        self, 
        start_url: str, 
        page_fetcher: Callable[[str], List[str]],
        prioritizer: Optional[Callable[[List[str]], List[Tuple[str, int]]]] = None
    ) -> List[str]:
        """Perform priority-based traversal of website pages.

        Args:
            start_url: Starting URL for traversal
            page_fetcher: Function that fetches links from a page
            prioritizer: Function that assigns priorities to pages

        Returns:
            List of visited URLs in priority order
        """
        visited_order = []
        self.initialize_page_queue()

        # Start with initial page
        self._visited_pages.add(start_url)
        visited_order.append(start_url)

        try:
            # Fetch initial page and discover links
            new_links = page_fetcher(start_url)
            if new_links:
                if prioritizer:
                    # Use custom prioritizer
                    pages_with_priority = prioritizer(new_links)
                    self.add_pages_to_queue_with_priority(pages_with_priority)
                else:
                    # Default priority system
                    pages_with_priority = self._default_prioritize_pages(new_links)
                    self.add_pages_to_queue_with_priority(pages_with_priority)

                # Process pages in priority order
                while self.has_pending_pages():
                    current_url = self.get_next_page()
                    if current_url is None:
                        break
                    visited_order.append(current_url)
        except Exception:
            # Continue even if errors occur
            pass

        return visited_order

    def _default_prioritize_pages(self, pages: List[str]) -> List[Tuple[str, int]]:
        """Default page prioritization based on URL patterns.

        Args:
            pages: List of page URLs

        Returns:
            List of (url, priority) tuples
        """
        priority_keywords = {
            "menu": 10,
            "contact": 8,
            "about": 6,
            "hours": 7,
            "location": 6,
            "home": 9,
            "blog": 2,
            "news": 3,
            "events": 4,
            "careers": 1,
            "privacy": 1,
        }

        pages_with_priority = []
        for page in pages:
            if page is None:
                continue
            
            priority = 5  # Default priority
            page_lower = page.lower()
            
            for keyword, keyword_priority in priority_keywords.items():
                if keyword in page_lower:
                    priority = max(priority, keyword_priority)
                    break
            
            pages_with_priority.append((page, priority))

        return pages_with_priority

    def get_traversal_stats(self) -> Dict[str, Any]:
        """Get traversal statistics.

        Returns:
            Dictionary with traversal statistics
        """
        with self._queue_lock:
            queue_len = len(self._page_queue) if self._page_queue else 0
            priority_len = len(self._priority_queue)
            
            return {
                "pages_discovered": len(self._visited_pages) + queue_len + priority_len,
                "pages_processed": len(self._visited_pages),
                "pages_failed": 0,  # Would need to track failures separately
                "traversal_strategy": self._queue_strategy,
            }