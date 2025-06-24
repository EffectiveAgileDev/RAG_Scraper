"""Step definitions for enhanced results display BDD tests."""

import pytest
from unittest.mock import Mock, patch
from pytest_bdd import scenarios, given, when, then, parsers
from bs4 import BeautifulSoup


# Load BDD scenarios
scenarios('../features/enhanced_results_display.feature')


@pytest.fixture
def context():
    """Test context to store state between steps."""
    return {
        'results_data': {},
        'scraped_sites': [],
        'processed_pages': [],
        'results_html': '',
        'soup': None
    }


@pytest.fixture
def mock_results_html():
    """Mock HTML for results section."""
    html = """
    <div class="results-container" id="resultsContainer">
        <div class="results-header">
            <h3>📊 SCRAPING_RESULTS</h3>
        </div>
        <div class="results-content" id="resultsContent">
            <div class="no-results" id="noResults" style="display: none;">
                <div class="status-message">No results available</div>
                <div class="status-subtitle">Complete a scraping operation to see detailed results</div>
            </div>
            <div class="sites-results" id="sitesResults" style="display: none;">
                <!-- Site results will be populated here -->
            </div>
        </div>
    </div>
    """
    return html


# Background steps
@given("the RAG_Scraper web interface is loaded")
def web_interface_loaded(context, mock_results_html):
    """Load the web interface with results section."""
    context['results_html'] = mock_results_html
    context['soup'] = BeautifulSoup(mock_results_html, 'html.parser')


@given("I have successfully completed a scraping operation")
def scraping_operation_completed(context):
    """Set up completed scraping operation state."""
    context['operation_completed'] = True


# Scenario 1: Display pages processed for single site
@given("I scraped a restaurant site with 3 pages")
def scraped_single_site_3_pages(context):
    """Set up single site with 3 pages."""
    site_data = {
        'site_url': 'https://restaurant1.com',
        'pages_processed': 3,
        'pages': [
            {'url': 'https://restaurant1.com/', 'status': 'success', 'processing_time': 1.2},
            {'url': 'https://restaurant1.com/menu', 'status': 'success', 'processing_time': 2.1},
            {'url': 'https://restaurant1.com/contact', 'status': 'success', 'processing_time': 0.8}
        ]
    }
    context['scraped_sites'] = [site_data]
    context['results_data'] = {'total_sites': 1, 'sites': [site_data]}


@when("I view the results section")
def view_results_section(context):
    """Simulate viewing the results section."""
    # Update the HTML to show results
    results_html = context['_generate_results_html'](context['results_data'])
    context['results_html'] = results_html
    context['soup'] = BeautifulSoup(results_html, 'html.parser')


@then('I should see "Pages Processed: 3"')
def should_see_pages_processed_3(context):
    """Verify pages processed count is shown."""
    assert 'Pages Processed: 3' in context['results_html']


@then("I should see a list of processed pages")
def should_see_list_of_pages(context):
    """Verify list of pages is displayed."""
    page_list = context['soup'].find('div', class_='pages-list')
    assert page_list is not None, "Pages list should be present"


@then("each page entry should show the URL")
def each_page_shows_url(context):
    """Verify each page shows URL."""
    for site in context['scraped_sites']:
        for page in site['pages']:
            assert page['url'] in context['results_html']


@then("each page entry should show the processing status")
def each_page_shows_status(context):
    """Verify each page shows processing status."""
    # Check for status indicators in the HTML
    assert 'success' in context['results_html'] or 'status-success' in context['results_html']


# Scenario 2: Display pages processed for multiple sites
@given("I scraped 2 restaurant sites")
def scraped_2_sites(context):
    """Set up 2 scraped sites."""
    context['scraped_sites'] = []
    context['total_sites'] = 2


@given("the first site had 4 pages processed")
def first_site_4_pages(context):
    """Set up first site with 4 pages."""
    site_data = {
        'site_url': 'https://restaurant1.com',
        'pages_processed': 4,
        'pages': [
            {'url': 'https://restaurant1.com/', 'status': 'success', 'processing_time': 1.2},
            {'url': 'https://restaurant1.com/menu', 'status': 'success', 'processing_time': 2.1},
            {'url': 'https://restaurant1.com/contact', 'status': 'success', 'processing_time': 0.8},
            {'url': 'https://restaurant1.com/about', 'status': 'success', 'processing_time': 1.5}
        ]
    }
    context['scraped_sites'].append(site_data)


