"""Multi-strategy restaurant data scraper combining all extraction methods."""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .json_ld_extractor import JSONLDExtractor, JSONLDExtractionResult
from .microdata_extractor import MicrodataExtractor, MicrodataExtractionResult
from .heuristic_extractor import HeuristicExtractor, HeuristicExtractionResult
from .ethical_scraper import EthicalScraper
from .javascript_handler import JavaScriptHandler, PopupInfo
from .restaurant_popup_detector import RestaurantPopupDetector
from ..config.scraping_config import ScrapingConfig


@dataclass
class RestaurantData:
    """Unified restaurant data from all extraction strategies."""

    name: str = ""
    address: str = ""
    phone: str = ""
    hours: str = ""
    price_range: str = ""
    cuisine: str = ""
    website: str = ""
    menu_items: Dict[str, List[str]] = None
    social_media: List[str] = None
    confidence: str = "medium"
    sources: List[str] = None

    def __post_init__(self):
        if self.menu_items is None:
            self.menu_items = {}
        if self.social_media is None:
            self.social_media = []
        if self.sources is None:
            self.sources = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "hours": self.hours,
            "price_range": self.price_range,
            "cuisine": self.cuisine,
            "website": self.website,
            "menu_items": self.menu_items,
            "social_media": self.social_media,
            "confidence": self.confidence,
            "sources": self.sources,
        }


