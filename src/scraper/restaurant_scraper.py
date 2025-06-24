"""Main restaurant scraper that integrates with the Flask web interface."""
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from .multi_strategy_scraper import MultiStrategyScraper, RestaurantData
from .batch_processor import BatchProcessor, BatchConfig
from .multi_page_scraper import MultiPageScraper, MultiPageScrapingResult


@dataclass
class ScrapingResult:
    """Result of restaurant scraping operation."""

    successful_extractions: List[RestaurantData]
    failed_urls: List[str]
    total_processed: int
    errors: List[str]
    output_files: Dict[str, List[str]] = None
    processing_time: float = 0.0
    # Multi-page specific data
    multi_page_results: List[MultiPageScrapingResult] = None

    def __post_init__(self):
        if self.output_files is None:
            self.output_files = {"text": [], "pdf": []}
        if self.multi_page_results is None:
            self.multi_page_results = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result_dict = {
            "successful_extractions": [
                data.to_dict() for data in self.successful_extractions
            ],
            "failed_urls": self.failed_urls,
            "total_processed": self.total_processed,
            "errors": self.errors,
            "output_files": self.output_files,
            "processing_time": self.processing_time,
        }
        
        # Include multi-page results if available (for backwards compatibility)
        if hasattr(self, 'multi_page_results') and self.multi_page_results:
            # Convert MultiPageScrapingResult objects to dictionaries
            result_dict["multi_page_results"] = [
                {
                    "restaurant_name": mp.restaurant_name,
                    "pages_processed": mp.pages_processed,
                    "successful_pages": mp.successful_pages,
                    "failed_pages": mp.failed_pages,
                    "processing_time": mp.processing_time,
                } for mp in self.multi_page_results
            ]
        
        return result_dict


class RestaurantScraper:
    """Main restaurant scraper class for Flask integration."""

    def __init__(
        self, enable_batch_processing: bool = True, enable_multi_page: bool = True
    ):
        """Initialize restaurant scraper with multi-strategy backend."""
        self.multi_scraper = MultiStrategyScraper(enable_ethical_scraping=True)
        self.enable_batch_processing = enable_batch_processing
        self.enable_multi_page = enable_multi_page
        self.batch_processor = None
        self.multi_page_scraper = None

        if enable_batch_processing:
            batch_config = BatchConfig(
                max_concurrent_requests=3,
                memory_limit_mb=512,
                chunk_size=10,
                enable_memory_monitoring=True,
            )
            self.batch_processor = BatchProcessor(batch_config)

        if enable_multi_page:
            self.multi_page_scraper = MultiPageScraper(
                max_pages=10, enable_ethical_scraping=True
            )

    def scrape_restaurants(
        self, config, progress_callback: Optional[Callable] = None
    ) -> ScrapingResult:
        """Scrape restaurants using the provided configuration."""
        urls = config.urls

        # Use batch processor for larger batches (>5 URLs) or if explicitly enabled
        if (
            self.enable_batch_processing
            and self.batch_processor
            and (len(urls) > 5 or getattr(config, "force_batch_processing", False))
        ):
            batch_result = self.batch_processor.process_batch(urls, progress_callback)
            # Convert batch processor result to ScrapingResult
            result = ScrapingResult(
                successful_extractions=batch_result["successful_extractions"],
                failed_urls=batch_result["failed_urls"],
                total_processed=batch_result["total_processed"],
                errors=batch_result["errors"],
                processing_time=batch_result["processing_time"],
            )
            return result
        else:
            # Use simple processing for small batches
            return self._process_simple_batch(urls, progress_callback, config)

    def _process_simple_batch(
        self, urls: List[str], progress_callback: Optional[Callable] = None, config=None
    ) -> ScrapingResult:
        """Process small batches using simple sequential method with optional multi-page support."""
        import time

        start_time = time.time()

        successful_extractions = []
        failed_urls = []
        errors = []
        multi_page_results = []

        if progress_callback:
            progress_callback("Starting restaurant data extraction...", 0)

        for i, url in enumerate(urls):
            try:
                if progress_callback:
                    progress_percentage = int((i / len(urls)) * 100)
                    if len(urls) > 1:
                        progress_callback(
                            f"Processing {i + 1} of {len(urls)}: {url}",
                            progress_percentage,
                        )
                    else:
                        progress_callback(f"Processing {url}", progress_percentage)

                # Check if multi-page processing is enabled and should be used
                if (
                    self.enable_multi_page
                    and self.multi_page_scraper
                    and getattr(config, "enable_multi_page", False)
                ):
                    # Use multi-page scraper
                    multi_page_result = self.multi_page_scraper.scrape_website(
                        url, progress_callback
                    )

                    # Store multi-page result for detailed reporting
                    multi_page_results.append(multi_page_result)
                    
                    if multi_page_result.aggregated_data:
                        successful_extractions.append(multi_page_result.aggregated_data)
                        if progress_callback:
                            progress_callback(
                                f"Successfully extracted data from {len(multi_page_result.successful_pages)} pages for {multi_page_result.restaurant_name or 'Unknown Restaurant'}"
                            )
                    else:
                        failed_urls.append(url)
                        errors.append(
                            f"No restaurant data found at {url} (checked {len(multi_page_result.pages_processed)} pages)"
                        )
                        if progress_callback:
                            progress_callback(f"No restaurant data found at {url}")
                else:
                    # Use single-page extraction
                    restaurant_data = self.multi_scraper.scrape_url(url)

                    if restaurant_data:
                        successful_extractions.append(restaurant_data)
                        if progress_callback:
                            progress_callback(
                                f"Successfully extracted data for {restaurant_data.name or 'Unknown Restaurant'}"
                            )
                    else:
                        failed_urls.append(url)
                        errors.append(f"No restaurant data found at {url}")
                        if progress_callback:
                            progress_callback(f"No restaurant data found at {url}")

            except Exception as e:
                failed_urls.append(url)
                error_msg = f"Error processing {url}: {str(e)}"
                errors.append(error_msg)
                if progress_callback:
                    progress_callback(f"Error: {error_msg}")

        processing_time = time.time() - start_time

        if progress_callback:
            progress_callback("Restaurant data extraction completed", 100)

        # Create result with timing information
        result = ScrapingResult(
            successful_extractions=successful_extractions,
            failed_urls=failed_urls,
            total_processed=len(urls),
            errors=errors,
            processing_time=processing_time,
            multi_page_results=multi_page_results,
        )

        return result

    def get_current_progress(self):
        """Get current batch processing progress."""
        if self.batch_processor:
            return self.batch_processor.get_current_progress()
        return None

    def get_memory_stats(self):
        """Get memory usage statistics."""
        if self.batch_processor:
            return self.batch_processor.get_memory_stats()
        return None

    def stop_processing(self):
        """Stop current batch processing."""
        if self.batch_processor:
            self.batch_processor.stop_processing()