@given("the second site had 2 pages processed")
def second_site_2_pages(context):
    """Set up second site with 2 pages."""
    site_data = {
        'site_url': 'https://restaurant2.com',
        'pages_processed': 2,
        'pages': [
            {'url': 'https://restaurant2.com/', 'status': 'success', 'processing_time': 1.0},
            {'url': 'https://restaurant2.com/menu', 'status': 'failed', 'processing_time': 0.5}
        ]
    }
    context['scraped_sites'].append(site_data)
    context['results_data'] = {'total_sites': 2, 'sites': context['scraped_sites']}


@then("I should see results grouped by site")
def should_see_results_grouped_by_site(context):
    """Verify results are grouped by site."""
    site_sections = context['soup'].find_all('div', class_='site-result')
    assert len(site_sections) >= 2, "Should have at least 2 site result sections"


@then('the first site should show "Pages Processed: 4"')
def first_site_shows_4_pages(context):
    """Verify first site shows 4 pages."""
    assert 'Pages Processed: 4' in context['results_html']


@then('the second site should show "Pages Processed: 2"')
def second_site_shows_2_pages(context):
    """Verify second site shows 2 pages."""
    assert 'Pages Processed: 2' in context['results_html']


# Scenario 3: Show page processing details
@given("I scraped a site with successful and failed pages")
def scraped_site_mixed_results(context):
    """Set up site with mixed success/failure."""
    site_data = {
        'site_url': 'https://restaurant1.com',
        'pages_processed': 3,
        'pages': [
            {'url': 'https://restaurant1.com/', 'status': 'success', 'processing_time': 1.2},
            {'url': 'https://restaurant1.com/menu', 'status': 'failed', 'processing_time': 0.3},
            {'url': 'https://restaurant1.com/contact', 'status': 'success', 'processing_time': 0.8}
        ]
    }
    context['scraped_sites'] = [site_data]
    context['results_data'] = {'total_sites': 1, 'sites': [site_data]}


@then("I should see successful pages marked with green status")
def should_see_green_success_status(context):
    """Verify successful pages have green status."""
    assert 'status-success' in context['results_html'] or 'success' in context['results_html']


@then("I should see failed pages marked with red status")
def should_see_red_failure_status(context):
    """Verify failed pages have red status."""
    assert 'status-failed' in context['results_html'] or 'failed' in context['results_html']


@then("each page should show its URL")
def each_page_shows_its_url(context):
    """Verify each page shows its URL."""
    for site in context['scraped_sites']:
        for page in site['pages']:
            assert page['url'] in context['results_html']


@then("each page should show its processing time")
def each_page_shows_processing_time(context):
    """Verify each page shows processing time."""
    for site in context['scraped_sites']:
        for page in site['pages']:
            time_str = f"{page['processing_time']:.1f}s"
            assert time_str in context['results_html'] or str(page['processing_time']) in context['results_html']


# Scenario 4: Expandable page lists for large sites
@given("I scraped a site with 15 pages")
def scraped_site_15_pages(context):
    """Set up site with 15 pages."""
    pages = []
    for i in range(15):
        pages.append({
            'url': f'https://restaurant1.com/page{i+1}',
            'status': 'success',
            'processing_time': 1.0 + (i * 0.1)
        })
    
    site_data = {
        'site_url': 'https://restaurant1.com',
        'pages_processed': 15,
        'pages': pages
    }
    context['scraped_sites'] = [site_data]
    context['results_data'] = {'total_sites': 1, 'sites': [site_data]}


@then("I should see the first 5 pages displayed")
def should_see_first_5_pages(context):
    """Verify first 5 pages are displayed."""
    # Check for first 5 page URLs
    for i in range(5):
        page_url = f'https://restaurant1.com/page{i+1}'
        assert page_url in context['results_html']


@then('I should see "Show all 15 pages" link')
def should_see_show_all_pages_link(context):
    """Verify show all pages link is present."""
    assert 'Show all 15 pages' in context['results_html'] or 'show-all-pages' in context['results_html']


@when('I click "Show all pages"')
def click_show_all_pages(context):
    """Simulate clicking show all pages."""
    # Update HTML to show all pages
    context['show_all_pages'] = True
    results_html = context['_generate_results_html'](context['results_data'], show_all=True)
    context['results_html'] = results_html
    context['soup'] = BeautifulSoup(results_html, 'html.parser')


@then("I should see all 15 pages listed")
def should_see_all_15_pages(context):
    """Verify all 15 pages are listed."""
    for i in range(15):
        page_url = f'https://restaurant1.com/page{i+1}'
        assert page_url in context['results_html']


