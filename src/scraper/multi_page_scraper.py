"""Multi-page restaurant website scraper with intelligent navigation and data aggregation."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
import time

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

            # Discover all relevant pages
            discovered_pages = self.page_discovery.discover_all_pages(url, initial_html)

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


@dataclass
class PageProcessingResult:
    """Result of processing multiple pages."""

    successful_pages: List[str] = field(default_factory=list)
    failed_pages: List[str] = field(default_factory=list)
