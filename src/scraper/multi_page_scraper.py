"""Multi-page restaurant website scraper with intelligent navigation and data aggregation."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Tuple
from collections import deque
import time
import heapq
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from .page_discovery import PageDiscovery
from .page_classifier import PageClassifier
from .data_aggregator import DataAggregator, PageData
from .multi_page_progress import MultiPageProgressNotifier
from .multi_strategy_scraper import MultiStrategyScraper, RestaurantData


@dataclass
class MultiPageScrapingResult:
    """Result of multi-page scraping operation."""

    restaurant_name: str = ""
    pages_processed: List[str] = field(default_factory=list)
    successful_pages: List[str] = field(default_factory=list)
    failed_pages: List[str] = field(default_factory=list)
    aggregated_data: Optional[RestaurantData] = None
    processing_time: float = 0.0
    data_sources_summary: Dict[str, Any] = field(default_factory=dict)


class MultiPageScraper:
    """Orchestrates multi-page restaurant website scraping with intelligent navigation."""

    def __init__(self, max_pages: int = 10, enable_ethical_scraping: bool = True):
        """Initialize multi-page scraper.

        Args:
            max_pages: Maximum number of pages to process per website
            enable_ethical_scraping: Whether to enable ethical scraping features
        """
        self.max_pages = max_pages
        self.enable_ethical_scraping = enable_ethical_scraping

        # Initialize components
        self.page_discovery = None  # Will be created per website
        self.page_classifier = PageClassifier()
        self.data_aggregator = DataAggregator()
        self.progress_notifier = MultiPageProgressNotifier()
        self.multi_strategy_scraper = MultiStrategyScraper(enable_ethical_scraping)

        # Queue management
        self._page_queue = None
        self._visited_pages = set()
        self._queue_strategy = "BFS"
        self._queue_lock = threading.Lock()
        self._priority_queue = []  # For priority-based ordering

        # Concurrent fetching statistics
        self._concurrent_stats = {
            "successful_fetches": 0,
            "failed_fetches": 0,
            "total_time": 0.0,
        }

        # Error handling
        self._error_log = []
        self._error_stats = {
            "total_errors": 0,
            "error_types": {},
            "retryable_errors": 0,
            "non_retryable_errors": 0,
        }

    def scrape_website(
        self, url: str, progress_callback: Optional[Callable] = None
    ) -> MultiPageScrapingResult:
        """Scrape a restaurant website with multi-page navigation.

        Args:
            url: Starting URL of the restaurant website
            progress_callback: Optional callback for progress updates

        Returns:
            MultiPageScrapingResult with aggregated data
        """
        start_time = time.time()
        result = MultiPageScrapingResult()

        try:
            # Initialize page discovery for this website
            self.page_discovery = PageDiscovery(url, self.max_pages)

            # Reset data aggregator for this website
            self.data_aggregator = DataAggregator()

            # Fetch initial page to start discovery
            initial_html = self._fetch_page(url)
            if not initial_html:
                result.failed_pages.append(url)
                return result

            # Discover all relevant pages with configurable depth
            max_depth = getattr(self, 'max_crawl_depth', 2)  # Default to 2 if not set
            discovered_pages = self.page_discovery.discover_all_pages(url, initial_html, max_depth)

            # Extract restaurant name from initial page for progress tracking
            restaurant_name = self._extract_restaurant_name(initial_html)
            result.restaurant_name = restaurant_name

            # Notify pages discovered
            if progress_callback:
                self.progress_notifier.notify_pages_discovered(
                    restaurant_name, discovered_pages, progress_callback
                )

            # Process all discovered pages
            page_results = self.process_discovered_pages(
                discovered_pages, progress_callback
            )

            # Update result with page processing outcomes
            result.pages_processed = discovered_pages
            result.successful_pages = page_results.successful_pages
            result.failed_pages = page_results.failed_pages

            # Aggregate data from all successful pages
            result.aggregated_data = self.data_aggregator.aggregate()
            result.data_sources_summary = (
                self.data_aggregator.get_data_sources_summary()
            )

            # Notify completion
            if progress_callback:
                self.progress_notifier.notify_restaurant_complete(
                    len(result.successful_pages),
                    len(result.failed_pages),
                    progress_callback,
                )

        except Exception as e:
            # Handle any unexpected errors
            result.failed_pages.append(url)
            if progress_callback:
                progress_callback(f"Error processing {url}: {str(e)}")

        finally:
            result.processing_time = time.time() - start_time

        return result

    def process_discovered_pages(
        self, pages: List[str], progress_callback: Optional[Callable] = None
    ) -> "PageProcessingResult":
        """Process a list of discovered pages.

        Args:
            pages: List of page URLs to process
            progress_callback: Optional progress callback

        Returns:
            PageProcessingResult with success/failure lists
        """
        result = PageProcessingResult()

        # Initialize progress tracking
        restaurant_name = (
            self.data_aggregator.page_data[0].restaurant_name
            if self.data_aggregator.page_data
            else "Restaurant"
        )
        self.progress_notifier.initialize_restaurant(restaurant_name, pages)

        for i, page_url in enumerate(pages):
            try:
                # Process individual page
                page_result = self._fetch_and_process_page(page_url)

                if page_result:
                    result.successful_pages.append(page_url)

                    # Add page data to aggregator
                    page_data = PageData(
                        url=page_url,
                        page_type=page_result["page_type"],
                        source=page_result["data"].sources[0]
                        if page_result["data"].sources
                        else "unknown",
                        restaurant_name=page_result["data"].name,
                        address=page_result["data"].address,
                        phone=page_result["data"].phone,
                        hours=page_result["data"].hours,
                        price_range=page_result["data"].price_range,
                        cuisine=page_result["data"].cuisine,
                        menu_items=page_result["data"].menu_items,
                        social_media=page_result["data"].social_media,
                        confidence=page_result["data"].confidence,
                    )

                    self.data_aggregator.add_page_data(page_data)

                    # Notify success
                    if progress_callback:
                        self.progress_notifier.notify_page_complete(
                            page_url, page_result["page_type"], True, progress_callback
                        )
                else:
                    result.failed_pages.append(page_url)

                    # Notify failure
                    if progress_callback:
                        self.progress_notifier.notify_page_complete(
                            page_url, "unknown", False, progress_callback
                        )

            except Exception as e:
                result.failed_pages.append(page_url)
                if progress_callback:
                    self.progress_notifier.notify_page_complete(
                        page_url, "unknown", False, progress_callback
                    )

        return result

    def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch HTML content from a URL.

        Args:
            url: URL to fetch

        Returns:
            HTML content or None if failed
        """
        try:
            if (
                self.enable_ethical_scraping
                and self.multi_strategy_scraper.ethical_scraper
            ):
                # Use ethical scraper with rate limiting
                html_content = (
                    self.multi_strategy_scraper.ethical_scraper.fetch_page_with_retry(
                        url
                    )
                )
                return html_content
            else:
                # Fallback method for testing
                import requests

                response = requests.get(url, timeout=30)
                response.raise_for_status()
                return response.text

        except Exception:
            return None

    def _fetch_and_process_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch and process a single page.

        Args:
            url: URL to fetch and process

        Returns:
            Dictionary with page_type and extracted data, or None if failed
        """
        # Fetch page content
        html_content = self._fetch_page(url)
        if not html_content:
            return None

        # Classify page type
        page_type = self.page_classifier.classify_page(url, html_content)

        # Extract restaurant data using multi-strategy approach
        restaurant_data = self.multi_strategy_scraper.scrape_url(url)

        if not restaurant_data:
            # If multi-strategy fails, create minimal data
            restaurant_data = RestaurantData(sources=["heuristic"])

        return {"page_type": page_type, "data": restaurant_data}

    def _extract_restaurant_name(self, html_content: str) -> str:
        """Extract restaurant name from HTML content for progress tracking.

        Args:
            html_content: HTML content to analyze

        Returns:
            Restaurant name or default
        """
        try:
            # Use multi-strategy scraper to extract basic info
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, "html.parser")

            # Try to find restaurant name in title or h1
            title = soup.find("title")
            if title:
                return title.get_text().strip().split("|")[0].split("-")[0].strip()

            h1 = soup.find("h1")
            if h1:
                return h1.get_text().strip()

            return "Restaurant"

        except Exception:
            return "Restaurant"

    def get_current_progress(self) -> Optional[Dict[str, Any]]:
        """Get current progress information.

        Returns:
            Current progress summary or None
        """
        return self.progress_notifier.get_current_progress_summary()

    # Queue Management Methods

    def _initialize_page_queue(self):
        """Initialize the page queue for processing."""
        with self._queue_lock:
            self._page_queue = deque()
            self._visited_pages.clear()
            self._priority_queue.clear()

    def _add_pages_to_queue(self, pages: List[str], strategy: str = "BFS"):
        """Add pages to the processing queue.

        Args:
            pages: List of page URLs to add
            strategy: Queue strategy ("BFS" for breadth-first, "DFS" for depth-first)
        """
        with self._queue_lock:
            self._queue_strategy = strategy

            # Remove duplicates and already visited pages
            unique_pages = []
            existing_in_queue = set(self._page_queue)
            for page in pages:
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

    def _add_pages_to_queue_with_priority(
        self, pages_with_priority: List[Tuple[str, int]]
    ):
        """Add pages to queue with priority ordering.

        Args:
            pages_with_priority: List of (url, priority) tuples
        """
        with self._queue_lock:
            for url, priority in pages_with_priority:
                if url not in self._visited_pages:
                    # Use negative priority for max-heap behavior
                    heapq.heappush(self._priority_queue, (-priority, url))

    def _get_next_page(self) -> Optional[str]:
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

    def _has_pending_pages(self) -> bool:
        """Check if there are pending pages in the queue.

        Returns:
            True if there are pages to process
        """
        with self._queue_lock:
            return len(self._page_queue) > 0 or len(self._priority_queue) > 0

    def _clear_page_queue(self):
        """Clear all pages from the queue."""
        with self._queue_lock:
            self._page_queue.clear()
            self._priority_queue.clear()

    def _get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics.

        Returns:
            Dictionary with queue statistics
        """
        with self._queue_lock:
            return {
                "total_queued": len(self._page_queue) + len(self._priority_queue),
                "pending": len(self._page_queue) + len(self._priority_queue),
                "visited": len(self._visited_pages),
                "strategy": self._queue_strategy,
            }

    # Traversal Strategy Methods

    def _get_traversal_strategy(self) -> str:
        """Get the current traversal strategy.

        Returns:
            Current traversal strategy ("BFS" or "DFS")
        """
        return self._queue_strategy

    def _set_traversal_strategy(self, strategy: str):
        """Set the traversal strategy.

        Args:
            strategy: Traversal strategy ("BFS" or "DFS")
        """
        if strategy in ["BFS", "DFS"]:
            self._queue_strategy = strategy
        else:
            raise ValueError(f"Invalid traversal strategy: {strategy}")

    def _breadth_first_traversal(
        self, start_url: str, max_depth: Optional[int] = None
    ) -> List[str]:
        """Perform breadth-first traversal of website pages.

        Args:
            start_url: Starting URL for traversal
            max_depth: Maximum depth to traverse (optional)

        Returns:
            List of visited URLs in BFS order
        """
        visited_order = []
        self._initialize_page_queue()
        self._add_pages_to_queue([start_url], strategy="BFS")

        current_depth = 0
        pages_at_current_depth = 1
        pages_at_next_depth = 0

        while self._has_pending_pages():
            if max_depth is not None and current_depth >= max_depth:
                break

            if pages_at_current_depth == 0:
                # Move to next depth level
                current_depth += 1
                pages_at_current_depth = pages_at_next_depth
                pages_at_next_depth = 0
                continue

            current_url = self._get_next_page()
            if current_url is None:
                break

            visited_order.append(current_url)
            pages_at_current_depth -= 1

            # Fetch page and discover new links
            try:
                html_content = self._fetch_page(current_url)
                if html_content:
                    # Discover new pages from this page
                    if self.page_discovery is None:
                        self.page_discovery = PageDiscovery(current_url, self.max_pages)

                    new_links = self.page_discovery.discover_navigation_links(
                        html_content
                    )
                    relevant_links = self.page_discovery.filter_relevant_pages(
                        new_links
                    )

                    # Add new links to queue for next depth level
                    new_pages = list(relevant_links)
                    if new_pages:
                        self._add_pages_to_queue(new_pages, strategy="BFS")
                        pages_at_next_depth += len(
                            [p for p in new_pages if p not in self._visited_pages]
                        )
            except Exception:
                # Continue traversal even if individual pages fail
                continue

        return visited_order

    def _depth_first_traversal(
        self, start_url: str, max_depth: Optional[int] = None
    ) -> List[str]:
        """Perform depth-first traversal of website pages.

        Args:
            start_url: Starting URL for traversal
            max_depth: Maximum depth to traverse (optional)

        Returns:
            List of visited URLs in DFS order
        """
        visited_order = []
        self._initialize_page_queue()

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
                html_content = self._fetch_page(url)
                if html_content:
                    if self.page_discovery is None:
                        self.page_discovery = PageDiscovery(url, self.max_pages)

                    new_links = self.page_discovery.discover_navigation_links(
                        html_content
                    )
                    relevant_links = self.page_discovery.filter_relevant_pages(
                        new_links
                    )

                    # Recursively visit each new link (depth-first)
                    for link in relevant_links:
                        if link not in self._visited_pages:
                            _dfs_recursive(link, current_depth + 1)
            except Exception:
                # Continue traversal even if individual pages fail
                pass

        _dfs_recursive(start_url)
        return visited_order

    def _priority_traversal(self, start_url: str) -> List[str]:
        """Perform priority-based traversal of website pages.

        Args:
            start_url: Starting URL for traversal

        Returns:
            List of visited URLs in priority order
        """
        visited_order = []
        self._initialize_page_queue()

        # Get page priorities from PageDiscovery
        if self.page_discovery is None:
            self.page_discovery = PageDiscovery(start_url, self.max_pages)

        # Start with initial page
        self._visited_pages.add(start_url)
        visited_order.append(start_url)

        try:
            # Fetch initial page and discover links
            html_content = self._fetch_page(start_url)
            if html_content:
                new_links = self.page_discovery.discover_navigation_links(html_content)
                relevant_links = self.page_discovery.filter_relevant_pages(new_links)

                # Get priorities for each link
                pages_with_priority = []
                for link in relevant_links:
                    # Use PageDiscovery priority system
                    priority_pages = self.page_discovery.prioritize_pages({link})
                    if priority_pages:
                        # Higher priority pages come first in the list
                        priority = len(priority_pages) - list(priority_pages).index(
                            link
                        )
                        pages_with_priority.append((link, priority))

                # Add to priority queue
                self._add_pages_to_queue_with_priority(pages_with_priority)

                # Process pages in priority order
                while self._has_pending_pages():
                    current_url = self._get_next_page()
                    if current_url is None:
                        break
                    visited_order.append(current_url)
        except Exception:
            # Continue even if errors occur
            pass

        return visited_order

    def _get_traversal_stats(self) -> Dict[str, Any]:
        """Get traversal statistics.

        Returns:
            Dictionary with traversal statistics
        """
        return {
            "pages_discovered": len(self._visited_pages)
            + len(self._page_queue)
            + len(self._priority_queue),
            "pages_processed": len(self._visited_pages),
            "pages_failed": 0,  # Would need to track failures separately
            "traversal_strategy": self._queue_strategy,
        }

    # Concurrent Fetching Methods

    def _fetch_pages_concurrently(
        self,
        pages: List[str],
        max_workers: int = 3,
        throttle_delay: float = 0.0,
        timeout: Optional[float] = None,
        progress_callback: Optional[Callable] = None,
    ) -> List[Optional[str]]:
        """Fetch multiple pages concurrently with optional throttling.

        Args:
            pages: List of page URLs to fetch
            max_workers: Maximum number of concurrent workers
            throttle_delay: Delay between requests in seconds
            timeout: Timeout for individual requests
            progress_callback: Optional progress callback

        Returns:
            List of HTML content (None for failed fetches), maintaining input order
        """
        start_time = time.time()
        results = [None] * len(pages)  # Maintain order

        # Reset statistics
        self._concurrent_stats.update(
            {"successful_fetches": 0, "failed_fetches": 0, "total_time": 0.0}
        )

        def fetch_with_index(url_index_tuple):
            url, index = url_index_tuple
            try:
                if throttle_delay > 0:
                    time.sleep(throttle_delay)

                if progress_callback:
                    progress_callback(f"Fetching page: {url}")

                # Apply timeout if specified (simplified for testing)
                if timeout:
                    # Use a simple approach for timeout testing
                    start_time = time.time()
                    html_content = self._fetch_page(url)
                    elapsed = time.time() - start_time

                    # If the request took longer than timeout, return None
                    if elapsed > timeout:
                        return index, None
                    return index, html_content
                else:
                    html_content = self._fetch_page(url)
                    return index, html_content

            except Exception:
                return index, None

        # Create URL-index pairs to maintain order
        url_index_pairs = [(url, i) for i, url in enumerate(pages)]

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_index = {
                executor.submit(fetch_with_index, url_index): url_index[1]
                for url_index in url_index_pairs
            }

            # Collect results as they complete
            for future in as_completed(future_to_index):
                try:
                    index, html_content = future.result()
                    results[index] = html_content

                    if html_content is not None:
                        self._concurrent_stats["successful_fetches"] += 1
                    else:
                        self._concurrent_stats["failed_fetches"] += 1

                except Exception:
                    index = future_to_index[future]
                    results[index] = None
                    self._concurrent_stats["failed_fetches"] += 1

        self._concurrent_stats["total_time"] = time.time() - start_time
        return results

    def _process_pages_concurrently(
        self,
        pages: List[str],
        max_workers: int = 3,
        progress_callback: Optional[Callable] = None,
    ) -> List[Optional[Dict[str, Any]]]:
        """Process multiple pages concurrently (fetch + process).

        Args:
            pages: List of page URLs to process
            max_workers: Maximum number of concurrent workers
            progress_callback: Optional progress callback

        Returns:
            List of processing results (None for failed processes), maintaining input order
        """
        results = [None] * len(pages)

        def process_with_index(url_index_tuple):
            url, index = url_index_tuple
            try:
                if progress_callback:
                    progress_callback(f"Processing page: {url}")

                result = self._fetch_and_process_page(url)
                return index, result

            except Exception:
                return index, None

        # Create URL-index pairs to maintain order
        url_index_pairs = [(url, i) for i, url in enumerate(pages)]

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_index = {
                executor.submit(process_with_index, url_index): url_index[1]
                for url_index in url_index_pairs
            }

            # Collect results as they complete
            for future in as_completed(future_to_index):
                try:
                    index, processing_result = future.result()
                    results[index] = processing_result

                except Exception:
                    index = future_to_index[future]
                    results[index] = None

        return results

    def _get_concurrent_fetch_stats(self) -> Dict[str, Any]:
        """Get concurrent fetching statistics.

        Returns:
            Dictionary with concurrent fetch statistics
        """
        return self._concurrent_stats.copy()

    # Error Handling Methods

    def _handle_page_error(
        self, url: str, error_type: str, error_message: str
    ) -> Dict[str, Any]:
        """Handle errors that occur during page processing.

        Args:
            url: URL where error occurred
            error_type: Type of error (e.g., "ConnectionError", "TimeoutError")
            error_message: Error message

        Returns:
            Dictionary with error details and handling instructions
        """
        error_info = {
            "url": url,
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": time.time(),
            "retry_attempted": False,
            "should_retry": self._should_retry_error(error_type),
            "retry_delay": self._get_retry_delay(error_type),
        }

        self._add_error_to_log(error_info)
        return error_info

    def _handle_http_error(self, url: str, status_code: int) -> Dict[str, Any]:
        """Handle HTTP error responses.

        Args:
            url: URL that returned the error
            status_code: HTTP status code

        Returns:
            Dictionary with error details
        """
        error_info = {
            "url": url,
            "error_type": "HTTPError",
            "status_code": status_code,
            "timestamp": time.time(),
            "should_retry": status_code in [429, 500, 502, 503, 504],
            "retry_delay": 5.0 if status_code == 429 else 1.0,
        }

        self._add_error_to_log(error_info)
        return error_info

    def _retry_failed_page(
        self, url: str, max_retries: int = 3, use_exponential_backoff: bool = False
    ) -> Optional[str]:
        """Retry fetching a failed page.

        Args:
            url: URL to retry
            max_retries: Maximum number of retry attempts
            use_exponential_backoff: Whether to use exponential backoff

        Returns:
            HTML content if successful, None if all retries failed
        """
        # Try initial fetch plus retries
        for attempt in range(max_retries + 1):
            try:
                if use_exponential_backoff and attempt > 0:
                    delay = 2**attempt  # Exponential backoff: 2, 4, 8 seconds
                    time.sleep(delay)

                result = self._fetch_page(url)
                if result:
                    return result

                # If _fetch_page returns None but no exception, continue to next attempt
                if attempt == max_retries:
                    return None

            except Exception as e:
                if attempt == max_retries:
                    # Last attempt failed
                    self._handle_page_error(url, type(e).__name__, str(e))
                    return None
                continue

        return None

    def _handle_processing_error(
        self, url: str, error_type: str, error_message: str
    ) -> Dict[str, Any]:
        """Handle errors during page processing.

        Args:
            url: URL being processed
            error_type: Type of processing error
            error_message: Error message

        Returns:
            Dictionary with error handling instructions
        """
        error_info = {
            "url": url,
            "error_type": error_type,
            "error_message": error_message,
            "should_skip": error_type in ["HTMLParsingError", "JSONDecodeError"],
            "should_retry": error_type in ["TemporaryError", "RateLimitError"],
        }

        self._add_error_to_log(error_info)
        return error_info

    def _handle_dependency_error(
        self, error_type: str, error_message: str
    ) -> Dict[str, Any]:
        """Handle missing dependency errors.

        Args:
            error_type: Type of dependency error
            error_message: Error message

        Returns:
            Dictionary with error handling instructions
        """
        error_info = {
            "error_type": error_type,
            "error_message": error_message,
            "is_critical": True,
            "should_abort": True,
        }

        self._add_error_to_log(error_info)
        return error_info

    def _add_error_to_log(self, error_info: Dict[str, Any]):
        """Add error to the error log and update statistics.

        Args:
            error_info: Dictionary containing error details
        """
        self._error_log.append(error_info)

        # Update statistics
        self._error_stats["total_errors"] += 1
        error_type = error_info.get("error_type", "Unknown")
        self._error_stats["error_types"][error_type] = (
            self._error_stats["error_types"].get(error_type, 0) + 1
        )

        # Check if error should be retried based on type and other factors
        should_retry = (
            error_info.get("should_retry", False)
            or self._should_retry_error(error_type)
            or (
                error_type == "HTTPError"
                and error_info.get("status_code") in [500, 503]
            )
        )

        if should_retry:
            self._error_stats["retryable_errors"] += 1
        else:
            self._error_stats["non_retryable_errors"] += 1

    def _get_error_summary(self) -> Dict[str, Any]:
        """Get summary of all errors encountered.

        Returns:
            Dictionary with error statistics
        """
        return self._error_stats.copy()

    def _apply_error_recovery_strategy(
        self, url: str, error_info: Dict[str, Any], strategy: str = "auto"
    ) -> Dict[str, Any]:
        """Apply error recovery strategy.

        Args:
            url: URL that encountered error
            error_info: Error information
            strategy: Recovery strategy ("skip", "retry", "fallback", "auto")

        Returns:
            Dictionary with recovery action
        """
        if strategy == "skip":
            return {"action": "skip", "url": url}
        elif strategy == "retry":
            return {"action": "retry", "url": url, "max_retries": 3}
        elif strategy == "fallback":
            return {
                "action": "fallback",
                "url": url,
                "fallback_method": "simple_extract",
            }
        else:  # auto
            error_type = error_info.get("error_type")
            if error_type == "HTTPError" and error_info.get("status_code") == 404:
                return {"action": "skip", "url": url}
            elif error_type in ["TimeoutError", "ConnectionError"]:
                return {"action": "retry", "url": url, "max_retries": 2}
            else:
                return {"action": "fallback", "url": url}

    def _is_critical_error(self, error_info: Dict[str, Any]) -> bool:
        """Check if an error is critical and should stop processing.

        Args:
            error_info: Error information

        Returns:
            True if error is critical
        """
        critical_error_types = [
            "MemoryError",
            "PermissionError",
            "ImportError",
            "SystemExit",
        ]
        return error_info.get("error_type") in critical_error_types

    def _log_error(self, error_info: Dict[str, Any]):
        """Log error information.

        Args:
            error_info: Error details to log
        """
        self._error_log.append(error_info)

    def _get_logged_errors(self) -> List[Dict[str, Any]]:
        """Get all logged errors.

        Returns:
            List of logged error dictionaries
        """
        return self._error_log.copy()

    def _handle_partial_failures(self, pages: List[str]) -> Dict[str, Any]:
        """Handle partial failures in multi-page processing.

        Args:
            pages: List of pages to process

        Returns:
            Dictionary with processing results
        """
        successful_pages = []
        failed_pages = []

        for page in pages:
            try:
                result = self._fetch_and_process_page(page)
                if result:
                    successful_pages.append(page)
                else:
                    failed_pages.append(page)
            except Exception:
                failed_pages.append(page)

        success_rate = len(successful_pages) / len(pages) if pages else 0

        return {
            "successful_pages": successful_pages,
            "failed_pages": failed_pages,
            "success_rate": success_rate,
            "should_continue": success_rate >= 0.3,  # Continue if at least 30% success
        }

    def _calculate_error_rate(self, window_seconds: int = 60) -> float:
        """Calculate error rate within a time window.

        Args:
            window_seconds: Time window in seconds

        Returns:
            Error rate (0.0 to 1.0)
        """
        current_time = time.time()
        recent_errors = [
            error
            for error in self._error_log
            if current_time - error.get("timestamp", 0) <= window_seconds
        ]

        # Simple approximation: errors per minute
        return len(recent_errors) / max(1, window_seconds / 60)

    def _should_trigger_circuit_breaker(
        self, error_rate: float, threshold: float = 0.8
    ) -> bool:
        """Check if circuit breaker should be triggered.

        Args:
            error_rate: Current error rate
            threshold: Error rate threshold

        Returns:
            True if circuit breaker should trigger
        """
        return error_rate > threshold

    def _log_error_with_context(self, error_info: Dict[str, Any]):
        """Log error with additional context.

        Args:
            error_info: Error information including context
        """
        self._error_log.append(error_info)

    def _should_retry_error(self, error_type: str) -> bool:
        """Determine if an error type should be retried.

        Args:
            error_type: Type of error

        Returns:
            True if error should be retried
        """
        retryable_errors = [
            "TimeoutError",
            "ConnectionError",
            "TemporaryError",
            "RateLimitError",
        ]
        return error_type in retryable_errors

    def _get_retry_delay(self, error_type: str) -> float:
        """Get retry delay for different error types.

        Args:
            error_type: Type of error

        Returns:
            Delay in seconds before retry
        """
        delays = {
            "TimeoutError": 2.0,
            "ConnectionError": 1.0,
            "RateLimitError": 5.0,
            "TemporaryError": 3.0,
        }
        return delays.get(error_type, 1.0)


@dataclass
class PageProcessingResult:
    """Result of processing multiple pages."""

    successful_pages: List[str] = field(default_factory=list)
    failed_pages: List[str] = field(default_factory=list)
