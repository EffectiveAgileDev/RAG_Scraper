"""Configuration management and initialization for MultiPageScraper."""
from typing import Dict, Any, Optional

from .page_classifier import PageClassifier
from .data_aggregator import DataAggregator
from .multi_page_progress import MultiPageProgressNotifier
from .multi_strategy_scraper import MultiStrategyScraper
from .page_processor import PageProcessor
from .multi_page_result_handler import MultiPageResultHandler
from .page_queue_manager import PageQueueManager


class MultiPageScraperConfig:
    """Manages configuration settings, validation, and component initialization for MultiPageScraper."""

    def __init__(
        self,
        max_pages: int = 10,
        enable_ethical_scraping: bool = True,
        max_crawl_depth: int = 2,
        concurrent_workers: int = 3,
        throttle_delay: float = 0.0,
        request_timeout: Optional[float] = None,
    ):
        """Initialize configuration with validation.
        
        Args:
            max_pages: Maximum number of pages to process per website
            enable_ethical_scraping: Whether to enable ethical scraping features
            max_crawl_depth: Maximum depth for page discovery
            concurrent_workers: Number of concurrent workers for parallel processing
            throttle_delay: Delay between requests in seconds
            request_timeout: Timeout for individual requests (None for no timeout)
            
        Raises:
            ValueError: If any configuration value is invalid
        """
        self._validate_config(
            max_pages=max_pages,
            max_crawl_depth=max_crawl_depth,
            concurrent_workers=concurrent_workers,
            throttle_delay=throttle_delay,
            request_timeout=request_timeout,
        )
        
        self.max_pages = max_pages
        self.enable_ethical_scraping = enable_ethical_scraping
        self.max_crawl_depth = max_crawl_depth
        self.concurrent_workers = concurrent_workers
        self.throttle_delay = throttle_delay
        self.request_timeout = request_timeout

    def _validate_config(
        self,
        max_pages: int,
        max_crawl_depth: int,
        concurrent_workers: int,
        throttle_delay: float,
        request_timeout: Optional[float],
    ):
        """Validate configuration parameters.
        
        Args:
            max_pages: Maximum number of pages to process per website
            max_crawl_depth: Maximum depth for page discovery
            concurrent_workers: Number of concurrent workers
            throttle_delay: Delay between requests in seconds
            request_timeout: Timeout for individual requests
            
        Raises:
            ValueError: If any configuration value is invalid
        """
        if max_pages <= 0:
            raise ValueError("max_pages must be positive")
            
        if max_crawl_depth <= 0:
            raise ValueError("max_crawl_depth must be positive")
            
        if concurrent_workers <= 0:
            raise ValueError("concurrent_workers must be positive")
            
        if throttle_delay < 0:
            raise ValueError("throttle_delay must be non-negative")
            
        if request_timeout is not None and request_timeout <= 0:
            raise ValueError("request_timeout must be positive when set")

    def initialize_components(self) -> Dict[str, Any]:
        """Initialize all required components for scraping.
        
        Returns:
            Dictionary containing initialized components
        """
        # Initialize core components
        page_classifier = PageClassifier()
        data_aggregator = DataAggregator()
        progress_notifier = MultiPageProgressNotifier()
        multi_strategy_scraper = MultiStrategyScraper(self.enable_ethical_scraping)
        page_processor = PageProcessor(self.enable_ethical_scraping)
        
        # Initialize result handler with dependencies
        result_handler = MultiPageResultHandler(
            progress_notifier=progress_notifier,
            data_aggregator=data_aggregator,
            page_processor=page_processor
        )
        
        # Initialize queue manager with configuration
        page_queue_manager = PageQueueManager(self.max_pages, default_strategy="BFS")
        
        return {
            'page_classifier': page_classifier,
            'data_aggregator': data_aggregator,
            'progress_notifier': progress_notifier,
            'multi_strategy_scraper': multi_strategy_scraper,
            'page_processor': page_processor,
            'result_handler': result_handler,
            'page_queue_manager': page_queue_manager,
        }

    def initialize_statistics(self) -> Dict[str, Any]:
        """Initialize statistics tracking dictionaries.
        
        Returns:
            Dictionary containing empty statistics structures
        """
        return {
            'concurrent_stats': {
                "successful_fetches": 0,
                "failed_fetches": 0,
                "total_time": 0.0,
            },
            'error_stats': {
                "total_errors": 0,
                "error_types": {},
                "retryable_errors": 0,
                "non_retryable_errors": 0,
            },
            'error_log': []
        }

    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of all configuration settings.
        
        Returns:
            Dictionary containing all configuration values
        """
        return {
            'max_pages': self.max_pages,
            'enable_ethical_scraping': self.enable_ethical_scraping,
            'max_crawl_depth': self.max_crawl_depth,
            'concurrent_workers': self.concurrent_workers,
            'throttle_delay': self.throttle_delay,
            'request_timeout': self.request_timeout,
        }

    def update_config(self, **kwargs):
        """Update configuration settings with validation.
        
        Args:
            **kwargs: Configuration parameters to update
            
        Raises:
            ValueError: If any new configuration value is invalid
        """
        # Get current values to validate against
        current_config = {
            'max_pages': kwargs.get('max_pages', self.max_pages),
            'max_crawl_depth': kwargs.get('max_crawl_depth', self.max_crawl_depth),
            'concurrent_workers': kwargs.get('concurrent_workers', self.concurrent_workers),
            'throttle_delay': kwargs.get('throttle_delay', self.throttle_delay),
            'request_timeout': kwargs.get('request_timeout', self.request_timeout),
        }
        
        # Validate new configuration
        self._validate_config(**current_config)
        
        # Update configuration
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def reset_statistics(self) -> Dict[str, Any]:
        """Reset all statistics to initial values.
        
        Returns:
            Dictionary containing reset statistics structures
        """
        return self.initialize_statistics()