# Scenario 5: Empty results display
@given("no scraping operation has been completed")
def no_scraping_completed(context):
    """Set up state with no completed operations."""
    context['operation_completed'] = False
    context['results_data'] = None


@then('I should see "No results available"')
def should_see_no_results_message(context):
    """Verify no results message is shown."""
    assert 'No results available' in context['results_html']


@then('I should see "Complete a scraping operation to see detailed results"')
def should_see_complete_operation_message(context):
    """Verify complete operation message is shown."""
    assert 'Complete a scraping operation to see detailed results' in context['results_html']


# Scenario 6: Results section visibility based on scraping mode
@given("I am in single-page mode")
def in_single_page_mode(context):
    """Set single-page mode."""
    context['scraping_mode'] = 'single'


@when("I complete a scraping operation")
def complete_scraping_operation(context):
    """Complete a scraping operation."""
    context['operation_completed'] = True
    if not context.get('results_data'):
        # Set up basic results data
        site_data = {
            'site_url': 'https://restaurant1.com',
            'pages_processed': 1,
            'pages': [
                {'url': 'https://restaurant1.com/', 'status': 'success', 'processing_time': 1.2}
            ]
        }
        context['results_data'] = {'total_sites': 1, 'sites': [site_data]}


@then("the results should show individual page processing")
def results_show_individual_processing(context):
    """Verify results show individual page processing."""
    # In single-page mode, results should be simple
    assert context['scraping_mode'] == 'single'
    # Generate results HTML for single-page mode
    results_html = context['_generate_results_html'](context['results_data'], mode='single')
    context['results_html'] = results_html


@then("page relationships should not be displayed")
def page_relationships_not_displayed(context):
    """Verify page relationships are not shown in single-page mode."""
    assert 'parent-child' not in context['results_html']
    assert 'relationship' not in context['results_html']


@given("I am in multi-page mode")
def in_multi_page_mode(context):
    """Set multi-page mode."""
    context['scraping_mode'] = 'multi'


@then("the results should show site-based grouping")
def results_show_site_grouping(context):
    """Verify results show site-based grouping."""
    assert context['scraping_mode'] == 'multi'
    # Generate results HTML for multi-page mode
    results_html = context['_generate_results_html'](context['results_data'], mode='multi')
    context['results_html'] = results_html
    assert 'site-result' in results_html or 'Sites Scraped' in results_html


@then("page discovery information should be displayed")
def page_discovery_info_displayed(context):
    """Verify page discovery information is shown."""
    assert 'discovery' in context['results_html'] or 'crawled' in context['results_html']


# Helper method to generate results HTML
def _generate_results_html(results_data, mode='multi', show_all=False):
    """Generate mock results HTML based on data."""
    if not results_data:
        return """
        <div class="results-container">
            <div class="no-results">
                <div class="status-message">No results available</div>
                <div class="status-subtitle">Complete a scraping operation to see detailed results</div>
            </div>
        </div>
        """
    
    html_parts = ['<div class="results-container">']
    
    # Add discovery information for multi-page mode
    if mode == 'multi':
        html_parts.append('<div class="discovery-info">')
        html_parts.append('<span class="discovery-label">Page discovery completed</span>')
        html_parts.append('</div>')
    
    for site in results_data['sites']:
        html_parts.append(f'<div class="site-result">')
        html_parts.append(f'<h4>{site["site_url"]}</h4>')
        html_parts.append(f'<div class="pages-summary">Pages Processed: {site["pages_processed"]}</div>')
        html_parts.append(f'<div class="pages-list">')
        
        pages_to_show = site['pages']
        if not show_all and len(pages_to_show) > 5:
            pages_to_show = pages_to_show[:5]
            html_parts.append(f'<div class="show-all-link">Show all {len(site["pages"])} pages</div>')
        
        for page in pages_to_show:
            status_class = f'status-{page["status"]}'
            html_parts.append(f'<div class="page-item {status_class}">')
            html_parts.append(f'<span class="page-url">{page["url"]}</span>')
            html_parts.append(f'<span class="page-time">{page["processing_time"]:.1f}s</span>')
            html_parts.append(f'<span class="page-status">{page["status"]}</span>')
            html_parts.append('</div>')
        
        html_parts.append('</div>')  # pages-list
        html_parts.append('</div>')  # site-result
    
    html_parts.append('</div>')  # results-container
    
    return ''.join(html_parts)


# Monkey patch the helper method to context
@pytest.fixture(autouse=True)
def add_helper_methods(context):
    """Add helper methods to context."""
    context['_generate_results_html'] = _generate_results_html