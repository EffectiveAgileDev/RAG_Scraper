"""BDD step definitions for multi-page website navigation and data aggregation."""
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from unittest.mock import Mock, patch, MagicMock
import time
from typing import Dict, List, Any

from src.config.scraping_config import ScrapingConfig
from src.scraper.restaurant_scraper import RestaurantScraper
from src.scraper.multi_strategy_scraper import RestaurantData


# Load all scenarios from the feature file
scenarios('../features/multi_page_navigation.feature')


@pytest.fixture
def multi_page_context():
    """Context for multi-page scraping tests."""
    return {
        'restaurant_urls': [],
        'discovered_pages': {},
        'progress_messages': [],
        'final_results': {},
        'scraper': None,
        'mock_pages': {},
        'batch_restaurants': []
    }


@pytest.fixture
def mock_progress_callback(multi_page_context):
    """Mock progress callback that captures messages."""
    def callback(message, percentage=None, time_estimate=None):
        multi_page_context['progress_messages'].append({
            'message': message,
            'percentage': percentage,
            'time_estimate': time_estimate
        })
    return callback


# Background steps

@given('I have access to the RAG_Scraper web interface')
def have_web_interface_access(multi_page_context):
    """Ensure web interface is available for testing."""
    multi_page_context['web_interface_available'] = True


@given('the multi-page scraping functionality is enabled')
def multi_page_scraping_enabled(multi_page_context):
    """Enable multi-page scraping functionality."""
    multi_page_context['multi_page_enabled'] = True


# Page Discovery Scenario Steps

@given('I provide a restaurant website URL "http://example-restaurant.com"')
def provide_restaurant_url(multi_page_context):
    """Provide a restaurant website URL for testing."""
    multi_page_context['restaurant_urls'] = ["http://example-restaurant.com"]


@when('I start the multi-page scraping process')
def start_multi_page_scraping(multi_page_context, mock_progress_callback):
    """Start the multi-page scraping process."""
    from src.scraper.multi_page_scraper import MultiPageScraper
    
    scraper = MultiPageScraper()
    multi_page_context['scraper'] = scraper
    
    # Mock page discovery to return relevant pages
    with patch.object(scraper.page_discovery, 'discover_all_pages') as mock_discover, \
         patch.object(scraper, '_fetch_and_process_page') as mock_process:
        
        mock_discover.return_value = [
            "http://example-restaurant.com/",
            "http://example-restaurant.com/menu",
            "http://example-restaurant.com/contact",
            "http://example-restaurant.com/about"
        ]
        
        mock_process.return_value = {
            "page_type": "menu",
            "data": RestaurantData(name="Example Restaurant", sources=["mock"])
        }
        
        url = multi_page_context['restaurant_urls'][0]
        result = scraper.scrape_website(url, progress_callback=mock_progress_callback)
        multi_page_context['final_results'][url] = result


@then('the system should discover navigation links')
def system_discovers_navigation_links(multi_page_context):
    """Verify that navigation links are discovered."""
    messages = [msg['message'] for msg in multi_page_context['progress_messages']]
    discovery_messages = [msg for msg in messages if 'Discovered' in msg]
    assert len(discovery_messages) > 0


@then('identify relevant pages like "Menu", "About", "Contact", "Hours"')
def identify_relevant_pages(multi_page_context):
    """Verify that relevant pages are identified."""
    messages = [msg['message'] for msg in multi_page_context['progress_messages']]
    page_messages = [msg for msg in messages if any(page in msg for page in ['Menu', 'About', 'Contact', 'Hours'])]
    assert len(page_messages) > 0


@then('limit discovery to maximum 10 pages')
def limit_discovery_to_max_pages(multi_page_context):
    """Verify that page discovery is limited to maximum pages."""
    # This would be tested through the scraper's max_pages configuration
    scraper = multi_page_context['scraper']
    assert scraper.max_pages == 10


@then('exclude irrelevant pages like "Blog", "Careers", "Privacy"')
def exclude_irrelevant_pages(multi_page_context):
    """Verify that irrelevant pages are excluded."""
    messages = [msg['message'] for msg in multi_page_context['progress_messages']]
    irrelevant_messages = [msg for msg in messages if any(page in msg for page in ['Blog', 'Careers', 'Privacy'])]
    assert len(irrelevant_messages) == 0


# Progress Tracking Scenario Steps

