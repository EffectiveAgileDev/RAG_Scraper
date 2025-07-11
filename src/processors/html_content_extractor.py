"""HTML content extractor for web-based restaurant data extraction."""

import re
import requests
from typing import Union, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from .base_import_processor import BaseContentExtractor


class HTMLContentExtractor(BaseContentExtractor):
    """Extracts text content from HTML sources (URLs or HTML content)."""
    
    def __init__(self, timeout: int = 30, user_agent: str = None):
        """Initialize HTML content extractor.
        
        Args:
            timeout: Request timeout in seconds
            user_agent: Custom user agent string
        """
        self.timeout = timeout
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
    
    def extract_content(self, source: Union[str, bytes], source_identifier: str) -> str:
        """Extract text content from HTML source.
        
        Args:
            source: URL string or HTML content
            source_identifier: URL or identifier for the source
            
        Returns:
            Extracted text content
            
        Raises:
            ValueError: If source is invalid
            requests.RequestException: If URL fetching fails
        """
        if not self.validate_source(source):
            raise ValueError(f"Invalid HTML source: {source}")
        
        # If source is a URL, fetch the content
        if isinstance(source, str) and self._is_url(source):
            html_content = self._fetch_html_from_url(source)
        else:
            # Assume source is HTML content
            html_content = source if isinstance(source, str) else source.decode('utf-8')
        
        # Extract text from HTML
        return self._extract_text_from_html(html_content)
    
    def validate_source(self, source: Union[str, bytes]) -> bool:
        """Validate that the source is valid for HTML extraction.
        
        Args:
            source: Source data to validate
            
        Returns:
            True if source is valid for HTML extraction
        """
        if isinstance(source, str):
            # Check if it's a URL or contains HTML-like content
            return self._is_url(source) or self._contains_html(source)
        elif isinstance(source, bytes):
            # Check if bytes contain HTML-like content
            try:
                content = source.decode('utf-8')
                return self._contains_html(content)
            except UnicodeDecodeError:
                return False
        
        return False
    
    def _is_url(self, text: str) -> bool:
        """Check if text is a valid URL.
        
        Args:
            text: Text to check
            
        Returns:
            True if text is a URL
        """
        try:
            result = urlparse(text)
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except Exception:
            return False
    
    def _contains_html(self, text: str) -> bool:
        """Check if text contains HTML-like content.
        
        Args:
            text: Text to check
            
        Returns:
            True if text contains HTML tags
        """
        # Simple check for HTML tags
        html_pattern = re.compile(r'<[^>]+>')
        return bool(html_pattern.search(text))
    
    def _fetch_html_from_url(self, url: str) -> str:
        """Fetch HTML content from URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string
            
        Raises:
            requests.RequestException: If fetching fails
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to fetch URL {url}: {e}")
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """Extract clean text from HTML content.
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            Extracted text content
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_structured_content(self, source: Union[str, bytes], source_identifier: str) -> dict:
        """Extract structured content from HTML source.
        
        Args:
            source: URL string or HTML content
            source_identifier: URL or identifier for the source
            
        Returns:
            Dictionary with structured content
        """
        if not self.validate_source(source):
            raise ValueError(f"Invalid HTML source: {source}")
        
        # If source is a URL, fetch the content
        if isinstance(source, str) and self._is_url(source):
            html_content = self._fetch_html_from_url(source)
        else:
            # Assume source is HTML content
            html_content = source if isinstance(source, str) else source.decode('utf-8')
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract structured data
        structured_data = {
            'title': self._extract_title(soup),
            'meta_description': self._extract_meta_description(soup),
            'headers': self._extract_headers(soup),
            'links': self._extract_links(soup),
            'text_content': self._extract_text_from_html(html_content),
            'json_ld': self._extract_json_ld(soup),
            'microdata': self._extract_microdata(soup)
        }
        
        return structured_data
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ''
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description."""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '').strip() if meta_desc else ''
    
    def _extract_headers(self, soup: BeautifulSoup) -> list:
        """Extract all headers (h1-h6)."""
        headers = []
        for i in range(1, 7):
            for header in soup.find_all(f'h{i}'):
                headers.append({
                    'level': i,
                    'text': header.get_text().strip()
                })
        return headers
    
    def _extract_links(self, soup: BeautifulSoup) -> list:
        """Extract all links."""
        links = []
        for link in soup.find_all('a', href=True):
            links.append({
                'href': link['href'],
                'text': link.get_text().strip()
            })
        return links
    
    def _extract_json_ld(self, soup: BeautifulSoup) -> list:
        """Extract JSON-LD structured data."""
        json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        json_ld_data = []
        
        for script in json_ld_scripts:
            try:
                import json
                data = json.loads(script.get_text())
                json_ld_data.append(data)
            except json.JSONDecodeError:
                continue
        
        return json_ld_data
    
    def _extract_microdata(self, soup: BeautifulSoup) -> list:
        """Extract microdata from HTML."""
        microdata_items = []
        
        # Find all elements with itemscope
        for item in soup.find_all(attrs={'itemscope': True}):
            item_data = {
                'type': item.get('itemtype', ''),
                'properties': {}
            }
            
            # Find all properties within this item
            for prop in item.find_all(attrs={'itemprop': True}):
                prop_name = prop.get('itemprop')
                prop_value = prop.get('content') or prop.get_text().strip()
                
                if prop_name in item_data['properties']:
                    # Handle multiple values
                    if not isinstance(item_data['properties'][prop_name], list):
                        item_data['properties'][prop_name] = [item_data['properties'][prop_name]]
                    item_data['properties'][prop_name].append(prop_value)
                else:
                    item_data['properties'][prop_name] = prop_value
            
            microdata_items.append(item_data)
        
        return microdata_items