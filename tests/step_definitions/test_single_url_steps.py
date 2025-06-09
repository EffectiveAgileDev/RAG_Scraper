"""Step definitions for single URL scraping acceptance tests."""
import os
import tempfile
import time
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from pytest_bdd import given, when, then, scenarios
import requests

# Load scenarios from feature file
scenarios('../features/single_url_scraping.feature')


@pytest.fixture
def scraper_context():
    """Test context for scraper operations."""
    return {
        'url': None,
        'output_dir': None,
        'result': None,
        'error': None,
        'generated_files': [],
        'progress_updates': []
    }


@pytest.fixture
def temp_output_dir():
    """Create temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


# Background steps
@given('the RAG_Scraper web interface is running')
def web_interface_running():
    """Ensure web interface is available for testing."""
    # This will be implemented when Flask server is created
    pass


@given('I have access to the localhost application')
def localhost_access():
    """Verify localhost application access."""
    # This will be implemented when Flask server is created
    pass


# Given steps
@given('I have a valid restaurant website URL "http://tonysitalian.com"')
def valid_restaurant_url(scraper_context):
    """Set a valid restaurant URL for testing."""
    scraper_context['url'] = "http://tonysitalian.com"


@given('I have selected default data fields')
def default_data_fields(scraper_context):
    """Configure default data field selection."""
    scraper_context['selected_fields'] = [
        'name', 'address', 'phone', 'website', 'hours', 'menu_items'
    ]


@given('I have an invalid URL "not-a-real-url"')
def invalid_url(scraper_context):
    """Set an invalid URL for testing."""
    scraper_context['url'] = "not-a-real-url"


@given('I have a valid but unreachable URL "http://nonexistent-restaurant.com"')
def unreachable_url(scraper_context):
    """Set a valid but unreachable URL for testing."""
    scraper_context['url'] = "http://nonexistent-restaurant.com"


@given('I have a valid URL "http://incomplete-restaurant.com" with minimal data')
def minimal_data_url(scraper_context):
    """Set URL that returns minimal restaurant data."""
    scraper_context['url'] = "http://incomplete-restaurant.com"


@given('I have not specified an output directory')
def no_output_directory(scraper_context):
    """Test with default output directory."""
    scraper_context['output_dir'] = None


# When steps
@when('I submit the URL for scraping')
def submit_url_for_scraping(scraper_context, temp_output_dir):
    """Submit URL for scraping process."""
    from src.scraper.restaurant_scraper import RestaurantScraper
    from src.config.scraping_config import ScrapingConfig
    
    try:
        # Configure scraping
        config = ScrapingConfig(
            urls=[scraper_context['url']],
            output_directory=scraper_context.get('output_dir', temp_output_dir),
            selected_fields=scraper_context.get('selected_fields', [])
        )
        
        # Create scraper and process
        scraper = RestaurantScraper()
        
        def progress_callback(update):
            scraper_context['progress_updates'].append(update)
        
        scraper_context['result'] = scraper.scrape_restaurants(
            config, 
            progress_callback=progress_callback
        )
        
    except Exception as e:
        scraper_context['error'] = str(e)


# Then steps
@then('I should see a progress indicator')
def should_see_progress_indicator(scraper_context):
    """Verify progress indicator is shown."""
    assert len(scraper_context['progress_updates']) > 0, \
        "No progress updates received"


@then('the scraping should complete successfully')
def scraping_completes_successfully(scraper_context):
    """Verify scraping completed without errors."""
    assert scraper_context['error'] is None, \
        f"Scraping failed with error: {scraper_context['error']}"
    assert scraper_context['result'] is not None, \
        "No scraping result returned"
    assert len(scraper_context['result'].successful_extractions) > 0, \
        "No successful extractions found"


@then('I should receive a properly formatted text file')
def should_receive_formatted_text_file(scraper_context):
    """Verify properly formatted text file is generated."""
    assert scraper_context['result'] is not None
    assert len(scraper_context['result'].output_files.get('text', [])) > 0, \
        "No text files generated"
    
    # Verify file exists and is readable
    text_files = scraper_context['result'].output_files['text']
    for file_path in text_files:
        assert os.path.exists(file_path), f"Generated file not found: {file_path}"
        assert os.path.getsize(file_path) > 0, f"Generated file is empty: {file_path}"


@then('the file should contain restaurant name')
def file_contains_restaurant_name(scraper_context):
    """Verify file contains restaurant name."""
    text_files = scraper_context['result'].output_files['text']
    file_path = text_files[0]
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for restaurant name in first line
    lines = content.strip().split('\n')
    assert len(lines) > 0, "File is empty"
    assert len(lines[0].strip()) > 0, "Restaurant name is missing"


@then('the file should contain restaurant address')
def file_contains_restaurant_address(scraper_context):
    """Verify file contains restaurant address."""
    text_files = scraper_context['result'].output_files['text']
    file_path = text_files[0]
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for address pattern in second line
    lines = content.strip().split('\n')
    assert len(lines) > 1, "Address line missing"
    # Address should contain street, city, state pattern
    address_line = lines[1]
    assert ',' in address_line or 'Street' in address_line or 'Ave' in address_line, \
        f"Address format incorrect: {address_line}"


@then('the file should contain restaurant phone number')
def file_contains_restaurant_phone(scraper_context):
    """Verify file contains restaurant phone number."""
    text_files = scraper_context['result'].output_files['text']
    file_path = text_files[0]
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for phone number pattern
    import re
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    assert re.search(phone_pattern, content), \
        "Phone number not found in file"


@then('the file should contain restaurant website')
def file_contains_restaurant_website(scraper_context):
    """Verify file contains restaurant website."""
    text_files = scraper_context['result'].output_files['text']
    file_path = text_files[0]
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for website URL
    assert 'http' in content.lower() or 'www.' in content.lower(), \
        "Website URL not found in file"


@then('the file should contain restaurant hours')
def file_contains_restaurant_hours(scraper_context):
    """Verify file contains restaurant hours."""
    text_files = scraper_context['result'].output_files['text']
    file_path = text_files[0]
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for hours pattern
    hours_keywords = ['hours', 'open', 'monday', 'tuesday', 'am', 'pm']
    content_lower = content.lower()
    
    assert any(keyword in content_lower for keyword in hours_keywords), \
        "Restaurant hours not found in file"


@then('the file should contain menu items with sections')
def file_contains_menu_items_with_sections(scraper_context):
    """Verify file contains menu items organized in sections."""
    text_files = scraper_context['result'].output_files['text']
    file_path = text_files[0]
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for menu section headers
    menu_sections = ['APPETIZERS', 'ENTREES', 'DESSERTS', 'MENU']
    content_upper = content.upper()
    
    assert any(section in content_upper for section in menu_sections), \
        "Menu sections not found in file"


@then('the file should follow RAG format standards')
def file_follows_rag_format_standards(scraper_context):
    """Verify file follows RAG format standards."""
    text_files = scraper_context['result'].output_files['text']
    file_path = text_files[0]
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verify basic format structure
    lines = content.strip().split('\n')
    assert len(lines) >= 6, "File format too short for RAG standards"
    
    # Verify UTF-8 encoding
    assert isinstance(content, str), "File content should be string"
    
    # Verify reasonable content length
    assert len(content) > 100, "File content too short for meaningful data"


@then('I should see an error message')
def should_see_error_message(scraper_context):
    """Verify error message is displayed."""
    assert scraper_context['error'] is not None, \
        "Expected error message but none was found"


@then('no file should be generated')
def no_file_generated(scraper_context):
    """Verify no output file was generated."""
    if scraper_context['result']:
        assert len(scraper_context['result'].output_files.get('text', [])) == 0, \
            "File was generated when none should have been"


@then('the error should specify the URL validation failure')
def error_specifies_url_validation_failure(scraper_context):
    """Verify error message specifies URL validation failure."""
    assert 'url' in scraper_context['error'].lower() or \
           'invalid' in scraper_context['error'].lower(), \
        f"Error message doesn't specify URL validation: {scraper_context['error']}"


@then('I should see a network error message')
def should_see_network_error_message(scraper_context):
    """Verify network error message is shown."""
    assert scraper_context['error'] is not None
    network_keywords = ['network', 'connection', 'unreachable', 'timeout', 'connect']
    error_lower = scraper_context['error'].lower()
    
    assert any(keyword in error_lower for keyword in network_keywords), \
        f"Error message doesn't indicate network issue: {scraper_context['error']}"


@then('the error should specify the connection failure')
def error_specifies_connection_failure(scraper_context):
    """Verify error specifies connection failure."""
    connection_keywords = ['connection', 'connect', 'unreachable', 'resolve']
    error_lower = scraper_context['error'].lower()
    
    assert any(keyword in error_lower for keyword in connection_keywords), \
        f"Error doesn't specify connection failure: {scraper_context['error']}"


@then('the scraping should complete with warnings')
def scraping_completes_with_warnings(scraper_context):
    """Verify scraping completes but with warnings."""
    assert scraper_context['result'] is not None
    # Should have some successful extraction but with warnings
    assert len(scraper_context['result'].successful_extractions) > 0
    # Could check for warnings in result if we implement that


@then('I should receive a text file with available data')
def receive_text_file_with_available_data(scraper_context):
    """Verify text file is generated with available data."""
    assert scraper_context['result'] is not None
    assert len(scraper_context['result'].output_files.get('text', [])) > 0
    
    # File should exist and contain some data
    text_file = scraper_context['result'].output_files['text'][0]
    assert os.path.exists(text_file)
    assert os.path.getsize(text_file) > 0


@then('missing fields should be indicated as "Not Available"')
def missing_fields_indicated_as_not_available(scraper_context):
    """Verify missing fields are marked as Not Available."""
    text_files = scraper_context['result'].output_files['text']
    file_path = text_files[0]
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Should contain "Not Available" for missing fields
    assert 'Not Available' in content or 'N/A' in content, \
        "Missing fields not properly indicated"


@then('the file should be saved to the default downloads location')
def file_saved_to_default_location(scraper_context):
    """Verify file is saved to default location."""
    assert scraper_context['result'] is not None
    assert len(scraper_context['result'].output_files.get('text', [])) > 0
    
    # Verify file path exists
    text_file = scraper_context['result'].output_files['text'][0]
    assert os.path.exists(text_file)


@then('the filename should include timestamp')
def filename_includes_timestamp(scraper_context):
    """Verify filename includes timestamp."""
    text_files = scraper_context['result'].output_files['text']
    file_path = text_files[0]
    filename = os.path.basename(file_path)
    
    # Should contain date/time pattern
    import re
    timestamp_pattern = r'\d{8}-\d{4}'
    assert re.search(timestamp_pattern, filename), \
        f"Filename doesn't include timestamp: {filename}"


@then('the filename should follow format "WebScrape_yyyymmdd-hhmm.txt"')
def filename_follows_format(scraper_context):
    """Verify filename follows specific format."""
    text_files = scraper_context['result'].output_files['text']
    file_path = text_files[0]
    filename = os.path.basename(file_path)
    
    # Should match exact format
    import re
    format_pattern = r'^WebScrape_\d{8}-\d{4}\.txt$'
    assert re.match(format_pattern, filename), \
        f"Filename doesn't follow required format: {filename}"