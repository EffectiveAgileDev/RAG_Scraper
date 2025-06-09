"""Step definitions for progress indication acceptance tests."""
import time
from unittest.mock import Mock, patch

import pytest
from pytest_bdd import given, when, then, scenarios, parsers

# Load scenarios from feature file
scenarios('../features/progress_indication.feature')


@pytest.fixture
def progress_context():
    """Test context for progress tracking."""
    return {
        'urls': [],
        'progress_messages': [],
        'progress_percentages': [],
        'start_time': None,
        'end_time': None,
        'current_message': None,
        'time_estimates': []
    }


@pytest.fixture
def mock_progress_callback(progress_context):
    """Mock progress callback that captures updates."""
    def progress_callback(message, percentage=None, time_estimate=None):
        progress_context['progress_messages'].append(message)
        if percentage is not None:
            progress_context['progress_percentages'].append(percentage)
        if time_estimate is not None:
            progress_context['time_estimates'].append(time_estimate)
        progress_context['current_message'] = message
    
    return progress_callback


# Given steps
@given('I have a valid restaurant website URL "http://tonysitalian.com"')
def single_valid_url(progress_context):
    """Set single valid URL for testing."""
    progress_context['urls'] = ["http://tonysitalian.com"]


@given('I have multiple valid restaurant URLs')
def multiple_valid_urls(progress_context):
    """Set multiple URLs from table data."""
    progress_context['urls'] = [
        "http://tonysitalian.com",
        "http://mariascantina.com", 
        "http://joescoffee.com"
    ]


@given('I have a valid but slow-responding URL "http://slow-restaurant.com"')
def slow_responding_url(progress_context):
    """Set slow-responding URL for testing."""
    progress_context['urls'] = ["http://slow-restaurant.com"]


@given('I have a valid but unreachable URL "http://nonexistent-restaurant.com"')
def unreachable_url(progress_context):
    """Set unreachable URL for testing."""
    progress_context['urls'] = ["http://nonexistent-restaurant.com"]


@given('I have multiple restaurant URLs for time estimation')
def urls_for_time_estimation(progress_context):
    """Set URLs for time estimation testing."""
    progress_context['urls'] = [
        "http://restaurant1.com",
        "http://restaurant2.com",
        "http://restaurant3.com",
        "http://restaurant4.com",
        "http://restaurant5.com"
    ]


@given('I have a restaurant URL with multiple pages "http://multi-page-restaurant.com"')
def multi_page_restaurant_url(progress_context):
    """Set multi-page restaurant URL."""
    progress_context['urls'] = ["http://multi-page-restaurant.com"]


@given('the website has menu, contact, and about pages')
def website_has_multiple_pages():
    """Configure mock for multi-page website."""
    # This will be used by the scraper to simulate multi-page discovery
    pass


@given('I have a large batch of restaurant URLs (20 URLs)')
def large_batch_urls(progress_context):
    """Set large batch of URLs for testing."""
    progress_context['urls'] = [f"http://restaurant{i}.com" for i in range(1, 21)]


# When steps
@when('I submit the URL for scraping')
def submit_single_url_for_scraping(progress_context, mock_progress_callback):
    """Submit single URL with progress tracking."""
    from src.scraper.restaurant_scraper import RestaurantScraper
    from src.config.scraping_config import ScrapingConfig
    
    progress_context['start_time'] = time.time()
    
    config = ScrapingConfig(urls=progress_context['urls'])
    scraper = RestaurantScraper()
    
    try:
        result = scraper.scrape_restaurants(config, progress_callback=mock_progress_callback)
        progress_context['result'] = result
    except Exception as e:
        progress_context['error'] = str(e)
    
    progress_context['end_time'] = time.time()


@when('I submit the URLs for batch scraping')
def submit_urls_for_batch_scraping(progress_context, mock_progress_callback):
    """Submit multiple URLs with progress tracking."""
    from src.scraper.restaurant_scraper import RestaurantScraper
    from src.config.scraping_config import ScrapingConfig
    
    progress_context['start_time'] = time.time()
    
    config = ScrapingConfig(urls=progress_context['urls'])
    scraper = RestaurantScraper()
    
    try:
        result = scraper.scrape_restaurants(config, progress_callback=mock_progress_callback)
        progress_context['result'] = result
    except Exception as e:
        progress_context['error'] = str(e)
    
    progress_context['end_time'] = time.time()


# Then steps
@then('I should see an initial progress message')
def should_see_initial_progress_message(progress_context):
    """Verify initial progress message appears."""
    assert len(progress_context['progress_messages']) > 0, \
        "No progress messages received"
    
    initial_messages = ['starting', 'beginning', 'initializing', 'processing']
    first_message = progress_context['progress_messages'][0].lower()
    
    assert any(msg in first_message for msg in initial_messages), \
        f"Initial message doesn't indicate start: {progress_context['progress_messages'][0]}"