class MultiStrategyScraper:
    """Scraper that combines JSON-LD, microdata, and heuristic extraction."""

    def __init__(self, enable_ethical_scraping: bool = True, ethical_scraper: Optional[EthicalScraper] = None, config: Optional[ScrapingConfig] = None):
        """Initialize multi-strategy scraper."""
        self.json_ld_extractor = JSONLDExtractor()
        self.microdata_extractor = MicrodataExtractor()
        self.heuristic_extractor = HeuristicExtractor()
        self.config = config

        if ethical_scraper:
            self.ethical_scraper = ethical_scraper
        elif enable_ethical_scraping:
            self.ethical_scraper = EthicalScraper()
        else:
            self.ethical_scraper = None

        # Initialize JavaScript components if enabled
        if config and config.enable_javascript_rendering:
            self.javascript_handler = JavaScriptHandler(
                timeout=config.javascript_timeout,
                enable_browser_automation=config.enable_browser_automation
            )
            # Configure browser options if automation is enabled
            if config.enable_browser_automation and self.javascript_handler.browser_automation_enabled:
                self.javascript_handler.browser_type = config.browser_type
                self.javascript_handler.headless = config.headless_browser
        else:
            self.javascript_handler = None

        if config and config.enable_popup_detection:
            self.popup_detector = RestaurantPopupDetector()
        else:
            self.popup_detector = None

    def scrape_url(self, url: str) -> Optional[RestaurantData]:
        """Scrape a single URL using all available strategies."""
        # Check robots.txt if ethical scraping is enabled
        if self.ethical_scraper and not self.ethical_scraper.is_allowed_by_robots(url):
            return None

        # Fetch the page content
        if self.ethical_scraper:
            html_content = self.ethical_scraper.fetch_page_with_retry(url)
        else:
            # Fallback for testing without rate limiting
            import requests

            try:
                response = requests.get(url, timeout=30)
                html_content = response.text
            except:
                html_content = None

        if not html_content:
            return None

        # Process JavaScript and handle popups if enabled
        html_content = self._process_javascript_and_popups(html_content, url)

        # Extract data using all strategies
        return self._extract_with_all_strategies(html_content, url)

    def _process_javascript_and_popups(self, html_content: str, url: str) -> str:
        """Process JavaScript rendering and handle popups."""
        try:
            # Check if JavaScript rendering is required and enabled
            if (self.javascript_handler and 
                self.javascript_handler.is_javascript_required(html_content)):
                rendered_content = self.javascript_handler.render_page(url)
                if rendered_content:
                    html_content = rendered_content

            # Detect and handle popups if enabled
            if self.popup_detector:
                popups = self.popup_detector.detect_restaurant_popups(html_content, url)
                if popups:
                    html_content = self._handle_detected_popups(html_content, popups)

        except Exception as e:
            # Log error but continue with original content
            print(f"JavaScript/popup processing error for {url}: {e}")

        return html_content

    def _handle_detected_popups(self, html_content: str, popups: List[dict]) -> str:
        """Handle detected popups based on configuration."""
        if not self.config or not popups:
            return html_content

        strategy = self.config.popup_handling_strategy
        
        if strategy == 'skip':
            return html_content
        elif strategy == 'manual':
            # For manual strategy, log detected popups but don't handle them
            print(f"Manual popup handling - detected {len(popups)} popups")
            return html_content
        else:  # strategy == 'auto'
            # Handle popups in priority order
            for popup in sorted(popups, key=lambda p: p['priority']):
                if self.javascript_handler:
                    # Create PopupInfo for the handler
                    popup_info = PopupInfo(
                        type=popup['type'],
                        selector=popup['selectors'][0] if popup['selectors'] else '',
                        action_required=popup['action_strategy']
                    )
                    html_content = self.javascript_handler.handle_popup(popup_info, html_content)
            
        return html_content

    def _extract_with_all_strategies(self, html_content: str, url: Optional[str] = None) -> Optional[RestaurantData]:
        """Extract data using all strategies and merge results."""
        json_ld_results = self.json_ld_extractor.extract_from_html(html_content)
        microdata_results = self.microdata_extractor.extract_from_html(html_content)
        heuristic_results = self.heuristic_extractor.extract_from_html(html_content, url)

        # Merge results with priority: JSON-LD > Microdata > Heuristic
        merged_data = self._merge_extraction_results(
            json_ld_results, microdata_results, heuristic_results, url
        )

        return merged_data

    def _merge_extraction_results(
        self,
        json_ld_results: List[JSONLDExtractionResult],
        microdata_results: List[MicrodataExtractionResult],
        heuristic_results: List[HeuristicExtractionResult],
        url: Optional[str] = None,
    ) -> Optional[RestaurantData]:
        """Merge results from all extraction strategies."""

        # Collect all results
        all_results = []
        sources = []

        if json_ld_results:
            all_results.extend(json_ld_results)
            sources.append("json-ld")

        if microdata_results:
            all_results.extend(microdata_results)
            sources.append("microdata")

        if heuristic_results:
            all_results.extend(heuristic_results)
            sources.append("heuristic")

        if not all_results:
            return None

        # Start with the highest confidence result as base
        base_result = max(
            all_results, key=lambda r: self._confidence_score(r.confidence)
        )

        # Create merged restaurant data
        # Extract base domain for website field
        website_url = ""
        if url:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            website_url = f"{parsed.scheme}://{parsed.netloc}/"
        
        merged = RestaurantData(name=base_result.name, sources=sources, website=website_url)

        # Merge fields with priority order
        self._merge_field(merged, all_results, "address")
        self._merge_field(merged, all_results, "phone")
        self._merge_field(merged, all_results, "hours")
        self._merge_field(merged, all_results, "price_range")
        self._merge_field(merged, all_results, "cuisine")

        # Merge menu items from all sources
        for result in all_results:
            if hasattr(result, "menu_items") and result.menu_items:
                for section, items in result.menu_items.items():
                    if section not in merged.menu_items:
                        merged.menu_items[section] = []
                    # Add unique items only
                    for item in items:
                        if item not in merged.menu_items[section]:
                            merged.menu_items[section].append(item)

        # Merge social media links
        for result in all_results:
            if hasattr(result, "social_media") and result.social_media:
                for link in result.social_media:
                    if link not in merged.social_media:
                        merged.social_media.append(link)

        # Calculate overall confidence
        merged.confidence = self._calculate_merged_confidence(all_results)

        return merged

    def _merge_field(self, merged: RestaurantData, results: List, field_name: str):
        """Merge a specific field from all results with priority."""
        # Priority order: json-ld > microdata > heuristic
        source_priority = {"json-ld": 3, "microdata": 2, "heuristic": 1}

        best_value = ""
        best_priority = 0

        for result in results:
            if hasattr(result, field_name):
                value = getattr(result, field_name, "")
                if value and value.strip():
                    source = getattr(result, "source", "unknown")
                    priority = source_priority.get(source, 0)

                    # Use this value if it has higher priority or if we don't have a value yet
                    if priority > best_priority or not best_value:
                        best_value = value
                        best_priority = priority

        setattr(merged, field_name, best_value)

    def _confidence_score(self, confidence: str) -> int:
        """Convert confidence string to numeric score."""
        confidence_scores = {"high": 3, "medium": 2, "low": 1}
        return confidence_scores.get(confidence.lower(), 1)

    def _calculate_merged_confidence(self, results: List) -> str:
        """Calculate overall confidence from all extraction results."""
        if not results:
            return "low"

        # Get the highest confidence level
        max_confidence = max(self._confidence_score(r.confidence) for r in results)

        # Factor in number of successful extraction methods
        num_sources = len(set(getattr(r, "source", "unknown") for r in results))

        if max_confidence >= 3 and num_sources >= 2:
            return "high"
        elif max_confidence >= 2 or num_sources >= 2:
            return "medium"
        else:
            return "low"

    def scrape_multiple_urls(self, urls: List[str]) -> List[RestaurantData]:
        """Scrape multiple URLs and return results."""
        results = []

        for url in urls:
            try:
                data = self.scrape_url(url)
                if data:
                    results.append(data)
            except Exception as e:
                # Log error but continue with other URLs
                print(f"Error scraping {url}: {e}")
                continue

        return results