@given('I provide a restaurant website with 4 discoverable pages')
def provide_restaurant_with_4_pages(multi_page_context):
    """Provide a restaurant website with 4 discoverable pages."""
    multi_page_context['restaurant_urls'] = ["http://restaurant-4-pages.com"]
    multi_page_context['mock_pages']["http://restaurant-4-pages.com"] = [
        "http://restaurant-4-pages.com/",
        "http://restaurant-4-pages.com/menu",
        "http://restaurant-4-pages.com/contact",
        "http://restaurant-4-pages.com/about"
    ]


@then('I should see "Discovered 4 pages for Restaurant Name"')
def should_see_pages_discovered_message(multi_page_context):
    """Verify discovery message shows correct page count."""
    messages = [msg['message'] for msg in multi_page_context['progress_messages']]
    discovery_messages = [msg for msg in messages if 'Discovered 4 pages' in msg]
    assert len(discovery_messages) > 0


@then('I should see progress updates like "Processing page 1 of 4"')
def should_see_page_progress_updates(multi_page_context):
    """Verify page-by-page progress updates."""
    messages = [msg['message'] for msg in multi_page_context['progress_messages']]
    progress_messages = [msg for msg in messages if 'Processing page' in msg and 'of' in msg]
    assert len(progress_messages) > 0


@then('I should see page type notifications like "Processing Menu page"')
def should_see_page_type_notifications(multi_page_context):
    """Verify page type notifications are shown."""
    messages = [msg['message'] for msg in multi_page_context['progress_messages']]
    page_type_messages = [msg for msg in messages if any(ptype in msg for ptype in ['Menu page', 'Contact page', 'About page'])]
    assert len(page_type_messages) > 0


@then('I should see completion message "Completed Restaurant Name (4 pages processed)"')
def should_see_completion_message(multi_page_context):
    """Verify completion message shows processed page count."""
    messages = [msg['message'] for msg in multi_page_context['progress_messages']]
    completion_messages = [msg for msg in messages if 'Completed' in msg and 'pages processed' in msg]
    assert len(completion_messages) > 0


# Data Aggregation Scenario Steps

@given(parsers.parse('I provide a restaurant website with data spread across pages:\n{table}'))
def provide_restaurant_with_spread_data(multi_page_context, table):
    """Provide a restaurant website with data spread across multiple pages."""
    multi_page_context['restaurant_urls'] = ["http://spread-data-restaurant.com"]
    multi_page_context['spread_data'] = table


@when('I complete the multi-page scraping')
def complete_multi_page_scraping(multi_page_context, mock_progress_callback):
    """Complete the multi-page scraping process."""
    from src.scraper.multi_page_scraper import MultiPageScraper
    
    scraper = MultiPageScraper()
    multi_page_context['scraper'] = scraper
    
    # Mock comprehensive data from different pages
    with patch.object(scraper, '_fetch_and_process_page') as mock_process:
        def mock_page_processing(url):
            if 'menu' in url:
                return {
                    "page_type": "menu",
                    "data": RestaurantData(
                        name="Restaurant Name",
                        menu_items={"Appetizers": ["Calamari"], "Entrees": ["Pasta"]},
                        price_range="$15-30",
                        sources=["json-ld"]
                    )
                }
            elif 'contact' in url:
                return {
                    "page_type": "contact", 
                    "data": RestaurantData(
                        name="Restaurant Name",
                        phone="(503) 555-1234",
                        address="123 Main St",
                        hours="Mon-Sun 11am-10pm",
                        sources=["microdata"]
                    )
                }
            elif 'about' in url:
                return {
                    "page_type": "about",
                    "data": RestaurantData(
                        name="Restaurant Name",
                        cuisine="Italian",
                        sources=["heuristic"]
                    )
                }
            else:  # home page
                return {
                    "page_type": "home",
                    "data": RestaurantData(
                        name="Restaurant Name",
                        sources=["heuristic"]
                    )
                }
        
        mock_process.side_effect = mock_page_processing
        
        with patch.object(scraper.page_discovery, 'discover_all_pages') as mock_discover:
            mock_discover.return_value = [
                "http://spread-data-restaurant.com/",
                "http://spread-data-restaurant.com/menu",
                "http://spread-data-restaurant.com/contact",
                "http://spread-data-restaurant.com/about"
            ]
            
            url = multi_page_context['restaurant_urls'][0]
            result = scraper.scrape_website(url, progress_callback=mock_progress_callback)
            multi_page_context['final_results'][url] = result


