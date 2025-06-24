"""Unit tests for JavaScript rendering and popup handling components."""
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.scraper.javascript_handler import JavaScriptHandler, PopupInfo


class TestJavaScriptHandler:
    """Test cases for JavaScript handler."""
    
    @pytest.fixture
    def handler(self):
        """Create JavaScript handler instance."""
        return JavaScriptHandler(timeout=30)
    
    def test_detect_age_verification_popup(self, handler):
        """Test detection of age verification popups."""
        html = '<div class="age-gate-modal">Are you 21 or older?</div>'
        popups = handler.detect_popups(html)
        
        assert len(popups) == 1
        assert popups[0].type == 'age_verification'
        assert popups[0].selector == '.age-gate'
        assert popups[0].action_required == 'click_confirm'
    
    def test_detect_multiple_popups(self, handler):
        """Test detection of multiple popups."""
        html = '''
        <div class="cookie-banner">Accept cookies</div>
        <div class="newsletter-modal">Subscribe to newsletter</div>
        '''
        popups = handler.detect_popups(html)
        
        assert len(popups) == 2
        popup_types = [p.type for p in popups]
        assert 'cookie_consent' in popup_types
        assert 'newsletter_signup' in popup_types
    
    def test_no_popups_detected(self, handler):
        """Test when no popups are present."""
        html = '<div class="menu">Restaurant menu content</div>'
        popups = handler.detect_popups(html)
        
        assert len(popups) == 0
    
    def test_handle_popup_removes_content(self, handler):
        """Test popup handling removes popup content."""
        popup = PopupInfo(
            type='newsletter_signup',
            selector='.newsletter-modal',
            action_required='close_button'
        )
        html = '<div class="newsletter-modal">Subscribe</div><div>Main content</div>'
        
        cleaned = handler.handle_popup(popup, html)
        assert '.newsletter-modal' not in cleaned
        assert 'Main content' in cleaned
    
    def test_render_page_with_timeout(self, handler):
        """Test page rendering with custom timeout."""
        url = "https://example.com"
        rendered = handler.render_page(url, timeout=45)
        
        assert rendered is not None
        assert url in rendered
        assert "timeout 45" in rendered
    
    def test_render_page_uses_default_timeout(self, handler):
        """Test page rendering uses default timeout."""
        url = "https://example.com"
        rendered = handler.render_page(url)
        
        assert rendered is not None
        assert "timeout 30" in rendered
    
    def test_javascript_required_detection(self, handler):
        """Test detection of JavaScript requirement."""
        # React app
        react_html = '<div id="root" data-react-app="true"></div>'
        assert handler.is_javascript_required(react_html) is True
        
        # Vue app
        vue_html = '<div id="app" vue-app></div>'
        assert handler.is_javascript_required(vue_html) is True
        
        # Static HTML
        static_html = '<div class="content">Static restaurant info</div>'
        assert handler.is_javascript_required(static_html) is False
    
    def test_location_selector_popup_with_options(self, handler):
        """Test location selector popup detection."""
        html = '<div class="location-modal">Choose your location</div>'
        popups = handler.detect_popups(html)
        
        assert len(popups) == 1
        assert popups[0].type == 'location_selector'
        assert popups[0].action_required == 'select_location'
    
    def test_custom_popup_patterns(self, handler):
        """Test adding custom popup patterns."""
        # Add custom pattern
        handler.popup_patterns['custom_modal'] = ['.custom-popup', '#customModal']
        
        html = '<div class="custom-popup">Custom content</div>'
        popups = handler.detect_popups(html)
        
        assert len(popups) == 1
        assert popups[0].type == 'custom_modal'


class TestPopupPriority:
    """Test popup handling priority."""
    
    def test_popup_priority_order(self):
        """Test that popups are handled in correct priority order."""
        handler = JavaScriptHandler()
        html = '''
        <div class="age-gate">Age verification</div>
        <div class="cookie-banner">Cookie consent</div>
        <div class="newsletter-modal">Newsletter</div>
        '''
        
        popups = handler.detect_popups(html)
        popup_types = [p.type for p in popups]
        
        # Age verification should be detected first (highest priority)
        assert popup_types[0] == 'age_verification'
        
        # All popups should be detected
        assert len(popups) == 3


class TestRenderingOptimization:
    """Test rendering optimization strategies."""
    
    def test_skip_rendering_for_static_content(self):
        """Test that rendering is skipped for static content."""
        handler = JavaScriptHandler()
        static_html = '''
        <html>
            <body>
                <h1>Restaurant Name</h1>
                <div class="menu">Menu items here</div>
                <div class="hours">Hours: 9am-10pm</div>
            </body>
        </html>
        '''
        
        # Should not require JavaScript rendering
        assert handler.is_javascript_required(static_html) is False
    
    def test_require_rendering_for_spa(self):
        """Test that rendering is required for single-page apps."""
        handler = JavaScriptHandler()
        spa_html = '''
        <html>
            <body>
                <div id="root"></div>
                <script>window.__INITIAL_STATE__ = {}</script>
            </body>
        </html>
        '''
        
        # Should require JavaScript rendering
        assert handler.is_javascript_required(spa_html) is True