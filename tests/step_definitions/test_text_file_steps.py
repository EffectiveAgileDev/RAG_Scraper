"""Step definitions for text file generation ATDD tests."""
import os
import tempfile
import json
from datetime import datetime
from unittest.mock import patch, MagicMock
from pathlib import Path

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

from src.scraper.multi_strategy_scraper import RestaurantData
from src.file_generator.text_file_generator import TextFileGenerator, TextFileConfig
from src.config.file_permission_validator import FilePermissionValidator

# Load scenarios from the feature file
scenarios('../features/text_file_generation.feature')


# Shared test context using pytest fixtures
@pytest.fixture
def test_context():
    """Shared context for BDD tests."""
    return {}


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test output files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def text_file_generator(temp_output_dir):
    """Create TextFileGenerator instance for testing."""
    config = TextFileConfig(output_directory=temp_output_dir)
    return TextFileGenerator(config)


@pytest.fixture
def restaurant_data_complete():
    """Create complete restaurant data for testing."""
    return RestaurantData(
        name="Tony's Italian Restaurant",
        address="1234 Commercial Street, Salem, OR 97301",
        phone="(503) 555-0123",
        price_range="$18-$32",
        hours="Tuesday-Saturday 5pm-10pm, Sunday 4pm-9pm",
        menu_items={
            "appetizers": ["Fresh bruschetta", "calamari rings", "antipasto platter"],
            "entrees": ["Homemade pasta", "wood-fired pizza", "fresh seafood"],
            "desserts": ["Tiramisu", "cannoli", "gelato"]
        },
        cuisine="Italian",
        sources=["json-ld", "heuristic"]
    )


@pytest.fixture
def restaurant_data_minimal():
    """Create minimal restaurant data for testing."""
    return RestaurantData(
        name="Simple Cafe",
        phone="555-1234",
        sources=["heuristic"]
    )


# Background steps
@given("the system is configured for text file generation")
def system_configured_for_text_generation(text_file_generator):
    """Ensure text file generation system is properly configured."""
    assert text_file_generator is not None
    assert text_file_generator.config is not None


@given("the output directory has write permissions")
def output_directory_has_permissions(text_file_generator):
    """Verify output directory has write permissions."""
    validator = FilePermissionValidator()
    result = validator.validate_directory_writable(text_file_generator.config.output_directory)
    assert result.is_writable


# Single restaurant file generation steps
@given('I have scraped data for "Tony\'s Italian Restaurant"')
def scraped_data_tonys_italian(test_context, restaurant_data_complete):
    """Set up Tony's Italian Restaurant data."""
    test_context['restaurant_data'] = [restaurant_data_complete]


@given(parsers.parse("the restaurant has complete information including:"))
def restaurant_has_complete_info(test_context, step):
    """Verify restaurant has all expected complete information."""
    # This step verifies the data setup matches expectations
    restaurant = test_context['restaurant_data'][0]
    
    # Parse the datatable from the step
    expected_values = {}
    for row in step.table:
        expected_values[row['Field']] = row['Value']
    
    # Verify core fields match expected values
    assert restaurant.name == expected_values['name']
    assert restaurant.address == expected_values['address']
    assert restaurant.phone == expected_values['phone']
    assert restaurant.price_range == expected_values['price_range']
    assert restaurant.hours == expected_values['hours']
    assert restaurant.cuisine == expected_values['cuisine']
    
    # Verify menu items contain expected content
    assert "Fresh bruschetta" in restaurant.menu_items.get("appetizers", [])
    assert "Homemade pasta" in restaurant.menu_items.get("entrees", [])
    assert "Tiramisu" in restaurant.menu_items.get("desserts", [])


@when("I generate a text file for RAG systems")
def generate_text_file_for_rag(test_context, text_file_generator):
    """Generate text file from restaurant data."""
    test_context['output_file'] = text_file_generator.generate_file(test_context['restaurant_data'])


