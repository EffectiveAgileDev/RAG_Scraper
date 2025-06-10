"""Main restaurant scraper that integrates with the Flask web interface."""
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from .multi_strategy_scraper import MultiStrategyScraper, RestaurantData


@dataclass
class ScrapingResult:
    """Result of restaurant scraping operation."""
    successful_extractions: List[RestaurantData]
    failed_urls: List[str]
    total_processed: int
    errors: List[str]
    output_files: Dict[str, List[str]] = None
    processing_time: float = 0.0
    
    def __post_init__(self):
        if self.output_files is None:
            self.output_files = {'text': [], 'pdf': []}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'successful_extractions': [data.to_dict() for data in self.successful_extractions],
            'failed_urls': self.failed_urls,
            'total_processed': self.total_processed,
            'errors': self.errors,
            'output_files': self.output_files,
            'processing_time': self.processing_time
        }


class RestaurantScraper:
    """Main restaurant scraper class for Flask integration."""
    
    def __init__(self):
        """Initialize restaurant scraper with multi-strategy backend."""
        self.multi_scraper = MultiStrategyScraper(enable_ethical_scraping=True)
    
    def scrape_restaurants(self, config, progress_callback: Optional[Callable] = None) -> ScrapingResult:
        """Scrape restaurants using the provided configuration."""
        import time
        start_time = time.time()
        
        urls = config.urls
        successful_extractions = []
        failed_urls = []
        errors = []
        
        if progress_callback:
            progress_callback("Starting restaurant data extraction...", 0)
        
        for i, url in enumerate(urls):
            try:
                if progress_callback:
                    progress_percentage = int((i / len(urls)) * 100)
                    progress_callback(
                        f"Processing restaurant {i + 1} of {len(urls)}",
                        progress_percentage,
                        url
                    )
                
                # Extract restaurant data
                restaurant_data = self.multi_scraper.scrape_url(url)
                
                if restaurant_data:
                    successful_extractions.append(restaurant_data)
                    if progress_callback:
                        progress_callback(
                            f"Successfully extracted data for {restaurant_data.name or 'Unknown Restaurant'}",
                            None,
                            url
                        )
                else:
                    failed_urls.append(url)
                    errors.append(f"No restaurant data found at {url}")
                    if progress_callback:
                        progress_callback(
                            f"No restaurant data found at {url}",
                            None,
                            url
                        )
                        
            except Exception as e:
                failed_urls.append(url)
                error_msg = f"Error processing {url}: {str(e)}"
                errors.append(error_msg)
                if progress_callback:
                    progress_callback(f"Error: {error_msg}", None, url)
        
        processing_time = time.time() - start_time
        
        if progress_callback:
            progress_callback("Restaurant data extraction completed", 100)
        
        # Create result with timing information
        result = ScrapingResult(
            successful_extractions=successful_extractions,
            failed_urls=failed_urls,
            total_processed=len(urls),
            errors=errors,
            processing_time=processing_time
        )
        
        # For now, we'll indicate that data was extracted but files aren't generated yet
        # (Sprint 3 will implement actual file generation)
        if successful_extractions:
            result.output_files['text'] = [f"Extracted data for {len(successful_extractions)} restaurants"]
        
        return result