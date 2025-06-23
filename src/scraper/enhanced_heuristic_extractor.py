"""Enhanced heuristic extraction engine with cross-page pattern learning."""
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass
from bs4 import BeautifulSoup
from .enhanced_json_ld_extractor import ExtractionContext
from .pattern_matchers import (
    PhonePatternMatcher,
    AddressPatternMatcher,
    HoursPatternMatcher,
    RestaurantNameExtractor,
)


class PatternLearner:
    """Learns successful extraction patterns across pages."""
    
    def __init__(self):
        self._patterns = {}
        
    def record_successful_pattern(self, field: str, selector: str, success: bool):
        """Record the success/failure of a pattern."""
        if field not in self._patterns:
            self._patterns[field] = {}
        if selector not in self._patterns[field]:
            self._patterns[field][selector] = {'successes': 0, 'attempts': 0}
            
        self._patterns[field][selector]['attempts'] += 1
        if success:
            self._patterns[field][selector]['successes'] += 1
            
    def get_best_patterns(self, field: str) -> List[Dict[str, Any]]:
        """Get best patterns for a field sorted by success rate."""
        if field not in self._patterns:
            return []
            
        patterns = []
        for selector, stats in self._patterns[field].items():
            success_rate = stats['successes'] / stats['attempts'] if stats['attempts'] > 0 else 0
            patterns.append({
                'selector': selector,
                'success_rate': success_rate,
                'attempts': stats['attempts']
            })
            
        return sorted(patterns, key=lambda x: (x['success_rate'], x['attempts']), reverse=True)


class CrossPagePatternAnalyzer:
    """Analyzes patterns across different page types."""
    
    def __init__(self):
        self._page_patterns = {}
        
    def record_pattern_usage(self, page_type: str, field: str, selector: str, success: bool):
        """Record pattern usage for a specific page type."""
        if page_type not in self._page_patterns:
            self._page_patterns[page_type] = {}
        if field not in self._page_patterns[page_type]:
            self._page_patterns[page_type][field] = {}
        if selector not in self._page_patterns[page_type][field]:
            self._page_patterns[page_type][field][selector] = {'successes': 0, 'attempts': 0}
            
        self._page_patterns[page_type][field][selector]['attempts'] += 1
        if success:
            self._page_patterns[page_type][field][selector]['successes'] += 1
            
    def get_pattern_correlations(self) -> Dict[str, Dict]:
        """Get correlations of patterns by page type."""
        correlations = {}
        
        for page_type, fields in self._page_patterns.items():
            correlations[page_type] = {}
            for field, selectors in fields.items():
                correlations[page_type][field] = {}
                for selector, stats in selectors.items():
                    success_rate = stats['successes'] / stats['attempts'] if stats['attempts'] > 0 else 0
                    correlations[page_type][field][selector] = {
                        'success_rate': success_rate,
                        'attempts': stats['attempts'],
                        'successes': stats['successes']
                    }
                    
        return correlations


class AdaptivePatternSelector:
    """Adaptively selects best patterns based on context."""
    
    def __init__(self):
        self._pattern_results = {}
        
    def add_pattern_result(self, field: str, selector: str, page_type: str, success: bool):
        """Add a pattern result."""
        key = f"{page_type}:{field}:{selector}"
        if key not in self._pattern_results:
            self._pattern_results[key] = {'successes': 0, 'attempts': 0}
            
        self._pattern_results[key]['attempts'] += 1
        if success:
            self._pattern_results[key]['successes'] += 1
            
    def get_best_patterns_for_page_type(self, page_type: str) -> Dict[str, Dict]:
        """Get best patterns for a specific page type."""
        best_patterns = {}
        
        for key, stats in self._pattern_results.items():
            if key.startswith(f"{page_type}:"):
                parts = key.split(":", 2)
                field = parts[1]
                selector = parts[2]
                
                confidence = stats['successes'] / stats['attempts'] if stats['attempts'] > 0 else 0
                
                if field not in best_patterns or confidence > best_patterns[field]['confidence']:
                    best_patterns[field] = {
                        'selector': selector,
                        'confidence': confidence,
                        'attempts': stats['attempts']
                    }
                    
        return best_patterns


