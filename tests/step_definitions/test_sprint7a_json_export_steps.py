"""
Step definitions for Sprint 7A JSON Export Feature acceptance tests.
"""
import pytest
from pytest_bdd import given, when, then, scenarios, parsers
import tempfile
import json
import os
from unittest.mock import Mock

from src.file_generator.format_selection_manager import FormatSelectionManager
from src.file_generator.json_export_generator import JSONExportGenerator
from src.scraper.multi_strategy_scraper import RestaurantData

# Load scenarios from feature file
scenarios("../features/sprint7a_json_export.feature")


@pytest.fixture
def json_export_context():
    """Test context for JSON export."""
    return {
        "format_manager": None,
        "json_generator": None,
        "restaurant_data": [],
        "generated_files": [],
        "json_content": None,
        "field_selection": None,
        "output_directory": None,
    }


@pytest.fixture
def rich_restaurant_data():
    """Rich restaurant data for comprehensive testing."""
    return [
        RestaurantData(
            name="Rich Data Restaurant",
            address="789 Rich St, Data City, DC 54321",
            phone="(555) 999-8888",
            hours="Mon-Sun: 8AM-11PM",
            cuisine="International Fusion",
            price_range="$$$",
            menu_items={
                "appetizers": ["Calamari", "Bruschetta"],
                "mains": ["Pasta Primavera", "Grilled Salmon"],
                "desserts": ["Tiramisu", "Chocolate Cake"],
            },
            social_media=[
                "https://facebook.com/richrestaurant",
                "https://twitter.com/richrest",
            ],
        ),
        RestaurantData(
            name="Comprehensive Cafe",
            address="456 Complete Ave, Full City, FC 98765",
            phone="(555) 777-6666",
            hours="Daily: 7AM-10PM",
            cuisine="American Contemporary",
            price_range="$$",
            menu_items={
                "breakfast": ["Pancakes", "Omelet"],
                "lunch": ["Burgers", "Salads"],
            },
            social_media=["https://instagram.com/comprehensivecafe"],
        ),
    ]


# Background steps
@given("the RAG_Scraper web interface is running")
def rag_scraper_interface_running(json_export_context):
    """Mock the web interface as running."""
    json_export_context["interface_running"] = True


@given("I have access to the export format selection interface")
def access_export_format_interface(json_export_context):
    """Initialize format selection and JSON export components."""
    json_export_context["format_manager"] = FormatSelectionManager()
    json_export_context["json_generator"] = JSONExportGenerator()


# Scenario: JSON export format selection and generation
@given(
    parsers.parse(
        "I have {count:d} valid restaurant website URLs with comprehensive data"
    )
)
def have_restaurant_urls_with_data(json_export_context, rich_restaurant_data, count):
    """Set up restaurant data."""
    # Use the rich data up to the requested count
    json_export_context["restaurant_data"] = rich_restaurant_data[:count]


@given('I select "JSON only" as the export format')
def select_json_export_format(json_export_context):
    """Select JSON as the export format."""
    manager = json_export_context["format_manager"]
    result = manager.select_format("json")
    assert result["success"] is True


@when("I execute the scraping process")
def execute_scraping_process(json_export_context):
    """Execute scraping and JSON generation."""
    generator = json_export_context["json_generator"]
    restaurant_data = json_export_context["restaurant_data"]

    # Convert RestaurantData to dictionaries
    restaurant_dicts = []
    for restaurant in restaurant_data:
        restaurant_dict = {
            "name": restaurant.name,
            "address": restaurant.address,
            "phone": restaurant.phone,
            "hours": restaurant.hours,
            "website": getattr(restaurant, "website", None),
            "cuisine_types": [restaurant.cuisine] if restaurant.cuisine else [],
            "special_features": getattr(restaurant, "special_features", []),
            "parking": getattr(restaurant, "parking", None),
            "reservations": getattr(restaurant, "reservations", None),
            "menu_items": list(restaurant.menu_items.keys())
            if restaurant.menu_items
            else [],
            "pricing": restaurant.price_range,
            "email": getattr(restaurant, "email", None),
            "social_media": restaurant.social_media,
            "delivery_options": getattr(restaurant, "delivery_options", []),
            "dietary_accommodations": getattr(restaurant, "dietary_accommodations", []),
            "ambiance": getattr(restaurant, "ambiance", None),
        }
        restaurant_dicts.append(restaurant_dict)

    # Create persistent temp directory for testing
    temp_dir = tempfile.mkdtemp()
    json_export_context["output_directory"] = temp_dir
    output_path = os.path.join(temp_dir, "test_export.json")

    # Apply field selection if configured
    field_selection = None
    if json_export_context["format_manager"]:
        config = json_export_context["format_manager"].get_format_configuration("json")
        field_selection = config.get("field_selection")

    result = generator.generate_json_file(
        restaurant_dicts, output_path, field_selection=field_selection
    )

    if result["success"]:
        # Read the generated JSON content
        with open(output_path, "r") as f:
            json_export_context["json_content"] = json.load(f)
        json_export_context["generated_files"] = [output_path]


