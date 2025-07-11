"""Multi-page scraping result handling and data aggregation."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
import time

from .data_aggregator import DataAggregator, PageData
from .multi_page_progress import MultiPageProgressNotifier
from .multi_strategy_scraper import RestaurantData


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


@dataclass
class PageProcessingResult:
    """Result of processing multiple pages."""

    successful_pages: List[str] = field(default_factory=list)
    failed_pages: List[str] = field(default_factory=list)


class MultiPageResultHandler:
    """Handles result collection, data aggregation, and result creation for multi-page scraping."""

    def __init__(
        self,
        progress_notifier: MultiPageProgressNotifier,
        data_aggregator: DataAggregator,
        page_processor: Any  # Avoiding circular import
    ):
        """Initialize result handler.

        Args:
            progress_notifier: Progress notification handler
            data_aggregator: Data aggregation handler
            page_processor: Page processing handler
        """
        self.progress_notifier = progress_notifier
        self.data_aggregator = data_aggregator
        self.page_processor = page_processor

    def create_scraping_result(
        self,
        restaurant_name: str = "",
        pages_processed: Optional[List[str]] = None
    ) -> MultiPageScrapingResult:
        """Create a new MultiPageScrapingResult.

        Args:
            restaurant_name: Name of the restaurant
            pages_processed: List of processed pages

        Returns:
            New MultiPageScrapingResult instance
        """
        return MultiPageScrapingResult(
            restaurant_name=restaurant_name,
            pages_processed=pages_processed or []
        )

    def process_discovered_pages(
        self, pages: List[str], progress_callback: Optional[Callable] = None
    ) -> PageProcessingResult:
        """Process a list of discovered pages.

        Args:
            pages: List of page URLs to process
            progress_callback: Optional progress callback

        Returns:
            PageProcessingResult with success/failure lists
        """
        result = PageProcessingResult()

        # Initialize progress tracking
        restaurant_name = self._extract_restaurant_name_from_data()
        self.progress_notifier.initialize_restaurant(restaurant_name, pages)

        for i, page_url in enumerate(pages):
            try:
                # Process individual page
                page_result = self.page_processor._fetch_and_process_page(page_url)

                if page_result:
                    result.successful_pages.append(page_url)

                    # Create PageData from result
                    page_data = self._create_page_data_from_result(page_url, page_result)
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

    def finalize_scraping_result(
        self,
        result: MultiPageScrapingResult,
        start_time: float,
        end_time: float
    ) -> MultiPageScrapingResult:
        """Finalize scraping result with aggregated data.

        Args:
            result: Partial scraping result to finalize
            start_time: Processing start time
            end_time: Processing end time

        Returns:
            Finalized MultiPageScrapingResult
        """
        # Aggregate data from all successful pages
        result.aggregated_data = self.data_aggregator.aggregate()
        result.data_sources_summary = self.data_aggregator.get_data_sources_summary()
        result.processing_time = end_time - start_time

        return result

    def notify_completion(
        self,
        successful_count: int,
        failed_count: int,
        progress_callback: Optional[Callable] = None
    ) -> None:
        """Notify completion of processing.

        Args:
            successful_count: Number of successfully processed pages
            failed_count: Number of failed pages
            progress_callback: Optional progress callback
        """
        if progress_callback:
            self.progress_notifier.notify_restaurant_complete(
                successful_count,
                failed_count,
                progress_callback,
            )

    def _extract_restaurant_name_from_data(self) -> str:
        """Extract restaurant name from existing page data for progress tracking.

        Returns:
            Restaurant name or default fallback
        """
        if self.data_aggregator.page_data:
            for page in self.data_aggregator.page_data:
                if hasattr(page, 'restaurant_name') and page.restaurant_name:
                    return page.restaurant_name
        
        return "Restaurant"

    def _create_page_data_from_result(self, url: str, page_result: Dict[str, Any]) -> PageData:
        """Create PageData from processing result.

        Args:
            url: Page URL
            page_result: Result from page processing

        Returns:
            PageData object
        """
        data = page_result["data"]
        
        return PageData(
            url=url,
            page_type=page_result["page_type"],
            source=data.sources[0] if data.sources else "unknown",
            restaurant_name=data.name,
            address=data.address,
            phone=data.phone,
            hours=data.hours,
            price_range=data.price_range,
            cuisine=data.cuisine,
            website=data.website,
            menu_items=data.menu_items,
            social_media=data.social_media,
            confidence=data.confidence,
        )