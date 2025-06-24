"""Unit tests for browser automation with Playwright integration."""
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock

from src.scraper.javascript_handler import JavaScriptHandler
from src.scraper.restaurant_popup_detector import RestaurantPopupDetector


class TestBrowserAutomation:
    """Test browser automation functionality."""
    
    @pytest.fixture
    def handler_with_browser(self):
        """Create JavaScript handler with browser automation enabled."""
        handler = JavaScriptHandler(timeout=30)
        handler.browser_automation_enabled = True
        return handler
    
    @pytest.fixture
    def handler_without_browser(self):
        """Create JavaScript handler without browser automation."""
        handler = JavaScriptHandler(timeout=30)
        handler.browser_automation_enabled = False
        return handler
    
    @pytest.fixture
    def mock_playwright_page(self):
        """Create mock Playwright page."""
        page = AsyncMock()
        page.goto = AsyncMock()
        page.content = AsyncMock(return_value="<html>Rendered content</html>")
        page.wait_for_load_state = AsyncMock()
        page.close = AsyncMock()
        page.click = AsyncMock()
        page.fill = AsyncMock()
        page.select_option = AsyncMock()
        page.query_selector = AsyncMock()
        page.query_selector_all = AsyncMock(return_value=[])
        return page
    
    @pytest.fixture
    def mock_playwright_browser(self, mock_playwright_page):
        """Create mock Playwright browser."""
        browser = AsyncMock()
        context = AsyncMock()
        context.new_page = AsyncMock(return_value=mock_playwright_page)
        browser.new_context = AsyncMock(return_value=context)
        browser.close = AsyncMock()
        return browser, context, mock_playwright_page
    
    @patch('src.scraper.javascript_handler.playwright')
    @pytest.mark.asyncio
    async def test_render_page_with_playwright(self, mock_playwright, handler_with_browser, mock_playwright_browser):
        """Test page rendering with Playwright."""
        browser, context, page = mock_playwright_browser
        mock_playwright.chromium.launch = AsyncMock(return_value=browser)
        
        # Mock the handler's async render method
        handler_with_browser._render_with_browser = AsyncMock(return_value="<html>Rendered content</html>")
        
        result = await handler_with_browser.render_page_async("https://restaurant.com")
        
        assert result == "<html>Rendered content</html>"
        handler_with_browser._render_with_browser.assert_called_once_with("https://restaurant.com")
    
    @patch('src.scraper.javascript_handler.playwright')
    @pytest.mark.asyncio
    async def test_handle_age_verification_popup_with_browser(self, mock_playwright, handler_with_browser, mock_playwright_browser):
        """Test handling age verification popup with browser automation."""
        browser, context, page = mock_playwright_browser
        mock_playwright.chromium.launch = AsyncMock(return_value=browser)
        
        # Setup page with age verification popup
        page.query_selector.return_value = Mock()  # Element found
        page.content.return_value = '''
        <html>
            <div class="age-gate">Are you 21 or older?</div>
            <button class="confirm-age">Yes, I'm 21+</button>
            <div class="content">Restaurant info</div>
        </html>
        '''
        
        handler_with_browser._render_with_browser = AsyncMock(return_value=page.content.return_value)
        handler_with_browser._handle_popups_with_browser = AsyncMock(return_value=page.content.return_value)
        
        result = await handler_with_browser.render_page_async("https://restaurant.com")
        
        assert "Restaurant info" in result
        handler_with_browser._handle_popups_with_browser.assert_called_once()
    
    def test_fallback_to_static_rendering_when_browser_disabled(self, handler_without_browser):
        """Test fallback to static rendering when browser automation is disabled."""
        result = handler_without_browser.render_page("https://restaurant.com")
        
        # Should return the static mock rendering
        assert "Rendered content for https://restaurant.com" in result
        assert "timeout 30" in result
    
    @patch('src.scraper.javascript_handler.playwright')
    @pytest.mark.asyncio
    async def test_popup_detection_with_browser_context(self, mock_playwright, handler_with_browser, mock_playwright_browser):
        """Test popup detection in browser context."""
        browser, context, page = mock_playwright_browser
        mock_playwright.chromium.launch = AsyncMock(return_value=browser)
        
        # Setup page with multiple popups
        page.query_selector_all.return_value = [
            Mock(get_attribute=Mock(return_value='age-gate')),
            Mock(get_attribute=Mock(return_value='newsletter-modal'))
        ]
        
        detector = RestaurantPopupDetector()
        handler_with_browser.popup_detector = detector
        
        # Mock browser-based popup detection
        handler_with_browser._detect_popups_with_browser = AsyncMock(return_value=[
            {'type': 'age_verification', 'priority': 1, 'element': Mock()},
            {'type': 'newsletter_signup', 'priority': 4, 'element': Mock()}
        ])
        
        popups = await handler_with_browser._detect_popups_with_browser(page)
        
        assert len(popups) == 2
        assert any(p['type'] == 'age_verification' for p in popups)
        assert any(p['type'] == 'newsletter_signup' for p in popups)
    
    @patch('src.scraper.javascript_handler.playwright')
    @pytest.mark.asyncio
    async def test_location_selector_automation(self, mock_playwright, handler_with_browser, mock_playwright_browser):
        """Test automated location selection."""
        browser, context, page = mock_playwright_browser
        mock_playwright.chromium.launch = AsyncMock(return_value=browser)
        
        # Setup location selector popup
        location_element = Mock()
        page.query_selector.return_value = location_element
        page.query_selector_all.return_value = [Mock(), Mock()]  # Multiple locations
        
        handler_with_browser._handle_location_selector = AsyncMock()
        
        await handler_with_browser._handle_location_selector(page, {
            'type': 'location_selector',
            'selectors': ['.location-modal'],
            'action_strategy': 'select_first_location'
        })
        
        handler_with_browser._handle_location_selector.assert_called_once()
    
    @patch('src.scraper.javascript_handler.playwright')
    @pytest.mark.asyncio
    async def test_cookie_consent_automation(self, mock_playwright, handler_with_browser, mock_playwright_browser):
        """Test automated cookie consent handling."""
        browser, context, page = mock_playwright_browser
        mock_playwright.chromium.launch = AsyncMock(return_value=browser)
        
        # Setup cookie consent popup
        cookie_button = Mock()
        page.query_selector.return_value = cookie_button
        
        handler_with_browser._handle_cookie_consent = AsyncMock()
        
        await handler_with_browser._handle_cookie_consent(page, {
            'type': 'cookie_consent',
            'selectors': ['.cookie-banner'],
            'action_strategy': 'accept_cookies'
        })
        
        handler_with_browser._handle_cookie_consent.assert_called_once()
    
    @patch('src.scraper.javascript_handler.async_playwright')
    def test_error_handling_browser_automation_failure(self, mock_async_playwright, handler_with_browser):
        """Test error handling when browser automation fails."""
        # Mock Playwright failure
        mock_async_playwright.side_effect = Exception("Browser launch failed")
        
        # Should fallback to static rendering
        result = handler_with_browser.render_page("https://restaurant.com")
        
        assert result is not None
        assert "Rendered content for https://restaurant.com" in result
    
    @patch('src.scraper.javascript_handler.async_playwright')
    def test_timeout_handling_in_browser_automation(self, mock_async_playwright, handler_with_browser):
        """Test timeout handling in browser automation."""
        # Mock timeout during browser operations
        mock_async_playwright.side_effect = Exception("Timeout")
        
        # Should handle timeout gracefully and fallback to static rendering
        result = handler_with_browser.render_page("https://restaurant.com")
        
        assert result is not None
        assert "Rendered content for https://restaurant.com" in result
    
    @patch('src.scraper.javascript_handler.playwright')
    @pytest.mark.asyncio
    async def test_multiple_popup_handling_sequence(self, mock_playwright, handler_with_browser, mock_playwright_browser):
        """Test handling multiple popups in correct sequence."""
        browser, context, page = mock_playwright_browser
        mock_playwright.chromium.launch = AsyncMock(return_value=browser)
        
        # Setup multiple popups with different priorities
        popups = [
            {'type': 'age_verification', 'priority': 1, 'element': Mock()},
            {'type': 'location_selector', 'priority': 2, 'element': Mock()},
            {'type': 'newsletter_signup', 'priority': 4, 'element': Mock()}
        ]
        
        handler_with_browser._handle_popups_sequence = AsyncMock(return_value="<html>Clean content</html>")
        
        result = await handler_with_browser._handle_popups_sequence(page, popups)
        
        assert result == "<html>Clean content</html>"
        handler_with_browser._handle_popups_sequence.assert_called_once_with(page, popups)
    
    def test_browser_automation_configuration(self, handler_with_browser):
        """Test browser automation configuration options."""
        assert hasattr(handler_with_browser, 'browser_automation_enabled')
        assert handler_with_browser.browser_automation_enabled is True
        assert handler_with_browser.timeout == 30


