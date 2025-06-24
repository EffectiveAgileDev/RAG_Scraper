"""Integration tests for JavaScript handler with existing scraper architecture."""
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.scraper.multi_strategy_scraper import MultiStrategyScraper
from src.scraper.javascript_handler import JavaScriptHandler
from src.scraper.restaurant_popup_detector import RestaurantPopupDetector
from src.config.scraping_config import ScrapingConfig


class TestJavaScriptScraperIntegration:
    """Test JavaScript handler integration with MultiStrategyScraper."""
    
    @pytest.fixture
    def config_with_js(self):
        """Create config with JavaScript enabled."""
        config = ScrapingConfig(urls=["https://test.com"])
        config.enable_javascript_rendering = True
        config.javascript_timeout = 30
        config.enable_popup_detection = True
        return config
    
    @pytest.fixture
    def config_without_js(self):
        """Create config with JavaScript disabled."""
        config = ScrapingConfig(urls=["https://test.com"])
        config.enable_javascript_rendering = False
        config.enable_popup_detection = False
        return config
    
    @pytest.fixture
    def mock_ethical_scraper(self):
        """Create mock ethical scraper."""
        mock = Mock()
        mock.fetch_page_with_retry.return_value = "<html>Static content</html>"
        return mock
    
    @pytest.fixture
    def scraper_with_js(self, config_with_js, mock_ethical_scraper):
        """Create scraper with JavaScript enabled."""
        return MultiStrategyScraper(
            ethical_scraper=mock_ethical_scraper,
            config=config_with_js
        )
    
    @pytest.fixture
    def scraper_without_js(self, config_without_js, mock_ethical_scraper):
        """Create scraper without JavaScript."""
        return MultiStrategyScraper(
            ethical_scraper=mock_ethical_scraper,
            config=config_without_js
        )
    
    def test_scraper_initializes_javascript_handler_when_enabled(self, scraper_with_js):
        """Test that JavaScript handler is initialized when enabled."""
        assert hasattr(scraper_with_js, 'javascript_handler')
        assert isinstance(scraper_with_js.javascript_handler, JavaScriptHandler)
        assert hasattr(scraper_with_js, 'popup_detector')
        assert isinstance(scraper_with_js.popup_detector, RestaurantPopupDetector)
    
    def test_scraper_skips_javascript_handler_when_disabled(self, scraper_without_js):
        """Test that JavaScript handler is not initialized when disabled."""
        assert not hasattr(scraper_without_js, 'javascript_handler') or scraper_without_js.javascript_handler is None
        assert not hasattr(scraper_without_js, 'popup_detector') or scraper_without_js.popup_detector is None
    
    @patch('src.scraper.multi_strategy_scraper.MultiStrategyScraper._extract_with_all_strategies')
    def test_javascript_detection_triggers_rendering(self, mock_extract, scraper_with_js, mock_ethical_scraper):
        """Test that JavaScript detection triggers page rendering."""
        # Setup - JavaScript required page
        js_html = '<div id="root"></div><script>window.__INITIAL_STATE__ = {}</script>'
        mock_ethical_scraper.fetch_page_with_retry.return_value = js_html
        mock_extract.return_value = Mock()
        
        # Mock JavaScript handler
        scraper_with_js.javascript_handler.is_javascript_required = Mock(return_value=True)
        scraper_with_js.javascript_handler.render_page = Mock(return_value="<html>Rendered content</html>")
        
        # Execute
        result = scraper_with_js.scrape_url("https://restaurant.com")
        
        # Verify JavaScript rendering was called
        scraper_with_js.javascript_handler.is_javascript_required.assert_called_once_with(js_html)
        scraper_with_js.javascript_handler.render_page.assert_called_once_with("https://restaurant.com")
    
    @patch('src.scraper.multi_strategy_scraper.MultiStrategyScraper._extract_with_all_strategies')
    def test_popup_detection_and_handling(self, mock_extract, scraper_with_js, mock_ethical_scraper):
        """Test that popups are detected and handled."""
        # Setup - Page with age verification popup
        popup_html = '''
        <html>
            <div class="age-gate">Are you 21 or older?</div>
            <div class="content">Restaurant info</div>
        </html>
        '''
        mock_ethical_scraper.fetch_page_with_retry.return_value = popup_html
        mock_extract.return_value = Mock()
        
        # Mock popup detection
        mock_popup = {
            'type': 'age_verification',
            'selectors': ['.age-gate'],
            'action_strategy': 'confirm_age',
            'priority': 1,
            'confidence': 0.8
        }
        scraper_with_js.popup_detector.detect_restaurant_popups = Mock(return_value=[mock_popup])
        scraper_with_js.javascript_handler.handle_popup = Mock(return_value="<html>Cleaned content</html>")
        
        # Execute
        result = scraper_with_js.scrape_url("https://restaurant.com")
        
        # Verify popup detection was called
        scraper_with_js.popup_detector.detect_restaurant_popups.assert_called_once()
    
    @patch('src.scraper.multi_strategy_scraper.MultiStrategyScraper._extract_with_all_strategies')
    def test_static_page_bypasses_javascript_rendering(self, mock_extract, scraper_with_js, mock_ethical_scraper):
        """Test that static pages bypass JavaScript rendering."""
        # Setup - Static HTML page
        static_html = '<html><h1>Restaurant Name</h1><div class="menu">Menu content</div></html>'
        mock_ethical_scraper.fetch_page_with_retry.return_value = static_html
        mock_extract.return_value = Mock()
        
        # Mock JavaScript handler
        scraper_with_js.javascript_handler.is_javascript_required = Mock(return_value=False)
        scraper_with_js.javascript_handler.render_page = Mock()
        
        # Execute
        result = scraper_with_js.scrape_url("https://restaurant.com")
        
        # Verify JavaScript rendering was not called
        scraper_with_js.javascript_handler.render_page.assert_not_called()
    
    @patch('src.scraper.multi_strategy_scraper.MultiStrategyScraper._extract_with_all_strategies')
    def test_javascript_disabled_bypasses_all_js_processing(self, mock_extract, scraper_without_js, mock_ethical_scraper):
        """Test that JavaScript processing is bypassed when disabled."""
        # Setup - JavaScript page but JS disabled
        js_html = '<div id="root"></div><script>window.__INITIAL_STATE__ = {}</script>'
        mock_ethical_scraper.fetch_page_with_retry.return_value = js_html
        mock_extract.return_value = Mock()
        
        # Execute
        result = scraper_without_js.scrape_url("https://restaurant.com")
        
        # Verify no JavaScript processing occurred
        assert not hasattr(scraper_without_js, 'javascript_handler') or scraper_without_js.javascript_handler is None
    
    @patch('src.scraper.multi_strategy_scraper.MultiStrategyScraper._extract_with_all_strategies')
    def test_popup_handling_with_multiple_popups(self, mock_extract, scraper_with_js, mock_ethical_scraper):
        """Test handling of multiple popups in priority order."""
        # Setup - Page with multiple popups
        multi_popup_html = '''
        <html>
            <div class="age-verification">Are you 21 or older?</div>
            <div class="newsletter-modal">Subscribe to newsletter</div>
            <div class="location-modal">Choose location</div>
        </html>
        '''
        mock_ethical_scraper.fetch_page_with_retry.return_value = multi_popup_html
        mock_extract.return_value = Mock()
        
        # Mock multiple popup detection
        mock_popups = [
            {'type': 'age_verification', 'priority': 1, 'confidence': 0.9},
            {'type': 'newsletter_signup', 'priority': 4, 'confidence': 0.7},
            {'type': 'location_selector', 'priority': 2, 'confidence': 0.8}
        ]
        scraper_with_js.popup_detector.detect_restaurant_popups = Mock(return_value=mock_popups)
        
        # Execute
        result = scraper_with_js.scrape_url("https://restaurant.com")
        
        # Verify popup detection was called
        scraper_with_js.popup_detector.detect_restaurant_popups.assert_called_once()
    
    def test_javascript_timeout_configuration(self, scraper_with_js):
        """Test that JavaScript timeout is properly configured."""
        assert scraper_with_js.javascript_handler.timeout == 30
    
    @patch('src.scraper.multi_strategy_scraper.MultiStrategyScraper._extract_with_all_strategies')
    def test_error_handling_javascript_rendering_failure(self, mock_extract, scraper_with_js, mock_ethical_scraper):
        """Test error handling when JavaScript rendering fails."""
        # Setup - JavaScript rendering fails
        js_html = '<div id="root"></div><script>window.__INITIAL_STATE__ = {}</script>'
        mock_ethical_scraper.fetch_page_with_retry.return_value = js_html
        mock_extract.return_value = Mock()
        
        # Mock JavaScript handler failure
        scraper_with_js.javascript_handler.is_javascript_required = Mock(return_value=True)
        scraper_with_js.javascript_handler.render_page = Mock(return_value=None)  # Rendering failed
        
        # Execute
        result = scraper_with_js.scrape_url("https://restaurant.com")
        
        # Should fallback to original HTML and continue processing
        assert result is not None  # Processing should continue
        mock_extract.assert_called_once()
    
    @patch('src.scraper.multi_strategy_scraper.MultiStrategyScraper._extract_with_all_strategies')
    def test_error_handling_popup_detection_failure(self, mock_extract, scraper_with_js, mock_ethical_scraper):
        """Test error handling when popup detection fails."""
        # Setup - Popup detection fails
        popup_html = '<div class="age-gate">Are you 21 or older?</div>'
        mock_ethical_scraper.fetch_page_with_retry.return_value = popup_html
        mock_extract.return_value = Mock()
        
        # Mock popup detection failure
        scraper_with_js.popup_detector.detect_restaurant_popups = Mock(side_effect=Exception("Detection failed"))
        
        # Execute
        result = scraper_with_js.scrape_url("https://restaurant.com")
        
        # Should continue processing despite popup detection failure
        assert result is not None
        mock_extract.assert_called_once()


class TestConfigurationIntegration:
    """Test configuration integration for JavaScript features."""
    
    def test_config_has_javascript_options(self):
        """Test that configuration includes JavaScript options."""
        config = ScrapingConfig(urls=["https://test.com"])
        
        # Check that JavaScript configuration options exist
        assert hasattr(config, 'enable_javascript_rendering')
        assert hasattr(config, 'javascript_timeout')
        assert hasattr(config, 'enable_popup_detection')
        assert hasattr(config, 'popup_handling_strategy')
    
    def test_config_default_values(self):
        """Test default configuration values."""
        config = ScrapingConfig(urls=["https://test.com"])
        
        # Check default values are reasonable
        assert isinstance(config.enable_javascript_rendering, bool)
        assert isinstance(config.javascript_timeout, int)
        assert config.javascript_timeout > 0
        assert isinstance(config.enable_popup_detection, bool)
        assert config.popup_handling_strategy in ['auto', 'skip', 'manual']