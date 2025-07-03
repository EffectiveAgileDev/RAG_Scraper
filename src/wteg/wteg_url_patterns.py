"""WTEG URL pattern recognition and construction system.

This module handles URL pattern matching, construction, and multi-page
aggregation for WTEG (Where To Eat Guide) restaurant scraping.
"""
import re
from typing import List, Dict, Optional, Union
from urllib.parse import urlparse


class WTEGURLPatternParser:
    """Parser for WTEG URL patterns with multi-page support."""
    
    def __init__(self):
        """Initialize WTEG URL pattern parser."""
        self.pattern_name: str = ""
        self.city_name: str = ""
        self.base_domain: str = "mobimag.co"
        self.base_scheme: str = "https"
        self.aggregation_mode: str = "single_page"
        self.page_list: List[int] = []
        
        # Regex pattern for WTEG URLs (specifically for wteg pattern)
        self.wteg_url_pattern = re.compile(
            r'^https://mobimag\.co/(wteg)/([a-zA-Z0-9_-]+)/(\d+)/?$'
        )
    
    def set_pattern(self, pattern: str) -> None:
        """Set the pattern name (e.g., 'WTEG')."""
        self.pattern_name = pattern.lower().strip()
    
    def set_city(self, city: str) -> None:
        """Set the city name (e.g., 'Portland')."""
        self.city_name = city.lower().strip()
    
    def construct_url(self, page_id: int) -> str:
        """Construct WTEG URL with pattern/city/page_id format."""
        if not self.pattern_name or not self.city_name:
            raise ValueError("Pattern name and city name must be set before constructing URLs")
        
        return f"{self.base_scheme}://{self.base_domain}/{self.pattern_name}/{self.city_name}/{page_id}"
    
    def is_wteg_url(self, url: str) -> bool:
        """Validate if URL matches WTEG pattern."""
        try:
            match = self.wteg_url_pattern.match(url.strip())
            if not match:
                return False
            
            # Extract components
            pattern, city, page_id = match.groups()
            
            # Validate components
            if not pattern or not city:
                return False
            
            # Validate page ID is non-negative integer
            try:
                page_num = int(page_id)
                return page_num >= 0
            except ValueError:
                return False
                
        except Exception:
            return False
    
    def parse_url(self, url: str) -> Dict[str, str]:
        """Extract pattern, city, and page ID from WTEG URL."""
        match = self.wteg_url_pattern.match(url.strip())
        if not match:
            raise ValueError(f"Invalid WTEG URL format: {url}")
        
        pattern, city, page_id = match.groups()
        
        return {
            "pattern": pattern,
            "city": city,
            "page_id": page_id
        }
    
    def generate_url_range(self, page_range: List[int]) -> List[str]:
        """Generate multiple URLs for specified page range."""
        if not self.pattern_name or not self.city_name:
            raise ValueError("Pattern name and city name must be set before generating URLs")
        
        urls = []
        for page_id in page_range:
            urls.append(self.construct_url(page_id))
        
        return urls
    
    def set_single_page_mode(self, page_id: int) -> None:
        """Set single page aggregation mode."""
        self.aggregation_mode = "single_page"
        self.page_list = [page_id]
    
    def set_multi_page_mode(self, page_range: List[int]) -> None:
        """Set multi-page aggregation mode."""
        self.aggregation_mode = "multi_page"
        self.page_list = page_range
    
    def set_page_range_mode(self, page_range: List[int]) -> None:
        """Set page range aggregation mode."""
        self.aggregation_mode = "page_range"
        self.page_list = page_range
    
    def set_all_available_mode(self, max_pages: int = 50) -> None:
        """Set all available pages mode (1 to max_pages)."""
        self.aggregation_mode = "all_available"
        self.page_list = list(range(1, max_pages + 1))
    
    def get_urls_to_scrape(self) -> List[str]:
        """Get URLs to scrape based on current aggregation mode."""
        if not self.page_list:
            raise ValueError("No pages specified for scraping")
        
        return self.generate_url_range(self.page_list)
    
    def validate_wteg_parameters(self, pattern: str, city: str) -> bool:
        """Validate WTEG pattern and city parameters."""
        # Check for empty or whitespace-only strings
        if not pattern or not pattern.strip():
            return False
        if not city or not city.strip():
            return False
        
        # Check for valid characters (alphanumeric, underscore, dash)
        pattern_regex = re.compile(r'^[a-zA-Z0-9_-]+$')
        city_regex = re.compile(r'^[a-zA-Z0-9_-]+$')
        
        return (pattern_regex.match(pattern.strip()) is not None and 
                city_regex.match(city.strip()) is not None)
    
    def extract_page_id_from_url(self, url: str) -> Optional[int]:
        """Extract page ID from WTEG URL."""
        try:
            parsed = self.parse_url(url)
            return int(parsed["page_id"])
        except (ValueError, KeyError):
            return None
    
    def normalize_pattern_and_city(self, pattern: str, city: str) -> tuple[str, str]:
        """Normalize pattern and city names to lowercase."""
        return pattern.lower().strip(), city.lower().strip()
    
    def is_valid_page_id(self, page_id: Union[str, int]) -> bool:
        """Validate if page ID is valid (non-negative integer)."""
        try:
            page_num = int(page_id)
            return page_num >= 0
        except (ValueError, TypeError):
            return False
    
    def get_wteg_base_url(self, pattern: str, city: str) -> str:
        """Get base URL for WTEG pattern and city."""
        normalized_pattern, normalized_city = self.normalize_pattern_and_city(pattern, city)
        return f"{self.base_scheme}://{self.base_domain}/{normalized_pattern}/{normalized_city}"
    
    def detect_wteg_pattern_from_url(self, url: str) -> Optional[Dict[str, str]]:
        """Detect WTEG pattern from any URL that might be WTEG format."""
        try:
            if self.is_wteg_url(url):
                return self.parse_url(url)
            return None
        except Exception:
            return None
    
    def suggest_related_urls(self, base_url: str, page_count: int = 5) -> List[str]:
        """Suggest related WTEG URLs based on a base URL."""
        try:
            parsed = self.parse_url(base_url)
            pattern = parsed["pattern"]
            city = parsed["city"]
            current_page = int(parsed["page_id"])
            
            # Suggest nearby page IDs
            suggested_pages = []
            
            # Add current page
            suggested_pages.append(current_page)
            
            # Add pages around current (±2)
            for offset in [-2, -1, 1, 2]:
                new_page = current_page + offset
                if new_page > 0:  # Only positive page numbers
                    suggested_pages.append(new_page)
            
            # Add some common starting pages
            for common_page in [1, 2, 3]:
                if common_page not in suggested_pages:
                    suggested_pages.append(common_page)
            
            # Limit to requested count and sort
            suggested_pages = sorted(list(set(suggested_pages)))[:page_count]
            
            # Generate URLs
            suggested_urls = []
            for page in suggested_pages:
                url = f"{self.base_scheme}://{self.base_domain}/{pattern}/{city}/{page}"
                suggested_urls.append(url)
            
            return suggested_urls
            
        except Exception:
            return []
    
    def get_aggregation_summary(self) -> Dict[str, any]:
        """Get summary of current aggregation configuration."""
        return {
            "pattern": self.pattern_name,
            "city": self.city_name,
            "aggregation_mode": self.aggregation_mode,
            "page_count": len(self.page_list),
            "pages": self.page_list,
            "total_urls": len(self.page_list) if self.page_list else 0
        }