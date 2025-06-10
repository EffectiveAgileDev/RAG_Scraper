"""Page discovery for multi-page website navigation."""
import re
from typing import Set, List, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


class PageDiscovery:
    """Discovers and filters relevant pages for restaurant data extraction."""
    
    # Keywords that indicate relevant restaurant pages
    RELEVANT_KEYWORDS = {
        'menu', 'about', 'contact', 'hours', 'location', 'info', 'information',
        'food', 'dining', 'story', 'history', 'cuisine', 'restaurant', 'dine',
        'reservations', 'reserve', 'book', 'directions', 'us', 'home'
    }
    
    # Keywords that indicate irrelevant pages
    IRRELEVANT_KEYWORDS = {
        'blog', 'news', 'careers', 'jobs', 'privacy', 'terms', 'legal',
        'admin', 'login', 'register', 'cart', 'checkout', 'order', 'delivery',
        'catering', 'events', 'private', 'press', 'media', 'franchise'
    }
    
    # Priority order for page types (higher number = higher priority)
    PAGE_PRIORITIES = {
        'menu': 10,
        'contact': 9,
        'about': 8,
        'hours': 7,
        'location': 6,
        'info': 5,
        'home': 4,
        'story': 3,
        'dining': 3,
        'food': 3
    }
    
    def __init__(self, base_url: str, max_pages: int = 10):
        """Initialize page discovery with base URL and limits.
        
        Args:
            base_url: Base URL of the website
            max_pages: Maximum number of pages to discover
        """
        self.base_url = base_url.rstrip('/')
        self.max_pages = max_pages
        self.discovered_pages: Set[str] = set()
        
        # Parse base domain for filtering
        parsed = urlparse(base_url)
        self.base_domain = parsed.netloc
    
    def discover_navigation_links(self, html_content: str) -> Set[str]:
        """Discover navigation links from HTML content.
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            Set of discovered navigation URLs
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find navigation elements
        nav_selectors = [
            'nav a',           # Navigation elements
            'header a',        # Header links
            '.navigation a',   # Navigation class
            '.nav a',          # Nav class
            '.menu a',         # Menu class (navigation, not food menu)
            'ul.menu a',       # Menu list
            '.main-nav a',     # Main navigation
            '.primary-nav a'   # Primary navigation
        ]
        
        links = set()
        for selector in nav_selectors:
            nav_links = soup.select(selector)
            for link in nav_links:
                href = link.get('href')
                if href:
                    absolute_url = self._normalize_url(href)
                    if absolute_url and self._is_internal_url(absolute_url):
                        links.add(absolute_url)
        
        return links
    
    def extract_all_internal_links(self, html_content: str) -> Set[str]:
        """Extract all internal links from HTML content.
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            Set of internal URLs
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        links = set()
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href:
                absolute_url = self._normalize_url(href)
                if absolute_url and self._is_internal_url(absolute_url):
                    links.add(absolute_url)
        
        return links
    
    def filter_relevant_pages(self, urls: Set[str]) -> Set[str]:
        """Filter URLs to keep only relevant restaurant pages.
        
        Args:
            urls: Set of URLs to filter
            
        Returns:
            Set of relevant URLs
        """
        relevant_urls = set()
        
        for url in urls:
            if self._is_relevant_page(url):
                relevant_urls.add(url)
        
        return relevant_urls
    
    def apply_page_limit(self, urls: Set[str]) -> Set[str]:
        """Apply maximum page limit to discovered URLs.
        
        Args:
            urls: Set of URLs to limit
            
        Returns:
            Limited set of URLs
        """
        if len(urls) <= self.max_pages:
            return urls
        
        # Prioritize URLs and take top max_pages
        prioritized = self.prioritize_pages(urls)
        return set(list(prioritized)[:self.max_pages])
    
    def get_new_pages(self, urls: Set[str]) -> Set[str]:
        """Get URLs that haven't been discovered yet.
        
        Args:
            urls: Set of URLs to check
            
        Returns:
            Set of new URLs
        """
        return urls - self.discovered_pages
    
    def prioritize_pages(self, urls: Set[str]) -> List[str]:
        """Prioritize URLs by relevance for restaurant data.
        
        Args:
            urls: Set of URLs to prioritize
            
        Returns:
            List of URLs sorted by priority (highest first)
        """
        def get_priority(url: str) -> int:
            """Get priority score for a URL."""
            url_lower = url.lower()
            path = urlparse(url).path.lower()
            
            # Check for high-priority keywords in path
            for keyword, priority in self.PAGE_PRIORITIES.items():
                if keyword in path or keyword in url_lower:
                    return priority
            
            # Default priority
            return 1
        
        # Sort by priority (descending)
        return sorted(urls, key=get_priority, reverse=True)
    
    def discover_all_pages(self, initial_url: str, html_content: str) -> List[str]:
        """Discover all relevant pages from a website starting point.
        
        Args:
            initial_url: Starting URL
            html_content: HTML content of the initial page
            
        Returns:
            List of discovered page URLs
        """
        # Start with the initial URL
        all_pages = {initial_url}
        self.discovered_pages.add(initial_url)
        
        # Discover navigation links
        nav_links = self.discover_navigation_links(html_content)
        
        # Filter and limit pages
        relevant_links = self.filter_relevant_pages(nav_links)
        new_links = self.get_new_pages(relevant_links)
        
        # Add new links to discovered pages
        all_pages.update(new_links)
        self.discovered_pages.update(new_links)
        
        # Apply page limit and prioritize
        limited_pages = self.apply_page_limit(all_pages)
        
        return self.prioritize_pages(limited_pages)
    
    def _normalize_url(self, href: str) -> Optional[str]:
        """Normalize a URL href to absolute URL.
        
        Args:
            href: URL href to normalize
            
        Returns:
            Absolute URL or None if invalid
        """
        if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
            return None
        
        # Handle empty href
        if not href.strip():
            return None
        
        try:
            # Convert to absolute URL
            absolute_url = urljoin(self.base_url, href)
            return absolute_url
        except Exception:
            return None
    
    def _is_internal_url(self, url: str) -> bool:
        """Check if URL is internal to the base domain.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is internal
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc == self.base_domain or parsed.netloc == ''
        except Exception:
            return False
    
    def _is_relevant_page(self, url: str) -> bool:
        """Check if a page is relevant for restaurant data extraction.
        
        Args:
            url: URL to check
            
        Returns:
            True if page is relevant
        """
        url_lower = url.lower()
        path = urlparse(url).path.lower()
        
        # Check for irrelevant keywords first
        for keyword in self.IRRELEVANT_KEYWORDS:
            if keyword in path or keyword in url_lower:
                return False
        
        # Check for relevant keywords
        for keyword in self.RELEVANT_KEYWORDS:
            if keyword in path or keyword in url_lower:
                return True
        
        # If no specific keywords found, check if it's a simple path
        # (likely to be relevant)
        path_parts = [p for p in path.split('/') if p]
        
        # Root path is relevant
        if not path_parts:
            return True
        
        # Simple single-word paths are likely relevant
        if len(path_parts) == 1 and len(path_parts[0]) <= 15:
            return True
        
        # Default to not relevant if we can't determine
        return False