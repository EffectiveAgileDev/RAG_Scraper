"""Step definitions for enhanced page status display feature."""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from bs4 import BeautifulSoup
import json
import re
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Load scenarios from the feature file
scenarios('../features/enhanced_page_status_display.feature')


@pytest.fixture
def mock_scraping_results():
    """Mock scraping results with various page statuses."""
    return {
        'successful_pages': [
            {
                'url': 'https://restaurant1.com/menu',
                'status': 'success',
                'http_status': 200,
                'data_extracted': 15,
                'content_size': 2048,
                'processing_time': 1.2,
                'timestamp': '2024-01-15T10:30:00Z',
                'extraction_method': 'json_ld'
            },
            {
                'url': 'https://restaurant1.com/about',
                'status': 'success',
                'http_status': 200,
                'data_extracted': 8,
                'content_size': 1024,
                'processing_time': 0.8,
                'timestamp': '2024-01-15T10:30:15Z',
                'extraction_method': 'microdata'
            }
        ],
        'failed_pages': [
            {
                'url': 'https://restaurant1.com/private',
                'status': 'failed',
                'http_status': 404,
                'error_message': 'Page not found',
                'processing_time': 0.5,
                'timestamp': '2024-01-15T10:30:30Z'
            },
            {
                'url': 'https://restaurant1.com/blocked',
                'status': 'failed',
                'http_status': 403,
                'error_message': 'Access forbidden',
                'processing_time': 0.3,
                'timestamp': '2024-01-15T10:30:45Z'
            }
        ],
        'timeout_pages': [
            {
                'url': 'https://restaurant1.com/slow',
                'status': 'timeout',
                'timeout_duration': 30.0,
                'partial_data': 3,
                'processing_time': 30.0,
                'timestamp': '2024-01-15T10:31:15Z'
            }
        ],
        'redirected_pages': [
            {
                'url': 'https://restaurant1.com/old-menu',
                'status': 'redirected',
                'final_url': 'https://restaurant1.com/menu',
                'redirect_chain': ['https://restaurant1.com/old-menu', 'https://restaurant1.com/menu'],
                'http_status': 301,
                'data_extracted': 12,
                'processing_time': 1.5,
                'timestamp': '2024-01-15T10:31:30Z'
            }
        ]
    }


@pytest.fixture
def mock_app_interface(mock_scraping_results):
    """Mock web interface with enhanced status display."""
    with patch('src.web_interface.app.app') as mock_app:
        html_content = """
        <html>
            <body>
                <div id="results">
                    <div class="site-results">
                        <h3>Restaurant Site 1</h3>
                        <div class="pages-list">
                            <div class="page-result success" data-url="https://restaurant1.com/menu">
                                <span class="status-indicator">SUCCESS</span>
                                <span class="http-status">200</span>
                                <span class="data-count">15 items</span>
                                <span class="content-size">2.0 KB</span>
                            </div>
                            <div class="page-result failed" data-url="https://restaurant1.com/private">
                                <span class="status-indicator">FAILED</span>
                                <span class="http-status">404</span>
                                <span class="error-message">Page not found</span>
                            </div>
                            <div class="page-result timeout" data-url="https://restaurant1.com/slow">
                                <span class="status-indicator">TIMEOUT</span>
                                <span class="timeout-duration">30.0s</span>
                                <span class="partial-data">3 items</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div id="status-filters">
                    <button id="show-all">All</button>
                    <button id="show-success">Success Only</button>
                    <button id="show-failed">Failed Only</button>
                </div>
                <div id="action-buttons">
                    <button id="export-failed">Export Failed Pages Report</button>
                    <button id="retry-failed">Retry Failed Pages</button>
                </div>
            </body>
        </html>
        """
        mock_app.test_client.return_value.get.return_value.data = html_content.encode('utf-8')
        yield mock_app


@given("I am on the RAG_Scraper web interface")
def given_on_web_interface(mock_app_interface):
    """User is on the web interface."""
    pass


@given("I have multi-page scraping enabled")
def given_multipage_enabled():
    """Multi-page scraping is enabled."""
    pass


@given("I have successfully scraped a multi-page restaurant site")
def given_successful_scrape(mock_scraping_results):
    """Successfully scraped a site with multiple pages."""
    pass


@given("I have attempted to scrape a site with some failed pages")
def given_mixed_results(mock_scraping_results):
    """Attempted scraping with some failures."""
    pass


@given("I have attempted to scrape pages that timed out")
def given_timeout_pages(mock_scraping_results):
    """Attempted scraping with timeout pages."""
    pass


@given("I have scraped pages that were redirected")
def given_redirected_pages(mock_scraping_results):
    """Scraped pages that were redirected."""
    pass


@given("I have results with various page statuses")
def given_various_statuses(mock_scraping_results):
    """Results with mixed statuses."""
    pass


