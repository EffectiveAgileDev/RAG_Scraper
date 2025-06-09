"""Multi-strategy restaurant data scraper combining all extraction methods."""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .json_ld_extractor import JSONLDExtractor, JSONLDExtractionResult
from .microdata_extractor import MicrodataExtractor, MicrodataExtractionResult  
from .heuristic_extractor import HeuristicExtractor, HeuristicExtractionResult
from .ethical_scraper import EthicalScraper


@dataclass
class RestaurantData:
    """Unified restaurant data from all extraction strategies."""
    name: str = ""
    address: str = ""
    phone: str = ""
    hours: str = ""
    price_range: str = ""
    cuisine: str = ""
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
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'hours': self.hours,
            'price_range': self.price_range,
            'cuisine': self.cuisine,
            'menu_items': self.menu_items,
            'social_media': self.social_media,
            'confidence': self.confidence,
            'sources': self.sources
        }


class MultiStrategyScraper:
    """Scraper that combines JSON-LD, microdata, and heuristic extraction."""
    
    def __init__(self, enable_ethical_scraping: bool = True):
        """Initialize multi-strategy scraper."""
        self.json_ld_extractor = JSONLDExtractor()
        self.microdata_extractor = MicrodataExtractor()
        self.heuristic_extractor = HeuristicExtractor()
        
        if enable_ethical_scraping:
            self.ethical_scraper = EthicalScraper()
        else:
            self.ethical_scraper = None
    
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
        
        # Extract data using all strategies
        json_ld_results = self.json_ld_extractor.extract_from_html(html_content)
        microdata_results = self.microdata_extractor.extract_from_html(html_content)
        heuristic_results = self.heuristic_extractor.extract_from_html(html_content)
        
        # Merge results with priority: JSON-LD > Microdata > Heuristic
        merged_data = self._merge_extraction_results(
            json_ld_results, microdata_results, heuristic_results
        )
        
        return merged_data
    
    def _merge_extraction_results(
        self, 
        json_ld_results: List[JSONLDExtractionResult],
        microdata_results: List[MicrodataExtractionResult],
        heuristic_results: List[HeuristicExtractionResult]
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
        base_result = max(all_results, key=lambda r: self._confidence_score(r.confidence))
        
        # Create merged restaurant data
        merged = RestaurantData(
            name=base_result.name,
            sources=sources
        )
        
        # Merge fields with priority order
        self._merge_field(merged, all_results, 'address')
        self._merge_field(merged, all_results, 'phone')
        self._merge_field(merged, all_results, 'hours')
        self._merge_field(merged, all_results, 'price_range')
        self._merge_field(merged, all_results, 'cuisine')
        
        # Merge menu items from all sources
        for result in all_results:
            if hasattr(result, 'menu_items') and result.menu_items:
                for section, items in result.menu_items.items():
                    if section not in merged.menu_items:
                        merged.menu_items[section] = []
                    # Add unique items only
                    for item in items:
                        if item not in merged.menu_items[section]:
                            merged.menu_items[section].append(item)
        
        # Merge social media links
        for result in all_results:
            if hasattr(result, 'social_media') and result.social_media:
                for link in result.social_media:
                    if link not in merged.social_media:
                        merged.social_media.append(link)
        
        # Calculate overall confidence
        merged.confidence = self._calculate_merged_confidence(all_results)
        
        return merged
    
    def _merge_field(self, merged: RestaurantData, results: List, field_name: str):
        """Merge a specific field from all results with priority."""
        # Priority order: json-ld > microdata > heuristic
        source_priority = {'json-ld': 3, 'microdata': 2, 'heuristic': 1}
        
        best_value = ""
        best_priority = 0
        
        for result in results:
            if hasattr(result, field_name):
                value = getattr(result, field_name, "")
                if value and value.strip():
                    source = getattr(result, 'source', 'unknown')
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
        num_sources = len(set(getattr(r, 'source', 'unknown') for r in results))
        
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