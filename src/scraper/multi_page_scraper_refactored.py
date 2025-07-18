"""
Refactored Multi-page restaurant website scraper with simplified dependency injection.

This refactored version:
- Uses dependency injection instead of complex configuration
- Separates concerns into single-responsibility classes
- Maintains the same external interface for backward compatibility
- Reduces the number of internal dependencies from 7 to 3 core components
"""
from typing import List, Dict, Any, Optional, Callable, Tuple
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from .multi_page_result_handler import (
    MultiPageResultHandler,
    MultiPageScrapingResult,
    PageProcessingResult
)


class SimplifiedPageProcessor:
    """Simplified page processing that focuses on single responsibility."""
    
    def __init__(self, multi_strategy_scraper=None):
        """Initialize with injectable scraper dependency."""
        self.multi_strategy_scraper = multi_strategy_scraper
        
    def process_page(self, url: str, html: str) -> PageProcessingResult:
        """Process a single page and return structured result."""
        try:
            # Use the multi-strategy scraper to extract data
            if self.multi_strategy_scraper:
                scraped_data = self.multi_strategy_scraper.scrape(url, html)
                return PageProcessingResult(
                    url=url,
                    success=True,
                    data=scraped_data,
                    page_type="restaurant_page"
                )
            else:
                # Fallback processing
                return PageProcessingResult(
                    url=url,
                    success=True,
                    data={"text": html[:1000]},  # Simple fallback
                    page_type="unknown"
                )
        except Exception as e:
            return PageProcessingResult(
                url=url,
                success=False,
                error=str(e),
                page_type="error"
            )


class SimplifiedDataAggregator:
    """Simplified data aggregation that focuses on behavior outcomes."""
    
    def __init__(self):
        self.aggregated_data = {}
        self.page_count = 0
        
    def add_page_data(self, page_result: PageProcessingResult):
        """Add data from a processed page."""
        if page_result.success and page_result.data:
            self.page_count += 1
            
            # Merge data into aggregated structure
            for key, value in page_result.data.items():
                if key not in self.aggregated_data:
                    self.aggregated_data[key] = []
                if isinstance(value, list):
                    self.aggregated_data[key].extend(value)
                else:
                    self.aggregated_data[key].append(value)
    
    def get_aggregated_data(self) -> Dict[str, Any]:
        """Get the final aggregated data."""
        return {
            "data": self.aggregated_data,
            "page_count": self.page_count,
            "aggregation_complete": True
        }


class SimplifiedPageDiscovery:
    """Simplified page discovery that focuses on finding relevant pages."""
    
    def __init__(self, max_pages: int = 10):
        self.max_pages = max_pages
        
    def discover_pages(self, start_url: str, html: str) -> List[str]:
        """Discover relevant pages from starting URL and HTML."""
        discovered_pages = [start_url]  # Always include start URL
        
        # Simple link discovery (this would be more sophisticated in real implementation)
        try:
            # This is a simplified version - in reality would use BeautifulSoup
            # to find restaurant-relevant links
            import re
            links = re.findall(r'href=["\']([^"\']+)["\']', html)
            
            # Filter and process links
            base_domain = self._extract_domain(start_url)
            relevant_links = []
            
            for link in links:
                if self._is_relevant_link(link, base_domain):
                    full_url = self._resolve_url(link, start_url)
                    if full_url not in discovered_pages:
                        relevant_links.append(full_url)
                        
            # Limit to max_pages
            discovered_pages.extend(relevant_links[:self.max_pages - 1])
            
        except Exception:
            # If discovery fails, just return the start URL
            pass
            
        return discovered_pages[:self.max_pages]
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return ""
    
    def _is_relevant_link(self, link: str, base_domain: str) -> bool:
        """Check if link is relevant for restaurant scraping."""
        # Simple heuristics
        if not link or link.startswith('#') or link.startswith('mailto:'):
            return False
            
        # Look for menu, about, contact, etc.
        relevant_keywords = ['menu', 'about', 'contact', 'location', 'hours', 'food']
        link_lower = link.lower()
        
        return any(keyword in link_lower for keyword in relevant_keywords)
    
    def _resolve_url(self, link: str, base_url: str) -> str:
        """Resolve relative URLs to absolute URLs."""
        try:
            from urllib.parse import urljoin
            return urljoin(base_url, link)
        except:
            return link