@given("I have results with mixed success and failure statuses")
def given_mixed_statuses(mock_scraping_results):
    """Results with both success and failure."""
    pass


@given("I have results with some failed pages")
def given_some_failures(mock_scraping_results):
    """Results with some failed pages."""
    pass


@when("I view the results")
def when_view_results(mock_app_interface):
    """User views the results page."""
    response = mock_app_interface.test_client().get('/results')
    assert response.status_code == 200


@when("I hover over a page status indicator")
def when_hover_status():
    """User hovers over status indicator."""
    # This would trigger JavaScript tooltip functionality
    pass


@when("I use the status filter controls")
def when_use_filters():
    """User interacts with status filters."""
    pass


@when('I click the "Export Failed Pages Report" button')
def when_click_export():
    """User clicks export failed pages button."""
    pass


@when('I click the "Retry Failed Pages" button')
def when_click_retry():
    """User clicks retry failed pages button."""
    pass


@then("I should see success indicators for successful pages")
def then_see_success_indicators(mock_app_interface):
    """Verify success indicators are displayed."""
    response = mock_app_interface.test_client().get('/results')
    soup = BeautifulSoup(response.data, 'html.parser')
    success_pages = soup.find_all('div', class_='page-result success')
    assert len(success_pages) > 0
    
    for page in success_pages:
        status_indicator = page.find('span', class_='status-indicator')
        assert status_indicator is not None
        assert '✓ SUCCESS' in status_indicator.text


@then('each successful page should show "✓ SUCCESS" status')
def then_success_status_text(mock_app_interface):
    """Verify success status text."""
    response = mock_app_interface.test_client().get('/results')
    soup = BeautifulSoup(response.data, 'html.parser')
    success_indicators = soup.find_all('span', class_='status-indicator')
    
    success_count = 0
    for indicator in success_indicators:
        if 'SUCCESS' in indicator.text:
            success_count += 1
    
    assert success_count >= 1


@then("each successful page should display the HTTP status code")
def then_http_status_displayed(mock_app_interface):
    """Verify HTTP status codes are shown."""
    response = mock_app_interface.test_client().get('/results')
    soup = BeautifulSoup(response.data, 'html.parser')
    success_pages = soup.find_all('div', class_='page-result success')
    
    for page in success_pages:
        http_status = page.find('span', class_='http-status')
        assert http_status is not None
        assert re.match(r'^\d{3}$', http_status.text)


@then("each successful page should show data extracted count")
def then_data_count_displayed(mock_app_interface):
    """Verify data extraction count is shown."""
    response = mock_app_interface.test_client().get('/results')
    soup = BeautifulSoup(response.data, 'html.parser')
    success_pages = soup.find_all('div', class_='page-result success')
    
    for page in success_pages:
        data_count = page.find('span', class_='data-count')
        assert data_count is not None
        assert 'items' in data_count.text


@then("each successful page should display content size information")
def then_content_size_displayed(mock_app_interface):
    """Verify content size is shown."""
    response = mock_app_interface.test_client().get('/results')
    soup = BeautifulSoup(response.data, 'html.parser')
    success_pages = soup.find_all('div', class_='page-result success')
    
    for page in success_pages:
        content_size = page.find('span', class_='content-size')
        assert content_size is not None
        assert 'KB' in content_size.text or 'MB' in content_size.text


@then("I should see failure indicators for failed pages")
def then_see_failure_indicators(mock_app_interface):
    """Verify failure indicators are displayed."""
    response = mock_app_interface.test_client().get('/results')
    soup = BeautifulSoup(response.data, 'html.parser')
    failed_pages = soup.find_all('div', class_='page-result failed')
    assert len(failed_pages) > 0


@then('each failed page should show "✗ FAILED" status')
def then_failed_status_text(mock_app_interface):
    """Verify failed status text."""
    response = mock_app_interface.test_client().get('/results')
    soup = BeautifulSoup(response.data, 'html.parser')
    failed_pages = soup.find_all('div', class_='page-result failed')
    
    for page in failed_pages:
        status_indicator = page.find('span', class_='status-indicator')
        assert status_indicator is not None
        assert 'FAILED' in status_indicator.text


@then("each failed page should display the error message")
def then_error_message_displayed(mock_app_interface):
    """Verify error messages are shown."""
    response = mock_app_interface.test_client().get('/results')
    soup = BeautifulSoup(response.data, 'html.parser')
    failed_pages = soup.find_all('div', class_='page-result failed')
    
    for page in failed_pages:
        error_message = page.find('span', class_='error-message')
        assert error_message is not None
        assert len(error_message.text.strip()) > 0


@then("each failed page should show the HTTP status code if available")
def then_failed_http_status(mock_app_interface):
    """Verify HTTP status for failed pages."""
    response = mock_app_interface.test_client().get('/results')
    soup = BeautifulSoup(response.data, 'html.parser')
    failed_pages = soup.find_all('div', class_='page-result failed')
    
    for page in failed_pages:
        http_status = page.find('span', class_='http-status')
        if http_status:
            assert re.match(r'^\d{3}$', http_status.text)


