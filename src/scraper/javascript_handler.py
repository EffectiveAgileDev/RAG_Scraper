"""JavaScript rendering and popup handling for restaurant websites."""
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class PopupInfo:
    """Information about detected popup."""
    type: str
    selector: str
    action_required: str
    blocking_content: bool = True
    options: List[str] = None


class JavaScriptHandler:
    """Handler for JavaScript rendering and popup management."""
    
    def __init__(self, timeout: int = 30):
        """Initialize JavaScript handler with timeout."""
        self.timeout = timeout
        self.popup_patterns = {
            'age_verification': [
                '.age-gate', '.age-verification', '.age-modal',
                '#ageGate', '#ageVerification', '[class*="age-check"]'
            ],
            'newsletter_signup': [
                '.newsletter-modal', '.email-signup', '.subscribe-popup',
                '#newsletterModal', '[class*="newsletter-popup"]'
            ],
            'cookie_consent': [
                '.cookie-banner', '.cookie-consent', '#cookieNotice',
                '[class*="cookie-policy"]', '.gdpr-banner'
            ],
            'location_selector': [
                '.location-modal', '.store-selector', '#locationPicker',
                '[class*="location-select"]', '.choose-location'
            ]
        }
    
    def detect_popups(self, html: str) -> List[PopupInfo]:
        """Detect popups in HTML content."""
        detected = []
        for popup_type, selectors in self.popup_patterns.items():
            for selector in selectors:
                # Convert CSS selector to class name for matching
                if selector.startswith('.'):
                    class_name = selector[1:]  # Remove the dot
                    if f'class="{class_name}' in html or f"class='{class_name}" in html or class_name in html:
                        detected.append(PopupInfo(
                            type=popup_type,
                            selector=selector,
                            action_required=self._get_action_for_type(popup_type)
                        ))
                        break
                elif selector.startswith('#'):
                    id_name = selector[1:]  # Remove the hash
                    if f'id="{id_name}' in html or f"id='{id_name}" in html:
                        detected.append(PopupInfo(
                            type=popup_type,
                            selector=selector,
                            action_required=self._get_action_for_type(popup_type)
                        ))
                        break
                elif selector in html:  # For attribute selectors or exact matches
                    detected.append(PopupInfo(
                        type=popup_type,
                        selector=selector,
                        action_required=self._get_action_for_type(popup_type)
                    ))
                    break
        return detected
    
    def _get_action_for_type(self, popup_type: str) -> str:
        """Get required action for popup type."""
        actions = {
            'age_verification': 'click_confirm',
            'newsletter_signup': 'close_button',
            'cookie_consent': 'accept_cookies',
            'location_selector': 'select_location'
        }
        return actions.get(popup_type, 'close')
    
    def handle_popup(self, popup: PopupInfo, page_content: str) -> str:
        """Handle popup and return cleaned content."""
        # Simplified popup handling - in real implementation would use browser automation
        return page_content.replace(popup.selector, '')
    
    def render_page(self, url: str, timeout: Optional[int] = None) -> Optional[str]:
        """Render page with JavaScript execution."""
        actual_timeout = timeout or self.timeout
        # Simplified rendering - in real implementation would use browser automation
        return f"<html>Rendered content for {url} with timeout {actual_timeout}</html>"
    
    def is_javascript_required(self, html: str) -> bool:
        """Check if JavaScript rendering is required."""
        js_indicators = [
            'ng-app', 'data-react', 'vue-app', 
            '__NEXT_DATA__', 'window.__INITIAL_STATE__',
            'require.config', 'webpack'
        ]
        return any(indicator in html for indicator in js_indicators)