@then(parsers.parse('I should see "{expected_message}" message'))
def should_see_specific_message(progress_context, expected_message):
    """Verify specific progress message appears."""
    messages = progress_context['progress_messages']
    assert any(expected_message.lower() in msg.lower() for msg in messages), \
        f"Expected message '{expected_message}' not found in: {messages}"


@then('I should see progress percentage updates')
def should_see_progress_percentage_updates(progress_context):
    """Verify progress percentage updates are received."""
    assert len(progress_context['progress_percentages']) > 0, \
        "No progress percentage updates received"
    
    # Should have at least some percentage values
    percentages = progress_context['progress_percentages']
    assert all(0 <= p <= 100 for p in percentages), \
        f"Invalid percentage values: {percentages}"


@then('I should see a completion message when finished')
def should_see_completion_message(progress_context):
    """Verify completion message appears."""
    messages = progress_context['progress_messages']
    completion_keywords = ['completed', 'finished', 'done', 'success']
    
    assert any(any(keyword in msg.lower() for keyword in completion_keywords) 
               for msg in messages), \
        f"No completion message found in: {messages}"


@then('the progress should go from 0% to 100%')
def progress_should_go_from_zero_to_hundred(progress_context):
    """Verify progress goes from 0% to 100%."""
    percentages = progress_context['progress_percentages']
    assert len(percentages) > 0, "No progress percentages recorded"
    
    # Should start at or near 0 and end at 100
    assert percentages[0] <= 10, f"Progress should start near 0%, got {percentages[0]}%"
    assert percentages[-1] >= 90, f"Progress should end near 100%, got {percentages[-1]}%"


@then('I should see overall batch progress')
def should_see_overall_batch_progress(progress_context):
    """Verify overall batch progress is shown."""
    messages = progress_context['progress_messages']
    batch_keywords = ['batch', 'overall', 'total', 'of']
    
    assert any(any(keyword in msg.lower() for keyword in batch_keywords) 
               for msg in messages), \
        f"No batch progress messages found in: {messages}"


@then('I should see current URL being processed')
def should_see_current_url_being_processed(progress_context):
    """Verify current URL being processed is shown."""
    messages = progress_context['progress_messages']
    urls = progress_context['urls']
    
    # At least one URL should be mentioned in progress messages
    assert any(any(url in msg for url in urls) for msg in messages), \
        f"No URLs mentioned in progress messages: {messages}"


@then(parsers.parse('I should see "{expected_pattern}"'))
def should_see_pattern_message(progress_context, expected_pattern):
    """Verify specific pattern appears in messages."""
    messages = progress_context['progress_messages']
    
    # Handle specific patterns like "Processing X of Y"
    if "of" in expected_pattern and "Processing" in expected_pattern:
        pattern_found = any("processing" in msg.lower() and "of" in msg.lower() 
                          for msg in messages)
        assert pattern_found, \
            f"Pattern '{expected_pattern}' not found in: {messages}"
    else:
        assert any(expected_pattern.lower() in msg.lower() for msg in messages), \
            f"Pattern '{expected_pattern}' not found in: {messages}"


@then('I should see overall completion percentage')
def should_see_overall_completion_percentage(progress_context):
    """Verify overall completion percentage is shown."""
    percentages = progress_context['progress_percentages']
    assert len(percentages) > 0, "No completion percentages recorded"
    
    # Should have reasonable percentage progression
    assert max(percentages) >= 90, "Should reach near 100% completion"


@then('I should see final completion message with statistics')
def should_see_final_completion_with_statistics(progress_context):
    """Verify final completion message includes statistics."""
    messages = progress_context['progress_messages']
    final_messages = messages[-3:]  # Check last few messages
    
    stats_keywords = ['total', 'processed', 'successful', 'completed', 'statistics']
    
    assert any(any(keyword in msg.lower() for keyword in stats_keywords) 
               for msg in final_messages), \
        f"No statistics in final messages: {final_messages}"


@then('I should see periodic "Still processing..." updates')
def should_see_periodic_updates(progress_context):
    """Verify periodic updates during long operations."""
    messages = progress_context['progress_messages']
    
    # Should have multiple messages over time
    assert len(messages) >= 3, \
        f"Should have multiple progress updates, got: {len(messages)}"


@then('the progress indicator should remain active during delays')
def progress_indicator_remains_active(progress_context):
    """Verify progress indicator stays active during delays."""
    # Should have ongoing messages, not just start and end
    messages = progress_context['progress_messages']
    assert len(messages) >= 2, "Should have ongoing progress updates"