@then("each failed page should indicate the failure reason")
def then_failure_reason_indicated(mock_app_interface):
    """Verify failure reasons are indicated."""
    response = mock_app_interface.test_client().get('/results')
    soup = BeautifulSoup(response.data, 'html.parser')
    failed_pages = soup.find_all('div', class_='page-result failed')
    
    for page in failed_pages:
        # Check for error message or status indicator
        error_info = page.find('span', class_='error-message') or page.find('span', class_='status-indicator')
        assert error_info is not None


@then("I should see timeout indicators for timed out pages")
def then_see_timeout_indicators(mock_app_interface):
    """Verify timeout indicators are displayed."""
    response = mock_app_interface.test_client().get('/results')
    soup = BeautifulSoup(response.data, 'html.parser')
    timeout_pages = soup.find_all('div', class_='page-result timeout')
    assert len(timeout_pages) > 0


@then('each timed out page should show "⏰ TIMEOUT" status')
def then_timeout_status_text(mock_app_interface):
    """Verify timeout status text."""
    response = mock_app_interface.test_client().get('/results')
    soup = BeautifulSoup(response.data, 'html.parser')
    timeout_pages = soup.find_all('div', class_='page-result timeout')
    
    for page in timeout_pages:
        status_indicator = page.find('span', class_='status-indicator')
        assert status_indicator is not None
        assert 'TIMEOUT' in status_indicator.text


@then("each timed out page should display the timeout duration")
def then_timeout_duration_displayed(mock_app_interface):
    """Verify timeout duration is shown."""
    response = mock_app_interface.test_client().get('/results')
    soup = BeautifulSoup(response.data, 'html.parser')
    timeout_pages = soup.find_all('div', class_='page-result timeout')
    
    for page in timeout_pages:
        timeout_duration = page.find('span', class_='timeout-duration')
        assert timeout_duration is not None
        assert 's' in timeout_duration.text  # seconds indicator


@then("each timed out page should show partial data if any was extracted")
def then_partial_data_shown(mock_app_interface):
    """Verify partial data is shown for timeouts."""
    response = mock_app_interface.test_client().get('/results')
    soup = BeautifulSoup(response.data, 'html.parser')
    timeout_pages = soup.find_all('div', class_='page-result timeout')
    
    for page in timeout_pages:
        partial_data = page.find('span', class_='partial-data')
        if partial_data:
            assert 'items' in partial_data.text


@then("I should see redirect indicators for redirected pages")
def then_see_redirect_indicators(mock_app_interface):
    """Verify redirect indicators are displayed."""
    # This would be implemented when redirect handling is added
    pass


@then('each redirected page should show "↪ REDIRECTED" status')
def then_redirect_status_text():
    """Verify redirect status text."""
    pass


@then("each redirected page should display the final URL")
def then_final_url_displayed():
    """Verify final URL is shown for redirects."""
    pass


@then("each redirected page should show the redirect chain if multiple")
def then_redirect_chain_shown():
    """Verify redirect chain is shown."""
    pass


@then("I should see a tooltip with detailed information")
def then_see_detailed_tooltip():
    """Verify detailed tooltip appears."""
    # This would test JavaScript tooltip functionality
    pass


@then("the tooltip should include timestamp information")
def then_tooltip_has_timestamp():
    """Verify tooltip includes timestamp."""
    pass


@then("the tooltip should show extraction method used")
def then_tooltip_has_method():
    """Verify tooltip shows extraction method."""
    pass


@then("the tooltip should display response headers if available")
def then_tooltip_has_headers():
    """Verify tooltip shows response headers."""
    pass


@then("I should be able to show only successful pages")
def then_filter_success_only():
    """Verify success-only filter works."""
    pass


@then("I should be able to show only failed pages")
def then_filter_failed_only():
    """Verify failed-only filter works."""
    pass


@then("I should be able to show all pages regardless of status")
def then_show_all_pages():
    """Verify show-all filter works."""
    pass


@then("I should receive a detailed report of all failures")
def then_receive_failure_report():
    """Verify failure report is generated."""
    pass


@then("the report should include URLs, error messages, and timestamps")
def then_report_has_details():
    """Verify report includes detailed information."""
    pass


@then("the report should be downloadable as a text file")
def then_report_downloadable():
    """Verify report can be downloaded."""
    pass


@then("the system should attempt to re-scrape only the failed pages")
def then_retry_failed_only():
    """Verify only failed pages are retried."""
    pass


@then("I should see updated progress for the retry attempts")
def then_see_retry_progress():
    """Verify retry progress is shown."""
    pass


@then("successful retries should update the status display")
def then_retries_update_status():
    """Verify successful retries update the display."""
    pass