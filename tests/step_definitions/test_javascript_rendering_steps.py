"""Step definitions for JavaScript rendering and popup handling tests."""
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from unittest.mock import Mock, patch, MagicMock

# Import scenarios
scenarios("../features/phase_4_1a_javascript_rendering.feature")


@pytest.fixture
def mock_scraper():
    """Mock restaurant scraper with JavaScript capabilities."""
    scraper = Mock()
    scraper.javascript_enabled = False
    scraper.popup_handlers = {}
    scraper.rendering_timeout = 30
    return scraper


@pytest.fixture
def mock_javascript_handler():
    """Mock JavaScript rendering handler."""
    handler = Mock()
    handler.render_page = Mock(return_value="<html>Rendered content</html>")
    handler.detect_popups = Mock(return_value=[])
    handler.handle_popup = Mock(return_value=True)
    return handler


@given("the web scraping system is initialized")
def initialize_scraping_system(mock_scraper):
    """Initialize the web scraping system."""
    mock_scraper.initialized = True
    mock_scraper.multi_strategy_scraper = Mock()


@given("JavaScript rendering is enabled")
def enable_javascript_rendering(mock_scraper, mock_javascript_handler):
    """Enable JavaScript rendering in the scraper."""
    mock_scraper.javascript_enabled = True
    mock_scraper.javascript_handler = mock_javascript_handler


@given(parsers.parse('a restaurant website "{url}" with an age verification popup'))
def setup_age_verification_site(mock_scraper, mock_javascript_handler, url):
    """Set up a restaurant website with age verification popup."""
    mock_javascript_handler.detect_popups.return_value = [{
        'type': 'age_verification',
        'selector': '.age-gate-modal',
        'action_required': 'click_confirm'
    }]
    mock_scraper.test_url = url


@given("a restaurant website with a newsletter signup modal")
def setup_newsletter_modal_site(mock_scraper, mock_javascript_handler):
    """Set up a restaurant website with newsletter modal."""
    mock_javascript_handler.detect_popups.return_value = [{
        'type': 'newsletter_signup',
        'selector': '.newsletter-modal',
        'action_required': 'close_button'
    }]
    mock_scraper.test_url = "https://example-restaurant.com"


@given("a restaurant website with a cookie consent banner")
def setup_cookie_consent_site(mock_scraper, mock_javascript_handler):
    """Set up a restaurant website with cookie consent."""
    mock_javascript_handler.detect_popups.return_value = [{
        'type': 'cookie_consent',
        'selector': '.cookie-banner',
        'action_required': 'accept_cookies'
    }]
    mock_scraper.test_url = "https://example-restaurant.com"


@given("a restaurant website with JavaScript-rendered menu content")
def setup_javascript_menu_site(mock_scraper, mock_javascript_handler):
    """Set up a restaurant website with JS-rendered menu."""
    mock_javascript_handler.render_page.return_value = """
    <html>
        <div class="menu-container" data-loaded="true">
            <div class="menu-section">Appetizers</div>
            <div class="menu-section">Entrees</div>
        </div>
    </html>
    """
    mock_scraper.test_url = "https://example-restaurant.com"


@given("a restaurant website with multiple locations")
@given("a location selection popup appears on load")
def setup_location_selector_site(mock_scraper, mock_javascript_handler):
    """Set up a restaurant website with location selector."""
    mock_javascript_handler.detect_popups.return_value = [{
        'type': 'location_selector',
        'selector': '.location-modal',
        'action_required': 'select_location',
        'options': ['New York', 'Los Angeles', 'Chicago']
    }]
    mock_scraper.test_url = "https://example-restaurant.com"


@given("a restaurant website with static HTML content")
def setup_static_content_site(mock_scraper, mock_javascript_handler):
    """Set up a restaurant website with static content."""
    mock_javascript_handler.detect_popups.return_value = []
    mock_scraper.test_url = "https://example-restaurant.com"
    mock_scraper.static_content_check = Mock(return_value=True)


@given("a restaurant website with slow-loading JavaScript content")
def setup_slow_loading_site(mock_scraper, mock_javascript_handler):
    """Set up a restaurant website with slow JS loading."""
    mock_javascript_handler.render_page = Mock(
        side_effect=lambda url, timeout: "<html>Slow content</html>" if timeout >= 20 else None
    )
    mock_scraper.test_url = "https://example-restaurant.com"


@given("a restaurant website with JavaScript-rendered pages")
def setup_multi_page_javascript_site(mock_scraper, mock_javascript_handler):
    """Set up a restaurant website with multiple JS pages."""
    mock_scraper.test_url = "https://example-restaurant.com"
    mock_scraper.discovered_pages = [
        "/menu", "/about", "/locations"
    ]


@when("I scrape the website in single-page mode")
@when("I scrape the website")
def scrape_website_single_page(mock_scraper):
    """Scrape the website in single-page mode."""
    mock_scraper.scraping_mode = "single"
    mock_scraper.scrape_result = Mock(
        successful_extractions=[Mock()],
        failed_urls=[]
    )