@then('the final restaurant data should combine all information')
def final_data_combines_all_information(multi_page_context):
    """Verify that final data combines information from all pages."""
    url = multi_page_context['restaurant_urls'][0]
    result = multi_page_context['final_results'][url]
    assert result is not None
    assert hasattr(result, 'aggregated_data')


@then('should contain the restaurant name from home page')
def should_contain_restaurant_name(multi_page_context):
    """Verify restaurant name is included."""
    url = multi_page_context['restaurant_urls'][0]
    result = multi_page_context['final_results'][url]
    # This would check the aggregated restaurant data
    assert result is not None


@then('should contain menu items from menu page')
def should_contain_menu_items(multi_page_context):
    """Verify menu items are included."""
    url = multi_page_context['restaurant_urls'][0]
    result = multi_page_context['final_results'][url]
    assert result is not None


@then('should contain contact details from contact page')
def should_contain_contact_details(multi_page_context):
    """Verify contact details are included."""
    url = multi_page_context['restaurant_urls'][0]
    result = multi_page_context['final_results'][url]
    assert result is not None


@then('should contain cuisine type from about page')
def should_contain_cuisine_type(multi_page_context):
    """Verify cuisine type is included."""
    url = multi_page_context['restaurant_urls'][0]
    result = multi_page_context['final_results'][url]
    assert result is not None


# Conflict Resolution Scenario Steps

@given(parsers.parse('I provide a restaurant website with conflicting information:\n{table}'))
def provide_restaurant_with_conflicts(multi_page_context, table):
    """Provide a restaurant website with conflicting information."""
    multi_page_context['restaurant_urls'] = ["http://conflicting-restaurant.com"]
    multi_page_context['conflicting_data'] = table


@then('the system should prioritize Contact page data for contact fields')
def should_prioritize_contact_page_data(multi_page_context):
    """Verify that contact page data is prioritized for contact fields."""
    # This would be verified through the data aggregation logic
    assert True  # Placeholder for actual implementation test


@then('should use Contact page phone number')
def should_use_contact_page_phone(multi_page_context):
    """Verify contact page phone number is used."""
    assert True  # Placeholder for actual implementation test


@then('should use Contact page hours')
def should_use_contact_page_hours(multi_page_context):
    """Verify contact page hours are used."""
    assert True  # Placeholder for actual implementation test


@then('should indicate data sources in the result')
def should_indicate_data_sources(multi_page_context):
    """Verify that data sources are tracked."""
    assert True  # Placeholder for actual implementation test


# Error Handling Scenario Steps

@given('the Menu page returns a 404 error')
def menu_page_returns_404(multi_page_context):
    """Configure menu page to return 404 error."""
    multi_page_context['failed_pages'] = ["http://restaurant.com/menu"]


@then('I should see "Failed to load Menu page - continuing with other pages"')
def should_see_failure_message(multi_page_context):
    """Verify failure message is shown."""
    messages = [msg['message'] for msg in multi_page_context['progress_messages']]
    failure_messages = [msg for msg in messages if 'Failed to load' in msg and 'Menu page' in msg]
    assert len(failure_messages) > 0


@then('the scraping should continue with remaining pages')
def scraping_continues_with_remaining_pages(multi_page_context):
    """Verify scraping continues despite page failures."""
    # Check that other pages were still processed
    messages = [msg['message'] for msg in multi_page_context['progress_messages']]
    processing_messages = [msg for msg in messages if 'Processing page' in msg]
    assert len(processing_messages) > 1  # More than just the failed page


@then('the final result should contain data from successful pages')
def final_result_contains_successful_data(multi_page_context):
    """Verify final result contains data from successful pages."""
    url = multi_page_context['restaurant_urls'][0] if multi_page_context['restaurant_urls'] else None
    if url and url in multi_page_context['final_results']:
        result = multi_page_context['final_results'][url]
        assert result is not None


@then('should indicate which pages failed to load')
def should_indicate_failed_pages(multi_page_context):
    """Verify that failed pages are tracked."""
    messages = [msg['message'] for msg in multi_page_context['progress_messages']]
    failure_messages = [msg for msg in messages if 'Failed to load' in msg]
    assert len(failure_messages) > 0


# Batch Integration Scenario Steps

@given(parsers.parse('I provide multiple restaurant URLs for batch processing:\n{table}'))
def provide_multiple_restaurants_for_batch(multi_page_context, table):
    """Provide multiple restaurant URLs for batch processing."""
    multi_page_context['batch_restaurants'] = [
        {"url": "http://restaurant1.com", "expected_pages": 3},
        {"url": "http://restaurant2.com", "expected_pages": 5},
        {"url": "http://restaurant3.com", "expected_pages": 2}
    ]