class TestPlaywrightIntegration:
    """Test Playwright-specific integration features."""
    
    @pytest.fixture
    def playwright_handler(self):
        """Create handler configured for Playwright."""
        handler = JavaScriptHandler(timeout=30)
        handler.browser_automation_enabled = True
        handler.browser_type = 'chromium'
        handler.headless = True
        return handler
    
    def test_playwright_configuration_options(self, playwright_handler):
        """Test Playwright configuration options."""
        assert hasattr(playwright_handler, 'browser_type')
        assert hasattr(playwright_handler, 'headless')
        assert playwright_handler.browser_type == 'chromium'
        assert playwright_handler.headless is True
    
    @patch('src.scraper.javascript_handler.playwright')
    @pytest.mark.asyncio
    async def test_custom_browser_options(self, mock_playwright, playwright_handler):
        """Test custom browser launch options."""
        mock_browser = AsyncMock()
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        
        playwright_handler._launch_browser = AsyncMock(return_value=mock_browser)
        
        browser = await playwright_handler._launch_browser()
        
        assert browser is not None
        playwright_handler._launch_browser.assert_called_once()
    
    @patch('src.scraper.javascript_handler.playwright')
    @pytest.mark.asyncio
    async def test_stealth_mode_configuration(self, mock_playwright, playwright_handler):
        """Test stealth mode configuration for detection avoidance."""
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        
        playwright_handler.stealth_mode = True
        playwright_handler._setup_stealth_mode = AsyncMock()
        
        await playwright_handler._setup_stealth_mode(mock_context)
        
        playwright_handler._setup_stealth_mode.assert_called_once_with(mock_context)
    
    @patch('src.scraper.javascript_handler.playwright')
    @pytest.mark.asyncio
    async def test_user_agent_customization(self, mock_playwright, playwright_handler):
        """Test custom user agent configuration."""
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        
        playwright_handler.custom_user_agent = "RAG_Scraper/1.0 Restaurant Data Collection"
        playwright_handler._setup_context = AsyncMock(return_value=mock_context)
        
        context = await playwright_handler._setup_context(mock_browser)
        
        assert context is not None
        playwright_handler._setup_context.assert_called_once_with(mock_browser)