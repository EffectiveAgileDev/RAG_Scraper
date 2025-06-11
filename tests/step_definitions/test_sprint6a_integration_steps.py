"""Step definitions for Sprint 6-A integration tests."""
import os
import pytest
import requests
import time
from pytest_bdd import scenarios, given, when, then, parsers

# Load scenarios from the feature file
scenarios("../features/sprint6a_integration.feature")


@pytest.fixture
def test_context():
    """Provide test context for sharing data between steps."""
    return {}


@pytest.fixture
def real_restaurant_urls():
    """Provide actual restaurant URLs for testing."""
    return ["https://rudyssteakhouse.com", "https://ilovewom.com"]


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


@given("I am on the main interface page")
def on_main_interface_page(test_context):
    """Navigate to the main interface page."""
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        test_context["main_page_html"] = response.text
        assert response.status_code == 200
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Cannot access main page: {e}")


@given("I have entered valid restaurant URLs")
def entered_valid_restaurant_urls(test_context, real_restaurant_urls):
    """Store restaurant URLs for testing."""
    test_context["restaurant_urls"] = real_restaurant_urls


@given(parsers.parse('I select "{format_option}" as the file format'))
def select_file_format(test_context, format_option):
    """Store the selected file format."""
    test_context["selected_format"] = format_option.lower()


# When steps
@when("I complete the scraping process")
def complete_scraping_process(test_context):
    """Perform the complete scraping workflow."""
    urls = test_context.get("restaurant_urls", [])
    format_option = test_context.get("selected_format", "text")

    # Use Downloads directory so files are accessible via download endpoint
    import os.path

    output_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    test_context["output_directory"] = output_dir

    # Make scraping request
    scrape_data = {
        "urls": urls,
        "output_dir": output_dir,
        "file_mode": "single",
        "file_format": format_option,
    }

    try:
        response = requests.post(
            "http://localhost:8080/api/scrape",
            json=scrape_data,
            timeout=120,  # Longer timeout for real scraping
        )

        test_context["scrape_response"] = response
        if response.status_code == 200:
            test_context["scrape_data"] = response.json()
        else:
            pytest.fail(f"Scraping failed: {response.status_code} {response.text}")

    except requests.exceptions.RequestException as e:
        pytest.fail(f"Scraping request failed: {e}")


# Then steps
@then('I should see "Scraping Completed Successfully!" message')
def should_see_success_message(test_context):
    """Verify successful completion message."""
    scrape_data = test_context.get("scrape_data")
    assert scrape_data is not None, "No scrape data received"
    assert scrape_data.get(
        "success"
    ), f"Scraping failed: {scrape_data.get('error', 'Unknown error')}"


@then("I should see clickable links to text files")
def should_see_clickable_text_file_links(test_context):
    """Verify clickable links to text files are present."""
    scrape_data = test_context.get("scrape_data")
    output_files = scrape_data.get("output_files", [])

    text_files = [f for f in output_files if f.endswith(".txt")]
    assert len(text_files) > 0, "No text file links found in output"


@then("I should see clickable links to PDF files")
def should_see_clickable_pdf_file_links(test_context):
    """Verify clickable links to PDF files are present."""
    scrape_data = test_context.get("scrape_data")
    output_files = scrape_data.get("output_files", [])

    pdf_files = [f for f in output_files if f.endswith(".pdf")]
    assert len(pdf_files) > 0, "No PDF file links found in output"


@then("I should see clickable links to both text and PDF files")
def should_see_clickable_links_to_both_formats(test_context):
    """Verify clickable links to both file types are present."""
    scrape_data = test_context.get("scrape_data")
    output_files = scrape_data.get("output_files", [])

    text_files = [f for f in output_files if f.endswith(".txt")]
    pdf_files = [f for f in output_files if f.endswith(".pdf")]

    assert len(text_files) > 0, "No text file links found"
    assert len(pdf_files) > 0, "No PDF file links found"