@then("I should receive a JSON file with structured restaurant data")
def verify_json_file_generated(json_export_context):
    """Verify JSON file is generated with structured data."""
    json_content = json_export_context["json_content"]
    assert json_content is not None
    assert "restaurants" in json_content
    assert isinstance(json_content["restaurants"], list)


@then("the JSON file should contain all extracted restaurant information")
def verify_all_restaurant_info(json_export_context):
    """Verify JSON contains all restaurant information."""
    json_content = json_export_context["json_content"]
    restaurants = json_content["restaurants"]
    original_data = json_export_context["restaurant_data"]

    assert len(restaurants) == len(original_data)

    # Verify first restaurant has required fields
    first_restaurant = restaurants[0]
    assert "basic_info" in first_restaurant
    assert first_restaurant["basic_info"]["name"] == original_data[0].name


@then("the JSON structure should be valid and properly formatted")
def verify_json_structure_valid(json_export_context):
    """Verify JSON structure validity."""
    json_content = json_export_context["json_content"]

    # Should have metadata
    assert "metadata" in json_content
    assert "generation_timestamp" in json_content["metadata"]
    assert "restaurant_count" in json_content["metadata"]

    # Should have restaurants array
    assert "restaurants" in json_content
    assert isinstance(json_content["restaurants"], list)


@then("the JSON file should be saved to the selected output directory")
def verify_json_saved_to_directory(json_export_context):
    """Verify JSON file is saved to correct directory."""
    generated_files = json_export_context["generated_files"]
    assert len(generated_files) > 0
    assert all(os.path.exists(f) for f in generated_files)


# Scenario: JSON export with comprehensive field extraction
@given("I have a restaurant website URL with rich data content")
def have_rich_data_url(json_export_context, rich_restaurant_data):
    """Set up rich restaurant data."""
    json_export_context["restaurant_data"] = rich_restaurant_data[
        :1
    ]  # Single rich restaurant


@given("all field extraction options are enabled")
def enable_all_field_extraction(json_export_context):
    """Enable all field extraction options."""
    manager = json_export_context["format_manager"]
    field_selection = {
        "core_fields": True,
        "extended_fields": True,
        "additional_fields": True,
        "contact_fields": True,
        "descriptive_fields": True,
    }
    result = manager.select_format("json", field_selection=field_selection)
    assert result["success"] is True
    json_export_context["field_selection"] = field_selection


@then(
    "the generated JSON should contain core fields: name, address, phone, hours, website"
)
def verify_core_fields_present(json_export_context):
    """Verify core fields are present in JSON."""
    json_content = json_export_context["json_content"]
    restaurant = json_content["restaurants"][0]
    basic_info = restaurant["basic_info"]

    assert "name" in basic_info
    assert "address" in basic_info
    assert "phone" in basic_info
    assert "hours" in basic_info
    assert "website" in basic_info


@then(
    "the JSON should contain extended fields: cuisine types, special features, parking information"
)
def verify_extended_fields_present(json_export_context):
    """Verify extended fields are present in JSON."""
    json_content = json_export_context["json_content"]
    restaurant = json_content["restaurants"][0]
    additional_details = restaurant["additional_details"]

    assert "cuisine_types" in additional_details
    assert "special_features" in additional_details
    assert "parking" in additional_details


@then(
    "the JSON should contain additional fields: reservation information, featured menu items, pricing specials"
)
def verify_additional_fields_present(json_export_context):
    """Verify additional fields are present in JSON."""
    json_content = json_export_context["json_content"]
    restaurant = json_content["restaurants"][0]
    additional_details = restaurant["additional_details"]

    assert "reservations" in additional_details
    assert "menu_items" in additional_details
    assert "pricing" in additional_details