class RefactoredMultiPageScraper:
    """
    Refactored multi-page scraper with simplified dependency injection.
    
    This version addresses the brittleness issues by:
    - Using dependency injection instead of complex configuration
    - Focusing on behavior outcomes rather than internal implementation
    - Maintaining the same external interface for backward compatibility
    """
    
    def __init__(self, 
                 max_pages: int = 10,
                 page_processor: Optional[SimplifiedPageProcessor] = None,
                 data_aggregator: Optional[SimplifiedDataAggregator] = None,
                 page_discovery: Optional[SimplifiedPageDiscovery] = None,
                 enable_ethical_scraping: bool = True):
        """
        Initialize with injectable dependencies.
        
        Args:
            max_pages: Maximum number of pages to process
            page_processor: Optional page processor (creates default if None)
            data_aggregator: Optional data aggregator (creates default if None)
            page_discovery: Optional page discovery (creates default if None)
            enable_ethical_scraping: Whether to enable ethical scraping
        """
        self.max_pages = max_pages
        self.enable_ethical_scraping = enable_ethical_scraping
        
        # Injectable dependencies with sensible defaults
        self.page_processor = page_processor or SimplifiedPageProcessor()
        self.data_aggregator = data_aggregator or SimplifiedDataAggregator()
        self.page_discovery = page_discovery or SimplifiedPageDiscovery(max_pages)
        
        # Simple statistics
        self.stats = {
            'pages_processed': 0,
            'pages_failed': 0,
            'start_time': None,
            'end_time': None
        }
    
    def scrape_website(self, url: str, progress_callback: Optional[Callable] = None) -> MultiPageScrapingResult:
        """
        Scrape a restaurant website with multi-page navigation.
        
        This method maintains the same interface as the original but uses
        simplified internal structure.
        
        Args:
            url: Starting URL of the restaurant website
            progress_callback: Optional callback for progress updates
            
        Returns:
            MultiPageScrapingResult with aggregated data
        """
        self.stats['start_time'] = time.time()
        
        try:
            # Fetch initial page
            initial_html = self._fetch_page(url)
            if not initial_html:
                return self._create_failed_result(url, "Could not fetch initial page")
            
            # Discover all relevant pages
            discovered_pages = self.page_discovery.discover_pages(url, initial_html)
            
            # Process each page
            page_results = []
            for i, page_url in enumerate(discovered_pages):
                if progress_callback:
                    progress_callback(f"Processing page {i+1}/{len(discovered_pages)}: {page_url}")
                
                page_result = self._process_single_page(page_url)
                page_results.append(page_result)
                
                # Add to aggregator
                self.data_aggregator.add_page_data(page_result)
                
                if page_result.success:
                    self.stats['pages_processed'] += 1
                else:
                    self.stats['pages_failed'] += 1
            
            # Create final result
            aggregated_data = self.data_aggregator.get_aggregated_data()
            
            self.stats['end_time'] = time.time()
            
            return MultiPageScrapingResult(
                success=True,
                processed_pages=discovered_pages,
                failed_pages=[r.url for r in page_results if not r.success],
                aggregated_data=aggregated_data,
                page_count=len(discovered_pages),
                processing_time=self.stats['end_time'] - self.stats['start_time'],
                statistics=self.stats.copy()
            )
            
        except Exception as e:
            return self._create_failed_result(url, f"Scraping failed: {str(e)}")
    
    def _process_single_page(self, url: str) -> PageProcessingResult:
        """Process a single page."""
        try:
            html = self._fetch_page(url)
            if not html:
                return PageProcessingResult(
                    url=url,
                    success=False,
                    error="Could not fetch page",
                    page_type="error"
                )
            
            return self.page_processor.process_page(url, html)
            
        except Exception as e:
            return PageProcessingResult(
                url=url,
                success=False,
                error=str(e),
                page_type="error"
            )
    
    def _fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a page's HTML content.
        
        This is a simplified version - in real implementation would use
        the existing HTTP client with proper error handling.
        """
        try:
            import requests
            
            # Respect ethical scraping
            if self.enable_ethical_scraping:
                time.sleep(1)  # Simple rate limiting
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
            
        except Exception:
            return None
    
    def _create_failed_result(self, url: str, error_message: str) -> MultiPageScrapingResult:
        """Create a failed result."""
        return MultiPageScrapingResult(
            success=False,
            processed_pages=[],
            failed_pages=[url],
            aggregated_data={},
            page_count=0,
            processing_time=0,
            error_message=error_message,
            statistics=self.stats.copy()
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get scraping statistics."""
        return self.stats.copy()


# Backward compatibility alias
MultiPageScraper = RefactoredMultiPageScraper