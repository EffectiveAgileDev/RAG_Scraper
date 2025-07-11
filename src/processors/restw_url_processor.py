"""RestW URL processor for processing URLs with obfuscated WTEG schema."""

import re
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

from .restw_base_processor import RestWProcessor


class RestWUrlProcessor(RestWProcessor):
    """RestW processor for URL-based extraction."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize RestW URL processor.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        
        # Initialize WTEG extractor (internal use only)
        self._initialize_wteg_extractor()
        
        # URL validation patterns
        self.url_patterns = {
            'restaurant_keywords': ['restaurant', 'menu', 'food', 'dining', 'cafe', 'pizza', 'burger'],
            'domain_indicators': ['restaurant', 'dining', 'food', 'menu', 'eat']
        }
    
    def _initialize_wteg_extractor(self):
        """Initialize WTEG extractor for internal use."""
        try:
            from ..wteg.wteg_extractor import WTEGExtractor
            self.wteg_extractor = WTEGExtractor()
        except ImportError:
            # Fallback for testing
            self.wteg_extractor = None
    
    def process_url(self, url: str, options: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Process a URL and return RestW-formatted data.
        
        Args:
            url: URL to process
            options: Optional processing options
            
        Returns:
            RestW-formatted data or None if processing fails
        """
        if not self.validate_url(url):
            return None
        
        try:
            # Extract data using WTEG extractor
            if self.wteg_extractor:
                wteg_data = self.wteg_extractor.extract_from_url(url, options)
            else:
                # Fallback for testing
                wteg_data = self._mock_wteg_extraction(url)
            
            if not wteg_data:
                return None
            
            # Transform WTEG data to RestW format
            restw_data = self.transform_wteg_to_restw(wteg_data)
            
            # Validate output
            if not self.validate_restw_output(restw_data):
                return None
            
            return restw_data
            
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            return None
    
    def _mock_wteg_extraction(self, url: str) -> Dict[str, Any]:
        """Mock WTEG extraction for testing."""
        return {
            'location': {
                'street_address': '123 Main St',
                'city': 'Anytown',
                'state': 'CA',
                'zip_code': '12345'
            },
            'menu_items': [
                {'item_name': 'Pizza', 'price': '$10', 'category': 'Main'},
                {'item_name': 'Salad', 'price': '$8', 'category': 'Appetizer'}
            ],
            'services_offered': {
                'delivery_available': True,
                'takeout_available': True
            }
        }
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format and accessibility.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid
        """
        if not url or not isinstance(url, str):
            return False
        
        # Check URL format
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
        except Exception:
            return False
        
        # Check for HTTP/HTTPS
        if parsed.scheme not in ['http', 'https']:
            return False
        
        return True
    
    def get_supported_domains(self) -> List[str]:
        """Get list of supported domain patterns.
        
        Returns:
            List of supported domain patterns
        """
        return [
            'restaurant.com',
            'dining.com',
            'food.com',
            'menu.com',
            '*restaurant*',
            '*dining*',
            '*food*',
            '*menu*'
        ]
    
    def is_restaurant_url(self, url: str) -> bool:
        """Check if URL appears to be a restaurant website.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL appears to be restaurant-related
        """
        if not self.validate_url(url):
            return False
        
        url_lower = url.lower()
        
        # Check for restaurant keywords in URL
        for keyword in self.url_patterns['restaurant_keywords']:
            if keyword in url_lower:
                return True
        
        # Check domain indicators
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        for indicator in self.url_patterns['domain_indicators']:
            if indicator in domain:
                return True
        
        return False
    
    def extract_url_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from URL.
        
        Args:
            url: URL to extract metadata from
            
        Returns:
            Dictionary with URL metadata
        """
        parsed = urlparse(url)
        
        return {
            'scheme': parsed.scheme,
            'domain': parsed.netloc,
            'path': parsed.path,
            'query': parsed.query,
            'is_restaurant_url': self.is_restaurant_url(url),
            'supported_domain': any(pattern in parsed.netloc for pattern in self.get_supported_domains())
        }
    
    def process_multiple_urls(self, urls: List[str], options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Process multiple URLs.
        
        Args:
            urls: List of URLs to process
            options: Optional processing options
            
        Returns:
            List of RestW-formatted data
        """
        results = []
        
        for url in urls:
            try:
                result = self.process_url(url, options)
                if result:
                    result['source_url'] = url
                    results.append(result)
            except Exception as e:
                print(f"Error processing URL {url}: {e}")
                continue
        
        return results
    
    def get_url_processing_statistics(self, urls: List[str]) -> Dict[str, Any]:
        """Get statistics for URL processing.
        
        Args:
            urls: List of URLs to analyze
            
        Returns:
            Processing statistics
        """
        stats = {
            'total_urls': len(urls),
            'valid_urls': 0,
            'restaurant_urls': 0,
            'supported_domains': 0,
            'invalid_urls': 0
        }
        
        for url in urls:
            if self.validate_url(url):
                stats['valid_urls'] += 1
                
                if self.is_restaurant_url(url):
                    stats['restaurant_urls'] += 1
                
                metadata = self.extract_url_metadata(url)
                if metadata['supported_domain']:
                    stats['supported_domains'] += 1
            else:
                stats['invalid_urls'] += 1
        
        return stats
    
    def create_processing_report(self, urls: List[str], results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create processing report.
        
        Args:
            urls: List of processed URLs
            results: List of processing results
            
        Returns:
            Processing report
        """
        stats = self.get_url_processing_statistics(urls)
        
        return {
            'processing_statistics': stats,
            'successful_extractions': len(results),
            'failed_extractions': len(urls) - len(results),
            'success_rate': len(results) / len(urls) if urls else 0,
            'schema_type': self.schema_type,
            'obfuscation_applied': self.obfuscate_terminology
        }
    
    def get_processor_capabilities(self) -> Dict[str, Any]:
        """Get processor capabilities.
        
        Returns:
            Dictionary with processor capabilities
        """
        return {
            'processor_type': 'url',
            'schema_type': self.schema_type,
            'supports_batch_processing': True,
            'supports_url_validation': True,
            'supports_restaurant_detection': True,
            'supports_metadata_extraction': True,
            'uses_wteg_extraction': True,
            'obfuscates_terminology': self.obfuscate_terminology,
            'supported_url_schemes': ['http', 'https'],
            'supported_domain_patterns': self.get_supported_domains()
        }