@then("the links should work for downloading files")
def links_should_work_for_downloading(test_context):
    """Verify the file links work for downloading."""
    scrape_data = test_context.get("scrape_data")
    output_files = scrape_data.get("output_files", [])

    assert len(output_files) > 0, "No output files to test downloading"

    # Test downloading the first file
    first_file = output_files[0]
    filename = first_file.split("/")[-1]
    download_url = f"http://localhost:8080/api/download/{filename}"

    try:
        response = requests.get(download_url, timeout=10)
        assert (
            response.status_code == 200
        ), f"File download failed: {response.status_code}"
        assert len(response.content) > 0, "Downloaded file is empty"
        test_context["downloaded_content"] = response.content
    except requests.exceptions.RequestException as e:
        pytest.fail(f"File download request failed: {e}")


@then("all links should work for downloading files")
def all_links_should_work_for_downloading(test_context):
    """Verify all file links work for downloading."""
    scrape_data = test_context.get("scrape_data")
    output_files = scrape_data.get("output_files", [])

    assert len(output_files) > 0, "No output files to test downloading"

    for file_path in output_files:
        filename = file_path.split("/")[-1]
        download_url = f"http://localhost:8080/api/download/{filename}"

        try:
            response = requests.get(download_url, timeout=10)
            assert (
                response.status_code == 200
            ), f"File download failed for {filename}: {response.status_code}"
            assert len(response.content) > 0, f"Downloaded file {filename} is empty"
        except requests.exceptions.RequestException as e:
            pytest.fail(f"File download request failed for {filename}: {e}")


@then("the downloaded files should contain restaurant data")
def downloaded_files_should_contain_restaurant_data(test_context):
    """Verify the downloaded files contain actual restaurant data."""
    downloaded_content = test_context.get("downloaded_content")
    scrape_data = test_context.get("scrape_data")
    output_files = scrape_data.get("output_files", [])

    if downloaded_content:
        assert len(downloaded_content) > 0, "Downloaded file should not be empty"

        # Check file type
        if output_files and output_files[0].endswith(".pdf"):
            # For PDF files, check that it's a valid PDF (starts with %PDF)
            if isinstance(downloaded_content, bytes):
                assert downloaded_content.startswith(
                    b"%PDF"
                ), "Should be a valid PDF file"
            else:
                assert downloaded_content.startswith(
                    "%PDF"
                ), "Should be a valid PDF file"
        else:
            # For text files, check content
            if isinstance(downloaded_content, bytes):
                content_str = downloaded_content.decode("utf-8", errors="ignore")
            else:
                content_str = str(downloaded_content)

            assert len(content_str.strip()) > 0, "Downloaded file should not be empty"

            # Check for restaurant data indicators
            content_lower = content_str.lower()
            has_restaurant_data = any(
                keyword in content_lower
                for keyword in [
                    "restaurant",
                    "menu",
                    "food",
                    "address",
                    "phone",
                    "hours",
                    "dining",
                ]
            )
            assert has_restaurant_data, "Downloaded file should contain restaurant data"


@then("all downloaded files should contain restaurant data")
def all_downloaded_files_should_contain_restaurant_data(test_context):
    """Verify all downloaded files contain actual restaurant data."""
    scrape_data = test_context.get("scrape_data")
    output_files = scrape_data.get("output_files", [])

    for file_path in output_files:
        filename = file_path.split("/")[-1]
        download_url = f"http://localhost:8080/api/download/{filename}"

        try:
            response = requests.get(download_url, timeout=10)
            assert len(response.content) > 0, f"File {filename} should not be empty"

            # Check file type and validate accordingly
            if filename.endswith(".pdf"):
                # For PDF files, check that it's a valid PDF (starts with %PDF)
                assert response.content.startswith(
                    b"%PDF"
                ), f"File {filename} should be a valid PDF"
            else:
                # For text files, check content
                content_str = response.content.decode("utf-8", errors="ignore")
                assert (
                    len(content_str.strip()) > 0
                ), f"File {filename} should not be empty"

                # Check for restaurant data indicators
                content_lower = content_str.lower()
                has_restaurant_data = any(
                    keyword in content_lower
                    for keyword in [
                        "restaurant",
                        "menu",
                        "food",
                        "address",
                        "phone",
                        "hours",
                        "dining",
                    ]
                )
                assert (
                    has_restaurant_data
                ), f"File {filename} should contain restaurant data"

        except requests.exceptions.RequestException as e:
            pytest.fail(f"Could not verify content of {filename}: {e}")