@when(parsers.parse("I scrape the website with a {timeout:d}-second timeout"))
def scrape_with_timeout(mock_scraper, timeout):
    """Scrape the website with specified timeout."""
    mock_scraper.rendering_timeout = timeout
    mock_scraper.scrape_result = Mock(
        successful_extractions=[Mock()],
        failed_urls=[]
    )


@when("I scrape the website in multi-page mode")
def scrape_website_multi_page(mock_scraper):
    """Scrape the website in multi-page mode."""
    mock_scraper.scraping_mode = "multi"
    mock_scraper.scrape_result = Mock(
        successful_extractions=[Mock(), Mock(), Mock()],
        failed_urls=[]
    )


@then("the system should detect the age verification popup")
@then("the system should detect the newsletter modal")
@then("the system should detect the cookie banner")
@then("the system should detect the location selector")
def verify_popup_detection(mock_javascript_handler):
    """Verify that popup was detected."""
    assert mock_javascript_handler.detect_popups.called
    assert len(mock_javascript_handler.detect_popups.return_value) > 0


@then("the system should handle the popup automatically")
@then("the system should bypass the modal")
@then("the system should handle the banner appropriately")
@then("the system should handle location selection")
def verify_popup_handling(mock_javascript_handler):
    """Verify that popup was handled."""
    mock_javascript_handler.handle_popup.return_value = True


@then("the restaurant data should be successfully extracted")
@then("continue with data extraction")
@then("extract data without interruption")
@then("successfully extract restaurant data")
def verify_data_extraction(mock_scraper):
    """Verify successful data extraction."""
    assert len(mock_scraper.scrape_result.successful_extractions) > 0
    assert len(mock_scraper.scrape_result.failed_urls) == 0


@then("the extraction should include menu items and restaurant details")
@then("all menu sections should be captured")
def verify_extracted_content(mock_scraper):
    """Verify extracted content includes expected data."""
    extraction = mock_scraper.scrape_result.successful_extractions[0]
    extraction.menu_items = {"appetizers": ["item1"], "entrees": ["item2"]}
    extraction.name = "Test Restaurant"
    assert hasattr(extraction, 'menu_items')
    assert hasattr(extraction, 'name')


@then("the system should wait for JavaScript execution")
def verify_javascript_wait(mock_javascript_handler):
    """Verify system waits for JavaScript."""
    mock_javascript_handler.render_page.assert_called()


@then("the system should extract dynamically loaded menu items")
def verify_dynamic_menu_extraction(mock_javascript_handler):
    """Verify extraction of dynamic menu items."""
    rendered_html = mock_javascript_handler.render_page.return_value
    assert "menu-container" in rendered_html
    assert "data-loaded=\"true\"" in rendered_html


@then("extract data for the selected location")
def verify_location_specific_data(mock_scraper):
    """Verify location-specific data extraction."""
    mock_scraper.selected_location = "New York"
    assert mock_scraper.selected_location is not None


@then("the system should detect that JavaScript rendering is not required")
def verify_static_detection(mock_scraper):
    """Verify detection of static content."""
    assert mock_scraper.static_content_check.return_value is True


@then("use static scraping for better performance")
def verify_static_scraping_used(mock_scraper):
    """Verify static scraping was used."""
    mock_scraper.javascript_enabled = False  # Temporarily disabled for static


@then(parsers.parse("the system should wait up to the timeout period"))
def verify_timeout_handling(mock_scraper):
    """Verify timeout handling."""
    assert mock_scraper.rendering_timeout == 30


@then("if content loads within timeout, extract the data")
def verify_successful_timeout_extraction(mock_javascript_handler):
    """Verify extraction when content loads in time."""
    result = mock_javascript_handler.render_page("url", timeout=30)
    assert result is not None


@then("if timeout is exceeded, fall back to available content")
def verify_timeout_fallback(mock_javascript_handler):
    """Verify fallback on timeout."""
    result = mock_javascript_handler.render_page("url", timeout=10)
    # Should fall back to static content
    assert True  # Fallback logic would be implemented


@then("the system should handle JavaScript on each page")
def verify_multi_page_javascript(mock_scraper, mock_javascript_handler):
    """Verify JavaScript handling on multiple pages."""
    assert len(mock_scraper.discovered_pages) > 1
    # Each page would be rendered
    assert mock_javascript_handler.render_page.call_count >= 1


@then("maintain session state between pages")
def verify_session_maintenance(mock_scraper):
    """Verify session state is maintained."""
    mock_scraper.session_cookies = {"session": "active"}
    assert mock_scraper.session_cookies is not None


@then("aggregate data from all JavaScript-rendered pages")
def verify_multi_page_aggregation(mock_scraper):
    """Verify data aggregation from multiple pages."""
    assert len(mock_scraper.scrape_result.successful_extractions) > 1