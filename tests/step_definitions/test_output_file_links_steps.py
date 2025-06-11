"""Step definitions for output file links tests."""
import os
import pytest
import requests
from pytest_bdd import scenarios, given, when, then, parsers

# Load scenarios from the feature file
scenarios("../features/output_file_links.feature")


@pytest.fixture
def test_context():
    """Provide test context for sharing data between steps."""
    return {}


@pytest.fixture
def real_restaurant_urls():
    """Provide actual restaurant URLs for testing."""
    return [
        "https://rudyssteakhouse.com",
        "https://ilovewom.com",
        "https://www.mcmenamins.com/thompson-brewery-public-house",
    ]


# Given steps
@given("the RAG_Scraper web interface is running")
def web_interface_running(test_context):
    """Verify the web interface is accessible."""
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        assert response.status_code == 200
        test_context["server_accessible"] = True
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Web interface not running: {e}")


@given("I have completed a successful scraping operation")
def completed_successful_scraping_operation(test_context):
    """Set up context for completed scraping operation."""
    test_context["scraping_completed"] = True


@given(parsers.parse('I have selected "{format_option}" as the file format'))
def selected_file_format(test_context, format_option):
    """Store the selected file format."""
    test_context["selected_format"] = format_option.lower()


@given("I have scraped restaurant data successfully")
def scraped_restaurant_data_successfully(test_context, real_restaurant_urls):
    """Perform actual scraping operation to generate real files."""
    urls = real_restaurant_urls
    format_option = test_context.get("selected_format", "text")

    # Create output directory for test
    output_dir = "/tmp/test_output_links"
    os.makedirs(output_dir, exist_ok=True)
    test_context["output_directory"] = output_dir

    # Make actual scraping request
    scrape_data = {
        "urls": urls,
        "output_dir": output_dir,
        "file_mode": "single",
        "file_format": format_option,
    }

    try:
        response = requests.post(
            "http://localhost:8080/api/scrape", json=scrape_data, timeout=60
        )

        test_context["scrape_response"] = response
        if response.status_code == 200:
            test_context["scrape_data"] = response.json()
        else:
            pytest.fail(f"Scraping failed: {response.status_code} {response.text}")

    except requests.exceptions.RequestException as e:
        pytest.fail(f"Scraping request failed: {e}")


@given("I have generated files from scraping")
def have_generated_files_from_scraping(test_context):
    """Verify files were generated from scraping."""
    scrape_data = test_context.get("scrape_data")
    assert scrape_data is not None, "No scrape data available"
    assert scrape_data.get("success"), "Scraping was not successful"


# When steps
@when("I view the results section")
def view_results_section(test_context):
    """Simulate viewing the results section."""
    scrape_data = test_context.get("scrape_data")
    test_context["output_files"] = scrape_data.get("output_files", [])


@when("I click on a file link in the results section")
def click_file_link_in_results(test_context):
    """Simulate clicking on a file link."""
    output_files = test_context.get("output_files", [])
    if output_files:
        # Test the first file link
        first_file = output_files[0]
        test_context["clicked_file"] = first_file


# Then steps
@then('I should see "Generated files:" section')
def should_see_generated_files_section(test_context):
    """Verify the generated files section is present."""
    scrape_data = test_context.get("scrape_data")
    assert scrape_data is not None, "No scrape data received"

    # This test should FAIL initially - we need to modify the interface to show clickable links
    output_files = scrape_data.get("output_files", [])
    assert (
        len(output_files) > 0
    ), "No output files in response - generated files section should show actual file paths"


@then("I should see clickable links to the text files")
def should_see_clickable_text_file_links(test_context):
    """Verify clickable links to text files are present."""
    output_files = test_context.get("output_files", [])

    # This test should FAIL initially - we need to implement clickable links in the interface
    text_files = [f for f in output_files if f.endswith(".txt")]
    assert len(text_files) > 0, "No text file links found in output"


@then("the links should have proper file names with .txt extension")
def links_should_have_txt_extension(test_context):
    """Verify text file links have .txt extension."""
    output_files = test_context.get("output_files", [])
    text_files = [f for f in output_files if f.endswith(".txt")]

    assert len(text_files) > 0, "No .txt files found"
    for file_path in text_files:
        assert file_path.endswith(
            ".txt"
        ), f"Text file should have .txt extension: {file_path}"


@then("I should see clickable links to the PDF files")
def should_see_clickable_pdf_file_links(test_context):
    """Verify clickable links to PDF files are present."""
    output_files = test_context.get("output_files", [])

    # This test should FAIL initially - we need to implement clickable links in the interface
    pdf_files = [f for f in output_files if f.endswith(".pdf")]
    assert len(pdf_files) > 0, "No PDF file links found in output"


@then("the links should have proper file names with .pdf extension")
def links_should_have_pdf_extension(test_context):
    """Verify PDF file links have .pdf extension."""
    output_files = test_context.get("output_files", [])
    pdf_files = [f for f in output_files if f.endswith(".pdf")]

    assert len(pdf_files) > 0, "No .pdf files found"
    for file_path in pdf_files:
        assert file_path.endswith(
            ".pdf"
        ), f"PDF file should have .pdf extension: {file_path}"


@then("I should see clickable links to both text and PDF files")
def should_see_both_text_and_pdf_links(test_context):
    """Verify clickable links to both file types are present."""
    output_files = test_context.get("output_files", [])

    text_files = [f for f in output_files if f.endswith(".txt")]
    pdf_files = [f for f in output_files if f.endswith(".pdf")]

    assert len(text_files) > 0, "No text file links found"
    assert len(pdf_files) > 0, "No PDF file links found"


@then("the text links should have .txt extension")
def text_links_should_have_txt_extension(test_context):
    """Verify text file links have .txt extension."""
    links_should_have_txt_extension(test_context)


@then("the PDF links should have .pdf extension")
def pdf_links_should_have_pdf_extension(test_context):
    """Verify PDF file links have .pdf extension."""
    links_should_have_pdf_extension(test_context)


@then("the file should be downloadable")
def file_should_be_downloadable(test_context):
    """Verify the file can be downloaded."""
    clicked_file = test_context.get("clicked_file")
    assert clicked_file is not None, "No file was clicked"

    # Test that the file actually exists and can be accessed
    assert os.path.exists(
        clicked_file
    ), f"File should exist and be downloadable: {clicked_file}"


@then("the file should contain the scraped restaurant data")
def file_should_contain_scraped_data(test_context):
    """Verify the file contains actual restaurant data."""
    clicked_file = test_context.get("clicked_file")

    if clicked_file and os.path.exists(clicked_file):
        with open(clicked_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert len(content.strip()) > 0, "File should not be empty"
        # Check for restaurant data indicators
        content_lower = content.lower()
        has_restaurant_data = any(
            keyword in content_lower
            for keyword in ["restaurant", "menu", "food", "address", "phone", "hours"]
        )
        assert has_restaurant_data, "File should contain restaurant data"