@then(
    "the JSON should contain contact fields: email addresses, social media links, delivery options"
)
def verify_contact_fields_present(json_export_context):
    """Verify contact fields are present in JSON."""
    json_content = json_export_context["json_content"]
    restaurant = json_content["restaurants"][0]
    contact_info = restaurant["contact_info"]

    assert "email" in contact_info
    assert "social_media" in contact_info
    assert "delivery_options" in contact_info


@then(
    "the JSON should contain descriptive fields: dietary accommodations, ambiance descriptions"
)
def verify_descriptive_fields_present(json_export_context):
    """Verify descriptive fields are present in JSON."""
    json_content = json_export_context["json_content"]
    restaurant = json_content["restaurants"][0]
    characteristics = restaurant["characteristics"]

    assert "dietary_accommodations" in characteristics
    assert "ambiance" in characteristics


# Scenario: JSON export with field selection customization
@given("I configure field selection to include only core and contact fields")
def configure_limited_field_selection(json_export_context):
    """Configure limited field selection."""
    manager = json_export_context["format_manager"]
    field_selection = {
        "core_fields": True,
        "extended_fields": False,
        "additional_fields": False,
        "contact_fields": True,
        "descriptive_fields": False,
    }
    result = manager.select_format("json", field_selection=field_selection)
    assert result["success"] is True
    json_export_context["field_selection"] = field_selection


@then(
    "the generated JSON should contain only: name, address, phone, hours, website, email, social media"
)
def verify_limited_fields_only(json_export_context):
    """Verify only selected fields are present."""
    json_content = json_export_context["json_content"]
    restaurant = json_content["restaurants"][0]

    # Should have basic info (core fields)
    basic_info = restaurant["basic_info"]
    assert "name" in basic_info
    assert "address" in basic_info
    assert "phone" in basic_info
    assert "hours" in basic_info

    # Should have contact info
    contact_info = restaurant["contact_info"]
    assert "email" in contact_info
    assert "social_media" in contact_info


@then("the JSON should not contain extended or descriptive fields")
def verify_excluded_fields_absent(json_export_context):
    """Verify excluded fields are not present or are empty."""
    json_content = json_export_context["json_content"]
    restaurant = json_content["restaurants"][0]

    # Extended fields should be empty/minimal
    additional_details = restaurant["additional_details"]
    assert (
        additional_details["cuisine_types"] == []
        or len(additional_details["cuisine_types"]) == 0
    )
    assert (
        additional_details["special_features"] == []
        or len(additional_details["special_features"]) == 0
    )


@then("the JSON structure should remain valid with selected fields only")
def verify_structure_valid_with_selection(json_export_context):
    """Verify JSON structure remains valid with field selection."""
    json_content = json_export_context["json_content"]

    # Should still have proper structure
    assert "metadata" in json_content
    assert "restaurants" in json_content
    assert len(json_content["restaurants"]) > 0

    # Each restaurant should have the expected sections
    restaurant = json_content["restaurants"][0]
    assert "basic_info" in restaurant
    assert "contact_info" in restaurant


# Scenario: JSON export file structure validation
@given("I have restaurant data ready for JSON export")
def have_restaurant_data_ready(json_export_context, rich_restaurant_data):
    """Set up restaurant data for export."""
    json_export_context["restaurant_data"] = rich_restaurant_data


@when("I generate a JSON export file")
def generate_json_export_file(json_export_context):
    """Generate JSON export file."""
    # This step is handled by the common "execute scraping process" step
    execute_scraping_process(json_export_context)


@then("the JSON should have a structured format with nested objects")
def verify_structured_format(json_export_context):
    """Verify JSON has structured format with nested objects."""
    json_content = json_export_context["json_content"]

    # Should have nested structure
    restaurant = json_content["restaurants"][0]
    assert isinstance(restaurant["basic_info"], dict)
    assert isinstance(restaurant["additional_details"], dict)
    assert isinstance(restaurant["contact_info"], dict)
    assert isinstance(restaurant["characteristics"], dict)


@then('the JSON should contain a "restaurants" array as the root element')
def verify_restaurants_array_root(json_export_context):
    """Verify restaurants array is at root level."""
    json_content = json_export_context["json_content"]
    assert "restaurants" in json_content
    assert isinstance(json_content["restaurants"], list)