class PatternEvolutionTracker:
    """Tracks how patterns evolve over time."""
    
    def __init__(self):
        self._evolution = {}
        
    def record_pattern_change(self, field: str, old_pattern: str, new_pattern: str, reason: str):
        """Record a pattern change."""
        if field not in self._evolution:
            self._evolution[field] = []
            
        self._evolution[field].append({
            'timestamp': datetime.now().isoformat(),
            'old_pattern': old_pattern,
            'new_pattern': new_pattern,
            'reason': reason
        })
        
    def get_pattern_evolution(self) -> Dict[str, List]:
        """Get pattern evolution history."""
        return self._evolution


class SiblingPatternSharer:
    """Shares successful patterns between sibling pages."""
    
    def __init__(self):
        self._shared_patterns = {}
        
    def share_pattern(self, entity_id: str, field: str, selector: str, success_rate: float):
        """Share a successful pattern from an entity."""
        if entity_id not in self._shared_patterns:
            self._shared_patterns[entity_id] = {}
            
        self._shared_patterns[entity_id][field] = {
            'selector': selector,
            'success_rate': success_rate,
            'shared_at': datetime.now().isoformat()
        }
        
    def get_patterns_for_sibling(self, target_entity: str, source_entity: str) -> Dict[str, Dict]:
        """Get patterns shared by a sibling entity."""
        return self._shared_patterns.get(source_entity, {})


class ExtractionFailureRecovery:
    """Provides recovery strategies when standard patterns fail."""
    
    def get_fallback_patterns(self) -> Dict[str, List[str]]:
        """Get fallback patterns for when standard extraction fails."""
        return {
            'name': [
                'span[id*="name"]',
                'div[data-name]',
                '*[class*="title"]',
                '*[class*="restaurant"]'
            ],
            'phone': [
                'div[data-phone]',
                '*[class*="contact"]',
                '*[class*="phone"]'
            ],
            'address': [
                '*[class*="address"]',
                '*[class*="location"]'
            ]
        }
        
    def attempt_fallback_extraction(self, html: str, fallback_patterns: Dict[str, List[str]]) -> Dict[str, Any]:
        """Attempt extraction using fallback patterns."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
        except Exception:
            return {}
            
        results = {}
        
        for field, selectors in fallback_patterns.items():
            for selector in selectors:
                try:
                    elements = soup.select(selector)
                    if elements:
                        text = elements[0].get_text(strip=True)
                        if text and field not in results:
                            results[field] = text
                            break
                except Exception:
                    continue
                    
        return results


class PatternConfidenceCalculator:
    """Calculates pattern confidence over time."""
    
    def __init__(self):
        self._usage_history = {}
        
    def record_pattern_usage(self, field: str, selector: str, success: bool):
        """Record pattern usage."""
        key = f"{field}:{selector}"
        if key not in self._usage_history:
            self._usage_history[key] = []
            
        self._usage_history[key].append({
            'success': success,
            'timestamp': datetime.now().isoformat()
        })
        
    def get_pattern_confidence(self, field: str, selector: str) -> float:
        """Calculate confidence for a pattern."""
        key = f"{field}:{selector}"
        if key not in self._usage_history:
            return 0.0
            
        history = self._usage_history[key]
        if not history:
            return 0.0
            
        successes = sum(1 for record in history if record['success'])
        return successes / len(history)


class MultiStrategyExtractor:
    """Uses multiple extraction strategies and combines results."""
    
    def extract_with_multiple_strategies(self, html: str) -> Dict[str, Any]:
        """Extract using multiple strategies."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
        except Exception:
            return {}
            
        results = {}
        
        # Strategy 1: Header elements
        header = soup.find(['header', 'h1', 'h2'])
        if header:
            name = header.get_text(strip=True)
            if name and 'name' not in results:
                results['name'] = name
                
        # Strategy 2: Footer contact info
        footer = soup.find('footer')
        if footer:
            phone_match = re.search(r'\b\d{3}[-.]?\d{4}\b', footer.get_text())
            if phone_match and 'phone' not in results:
                results['phone'] = phone_match.group()
                
        # Strategy 3: Address elements
        address_elem = soup.find('address')
        if address_elem:
            results['address'] = address_elem.get_text(strip=True)
            
        return results