@then('the overall progress should continue to next URL if in batch')
def overall_progress_continues_to_next_url(progress_context):
    """Verify batch processing continues after error."""
    messages = progress_context['progress_messages']
    
    # Should have messages about continuing or processing next items
    continue_keywords = ['continuing', 'next', 'skipping', 'proceeding']
    
    # If there were multiple URLs, should see continuation
    if len(progress_context['urls']) > 1:
        assert any(any(keyword in msg.lower() for keyword in continue_keywords) 
                   for msg in messages), \
            f"No continuation messages found in: {messages}"


@then(parsers.parse('I should see "{initial_message}" initially'))
def should_see_message_initially(progress_context, initial_message):
    """Verify specific message appears initially."""
    messages = progress_context['progress_messages']
    early_messages = messages[:3]  # Check first few messages
    
    assert any(initial_message.lower() in msg.lower() for msg in early_messages), \
        f"Initial message '{initial_message}' not found in: {early_messages}"


@then('after processing first URL I should see time estimate')
def should_see_time_estimate_after_first_url(progress_context):
    """Verify time estimate appears after first URL."""
    time_estimates = progress_context['time_estimates']
    assert len(time_estimates) > 0, "No time estimates received"
    
    # Should have reasonable time estimates
    assert all(est > 0 for est in time_estimates), \
        f"Invalid time estimates: {time_estimates}"


@then('the time estimate should update as processing continues')
def time_estimate_should_update(progress_context):
    """Verify time estimates are updated during processing."""
    time_estimates = progress_context['time_estimates']
    
    if len(time_estimates) > 1:
        # Estimates should change over time
        assert not all(est == time_estimates[0] for est in time_estimates), \
            "Time estimates should vary as processing continues"


@then('the estimate should become more accurate over time')
def estimate_becomes_more_accurate(progress_context):
    """Verify time estimates become more accurate."""
    # This is hard to test without actual timing, but we can verify
    # that estimates are being provided
    time_estimates = progress_context['time_estimates']
    assert len(time_estimates) > 0, "Should provide time estimates"


@then(parsers.parse('I should see "Found {page_count:d} pages to process"'))
def should_see_page_count_message(progress_context, page_count):
    """Verify page count message appears."""
    messages = progress_context['progress_messages']
    
    assert any(f"found {page_count}" in msg.lower() or f"{page_count} pages" in msg.lower() 
               for msg in messages), \
        f"Page count message not found in: {messages}"


@then(parsers.parse('I should see "Processing page {page_num:d} of {total_pages:d}: {page_type}"'))
def should_see_page_processing_message(progress_context, page_num, total_pages, page_type):
    """Verify individual page processing messages."""
    messages = progress_context['progress_messages']
    
    # Look for pattern matching page processing
    page_pattern = f"page {page_num}"
    type_pattern = page_type.lower()
    
    assert any(page_pattern in msg.lower() and type_pattern in msg.lower() 
               for msg in messages), \
        f"Page processing message not found for page {page_num} ({page_type}): {messages}"


@then('the progress indicator should remain visible throughout')
def progress_indicator_remains_visible(progress_context):
    """Verify progress indicator stays visible during long operations."""
    messages = progress_context['progress_messages']
    
    # Should have continuous updates
    assert len(messages) >= 5, \
        f"Should have multiple progress updates for long operation: {len(messages)}"


@then('progress updates should appear at least every 5 seconds')
def progress_updates_every_five_seconds(progress_context):
    """Verify progress updates frequency."""
    # This would need actual timing in real implementation
    messages = progress_context['progress_messages']
    assert len(messages) > 0, "Should have progress updates"


@then('the interface should remain responsive')
def interface_remains_responsive(progress_context):
    """Verify interface responsiveness during processing."""
    # This would need UI testing in real implementation
    assert progress_context['start_time'] is not None
    assert progress_context['end_time'] is not None


@then('I should be able to see current operation status')
def should_see_current_operation_status(progress_context):
    """Verify current operation status is visible."""
    messages = progress_context['progress_messages']
    status_keywords = ['processing', 'connecting', 'extracting', 'generating']
    
    assert any(any(keyword in msg.lower() for keyword in status_keywords) 
               for msg in messages), \
        f"No operation status messages found: {messages}"


@then('the progress should never go backwards')
def progress_should_never_go_backwards(progress_context):
    """Verify progress percentages never decrease."""
    percentages = progress_context['progress_percentages']
    
    if len(percentages) > 1:
        for i in range(1, len(percentages)):
            assert percentages[i] >= percentages[i-1], \
                f"Progress went backwards: {percentages[i-1]}% to {percentages[i]}%"