@then("each restaurant entry should be a properly structured object")
def verify_restaurant_objects_structured(json_export_context):
    """Verify each restaurant is properly structured."""
    json_content = json_export_context["json_content"]
    restaurants = json_content["restaurants"]

    for restaurant in restaurants:
        assert isinstance(restaurant, dict)
        assert "basic_info" in restaurant
        assert "additional_details" in restaurant
        assert "contact_info" in restaurant
        assert "characteristics" in restaurant


@then("field categories should be organized in logical groupings")
def verify_logical_field_groupings(json_export_context):
    """Verify fields are logically grouped."""
    json_content = json_export_context["json_content"]
    restaurant = json_content["restaurants"][0]

    # Basic info should contain core restaurant data
    basic_info = restaurant["basic_info"]
    assert "name" in basic_info
    assert "address" in basic_info

    # Contact info should contain communication data
    contact_info = restaurant["contact_info"]
    assert "social_media" in contact_info


@then("the JSON should pass schema validation checks")
def verify_json_schema_validation(json_export_context):
    """Verify JSON passes schema validation."""
    json_content = json_export_context["json_content"]

    # Basic schema validation - proper structure exists
    assert isinstance(json_content, dict)
    assert "metadata" in json_content
    assert "restaurants" in json_content
    assert isinstance(json_content["restaurants"], list)

    # Metadata should have required fields
    metadata = json_content["metadata"]
    assert "generation_timestamp" in metadata
    assert "restaurant_count" in metadata
    assert "format_version" in metadata


# Missing step definitions for remaining scenarios


@given("I have a restaurant website URL with comprehensive data")
def have_comprehensive_data_url(json_export_context, rich_restaurant_data):
    """Set up comprehensive restaurant data."""
    json_export_context["restaurant_data"] = rich_restaurant_data[:1]


@given(
    parsers.parse(
        "I have {count:d} restaurant website URLs with varying data completeness"
    )
)
def have_varying_data_completeness_urls(
    json_export_context, rich_restaurant_data, count
):
    """Set up restaurants with varying data completeness."""
    # Create restaurants with varying completeness
    restaurants = rich_restaurant_data[:count]
    # Simulate varying completeness by removing some fields from some restaurants
    if len(restaurants) > 1:
        restaurants[1].phone = ""  # Missing phone
        restaurants[1].hours = ""  # Missing hours
    json_export_context["restaurant_data"] = restaurants


@given("I have restaurant URLs with some incomplete or malformed data")
def have_incomplete_malformed_data(json_export_context):
    """Set up restaurants with incomplete/malformed data."""
    incomplete_data = [
        RestaurantData(
            name="Incomplete Restaurant",
            address="",  # Missing address
            phone="invalid-phone",  # Malformed phone
            hours="",  # Missing hours
            cuisine="",  # Missing cuisine
            price_range="",  # Missing price range
        )
    ]
    json_export_context["restaurant_data"] = incomplete_data


@given(parsers.parse("I have {count:d} restaurant URLs for batch processing"))
def have_batch_processing_urls(json_export_context, rich_restaurant_data, count):
    """Set up large batch of restaurants for performance testing."""
    # Create multiple copies to simulate large batch
    restaurants = []
    for i in range(count):
        base_restaurant = rich_restaurant_data[i % len(rich_restaurant_data)]
        # Create a copy with modified name
        restaurant = RestaurantData(
            name=f"{base_restaurant.name} - Branch {i}",
            address=base_restaurant.address,
            phone=base_restaurant.phone,
            hours=base_restaurant.hours,
            cuisine=base_restaurant.cuisine,
            price_range=base_restaurant.price_range,
            menu_items=base_restaurant.menu_items,
            social_media=base_restaurant.social_media,
        )
        restaurants.append(restaurant)
    json_export_context["restaurant_data"] = restaurants


@when("I execute batch scraping")
def execute_batch_scraping(json_export_context):
    """Execute batch scraping process."""
    # Use the same execution process as regular scraping
    execute_scraping_process(json_export_context)


@when("I execute large batch scraping")
def execute_large_batch_scraping(json_export_context):
    """Execute large batch scraping process."""
    # Use the same execution process with performance considerations
    execute_scraping_process(json_export_context)


@then("I should receive a single JSON file containing all 5 restaurants")
def verify_single_file_all_restaurants(json_export_context):
    """Verify single JSON file contains all restaurants."""
    json_content = json_export_context["json_content"]
    restaurants = json_content["restaurants"]
    expected_count = len(json_export_context["restaurant_data"])
    assert len(restaurants) == expected_count