class PageStructureAnalyzer:
    """Analyzes page structure for pattern optimization."""
    
    def analyze_structure(self, html: str) -> Dict[str, Any]:
        """Analyze the structure of a page."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
        except Exception:
            return {}
            
        structure = {
            'header_elements': [],
            'content_hierarchy': {},
            'max_depth': 0
        }
        
        # Find header elements
        for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            structure['header_elements'].append({
                'tag': header.name,
                'text': header.get_text(strip=True),
                'classes': header.get('class', [])
            })
            
        # Calculate max nesting depth
        def calculate_depth(element, current_depth=0):
            max_child_depth = current_depth
            for child in element.find_all(recursive=False):
                child_depth = calculate_depth(child, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)
            return max_child_depth
            
        structure['max_depth'] = calculate_depth(soup.body if soup.body else soup)
        
        return structure


class PatternOptimizer:
    """Optimizes extraction patterns based on success rates."""
    
    def __init__(self):
        self._pattern_stats = {}
        
    def add_pattern_stats(self, field: str, selector: str, success_rate: float, usage_count: int):
        """Add pattern statistics."""
        if field not in self._pattern_stats:
            self._pattern_stats[field] = []
            
        self._pattern_stats[field].append({
            'selector': selector,
            'success_rate': success_rate,
            'usage_count': usage_count,
            'score': success_rate * (1 + min(usage_count / 100, 1))  # Boost for high usage
        })
        
    def get_optimized_patterns(self, field: str) -> List[Dict]:
        """Get optimized patterns sorted by effectiveness."""
        if field not in self._pattern_stats:
            return []
            
        return sorted(self._pattern_stats[field], key=lambda x: x['score'], reverse=True)


class EnhancedHeuristicExtractionResult:
    """Enhanced heuristic extraction result with metadata tracking."""
    
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
        source: str = "heuristic",
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


class HeuristicExtractor:
    """Enhanced heuristic extractor with cross-page pattern learning."""
    
    RESTAURANT_KEYWORDS = {
        "menu", "restaurant", "dining", "cuisine", "food", "chef", "kitchen",
        "appetizers", "entrees", "desserts", "drinks", "wine", "bar"
    }
    
    CUISINE_KEYWORDS = {
        "italian", "chinese", "mexican", "french", "indian", "thai", "japanese",
        "american", "mediterranean", "greek", "korean", "vietnamese"
    }
    
    def __init__(self, extraction_context: Optional[ExtractionContext] = None):
        """Initialize with optional extraction context."""
        self.extraction_context = extraction_context or ExtractionContext()
        
        # Initialize pattern matchers
        self.phone_matcher = PhonePatternMatcher()
        self.address_matcher = AddressPatternMatcher()
        self.hours_matcher = HoursPatternMatcher()
        self.name_extractor = RestaurantNameExtractor()
        
    def extract_from_html(self, html_content: str) -> List[EnhancedHeuristicExtractionResult]:
        """Extract restaurant data from HTML using enhanced heuristics."""
        if not html_content or not html_content.strip():
            return []
            
        # Check if this looks like a restaurant page
        if not self._is_restaurant_page(html_content):
            return []
            
        try:
            soup = BeautifulSoup(html_content, "html.parser")
        except Exception:
            return []
            
        # Extract data using various strategies
        extracted_data = self._extract_all_data(soup)
        
        if not extracted_data.get('name'):
            return []
            
        # Build extraction metadata
        extraction_metadata = self._build_extraction_metadata(soup)
        
        # Apply pattern learning if available
        if self.extraction_context.pattern_learner:
            extraction_metadata['learned_pattern'] = True
            
        # Check for menu-focused extraction
        if self.extraction_context.page_type == "menu":
            extraction_metadata['menu_focused'] = True
            
        # Calculate confidence with pattern boosting  
        confidence = self._calculate_confidence_with_patterns(extracted_data)
        
        # Update metadata with any confidence boost
        if hasattr(self, '_pattern_confidence_boost'):
            extraction_metadata['pattern_confidence_boost'] = self._pattern_confidence_boost
        
        result = EnhancedHeuristicExtractionResult(
            name=extracted_data.get('name', ''),
            address=extracted_data.get('address', ''),
            phone=extracted_data.get('phone', ''),
            hours=extracted_data.get('hours', ''),
            price_range=extracted_data.get('price_range', ''),
            cuisine=extracted_data.get('cuisine', ''),
            confidence=confidence,
            source="heuristic",
            extraction_metadata=extraction_metadata
        )
        
        return [result] if result.is_valid() else []
        
    def _is_restaurant_page(self, html_content: str) -> bool:
        """Check if the page appears to be restaurant-related."""
        content_lower = html_content.lower()
        keyword_count = sum(1 for keyword in self.RESTAURANT_KEYWORDS if keyword in content_lower)
        return keyword_count >= 2
        
    def _extract_all_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract all data using pattern matchers."""
        extracted = {}
        
        # Use learned patterns if available
        if self.extraction_context.pattern_learner:
            extracted.update(self._extract_with_learned_patterns(soup))
            
        # Fallback to standard extraction
        if not extracted.get('name'):
            extracted['name'] = self.name_extractor.extract(soup)
            
        if not extracted.get('phone'):
            extracted['phone'] = self.phone_matcher.extract(soup)
            
        if not extracted.get('address'):
            extracted['address'] = self.address_matcher.extract(soup)
            
        if not extracted.get('hours'):
            extracted['hours'] = self.hours_matcher.extract(soup)
            
        # Extract additional fields
        extracted['cuisine'] = self._extract_cuisine(soup)
        extracted['price_range'] = self._extract_price_range(soup)
        
        return extracted
        
    def _extract_with_learned_patterns(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract using learned patterns."""
        extracted = {}
        
        if not hasattr(self.extraction_context, 'pattern_learner'):
            return extracted
            
        learner = self.extraction_context.pattern_learner
        
        for field in ['name', 'phone', 'address']:
            best_patterns = learner.get_best_patterns(field)
            for pattern in best_patterns[:3]:  # Try top 3 patterns
                try:
                    elements = soup.select(pattern['selector'])
                    if elements:
                        text = elements[0].get_text(strip=True)
                        if text:
                            extracted[field] = text
                            break
                except Exception:
                    continue
                    
        return extracted
        
    def _extract_cuisine(self, soup: BeautifulSoup) -> str:
        """Extract cuisine type using heuristics."""
        text = soup.get_text().lower()
        found_cuisines = [cuisine for cuisine in self.CUISINE_KEYWORDS if cuisine in text]
        return ", ".join(found_cuisines[:3])  # Limit to 3 cuisines
        
    def _extract_price_range(self, soup: BeautifulSoup) -> str:
        """Extract price range using heuristics."""
        text = soup.get_text()
        
        # Look for dollar signs
        dollar_matches = re.findall(r'\$+', text)
        if dollar_matches:
            max_dollars = max(len(match) for match in dollar_matches)
            if max_dollars >= 4:
                return "$$$$"
            elif max_dollars == 3:
                return "$$$"
            elif max_dollars == 2:
                return "$$"
            else:
                return "$"
                
        return ""
        
    def _calculate_confidence_with_patterns(self, extracted_data: Dict[str, str]) -> str:
        """Calculate confidence with pattern learning boost."""
        field_count = sum(1 for value in extracted_data.values() if value)
        
        base_confidence = "low"
        if field_count >= 4:
            base_confidence = "medium"
        elif field_count >= 2:
            base_confidence = "low"
            
        # Pattern boost
        if (hasattr(self.extraction_context, 'pattern_learner') and 
            self.extraction_context.pattern_learner):
            self._pattern_confidence_boost = 0.1
            if hasattr(self, '_pattern_confidence_boost'):
                self.extraction_metadata = getattr(self, 'extraction_metadata', {})
                self.extraction_metadata['pattern_confidence_boost'] = self._pattern_confidence_boost
                
        return base_confidence
        
    def _build_extraction_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Build extraction metadata."""
        metadata = {
            'method': 'heuristic',
            'timestamp': datetime.now().isoformat(),
        }
        
        # Add entity relationship info
        if self.extraction_context.entity_id:
            metadata['entity_id'] = self.extraction_context.entity_id
        if self.extraction_context.parent_id:
            metadata['parent_id'] = self.extraction_context.parent_id
        if self.extraction_context.source_url:
            metadata['source_url'] = self.extraction_context.source_url
            
        # Add pattern confidence boost if applicable
        if hasattr(self, '_pattern_confidence_boost'):
            metadata['pattern_confidence_boost'] = self._pattern_confidence_boost
            
        return metadata