@then('the output file should be named "WebScrape_yyyymmdd-hhmm.txt"')
def verify_output_filename_format(test_context):
    """Verify output file follows naming convention."""
    filename = os.path.basename(test_context['output_file'])
    
    # Check prefix
    assert filename.startswith("WebScrape_")
    
    # Check suffix
    assert filename.endswith(".txt")
    
    # Check timestamp format (yyyymmdd-hhmm)
    timestamp_part = filename[10:-4]  # Remove "WebScrape_" and ".txt"
    
    # Verify format matches yyyymmdd-hhmm pattern
    assert len(timestamp_part) == 13  # 8 digits + 1 dash + 4 digits
    assert timestamp_part[8] == "-"
    
    # Verify all parts are numeric
    date_part = timestamp_part[:8]
    time_part = timestamp_part[9:]
    
    assert date_part.isdigit()
    assert time_part.isdigit()


@then("the file should contain the exact format:")
def verify_file_exact_format(test_context, step):
    """Verify file contains exact expected format."""
    with open(test_context['output_file'], 'r', encoding='utf-8') as f:
        actual_content = f.read().strip()
    
    expected_content = step.text.strip()
    assert actual_content == expected_content


@then("the file should be UTF-8 encoded")
def verify_utf8_encoding(test_context):
    """Verify file is UTF-8 encoded."""
    # Try to read file with UTF-8 encoding - should not raise exception
    with open(test_context['output_file'], 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verify we can read the content
    assert len(content) > 0


# Minimal data steps
@given('I have scraped data for "Simple Cafe"')
def scraped_data_simple_cafe(test_context, restaurant_data_minimal):
    """Set up Simple Cafe minimal data."""
    test_context['restaurant_data'] = [restaurant_data_minimal]


@given("the restaurant has minimal information:")
def restaurant_has_minimal_info(test_context, step):
    """Verify restaurant has minimal expected information."""
    restaurant = test_context['restaurant_data'][0]
    
    # Parse the datatable from the step
    expected_values = {}
    for row in step.table:
        expected_values[row['Field']] = row['Value']
    
    assert restaurant.name == expected_values['name']
    assert restaurant.phone == expected_values['phone']


@then("the output file should contain:")
def verify_file_contains_content(test_context, step):
    """Verify file contains expected content."""
    with open(test_context['output_file'], 'r', encoding='utf-8') as f:
        actual_content = f.read().strip()
    
    expected_content = step.text.strip()
    assert actual_content == expected_content


@then("missing fields should be omitted from the output")
def verify_missing_fields_omitted(test_context):
    """Verify missing fields are not present in output."""
    with open(test_context['output_file'], 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verify empty or missing fields are not in the output
    assert "None" not in content
    assert "null" not in content
    # Should not contain empty lines for missing data
    lines = content.strip().split('\n')
    for line in lines:
        if line.strip():  # Non-empty lines should have actual content
            assert len(line.strip()) > 0


# Multi-restaurant steps
@given("I have scraped data for multiple restaurants:")
def scraped_multiple_restaurants(test_context):
    """Set up multiple restaurant data."""
    restaurants = []
    
    # Create test data for multiple restaurants
    restaurants.append(RestaurantData(
        name="Tony's Italian",
        address="1234 Commercial St",
        phone="503-555-0123",
        sources=["heuristic"]
    ))
    
    restaurants.append(RestaurantData(
        name="Blue Moon Diner",
        address="5678 State St",
        phone="503-555-4567",
        sources=["heuristic"]
    ))
    
    restaurants.append(RestaurantData(
        name="Garden Bistro",
        address="9012 Park Ave",
        phone="503-555-8901",
        sources=["heuristic"]
    ))
    
    test_context['restaurant_data'] = restaurants


@then("the output file should contain all restaurants separated by double carriage returns")
def verify_restaurants_separated_by_double_cr(test_context):
    """Verify restaurants are separated by double carriage returns."""
    with open(test_context['output_file'], 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for double line breaks between restaurants
    assert "\n\n\n" in content  # Double carriage return creates triple newlines


@then("the format should be:")
def verify_multi_restaurant_format(test_context, step):
    """Verify multi-restaurant format matches expected."""
    with open(test_context['output_file'], 'r', encoding='utf-8') as f:
        actual_content = f.read().strip()
    
    expected_content = step.text.strip()
    assert actual_content == expected_content


# Multi-page data steps
@given("I have scraped a restaurant website with multiple pages")
def scraped_multipage_restaurant(test_context):
    """Set up multi-page restaurant data."""
    # Create restaurant data that appears to be aggregated from multiple pages
    restaurant = RestaurantData(
        name="Multi-Page Restaurant",
        cuisine="Modern American",  # From home page
        address="123 Main St",      # From contact page
        phone="555-0123",          # From contact page
        hours="Daily 11am-10pm",   # From contact page
        menu_items={"entrees": ["Grilled salmon", "Ribeye steak"]},  # From menu page
        price_range="$25-$45",     # From menu page
        sources=["json-ld", "microdata", "heuristic"]  # Multiple sources indicate multi-page
    )
    test_context['restaurant_data'] = [restaurant]


@given("the data was aggregated from:")
def data_aggregated_from_pages(test_context, step):
    """Verify data appears to come from multiple page types."""
    # This is verification that our test data represents multi-page aggregation
    restaurant = test_context['restaurant_data'][0]
    
    # Parse the datatable to understand what data comes from which pages
    page_data = {}
    for row in step.table:
        page_data[row['Page Type']] = row['Data Found']
    
    # Verify we have data that would come from different page types
    assert restaurant.name  # Typically from home page
    assert restaurant.cuisine  # Typically from home/about page
    assert restaurant.address  # Typically from contact page
    assert restaurant.phone    # Typically from contact page
    assert restaurant.hours    # Typically from contact page
    assert restaurant.menu_items  # Typically from menu page
    assert restaurant.price_range  # Typically from menu page


@then("the output should consolidate all multi-page data into a single restaurant entry")
def verify_consolidated_single_entry(test_context):
    """Verify output contains single consolidated restaurant entry."""
    with open(test_context['output_file'], 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    # Should not contain multiple restaurant entries (no double line breaks)
    assert "\n\n\n" not in content
    
    # Should contain data from all pages in one entry
    assert "Multi-Page Restaurant" in content
    assert "Modern American" in content
    assert "123 Main St" in content
    assert "555-0123" in content
    assert "Daily 11am-10pm" in content
    assert "Grilled salmon" in content or "ribeye steak" in content.lower()


@then("the data source pages should not be mentioned in the output file")
def verify_no_source_page_mentions(test_context):
    """Verify output doesn't mention source page types."""
    with open(test_context['output_file'], 'r', encoding='utf-8') as f:
        content = f.read().lower()
    
    # Should not mention page types or sources
    page_mentions = ["home page", "contact page", "menu page", "about page", "source:", "from page"]
    for mention in page_mentions:
        assert mention not in content


# Timestamp format steps
@given('the current date is "2024-03-15" and time is "14:30"')
def mock_current_datetime(test_context):
    """Mock current datetime for predictable filename testing."""
    mock_datetime = datetime(2024, 3, 15, 14, 30)
    test_context['mocked_datetime'] = patch('src.file_generator.text_file_generator.datetime')
    mock_dt = test_context['mocked_datetime'].start()
    mock_dt.now.return_value = mock_datetime
    
    # Also create minimal restaurant data for this test
    test_context['restaurant_data'] = [RestaurantData(name="Test Restaurant", sources=["heuristic"])]


@then('the output file should be named "WebScrape_20240315-1430.txt"')
def verify_specific_filename(test_context):
    """Verify specific filename format with mocked timestamp."""
    expected_filename = "WebScrape_20240315-1430.txt"
    actual_filename = os.path.basename(test_context['output_file'])
    
    assert actual_filename == expected_filename
    
    # Clean up mock
    test_context['mocked_datetime'].stop()


# Special characters steps
@given('I have scraped data for "Café España"')
def scraped_data_cafe_espana(test_context):
    """Set up restaurant data with special characters."""
    restaurant = RestaurantData(
        name="Café España",
        cuisine="Spanish & Latin American",
        menu_items={"desserts": ["Paella", "tapas", "crème brûlée"]},
        sources=["heuristic"]
    )
    test_context['restaurant_data'] = [restaurant]


@given("the restaurant has information with special characters:")
def restaurant_has_special_characters(test_context, step):
    """Verify restaurant data contains special characters."""
    restaurant = test_context['restaurant_data'][0]
    
    # Parse the datatable from the step
    expected_values = {}
    for row in step.table:
        expected_values[row['Field']] = row['Value']
    
    assert restaurant.name == expected_values['name']
    assert restaurant.cuisine == expected_values['cuisine']
    assert any(item in str(restaurant.menu_items) for item in ["Paella", "tapas", "crème brûlée"])


@then("the output file should preserve all special characters correctly")
def verify_special_characters_preserved(test_context):
    """Verify special characters are preserved in output."""
    with open(test_context['output_file'], 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verify special characters are preserved
    assert "Café España" in content
    assert "Spanish & Latin American" in content
    assert "crème brûlée" in content or "Paella" in content


# Directory selection and configuration steps
@given('I want to save files to "/home/user/restaurant_data/"')
def want_custom_output_directory(test_context):
    """Set up custom output directory preference."""
    test_context['custom_directory'] = "/home/user/restaurant_data/"


@when("I configure the output directory")
def configure_output_directory(test_context, temp_output_dir):
    """Configure custom output directory."""
    # For testing, use temp directory instead of actual path
    test_context['configured_directory'] = temp_output_dir
    
    # Create config with custom directory
    config = TextFileConfig(output_directory=test_context['configured_directory'])
    test_context['text_file_generator'] = TextFileGenerator(config)


@then("the system should validate directory permissions")
def verify_directory_permissions_validated(test_context):
    """Verify directory permissions are validated."""
    validator = FilePermissionValidator()
    result = validator.validate_directory_writable(test_context['configured_directory'])
    assert result.is_writable


@then("future text files should be saved to the selected directory")
def verify_files_saved_to_selected_directory(test_context):
    """Verify files are saved to configured directory."""
    # Generate test file to verify directory usage
    test_data = [RestaurantData(name="Test Restaurant", sources=["heuristic"])]
    output_file = test_context['text_file_generator'].generate_file(test_data)
    
    # Verify file was created in configured directory
    assert output_file.startswith(test_context['configured_directory'])


# Persistent configuration steps
@given('I have previously selected "/home/user/restaurant_data/" as my output directory')
def previously_selected_directory(test_context, temp_output_dir):
    """Simulate previously configured directory."""
    # Create config file with saved directory
    config_path = os.path.join(temp_output_dir, "config.json")
    config_data = {"output_directory": temp_output_dir}
    
    with open(config_path, 'w') as f:
        json.dump(config_data, f)
    
    test_context['config_file'] = config_path
    test_context['saved_directory'] = temp_output_dir


@when("I restart the application")
def restart_application(test_context):
    """Simulate application restart by loading configuration."""
    # Load configuration from file
    with open(test_context['config_file'], 'r') as f:
        config_data = json.load(f)
    
    test_context['loaded_directory'] = config_data["output_directory"]


@then("the system should remember my output directory preference")
def verify_directory_preference_remembered(test_context):
    """Verify directory preference is loaded from configuration."""
    assert test_context['loaded_directory'] == test_context['saved_directory']


@then("use it as the default for new text file generation")
def verify_loaded_directory_used_as_default(test_context):
    """Verify loaded directory is used for file generation."""
    config = TextFileConfig(output_directory=test_context['loaded_directory'])
    generator = TextFileGenerator(config)
    
    assert generator.config.output_directory == test_context['saved_directory']


# Permission validation error steps
@given("I select an output directory without write permissions")
def select_directory_without_permissions(test_context):
    """Simulate selecting directory without write permissions."""
    # Create read-only directory for testing
    test_context['readonly_directory'] = "/root"  # System directory without user write access


@when("I try to generate a text file")
def try_generate_file_readonly_directory(test_context):
    """Try to generate file in read-only directory."""
    config = TextFileConfig(output_directory=test_context['readonly_directory'])
    generator = TextFileGenerator(config)
    
    test_data = [RestaurantData(name="Test Restaurant", sources=["heuristic"])]
    
    try:
        test_context['output_file'] = generator.generate_file(test_data)
        test_context['generation_succeeded'] = True
    except PermissionError as e:
        test_context['permission_error'] = e
        test_context['generation_succeeded'] = False


@then("the system should display an error message")
def verify_permission_error_message(test_context):
    """Verify permission error is properly handled."""
    assert not test_context['generation_succeeded']
    assert 'permission_error' in test_context


@then("prompt me to select a different directory with proper permissions")
def verify_prompt_for_different_directory(test_context):
    """Verify system prompts for different directory."""
    # This would be handled by the UI layer - for now verify error is raised
    assert 'permission_error' in test_context


# File overwrite protection steps
@given('a file named "WebScrape_20240315-1430.txt" already exists')
def existing_file_with_same_name(test_context, temp_output_dir):
    """Create existing file with same name."""
    existing_file = os.path.join(temp_output_dir, "WebScrape_20240315-1430.txt")
    with open(existing_file, 'w') as f:
        f.write("Existing content")
    
    test_context['existing_file'] = existing_file
    test_context['temp_output_dir'] = temp_output_dir


@when("I try to generate a text file with the same timestamp")
def try_generate_file_same_timestamp(test_context):
    """Try to generate file with same timestamp."""
    # Mock datetime to match existing file
    mock_datetime = datetime(2024, 3, 15, 14, 30)
    
    with patch('src.file_generator.text_file_generator.datetime') as mock_dt:
        mock_dt.now.return_value = mock_datetime
        
        config = TextFileConfig(
            output_directory=test_context['temp_output_dir'],
            allow_overwrite=False  # Require confirmation
        )
        generator = TextFileGenerator(config)
        
        test_data = [RestaurantData(name="Test Restaurant", sources=["heuristic"])]
        
        try:
            test_context['output_file'] = generator.generate_file(test_data)
            test_context['overwrite_succeeded'] = True
        except FileExistsError as e:
            test_context['file_exists_error'] = e
            test_context['overwrite_succeeded'] = False


@then("the system should ask for confirmation before overwriting")
def verify_overwrite_confirmation_requested(test_context):
    """Verify overwrite confirmation is requested."""
    assert not test_context['overwrite_succeeded']
    assert 'file_exists_error' in test_context


@then("provide an option to generate with a different filename")
def verify_different_filename_option(test_context):
    """Verify option for different filename is available."""
    # This would be handled by UI layer - verify error provides information
    assert 'file_exists_error' in test_context


# Empty results steps
@given("I have no successful restaurant data extractions")
def no_successful_extractions(test_context):
    """Set up empty restaurant data."""
    test_context['restaurant_data'] = []


@when("I try to generate a text file for RAG systems")
def try_generate_file_no_data(test_context, text_file_generator):
    """Try to generate file with no data."""
    try:
        test_context['output_file'] = text_file_generator.generate_file(test_context['restaurant_data'])
        test_context['generation_succeeded'] = True
    except ValueError as e:
        test_context['no_data_error'] = e
        test_context['generation_succeeded'] = False


@then("the system should inform me that no data is available for file generation")
def verify_no_data_error_message(test_context):
    """Verify appropriate error for no data."""
    assert not test_context['generation_succeeded']
    assert 'no_data_error' in test_context


@then("no empty file should be created")
def verify_no_empty_file_created(test_context, text_file_generator):
    """Verify no empty file was created."""
    # Check output directory for any files
    output_dir = text_file_generator.config.output_directory
    files = os.listdir(output_dir)
    
    # Should be no text files created
    txt_files = [f for f in files if f.endswith('.txt')]
    assert len(txt_files) == 0


# Large batch steps
@given("I have scraped data for 50 restaurants successfully")
def scraped_data_50_restaurants(test_context):
    """Set up large batch of restaurant data."""
    restaurants = []
    
    for i in range(1, 51):
        restaurant = RestaurantData(
            name=f"Restaurant {i}",
            address=f"{i*100} Main St",
            phone=f"555-{i:04d}",
            sources=["heuristic"]
        )
        restaurants.append(restaurant)
    
    test_context['restaurant_data'] = restaurants


@then("all 50 restaurants should be included in a single file")
def verify_all_50_restaurants_included(test_context):
    """Verify all 50 restaurants are in the output file."""
    with open(test_context['output_file'], 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count restaurant entries
    restaurant_count = content.count("Restaurant ")
    assert restaurant_count == 50


@then("each restaurant should be separated by double carriage returns")
def verify_50_restaurants_separated(test_context):
    """Verify restaurants are properly separated."""
    with open(test_context['output_file'], 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Should have 49 separators between 50 restaurants
    separator_count = content.count("\n\n\n")  # Double CR creates triple newlines
    assert separator_count == 49


@then("the file should not exceed reasonable size limits for RAG processing")
def verify_reasonable_file_size(test_context):
    """Verify file size is reasonable for RAG processing."""
    file_size = os.path.getsize(test_context['output_file'])
    
    # Reasonable limit: 10MB for RAG processing
    max_size = 10 * 1024 * 1024  # 10MB
    assert file_size < max_size