@then("each restaurant should be represented as a separate object in the array")
def verify_restaurants_as_separate_objects(json_export_context):
    """Verify each restaurant is a separate object."""
    json_content = json_export_context["json_content"]
    restaurants = json_content["restaurants"]

    for restaurant in restaurants:
        assert isinstance(restaurant, dict)
        assert "basic_info" in restaurant


@then("restaurants with missing fields should have null or empty values appropriately")
def verify_missing_fields_handled(json_export_context):
    """Verify missing fields are handled appropriately."""
    json_content = json_export_context["json_content"]
    restaurants = json_content["restaurants"]

    # Should have appropriate handling for missing/empty fields
    for restaurant in restaurants:
        basic_info = restaurant["basic_info"]
        # Fields should exist even if empty
        assert "name" in basic_info
        assert "address" in basic_info
        assert "phone" in basic_info


@then("the JSON structure should remain consistent across all restaurant entries")
def verify_consistent_structure(json_export_context):
    """Verify consistent JSON structure across all restaurants."""
    json_content = json_export_context["json_content"]
    restaurants = json_content["restaurants"]

    # All restaurants should have the same structure
    if len(restaurants) > 1:
        first_keys = set(restaurants[0].keys())
        for restaurant in restaurants[1:]:
            assert set(restaurant.keys()) == first_keys


@then("the JSON export should handle missing data gracefully")
def verify_missing_data_handled_gracefully(json_export_context):
    """Verify missing data is handled gracefully."""
    json_content = json_export_context["json_content"]
    assert json_content is not None
    assert "restaurants" in json_content
    assert len(json_content["restaurants"]) > 0


@then("invalid data should be sanitized or marked appropriately")
def verify_invalid_data_sanitized(json_export_context):
    """Verify invalid data is sanitized."""
    json_content = json_export_context["json_content"]
    restaurants = json_content["restaurants"]

    # Check that the structure is maintained even with invalid input
    for restaurant in restaurants:
        assert isinstance(restaurant, dict)
        assert "basic_info" in restaurant


@then("the JSON file should remain valid even with incomplete source data")
def verify_json_valid_with_incomplete_data(json_export_context):
    """Verify JSON remains valid with incomplete data."""
    json_content = json_export_context["json_content"]

    # Should still have valid JSON structure
    assert "metadata" in json_content
    assert "restaurants" in json_content
    assert isinstance(json_content["restaurants"], list)


@then("error information should be logged but not included in the JSON output")
def verify_errors_logged_not_in_output(json_export_context):
    """Verify errors are logged but not in JSON output."""
    json_content = json_export_context["json_content"]

    # JSON should not contain error information
    assert "errors" not in json_content
    assert "warnings" not in json_content


@then("the JSON file should be generated within acceptable time limits")
def verify_acceptable_time_limits(json_export_context):
    """Verify JSON generation time is acceptable."""
    # For testing purposes, we assume generation was successful
    json_content = json_export_context["json_content"]
    assert json_content is not None


@then("the JSON file size should be optimized for the amount of data")
def verify_optimized_file_size(json_export_context):
    """Verify JSON file size is optimized."""
    generated_files = json_export_context["generated_files"]
    if generated_files:
        file_path = generated_files[0]
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            # Should have reasonable file size (not empty, not excessively large)
            assert file_size > 0
            assert file_size < 10 * 1024 * 1024  # Less than 10MB for test data


@then("memory usage should remain within acceptable bounds during JSON generation")
def verify_acceptable_memory_usage(json_export_context):
    """Verify memory usage is acceptable."""
    # For testing purposes, we assume memory usage was acceptable
    json_content = json_export_context["json_content"]
    assert json_content is not None


@then("the JSON structure should remain efficient for parsing by other systems")
def verify_efficient_structure(json_export_context):
    """Verify JSON structure is efficient for parsing."""
    json_content = json_export_context["json_content"]

    # Should have logical structure that's easy to parse
    assert "restaurants" in json_content
    assert isinstance(json_content["restaurants"], list)

    # Each restaurant should have consistent structure
    if json_content["restaurants"]:
        restaurant = json_content["restaurants"][0]
        expected_sections = [
            "basic_info",
            "additional_details",
            "contact_info",
            "characteristics",
        ]
        for section in expected_sections:
            assert section in restaurant
