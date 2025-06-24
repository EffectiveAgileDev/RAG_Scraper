"""Specialized popup detector for restaurant websites."""
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class RestaurantPopupPattern:
    """Pattern for detecting restaurant-specific popups."""
    type: str
    selectors: List[str]
    keywords: List[str]
    priority: int
    action_strategy: str


class RestaurantPopupDetector:
    """Specialized popup detector for restaurant websites."""
    
    def __init__(self):
        self.patterns = self._load_restaurant_patterns()
    
    def _load_restaurant_patterns(self) -> List[RestaurantPopupPattern]:
        """Load restaurant-specific popup patterns."""
        return [
            RestaurantPopupPattern(
                type='age_verification',
                selectors=['.age-gate', '.age-verification', '#ageModal', '.verify-age'],
                keywords=['21', 'age', 'verify', 'older', 'drinking age'],
                priority=1,  # Highest priority
                action_strategy='confirm_age'
            ),
            RestaurantPopupPattern(
                type='location_selector',
                selectors=['.location-modal', '.store-selector', '.choose-location'],
                keywords=['location', 'restaurant', 'nearest', 'find location'],
                priority=2,
                action_strategy='select_first_location'
            ),
            RestaurantPopupPattern(
                type='reservation_prompt',
                selectors=['.reservation-modal', '.book-table', '.make-reservation'],
                keywords=['reservation', 'book', 'table', 'reserve now'],
                priority=3,
                action_strategy='dismiss'
            ),
            RestaurantPopupPattern(
                type='newsletter_signup',
                selectors=['.newsletter-modal', '.email-signup', '.subscribe-popup'],
                keywords=['newsletter', 'subscribe', 'email', 'updates', 'deals'],
                priority=4,
                action_strategy='close'
            ),
            RestaurantPopupPattern(
                type='covid_notice',
                selectors=['.covid-modal', '.health-notice', '.safety-notice'],
                keywords=['covid', 'safety', 'health', 'guidelines', 'masks'],
                priority=5,
                action_strategy='acknowledge'
            )
        ]
    
    def detect_restaurant_popups(self, html: str, url: str = "") -> List[dict]:
        """Detect restaurant-specific popups."""
        detected = []
        
        for pattern in sorted(self.patterns, key=lambda p: p.priority):
            if self._matches_pattern(html, pattern):
                detected.append({
                    'type': pattern.type,
                    'selectors': pattern.selectors,
                    'action_strategy': pattern.action_strategy,
                    'priority': pattern.priority,
                    'confidence': self._calculate_confidence(html, pattern)
                })
        
        return detected
    
    def _matches_pattern(self, html: str, pattern: RestaurantPopupPattern) -> bool:
        """Check if HTML matches popup pattern."""
        # Check selectors
        selector_match = any(self._selector_matches_html(selector, html) for selector in pattern.selectors)
        
        # Check keywords (if selectors found)
        if selector_match:
            # Look for keywords in both text content and attributes, 
            # but prefer matches in text content
            import re
            
            # Extract text content (between tags)
            text_content = re.sub(r'<[^>]*>', ' ', html)
            text_content = re.sub(r'\s+', ' ', text_content.strip())
            
            # Check if any keywords appear in text content
            text_keyword_match = any(keyword.lower() in text_content.lower() for keyword in pattern.keywords)
            
            # If no text keywords, also check full HTML (for backwards compatibility)
            # but exclude very generic words that might appear in class names
            if not text_keyword_match:
                # Only allow this fallback for non-generic keywords
                non_generic_keywords = [kw for kw in pattern.keywords if len(kw) > 3 and kw not in ['age']]
                html_keyword_match = any(keyword.lower() in html.lower() for keyword in non_generic_keywords)
                return html_keyword_match
            
            return text_keyword_match
        
        return False
    
    def _selector_matches_html(self, selector: str, html: str) -> bool:
        """Check if a CSS selector matches HTML content."""
        if selector.startswith('.'):
            class_name = selector[1:]  # Remove the dot
            return (f'class="{class_name}' in html or 
                   f"class='{class_name}" in html or 
                   class_name in html)
        elif selector.startswith('#'):
            id_name = selector[1:]  # Remove the hash
            return (f'id="{id_name}' in html or 
                   f"id='{id_name}" in html)
        else:
            return selector in html
    
    def _calculate_confidence(self, html: str, pattern: RestaurantPopupPattern) -> float:
        """Calculate confidence score for popup detection."""
        score = 0.0
        
        # Selector matches (40% weight)
        matching_selectors = sum(1 for sel in pattern.selectors if self._selector_matches_html(sel, html))
        selector_score = (matching_selectors / len(pattern.selectors)) * 0.4
        
        # Keyword matches (40% weight)
        matching_keywords = sum(1 for kw in pattern.keywords if kw.lower() in html.lower())
        keyword_score = (matching_keywords / len(pattern.keywords)) * 0.4
        
        # Pattern priority boost (20% weight)
        priority_score = (6 - pattern.priority) / 5 * 0.2
        
        return min(1.0, selector_score + keyword_score + priority_score)
    
    def get_handling_strategy(self, popup_type: str) -> dict:
        """Get handling strategy for popup type."""
        strategies = {
            'age_verification': {
                'method': 'click_button',
                'targets': ['.confirm-age', '.yes-button', '[data-age="21"]'],
                'fallback': 'continue_anyway'
            },
            'location_selector': {
                'method': 'select_option',
                'targets': ['.location-item:first', '.store-list li:first'],
                'fallback': 'skip_modal'
            },
            'reservation_prompt': {
                'method': 'dismiss',
                'targets': ['.close-button', '.no-thanks', '.skip-reservation'],
                'fallback': 'overlay_click'
            },
            'newsletter_signup': {
                'method': 'close',
                'targets': ['.close-btn', '.no-thanks', '.skip'],
                'fallback': 'escape_key'
            },
            'covid_notice': {
                'method': 'acknowledge',
                'targets': ['.understand', '.acknowledge', '.continue'],
                'fallback': 'auto_dismiss'
            }
        }
        
        return strategies.get(popup_type, {
            'method': 'generic_close',
            'targets': ['.close', '.dismiss', '.skip'],
            'fallback': 'continue'
        })