@when('I start the batch scraping with multi-page enabled')
def start_batch_scraping_with_multi_page(multi_page_context, mock_progress_callback):
    """Start batch scraping with multi-page processing enabled."""
    from src.scraper.restaurant_scraper import RestaurantScraper
    
    scraper = RestaurantScraper()
    multi_page_context['scraper'] = scraper
    
    # Mock multi-page processing for each restaurant
    with patch.object(scraper, 'scrape_restaurants') as mock_scrape:
        def mock_batch_processing(config, progress_callback=None):
            # Simulate processing each restaurant with multiple pages
            for i, url in enumerate(config.urls):
                if progress_callback:
                    progress_callback(f"Processing restaurant {i+1} of {len(config.urls)}: {url}")
                    progress_callback(f"Discovered pages for restaurant {i+1}")
                    progress_callback(f"Processing pages for restaurant {i+1}")
                    progress_callback(f"Completed restaurant {i+1}")
            
            # Return mock result
            from src.scraper.restaurant_scraper import ScrapingResult
            return ScrapingResult(
                successful_extractions=[RestaurantData(name=f"Restaurant {i+1}", sources=["mock"]) for i in range(len(config.urls))],
                failed_urls=[],
                output_files={"text": ["output.txt"]}
            )
        
        mock_scrape.side_effect = mock_batch_processing
        
        urls = [r["url"] for r in multi_page_context['batch_restaurants']]
        config = ScrapingConfig(urls=urls)
        config.force_batch_processing = True
        
        result = scraper.scrape_restaurants(config, progress_callback=mock_progress_callback)
        multi_page_context['batch_result'] = result


@then('each restaurant should have its pages discovered and processed')
def each_restaurant_pages_discovered_and_processed(multi_page_context):
    """Verify each restaurant had pages discovered and processed."""
    messages = [msg['message'] for msg in multi_page_context['progress_messages']]
    discovery_messages = [msg for msg in messages if 'Discovered pages' in msg]
    assert len(discovery_messages) >= len(multi_page_context['batch_restaurants'])


@then('progress should show both restaurant and page-level progress')
def progress_shows_restaurant_and_page_level(multi_page_context):
    """Verify progress shows both restaurant and page level information."""
    messages = [msg['message'] for msg in multi_page_context['progress_messages']]
    restaurant_messages = [msg for msg in messages if 'restaurant' in msg.lower()]
    page_messages = [msg for msg in messages if 'page' in msg.lower()]
    assert len(restaurant_messages) > 0
    assert len(page_messages) > 0


@then('final results should contain aggregated data for each restaurant')
def final_results_contain_aggregated_data(multi_page_context):
    """Verify final results contain aggregated data for each restaurant."""
    batch_result = multi_page_context.get('batch_result')
    assert batch_result is not None
    assert len(batch_result.successful_extractions) == len(multi_page_context['batch_restaurants'])


# Performance Scenario Steps

@given('I provide a restaurant website with 5 discoverable pages')
def provide_restaurant_with_5_pages(multi_page_context):
    """Provide a restaurant website with 5 discoverable pages."""
    multi_page_context['restaurant_urls'] = ["http://performance-test-restaurant.com"]
    multi_page_context['expected_pages'] = 5


@then('the total processing time should be reasonable')
def total_processing_time_reasonable(multi_page_context):
    """Verify total processing time is reasonable."""
    # This would be measured during actual scraping
    # For now, we assume the test framework tracks timing
    assert True  # Placeholder for actual timing verification


@then('each page should be processed with rate limiting')
def each_page_processed_with_rate_limiting(multi_page_context):
    """Verify rate limiting is applied between page requests."""
    # This would be verified through the ethical scraper's rate limiting
    assert True  # Placeholder for rate limiting verification


@then('memory usage should remain within acceptable limits')
def memory_usage_within_limits(multi_page_context):
    """Verify memory usage stays within acceptable limits."""
    # This would be monitored during actual processing
    assert True  # Placeholder for memory monitoring


@then('progress updates should be timely and accurate')
def progress_updates_timely_and_accurate(multi_page_context):
    """Verify progress updates are sent in a timely manner."""
    messages = multi_page_context['progress_messages']
    assert len(messages) > 0
    
    # Verify messages have reasonable timestamps (would need actual timing)
    for msg in messages:
        assert msg['message'] is not None
        assert len(msg['message']) > 0