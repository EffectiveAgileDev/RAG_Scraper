"""Progress notification system for multi-page restaurant scraping."""
import time
from typing import List, Callable, Optional
from dataclasses import dataclass


@dataclass
class MultiPageProgressState:
    """State tracking for multi-page scraping progress."""

    current_restaurant: str = ""
    total_pages: int = 0
    current_page: int = 0
    total_restaurants: int = 0
    current_restaurant_index: int = 0
    start_time: float = 0.0
    successful_pages: int = 0
    failed_pages: int = 0


class MultiPageProgressNotifier:
    """Manages progress notifications for multi-page website scraping."""

    def __init__(self):
        """Initialize progress notifier."""
        self.state = MultiPageProgressState()
        self.page_type_display_names = {
            "menu": "Menu page",
            "contact": "Contact page",
            "about": "About page",
            "home": "Home page",
            "hours": "Hours page",
            "location": "Location page",
            "info": "Info page",
            "unknown": "Page",
        }

    @property
    def current_restaurant(self) -> str:
        """Get current restaurant name."""
        return self.state.current_restaurant

    @property
    def total_pages(self) -> int:
        """Get total pages for current restaurant."""
        return self.state.total_pages

    @property
    def current_page(self) -> int:
        """Get current page index."""
        return self.state.current_page

    def initialize_batch(self, total_restaurants: int) -> None:
        """Initialize batch processing with total restaurant count.

        Args:
            total_restaurants: Total number of restaurants to process
        """
        self.state.total_restaurants = total_restaurants
        self.state.current_restaurant_index = 0

    def initialize_restaurant(self, restaurant_name: str, pages: List[str]) -> None:
        """Initialize progress tracking for a restaurant.

        Args:
            restaurant_name: Name of the restaurant
            pages: List of page URLs to process
        """
        self.state.current_restaurant = restaurant_name
        self.state.total_pages = len(pages)
        self.state.current_page = 0
        self.state.start_time = time.time()
        self.state.successful_pages = 0
        self.state.failed_pages = 0

    def notify_pages_discovered(
        self, restaurant_name: str, pages: List[str], callback: Callable
    ) -> None:
        """Notify that pages have been discovered for a restaurant.

        Args:
            restaurant_name: Name of the restaurant
            pages: List of discovered page URLs
            callback: Progress callback function
        """
        page_count = len(pages)
        message = f"Discovered {page_count} pages for {restaurant_name}"
        callback(message)

    def notify_page_start(self, url: str, page_type: str, callback: Callable) -> None:
        """Notify that processing of a page has started.

        Args:
            url: URL of the page being processed
            page_type: Type of the page (menu, contact, etc.)
            callback: Progress callback function
        """
        page_display = self.get_page_type_display(page_type)
        percentage = self.calculate_page_percentage()

        # Include both page number and type information
        message = f"Processing page {self.state.current_page + 1} of {self.state.total_pages}: {page_display}"

        # Add restaurant context if in batch mode
        if self.state.total_restaurants > 1:
            message = f"Restaurant {self.state.current_restaurant_index + 1} of {self.state.total_restaurants} - {message}"

        callback(message, percentage)

    def notify_page_complete(
        self, url: str, page_type: str, success: bool, callback: Callable
    ) -> None:
        """Notify that processing of a page has completed.

        Args:
            url: URL of the page that was processed
            page_type: Type of the page
            success: Whether processing was successful
            callback: Progress callback function
        """
        if success:
            self.state.successful_pages += 1
        else:
            self.state.failed_pages += 1
            page_display = self.get_page_type_display(page_type)
            failure_message = (
                f"Failed to load {page_display} - continuing with other pages"
            )
            callback(failure_message)
            return

        # Update current page counter
        self.state.current_page += 1

        # Calculate progress
        percentage = self.calculate_page_percentage()
        time_estimate = self.estimate_remaining_time()

        # Create progress message
        message = (
            f"Completed page {self.state.current_page} of {self.state.total_pages}"
        )

        callback(message, percentage, time_estimate)

    def notify_restaurant_complete(
        self, successful_pages: int, failed_pages: int, callback: Callable
    ) -> None:
        """Notify that processing of a restaurant has completed.

        Args:
            successful_pages: Number of pages processed successfully
            failed_pages: Number of pages that failed
            callback: Progress callback function
        """
        total_pages = successful_pages + failed_pages

        if failed_pages > 0:
            message = f"Completed {self.state.current_restaurant} ({successful_pages} of {total_pages} pages successful)"
        else:
            message = f"Completed {self.state.current_restaurant} ({total_pages} pages processed)"

        # Update restaurant counter if in batch mode
        if self.state.total_restaurants > 1:
            self.state.current_restaurant_index += 1

        callback(message, 100)

    def get_page_type_display(self, page_type: str) -> str:
        """Get display name for page type.

        Args:
            page_type: Page type identifier

        Returns:
            Human-readable page type name
        """
        return self.page_type_display_names.get(page_type.lower(), "Page")

    def calculate_page_percentage(self) -> int:
        """Calculate current progress percentage for pages.

        Returns:
            Progress percentage (0-100)
        """
        if self.state.total_pages == 0:
            return 0

        return int((self.state.current_page / self.state.total_pages) * 100)

    def estimate_remaining_time(self) -> float:
        """Estimate remaining time for current restaurant.

        Returns:
            Estimated remaining time in seconds
        """
        if self.state.current_page == 0 or self.state.start_time == 0:
            return 0.0

        elapsed_time = time.time() - self.state.start_time
        avg_time_per_page = elapsed_time / self.state.current_page
        remaining_pages = self.state.total_pages - self.state.current_page

        return avg_time_per_page * remaining_pages

    def get_current_progress_summary(self) -> dict:
        """Get current progress summary.

        Returns:
            Dictionary with current progress information
        """
        return {
            "current_restaurant": self.state.current_restaurant,
            "restaurant_progress": f"{self.state.current_restaurant_index + 1}/{self.state.total_restaurants}"
            if self.state.total_restaurants > 1
            else "1/1",
            "page_progress": f"{self.state.current_page}/{self.state.total_pages}",
            "page_percentage": self.calculate_page_percentage(),
            "successful_pages": self.state.successful_pages,
            "failed_pages": self.state.failed_pages,
            "estimated_remaining_time": self.estimate_remaining_time(),
            "elapsed_time": time.time() - self.state.start_time
            if self.state.start_time > 0
            else 0,
        }

    def reset(self) -> None:
        """Reset progress state."""
        self.state = MultiPageProgressState()
