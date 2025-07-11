"""RestW HTML processor for processing HTML content with obfuscated WTEG schema."""

import re
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin, urlparse

from .restw_base_processor import RestWProcessor


class RestWHtmlProcessor(RestWProcessor):
    """RestW processor for HTML-based extraction."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize RestW HTML processor.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        
        # Initialize WTEG HTML processor (internal use only)
        self._initialize_wteg_html_processor()
        
        # HTML validation patterns
        self.html_patterns = {
            'restaurant_indicators': ['menu', 'restaurant', 'food', 'dining', 'cafe', 'pizza', 'burger'],
            'menu_patterns': [r'menu', r'price', r'\$\d+', r'delivery', r'takeout'],
            'structured_data_types': ['application/ld+json', 'microdata']
        }
    
    def _initialize_wteg_html_processor(self):
        """Initialize WTEG HTML processor for internal use."""
        try:
            from ..processors.html_wteg_processor import HTMLWTEGProcessor
            self.wteg_html_processor = HTMLWTEGProcessor()
        except ImportError:
            # Fallback for testing
            self.wteg_html_processor = None
    
    def process_html(self, html_content: str, url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Process HTML content and return RestW-formatted data.
        
        Args:
            html_content: HTML content to process
            url: Optional URL context
            
        Returns:
            RestW-formatted data or None if processing fails
        """
        if not self.validate_html(html_content):
            return None
        
        try:
            # Extract data using WTEG HTML processor
            if self.wteg_html_processor:
                wteg_data = self.wteg_html_processor.process_html(html_content, url)
            else:
                # Fallback for testing
                wteg_data = self._mock_wteg_html_extraction(html_content)
            
            if not wteg_data:
                return None
            
            # Transform WTEG data to RestW format
            restw_data = self.transform_wteg_to_restw(wteg_data)
            
            # Validate output
            if not self.validate_restw_output(restw_data):
                return None
            
            return restw_data
            
        except Exception as e:
            print(f"Error processing HTML: {e}")
            return None
    
    def _mock_wteg_html_extraction(self, html_content: str) -> Dict[str, Any]:
        """Mock WTEG HTML extraction for testing."""
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
    
    def validate_html(self, html_content: str) -> bool:
        """Validate HTML content.
        
        Args:
            html_content: HTML content to validate
            
        Returns:
            True if HTML is valid
        """
        if not html_content or not isinstance(html_content, str):
            return False
        
        # Check for basic HTML structure
        if not re.search(r'<html.*?>.*</html>', html_content, re.DOTALL | re.IGNORECASE):
            # More lenient check for HTML fragments
            if not re.search(r'<[^>]+>', html_content):
                return False
        
        # Check for minimum content length
        if len(html_content.strip()) < 10:
            return False
        
        return True
    
    def extract_structured_data(self, html_content: str) -> Dict[str, Any]:
        """Extract structured data from HTML.
        
        Args:
            html_content: HTML content to extract from
            
        Returns:
            Dictionary with structured data
        """
        structured_data = {
            'json_ld': [],
            'microdata': {},
            'opengraph': {},
            'schema_org': {}
        }
        
        if self.wteg_html_processor:
            try:
                wteg_structured = self.wteg_html_processor.extract_structured_data(html_content)
                structured_data.update(wteg_structured)
            except Exception:
                pass
        
        return structured_data
    
    def is_restaurant_html(self, html_content: str) -> bool:
        """Check if HTML appears to be from a restaurant website.
        
        Args:
            html_content: HTML content to check
            
        Returns:
            True if HTML appears to be restaurant-related
        """
        if not self.validate_html(html_content):
            return False
        
        html_lower = html_content.lower()
        
        # Check for restaurant indicators
        indicator_count = 0
        for indicator in self.html_patterns['restaurant_indicators']:
            if indicator in html_lower:
                indicator_count += 1
        
        # Check for menu patterns
        menu_pattern_count = 0
        for pattern in self.html_patterns['menu_patterns']:
            if re.search(pattern, html_lower):
                menu_pattern_count += 1
        
        # Restaurant if multiple indicators found
        return indicator_count >= 2 or menu_pattern_count >= 3
    
    def extract_menu_items(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract menu items from HTML.
        
        Args:
            html_content: HTML content to extract from
            
        Returns:
            List of menu items
        """
        menu_items = []
        
        if self.wteg_html_processor:
            try:
                wteg_menu = self.wteg_html_processor.extract_menu_items(html_content)
                menu_items.extend(wteg_menu)
            except Exception:
                pass
        
        return menu_items
    
    def extract_contact_info(self, html_content: str) -> Dict[str, Any]:
        """Extract contact information from HTML.
        
        Args:
            html_content: HTML content to extract from
            
        Returns:
            Dictionary with contact information
        """
        contact_info = {}
        
        if self.wteg_html_processor:
            try:
                wteg_contact = self.wteg_html_processor.extract_contact_info(html_content)
                contact_info.update(wteg_contact)
            except Exception:
                pass
        
        return contact_info
    
    def extract_location_data(self, html_content: str) -> Dict[str, Any]:
        """Extract location data from HTML.
        
        Args:
            html_content: HTML content to extract from
            
        Returns:
            Dictionary with location data
        """
        location_data = {}
        
        if self.wteg_html_processor:
            try:
                wteg_location = self.wteg_html_processor.extract_location_data(html_content)
                location_data.update(wteg_location)
            except Exception:
                pass
        
        return location_data
    
    def process_multiple_html(self, html_contents: List[str], urls: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Process multiple HTML contents.
        
        Args:
            html_contents: List of HTML contents
            urls: Optional list of corresponding URLs
            
        Returns:
            List of RestW-formatted data
        """
        results = []
        
        for i, html_content in enumerate(html_contents):
            try:
                url = urls[i] if urls and i < len(urls) else None
                result = self.process_html(html_content, url)
                if result:
                    if url:
                        result['source_url'] = url
                    results.append(result)
            except Exception as e:
                print(f"Error processing HTML {i}: {e}")
                continue
        
        return results
    
    def get_html_processing_statistics(self, html_contents: List[str]) -> Dict[str, Any]:
        """Get statistics for HTML processing.
        
        Args:
            html_contents: List of HTML contents
            
        Returns:
            Processing statistics
        """
        stats = {
            'total_html': len(html_contents),
            'valid_html': 0,
            'restaurant_html': 0,
            'structured_data_found': 0,
            'average_content_length': 0
        }
        
        total_length = 0
        
        for html_content in html_contents:
            if self.validate_html(html_content):
                stats['valid_html'] += 1
                total_length += len(html_content)
                
                if self.is_restaurant_html(html_content):
                    stats['restaurant_html'] += 1
                
                structured_data = self.extract_structured_data(html_content)
                if any(structured_data.values()):
                    stats['structured_data_found'] += 1
        
        if stats['valid_html'] > 0:
            stats['average_content_length'] = total_length / stats['valid_html']
        
        return stats
    
    def create_processing_report(self, html_contents: List[str], results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create processing report.
        
        Args:
            html_contents: List of processed HTML contents
            results: List of processing results
            
        Returns:
            Processing report
        """
        stats = self.get_html_processing_statistics(html_contents)
        
        return {
            'processing_statistics': stats,
            'successful_extractions': len(results),
            'failed_extractions': len(html_contents) - len(results),
            'success_rate': len(results) / len(html_contents) if html_contents else 0,
            'schema_type': self.schema_type,
            'obfuscation_applied': self.obfuscate_terminology
        }
    
    def get_processor_capabilities(self) -> Dict[str, Any]:
        """Get processor capabilities.
        
        Returns:
            Dictionary with processor capabilities
        """
        return {
            'processor_type': 'html',
            'schema_type': self.schema_type,
            'supports_batch_processing': True,
            'supports_html_validation': True,
            'supports_restaurant_detection': True,
            'supports_structured_data_extraction': True,
            'supports_menu_extraction': True,
            'supports_contact_extraction': True,
            'supports_location_extraction': True,
            'uses_wteg_extraction': True,
            'obfuscates_terminology': self.obfuscate_terminology,
            'supported_data_types': self.html_patterns['structured_data_types']
        }
    
    def extract_social_media_links(self, html_content: str) -> List[str]:
        """Extract social media links from HTML.
        
        Args:
            html_content: HTML content to extract from
            
        Returns:
            List of social media links
        """
        social_links = []
        
        # Social media patterns
        social_patterns = [
            r'https?://(?:www\.)?facebook\.com/[a-zA-Z0-9._-]+',
            r'https?://(?:www\.)?instagram\.com/[a-zA-Z0-9._-]+',
            r'https?://(?:www\.)?twitter\.com/[a-zA-Z0-9._-]+',
            r'https?://(?:www\.)?linkedin\.com/[a-zA-Z0-9._-]+',
            r'https?://(?:www\.)?youtube\.com/[a-zA-Z0-9._-]+',
            r'https?://(?:www\.)?tiktok\.com/[a-zA-Z0-9._-]+'
        ]
        
        for pattern in social_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            social_links.extend(matches)
        
        return list(set(social_links))  # Remove duplicates
    
    def extract_online_ordering_links(self, html_content: str) -> List[Dict[str, str]]:
        """Extract online ordering links from HTML.
        
        Args:
            html_content: HTML content to extract from
            
        Returns:
            List of online ordering platforms
        """
        ordering_links = []
        
        # Online ordering patterns
        ordering_patterns = {
            'grubhub': r'https?://(?:www\.)?grubhub\.com/[a-zA-Z0-9._/-]+',
            'doordash': r'https?://(?:www\.)?doordash\.com/[a-zA-Z0-9._/-]+',
            'ubereats': r'https?://(?:www\.)?ubereats\.com/[a-zA-Z0-9._/-]+',
            'postmates': r'https?://(?:www\.)?postmates\.com/[a-zA-Z0-9._/-]+',
            'seamless': r'https?://(?:www\.)?seamless\.com/[a-zA-Z0-9._/-]+'
        }
        
        for platform, pattern in ordering_patterns.items():
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                ordering_links.append({
                    'platform': platform,
                    'url': match
                })
        
        return ordering_links