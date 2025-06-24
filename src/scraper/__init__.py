"""Web scraping engines for restaurant data extraction."""

from .page_processor import PageProcessor
from .multi_page_scraper_config import MultiPageScraperConfig

__all__ = ['PageProcessor', 'MultiPageScraperConfig']
