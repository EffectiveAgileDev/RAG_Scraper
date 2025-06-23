"""Enhanced microdata extraction engine with entity correlation."""
import re
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass
from bs4 import BeautifulSoup
from .enhanced_json_ld_extractor import ExtractionContext


class DataCorrelator:
    """Correlates data between parent and child pages."""
    
    def merge_parent_child_data(self, parent_data: Dict[str, Any], child_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge parent and child data with child taking precedence."""
        merged = parent_data.copy()
        
        # Child data overrides parent data
        for key, value in child_data.items():
            if value:  # Only override if child has non-empty value
                merged[key] = value
                
        return merged


class EntityCorrelationTracker:
    """Tracks entity correlations across multiple pages."""
    
    def __init__(self):
        self._entities = {}
        
    def add_entity_mention(self, entity_name: str, page_id: str, data: Dict[str, Any]):
        """Add an entity mention from a page."""
        if entity_name not in self._entities:
            self._entities[entity_name] = []
            
        self._entities[entity_name].append({
            'page_id': page_id,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
        
    def get_correlations(self, entity_name: str) -> List[Dict[str, Any]]:
        """Get all correlations for an entity."""
        return self._entities.get(entity_name, [])


class MicrodataPatternRecognizer:
    """Recognizes microdata patterns across pages."""
    
    def __init__(self):
        self._patterns = {}
        
    def record_successful_extraction(self, pattern: str, selector: str, success: bool):
        """Record a successful extraction pattern."""
        if pattern not in self._patterns:
            self._patterns[pattern] = {'attempts': 0, 'successes': 0, 'selectors': {}}
            
        self._patterns[pattern]['attempts'] += 1
        if success:
            self._patterns[pattern]['successes'] += 1
            
        if selector not in self._patterns[pattern]['selectors']:
            self._patterns[pattern]['selectors'][selector] = {'attempts': 0, 'successes': 0}
            
        self._patterns[pattern]['selectors'][selector]['attempts'] += 1
        if success:
            self._patterns[pattern]['selectors'][selector]['successes'] += 1
            
    def get_reliable_patterns(self) -> Dict[str, Dict]:
        """Get patterns with high reliability."""
        reliable = {}
        
        for pattern, stats in self._patterns.items():
            if stats['attempts'] >= 2:  # Minimum attempts
                confidence = stats['successes'] / stats['attempts']
                if confidence >= 0.8:  # High confidence threshold
                    reliable[pattern] = {
                        'confidence': confidence,
                        'attempts': stats['attempts'],
                        'successes': stats['successes']
                    }
                    
        return reliable


class MicrodataValidator:
    """Validates microdata against schema requirements."""
    
    def validate_restaurant_data(self, data: Dict[str, Any]) -> bool:
        """Validate restaurant data completeness."""
        required_fields = ['name']
        return all(data.get(field) for field in required_fields)


class CorrelationScorer:
    """Scores correlations between entities."""
    
    def calculate_correlation_score(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> float:
        """Calculate correlation score between two entities."""
        score = 0.0
        
        # Exact name match
        if entity1.get('name') == entity2.get('name'):
            score += 0.7
            
        # Partial name match
        elif entity1.get('name') and entity2.get('name'):
            name1 = entity1['name'].lower()
            name2 = entity2['name'].lower()
            if name1 in name2 or name2 in name1:
                score += 0.4
                
        # Address match
        if entity1.get('address') == entity2.get('address') and entity1.get('address'):
            score += 0.2
            
        # Phone match
        if entity1.get('phone') == entity2.get('phone') and entity1.get('phone'):
            score += 0.1
            
        return min(score, 1.0)


class DirectoryListingCorrelator:
    """Correlates restaurant listings in directory pages."""
    
    def extract_restaurant_listings(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract restaurant listings from directory HTML."""
        listings = []
        
        try:
            soup = BeautifulSoup(html_content, "html.parser")
        except Exception:
            return listings
            
        # Find all restaurant microdata blocks
        restaurant_elements = soup.find_all(attrs={
            "itemscope": True,
            "itemtype": re.compile(r".*schema\.org/Restaurant", re.IGNORECASE)
        })
        
        for element in restaurant_elements:
            listing = {}
            
            # Extract name
            name_elem = element.find(attrs={"itemprop": "name"})
            if name_elem:
                listing['name'] = name_elem.get_text(strip=True)
                
            # Extract URL
            url_elem = element.find(attrs={"itemprop": "url"})
            if url_elem:
                listing['detail_url'] = url_elem.get_text(strip=True)
                
            if listing.get('name'):
                listings.append(listing)
                
        return listings


class EnhancedMicrodataExtractionResult:
    """Enhanced microdata extraction result with metadata tracking."""
    
    def __init__(
        self,
        name: str = "",
        address: str = "",
        phone: str = "",
        hours: str = "",
        price_range: str = "",
        cuisine: str = "",
        menu_items: Optional[Dict[str, List[str]]] = None,
        social_media: Optional[List[str]] = None,
        confidence: str = "medium",
        source: str = "microdata",
        extraction_metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.address = address
        self.phone = phone
        self.hours = hours
        self.price_range = price_range
        self.cuisine = cuisine
        self.menu_items = menu_items or {}
        self.social_media = social_media or []
        self.confidence = confidence
        self.source = source
        self.extraction_metadata = extraction_metadata or {}
        
    def is_valid(self) -> bool:
        """Check if extraction result has valid data."""
        return bool(self.name and self.name.strip())
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "hours": self.hours,
            "price_range": self.price_range,
            "cuisine": self.cuisine,
            "menu_items": self.menu_items,
            "social_media": self.social_media,
            "confidence": self.confidence,
            "source": self.source,
            "extraction_metadata": self.extraction_metadata
        }


class MicrodataExtractor:
    """Enhanced microdata extractor with entity correlation."""
    
    RELEVANT_ITEMTYPES = {
        "http://schema.org/restaurant",
        "http://schema.org/foodestablishment", 
        "http://schema.org/localbusiness",
        "https://schema.org/restaurant",
        "https://schema.org/foodestablishment",
        "https://schema.org/localbusiness",
    }
    
    def __init__(self, extraction_context: Optional[ExtractionContext] = None):
        """Initialize with optional extraction context."""
        self.extraction_context = extraction_context or ExtractionContext()
        
    def extract_from_html(self, html_content: str) -> List[EnhancedMicrodataExtractionResult]:
        """Extract restaurant data from HTML containing microdata."""
        if not html_content or not html_content.strip():
            return []
            
        try:
            soup = BeautifulSoup(html_content, "html.parser")
        except Exception:
            return []
            
        results = []
        all_extractions = []
        
        # Find all elements with relevant itemscope and itemtype
        microdata_elements = soup.find_all(attrs={"itemscope": True, "itemtype": True})
        
        for element in microdata_elements:
            itemtype = element.get("itemtype", "")
            if self.is_relevant_itemtype(itemtype):
                result = self.extract_restaurant_data(element)
                if result and result.is_valid():
                    all_extractions.append(result)
                    
        # Correlate multiple blocks if they exist
        if len(all_extractions) > 1:
            merged_result = self._correlate_multiple_blocks(all_extractions)
            if merged_result:
                results.append(merged_result)
        elif all_extractions:
            results.extend(all_extractions)
            
        # Apply parent correlation if context available
        if self.extraction_context.parent_data and results:
            for result in results:
                self._apply_parent_correlation(result)
                
        return results
        
    def extract_restaurant_data(self, element) -> Optional[EnhancedMicrodataExtractionResult]:
        """Extract restaurant data from microdata element."""
        # Extract basic information
        name = self._extract_name(element)
        if not name:
            return None
            
        address = self._extract_address(element)
        phone = self._extract_phone(element)
        hours = self._extract_hours(element)
        price_range = self._extract_price_range(element)
        cuisine = self._extract_cuisine(element)
        menu_items = self._extract_menu(element)
        social_media = self._extract_social_media(element)
        
        # Calculate confidence with context
        confidence = self._calculate_confidence_with_context(element)
        
        # Build extraction metadata
        extraction_metadata = self._build_extraction_metadata(element)
        
        return EnhancedMicrodataExtractionResult(
            name=name,
            address=address,
            phone=phone,
            hours=hours,
            price_range=price_range,
            cuisine=cuisine,
            menu_items=menu_items,
            social_media=social_media,
            confidence=confidence,
            source="microdata",
            extraction_metadata=extraction_metadata
        )
        
    def _correlate_multiple_blocks(self, extractions: List[EnhancedMicrodataExtractionResult]) -> Optional[EnhancedMicrodataExtractionResult]:
        """Correlate and merge multiple microdata blocks."""
        if not extractions:
            return None
            
        # Start with first extraction as base
        merged = extractions[0]
        
        # Merge data from other extractions
        for extraction in extractions[1:]:
            if not merged.phone and extraction.phone:
                merged.phone = extraction.phone
            if not merged.address and extraction.address:
                merged.address = extraction.address
            if not merged.cuisine and extraction.cuisine:
                merged.cuisine = extraction.cuisine
            if not merged.hours and extraction.hours:
                merged.hours = extraction.hours
            if not merged.price_range and extraction.price_range:
                merged.price_range = extraction.price_range
                
        # Mark as correlated
        merged.extraction_metadata['block_correlation'] = True
        
        return merged
        
    def _apply_parent_correlation(self, result: EnhancedMicrodataExtractionResult):
        """Apply correlation with parent page data."""
        if not self.extraction_context.parent_data:
            return
            
        parent_data = self.extraction_context.parent_data
        
        # Mark correlation in metadata
        result.extraction_metadata['parent_correlation'] = True
        
        # Boost confidence if parent data provides context
        if (hasattr(parent_data, 'cuisine') and parent_data.cuisine and 
            not result.cuisine):
            result.extraction_metadata['correlation_boost'] = True
            
    def _build_extraction_metadata(self, element) -> Dict[str, Any]:
        """Build extraction metadata including relationships and tracking info."""
        metadata = {
            'method': 'microdata',
            'timestamp': datetime.now().isoformat(),
        }
        
        # Add entity relationship info
        if self.extraction_context.entity_id:
            metadata['entity_id'] = self.extraction_context.entity_id
        if self.extraction_context.parent_id:
            metadata['parent_id'] = self.extraction_context.parent_id
        if self.extraction_context.source_url:
            metadata['source_url'] = self.extraction_context.source_url
            
        # Add inherited context
        if self.extraction_context.parent_context:
            metadata['inherited_context'] = self.extraction_context.parent_context
            
        return metadata
        
    def _calculate_confidence_with_context(self, element) -> str:
        """Calculate confidence with context awareness."""
        # Base confidence calculation
        base_confidence = self._calculate_confidence(element)
        
        # Boost if we have parent correlation
        if self.extraction_context.parent_data:
            # Could boost confidence here
            pass
            
        return base_confidence
        
    def is_relevant_itemtype(self, itemtype: str) -> bool:
        """Check if itemtype is relevant for restaurant extraction."""
        if not itemtype:
            return False
            
        itemtype_lower = itemtype.lower()
        return any(
            relevant.lower() in itemtype_lower
            for relevant in ["restaurant", "foodestablishment", "localbusiness"]
        )
        
    def _extract_name(self, element) -> str:
        """Extract name from microdata element."""
        name_elem = element.find(attrs={"itemprop": "name"})
        if name_elem:
            return name_elem.get_text(strip=True)
        return ""
        
    def _extract_address(self, element) -> str:
        """Extract address from microdata element."""
        # Look for postal address first
        address_elem = element.find(attrs={"itemprop": "address"})
        if address_elem:
            return self._extract_postal_address(address_elem)
            
        return ""
        
    def _extract_postal_address(self, address_element) -> str:
        """Extract postal address from address element."""
        parts = []
        
        # Street address
        street_elem = address_element.find(attrs={"itemprop": "streetAddress"})
        if street_elem:
            parts.append(street_elem.get_text(strip=True))
            
        # City, state, zip
        city_elem = address_element.find(attrs={"itemprop": "addressLocality"})
        state_elem = address_element.find(attrs={"itemprop": "addressRegion"}) 
        zip_elem = address_element.find(attrs={"itemprop": "postalCode"})
        
        location_parts = []
        if city_elem:
            location_parts.append(city_elem.get_text(strip=True))
        if state_elem:
            state_text = state_elem.get_text(strip=True)
            if location_parts:
                location_parts.append(f", {state_text}")
            else:
                location_parts.append(state_text)
        if zip_elem:
            location_parts.append(f" {zip_elem.get_text(strip=True)}")
            
        if location_parts:
            parts.append("".join(location_parts))
            
        return ", ".join(parts)
        
    def _extract_phone(self, element) -> str:
        """Extract phone from microdata element."""
        phone_elem = element.find(attrs={"itemprop": "telephone"})
        if phone_elem:
            return phone_elem.get_text(strip=True)
        return ""
        
    def _extract_hours(self, element) -> str:
        """Extract hours from microdata element."""
        hours_elem = element.find(attrs={"itemprop": "openingHours"})
        if hours_elem:
            return hours_elem.get_text(strip=True)
        return ""
        
    def _extract_price_range(self, element) -> str:
        """Extract price range from microdata element."""
        price_elem = element.find(attrs={"itemprop": "priceRange"})
        if price_elem:
            return price_elem.get_text(strip=True)
        return ""
        
    def _extract_cuisine(self, element) -> str:
        """Extract cuisine from microdata element."""
        cuisine_elem = element.find(attrs={"itemprop": "servesCuisine"})
        if cuisine_elem:
            return cuisine_elem.get_text(strip=True)
        return ""
        
    def _extract_menu(self, element) -> Dict[str, List[str]]:
        """Extract menu items from microdata element."""
        # Basic implementation - could be enhanced
        return {}
        
    def _extract_social_media(self, element) -> List[str]:
        """Extract social media links from microdata element."""
        social_links = []
        same_as_elems = element.find_all(attrs={"itemprop": "sameAs"})
        for elem in same_as_elems:
            href = elem.get("href")
            if href:
                social_links.append(href)
        return social_links
        
    def _calculate_confidence(self, element) -> str:
        """Calculate confidence score based on data completeness."""
        field_count = 0
        
        # Count available fields
        if element.find(attrs={"itemprop": "name"}):
            field_count += 1
        if element.find(attrs={"itemprop": "address"}):
            field_count += 1
        if element.find(attrs={"itemprop": "telephone"}):
            field_count += 1
        if element.find(attrs={"itemprop": "openingHours"}):
            field_count += 1
        if element.find(attrs={"itemprop": "priceRange"}):
            field_count += 1
        if element.find(attrs={"itemprop": "servesCuisine"}):
            field_count += 1
            
        # Calculate confidence based on field count
        if field_count >= 4:
            return "high"
        elif field_count >= 2:
            return "medium"
        else:
            return "low"