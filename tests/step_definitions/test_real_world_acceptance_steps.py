"""Step definitions for real world restaurant scraping acceptance test."""
import os
import pytest
import requests
from pytest_bdd import scenarios, given, when, then, parsers

# Load scenarios from the feature file
scenarios("../features/real_world_acceptance_test.feature")


@pytest.fixture
def test_context():
    """Provide test context for sharing data between steps."""
    return {}


@pytest.fixture
def real_restaurant_urls():
    """Provide the actual restaurant URLs for testing."""
    return [
        "https://rudyssteakhouse.com",
        "https://ilovewom.com",
        "https://www.mcmenamins.com/thompson-brewery-public-house",
    ]


# Given steps
@given("the RAG_Scraper web interface is running on localhost:8080")
def web_interface_running_on_8080(test_context):
    """Verify the web interface is accessible on port 8080."""
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        assert (
            response.status_code == 200
        ), f"Web interface not accessible: {response.status_code}"
        test_context["server_accessible"] = True
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Web interface not running on localhost:8080: {e}")


@given("I am on the main interface page")
def on_main_interface_page(test_context):
    """Navigate to the main interface page."""
    # Verified by previous step
    assert test_context.get("server_accessible"), "Server must be accessible"


@given("I have entered the real restaurant URLs")
def entered_real_restaurant_urls(test_context, real_restaurant_urls):
    """Store the real restaurant URLs for testing."""
    test_context["urls"] = real_restaurant_urls
    assert (
        len(real_restaurant_urls) == 3
    ), f"Expected 3 URLs, got {len(real_restaurant_urls)}: {real_restaurant_urls}"


@given(parsers.parse('I have set the output directory to "{output_dir}"'))
def set_output_directory(test_context, output_dir):
    """Set the output directory."""
    test_context["output_directory"] = output_dir
    # Ensure directory exists
    os.makedirs(output_dir, exist_ok=True)


@given('I have left file mode as "Single file for all restaurants"')
def set_single_file_mode(test_context):
    """Set file mode to single."""
    test_context["file_mode"] = "single"


@given("I have completed scraping of real restaurant URLs")
def completed_scraping_real_urls(test_context, real_restaurant_urls):
    """Set up context for completed scraping."""
    test_context["urls"] = real_restaurant_urls
    test_context["scraping_completed"] = True


@given("the scraping reports success")
def scraping_reports_success(test_context):
    """Verify scraping reported success."""
    assert test_context.get("scraping_completed"), "Scraping must be completed"


# When steps
@when('I click "Start Scraping"')
def click_start_scraping(test_context):
    """Simulate clicking the start scraping button via API."""
    urls = test_context.get("urls", [])
    output_dir = test_context.get("output_directory", "")
    file_mode = test_context.get("file_mode", "single")

    # Make API request to scrape endpoint
    scrape_data = {"urls": urls, "output_dir": output_dir, "file_mode": file_mode}

    try:
        response = requests.post(
            "http://localhost:8080/api/scrape",
            json=scrape_data,
            timeout=60,  # Allow time for real scraping
        )

        test_context["scrape_response"] = response
        if response.status_code == 200:
            test_context["scrape_data"] = response.json()
        else:
            test_context["scrape_data"] = None
            test_context["error"] = f"HTTP {response.status_code}: {response.text}"

    except requests.exceptions.RequestException as e:
        test_context["error"] = f"Request failed: {e}"
        test_context["scrape_response"] = None
        test_context["scrape_data"] = None


@when("I check the API response for file generation")
def check_api_response_for_file_generation(test_context):
    """Check the API response for file generation details."""
    scrape_data = test_context.get("scrape_data")
    if scrape_data:
        test_context["output_files"] = scrape_data.get("output_files", [])
        test_context["file_generation_warnings"] = scrape_data.get(
            "file_generation_warnings", []
        )


