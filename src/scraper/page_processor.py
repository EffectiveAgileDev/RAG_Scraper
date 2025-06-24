"""Page processor for fetching and processing individual pages."""
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup

from .page_classifier import PageClassifier
from .multi_strategy_scraper import MultiStrategyScraper, RestaurantData


class PageProcessor:
    """Handles fetching and processing of individual web pages."""

    def __init__(self, enable_ethical_scraping: bool = True):
        """Initialize PageProcessor with required components.
        
        Args:
            enable_ethical_scraping: Whether to enable ethical scraping features
        """
        self.enable_ethical_scraping = enable_ethical_scraping
        self.page_classifier = PageClassifier()
        self.multi_strategy_scraper = MultiStrategyScraper(enable_ethical_scraping)

    def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch HTML content from a URL.

        Args:
            url: URL to fetch

        Returns:
            HTML content or None if failed
        """
        try:
            if (
                self.enable_ethical_scraping
                and self.multi_strategy_scraper.ethical_scraper
            ):
                # Use ethical scraper with rate limiting
                html_content = (
                    self.multi_strategy_scraper.ethical_scraper.fetch_page_with_retry(
                        url
                    )
                )
                return html_content
            else:
                # Fallback method for testing
                import requests

                response = requests.get(url, timeout=30)
                response.raise_for_status()
                return response.text

        except Exception:
            return None

    def _fetch_and_process_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch and process a single page.

        Args:
            url: URL to fetch and process

        Returns:
            Dictionary with page_type and extracted data, or None if failed
        """
        # Fetch page content
        html_content = self._fetch_page(url)
        if not html_content:
            return None

        # Classify page type
        page_type = self.page_classifier.classify_page(url, html_content)

        # Extract restaurant data using multi-strategy approach
        restaurant_data = self.multi_strategy_scraper.scrape_url(url)

        if not restaurant_data:
            # If multi-strategy fails, create minimal data
            restaurant_data = RestaurantData(sources=["heuristic"])

        return {"page_type": page_type, "data": restaurant_data}

    def _extract_restaurant_name(self, html_content: str) -> str:
        """Extract restaurant name from HTML content for progress tracking.

        Args:
            html_content: HTML content to analyze

        Returns:
            Restaurant name or default
        """
        try:
            # Use BeautifulSoup to parse HTML
            soup = BeautifulSoup(html_content, "html.parser")

            # Try to find restaurant name in title or h1
            title = soup.find("title")
            if title:
                return title.get_text().strip().split("|")[0].split("-")[0].strip()

            h1 = soup.find("h1")
            if h1:
                return h1.get_text().strip()

            return "Restaurant"

        except Exception:
            return "Restaurant"