# Then steps
@then('I should see "Scraping Completed Successfully!" message')
def should_see_scraping_success_message(test_context):
    """Verify scraping success message."""
    scrape_data = test_context.get("scrape_data")
    error = test_context.get("error")

    if error:
        pytest.fail(f"Scraping failed with error: {error}")

    assert scrape_data is not None, "No scrape data received"
    assert (
        scrape_data.get("success") is True
    ), f"Scraping was not successful: {scrape_data}"


@then(parsers.parse('I should see "Successfully processed {count:d} restaurant(s)"'))
def should_see_processed_count(test_context, count):
    """Verify the correct number of restaurants were processed."""
    scrape_data = test_context.get("scrape_data")
    assert scrape_data is not None, "No scrape data received"

    processed_count = scrape_data.get("processed_count", 0)
    assert (
        processed_count == count
    ), f"Expected {count} processed restaurants, got {processed_count}"


@then("the Generated files section should show actual file paths")
def generated_files_should_show_file_paths(test_context):
    """Verify generated files section shows actual file paths."""
    scrape_data = test_context.get("scrape_data")
    assert scrape_data is not None, "No scrape data received"

    output_files = scrape_data.get("output_files", [])
    assert len(output_files) > 0, "No output files reported in response"

    # Check that these are actual file paths, not descriptions
    for file_path in output_files:
        assert file_path.startswith(
            "/"
        ), f"Expected file path, got description: {file_path}"
        assert (
            "Extracted data" not in file_path
        ), f"Got description instead of file path: {file_path}"


@then(parsers.parse('files should be created in "{directory}" directory'))
def files_should_be_created_in_directory(test_context, directory):
    """Verify files are created in the specified directory."""
    scrape_data = test_context.get("scrape_data")
    assert scrape_data is not None, "No scrape data received"

    output_files = scrape_data.get("output_files", [])
    assert len(output_files) > 0, f"No files were generated"

    # Check that files exist in the specified directory
    for file_path in output_files:
        assert os.path.exists(file_path), f"File does not exist: {file_path}"
        assert file_path.startswith(
            directory
        ), f"File not in expected directory {directory}: {file_path}"


@then("the files should contain extracted restaurant data")
def files_should_contain_restaurant_data(test_context):
    """Verify files contain actual restaurant data."""
    scrape_data = test_context.get("scrape_data")
    output_files = scrape_data.get("output_files", [])

    for file_path in output_files:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            assert len(content.strip()) > 0, f"File is empty: {file_path}"
            # Check for basic restaurant data indicators
            content_lower = content.lower()
            has_restaurant_data = any(
                keyword in content_lower
                for keyword in [
                    "restaurant",
                    "menu",
                    "food",
                    "address",
                    "phone",
                    "hours",
                ]
            )
            assert (
                has_restaurant_data
            ), f"File does not contain restaurant data: {file_path}"


@then("the response should contain actual file paths not descriptions")
def response_should_contain_file_paths_not_descriptions(test_context):
    """Verify API response contains file paths, not descriptions."""
    output_files = test_context.get("output_files", [])

    # This is the key test - should fail with current implementation
    assert len(output_files) > 0, "No output files in response"

    for file_path in output_files:
        # File paths start with "/" and don't contain descriptive text
        assert file_path.startswith(
            "/"
        ), f"Expected absolute file path, got: {file_path}"
        assert (
            "Extracted data" not in file_path
        ), f"Got description instead of file path: {file_path}"
        assert "restaurants" not in file_path or file_path.endswith(
            (".txt", ".pdf")
        ), f"Suspicious file path: {file_path}"


@then("the output_files array should not be empty")
def output_files_array_should_not_be_empty(test_context):
    """Verify output_files array is not empty."""
    output_files = test_context.get("output_files", [])
    assert len(output_files) > 0, "output_files array should not be empty"


@then("files should physically exist at the reported paths")
def files_should_physically_exist(test_context):
    """Verify files physically exist at reported paths."""
    output_files = test_context.get("output_files", [])

    for file_path in output_files:
        if file_path.startswith("/"):  # Only check actual file paths
            assert os.path.exists(
                file_path
            ), f"File should exist at reported path: {file_path}"
