"""Step definitions for file generation integration tests."""
import os
import tempfile
import time
import requests
import json
from pytest_bdd import scenarios, given, when, then, parsers
import pytest

# Load scenarios from the feature file
scenarios("../features/file_generation_integration.feature")


@pytest.fixture
def test_output_directory():
    """Create temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_restaurant_url():
    """Provide a sample URL for testing."""
    return "https://example.com"


@pytest.fixture
def flask_test_client():
    """Create Flask test client."""
    from src.web_interface.app import create_app
    app = create_app(testing=True)
    return app.test_client()


# Given steps
@given("the RAG_Scraper web interface is running")
def web_interface_running(flask_test_client):
    """Verify the web interface is accessible."""
    response = flask_test_client.get("/")
    assert response.status_code == 200


@given("I have a valid restaurant website URL")
def valid_restaurant_url(sample_restaurant_url):
    """Store a valid restaurant URL for testing."""
    # This will be used by subsequent steps
    pass


@given("I have selected text file output format")
def select_text_output_format(test_context):
    """Configure text file output format."""
    test_context["file_format"] = "text"


@given("I have selected PDF file output format")
def select_pdf_output_format(test_context):
    """Configure PDF file output format."""
    test_context["file_format"] = "pdf"


@given("I have selected both text and PDF output formats")
def select_dual_output_format(test_context):
    """Configure dual output format."""
    test_context["file_format"] = "both"


@given("I have entered a restaurant website URL")
def enter_restaurant_url(test_context, sample_restaurant_url):
    """Store restaurant URL in test context."""
    test_context["url"] = sample_restaurant_url


@given("the URL validation shows the URL is valid")
def url_validation_valid(flask_test_client, test_context):
    """Verify URL validation passes."""
    response = flask_test_client.post(
        "/api/validate",
        json={"urls": [test_context["url"]]}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["results"][0]["is_valid"] is True


@given("I have configured output directory and file format")
def configure_output_settings(test_context, test_output_directory):
    """Configure output directory and file format."""
    test_context["output_directory"] = test_output_directory
    if "file_format" not in test_context:
        test_context["file_format"] = "text"


# When steps
@when("I execute the scraping process via the web interface")
def execute_scraping_via_web_interface(flask_test_client, test_context, sample_restaurant_url, test_output_directory):
    """Execute scraping through the web interface."""
    scrape_data = {
        "urls": [sample_restaurant_url],
        "output_dir": test_output_directory,
        "file_mode": "single",
        "file_format": test_context.get("file_format", "text")
    }
    
    response = flask_test_client.post("/api/scrape", json=scrape_data)
    test_context["scrape_response"] = response
    test_context["scrape_data"] = response.get_json() if response.status_code == 200 else None


@when("I execute the scraping process")
def execute_scraping_process(flask_test_client, test_context, sample_restaurant_url, test_output_directory):
    """Execute scraping process."""
    execute_scraping_via_web_interface(flask_test_client, test_context, sample_restaurant_url, test_output_directory)


@when("I start the scraping process")
def start_scraping_process(flask_test_client, test_context):
    """Start the scraping process with configured settings."""
    scrape_data = {
        "urls": [test_context["url"]],
        "output_dir": test_context["output_directory"],
        "file_mode": "single",
        "file_format": test_context.get("file_format", "text")
    }
    
    response = flask_test_client.post("/api/scrape", json=scrape_data)
    test_context["scrape_response"] = response
    test_context["scrape_data"] = response.get_json() if response.status_code == 200 else None


@when("the scraping process completes successfully")
def scraping_completes_successfully(test_context):
    """Verify scraping completed successfully."""
    assert test_context["scrape_response"].status_code == 200
    assert test_context["scrape_data"]["success"] is True


@when("the scraping reports success")
def scraping_reports_success(test_context):
    """Verify scraping reports success."""
    assert test_context["scrape_response"].status_code == 200
    assert test_context["scrape_data"]["success"] is True


@when("no output files are generated")
def no_output_files_generated(test_context):
    """Verify no actual output files exist."""
    output_dir = test_context.get("output_directory", "/tmp")
    text_files = [f for f in os.listdir(output_dir) if f.endswith('.txt') and f.startswith('WebScrape_')]
    pdf_files = [f for f in os.listdir(output_dir) if f.endswith('.pdf') and f.startswith('WebScrape_')]
    
    test_context["actual_text_files"] = text_files
    test_context["actual_pdf_files"] = pdf_files


# Then steps
@then("I should receive a success response")
def should_receive_success_response(test_context):
    """Verify successful response from scraping."""
    assert test_context["scrape_response"].status_code == 200
    assert test_context["scrape_data"]["success"] is True


@then("a text file should be created in the output directory")
def text_file_should_be_created(test_context, test_output_directory):
    """Verify text file was created."""
    # Check for WebScrape_*.txt files in output directory
    text_files = [f for f in os.listdir(test_output_directory) 
                 if f.endswith('.txt') and f.startswith('WebScrape_')]
    
    # THIS IS WHERE THE TEST SHOULD FAIL - no files are actually generated
    assert len(text_files) > 0, f"Expected text file to be created in {test_output_directory}, but found none"
    test_context["generated_text_file"] = os.path.join(test_output_directory, text_files[0])


@then("the text file should contain the scraped restaurant data")
def text_file_should_contain_data(test_context):
    """Verify text file contains scraped data."""
    file_path = test_context["generated_text_file"]
    assert os.path.exists(file_path), f"Text file {file_path} does not exist"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Should contain basic restaurant information
    assert len(content.strip()) > 0, "Text file is empty"


@then("a PDF file should be created in the output directory")
def pdf_file_should_be_created(test_context, test_output_directory):
    """Verify PDF file was created."""
    pdf_files = [f for f in os.listdir(test_output_directory) 
                if f.endswith('.pdf') and f.startswith('WebScrape_')]
    
    # THIS IS WHERE THE TEST SHOULD FAIL - no files are actually generated
    assert len(pdf_files) > 0, f"Expected PDF file to be created in {test_output_directory}, but found none"
    test_context["generated_pdf_file"] = os.path.join(test_output_directory, pdf_files[0])


@then("the PDF file should contain the scraped restaurant data")
def pdf_file_should_contain_data(test_context):
    """Verify PDF file contains scraped data."""
    file_path = test_context["generated_pdf_file"]
    assert os.path.exists(file_path), f"PDF file {file_path} does not exist"
    
    # Verify PDF has content (size > header size)
    file_size = os.path.getsize(file_path)
    assert file_size > 1000, f"PDF file {file_path} is too small ({file_size} bytes)"


@then("both text and PDF files should be created in the output directory")
def both_files_should_be_created(test_context, test_output_directory):
    """Verify both text and PDF files were created."""
    text_files = [f for f in os.listdir(test_output_directory) 
                 if f.endswith('.txt') and f.startswith('WebScrape_')]
    pdf_files = [f for f in os.listdir(test_output_directory) 
                if f.endswith('.pdf') and f.startswith('WebScrape_')]
    
    # BOTH OF THESE SHOULD FAIL - no files are actually generated
    assert len(text_files) > 0, f"Expected text file to be created in {test_output_directory}, but found none"
    assert len(pdf_files) > 0, f"Expected PDF file to be created in {test_output_directory}, but found none"


@then("both files should contain the same restaurant data")
def both_files_should_contain_same_data(test_context):
    """Verify both files contain consistent data."""
    # This step would only run if previous assertions pass
    pass


@then("output files should be automatically generated")
def output_files_should_be_generated(test_context):
    """Verify output files are automatically generated after scraping."""
    output_dir = test_context["output_directory"]
    
    # Check for any WebScrape_* files
    output_files = [f for f in os.listdir(output_dir) 
                   if f.startswith('WebScrape_') and (f.endswith('.txt') or f.endswith('.pdf'))]
    
    # THIS SHOULD FAIL - demonstrating the integration issue
    assert len(output_files) > 0, f"Expected output files to be automatically generated in {output_dir}, but found none"


@then("the files should be accessible at the specified output directory")
def files_should_be_accessible(test_context):
    """Verify files are accessible at output directory."""
    # This step depends on previous assertions passing
    pass


@then("the response should include the actual file paths")
def response_should_include_file_paths(test_context):
    """Verify response includes actual file paths, not just descriptions."""
    scrape_data = test_context["scrape_data"]
    output_files = scrape_data.get("output_files", [])
    
    # THIS SHOULD FAIL - current implementation returns descriptions, not file paths
    for file_info in output_files:
        assert file_info.startswith("/"), f"Expected file path starting with '/', got: {file_info}"
        assert os.path.exists(file_info), f"File path in response does not exist: {file_info}"


@then("the system should detect this inconsistency")
def system_should_detect_inconsistency(test_context):
    """Verify system detects scraping success but missing files."""
    # Current implementation doesn't detect this - this test should fail
    scrape_data = test_context["scrape_data"]
    
    # Check if system detected the inconsistency
    # This should fail because current implementation doesn't check for actual files
    assert "file_generation_error" in scrape_data or scrape_data["success"] is False, \
        "System should detect when scraping succeeds but no files are generated"


@then("return an error indicating file generation failure")
def return_file_generation_error(test_context):
    """Verify error is returned for file generation failure."""
    scrape_data = test_context["scrape_data"]
    
    # This should fail because current implementation doesn't return file generation errors
    assert "error" in scrape_data or "file_generation_error" in scrape_data, \
        "Expected error message about file generation failure"


@pytest.fixture
def test_context():
    """Provide test context for sharing data between steps."""
    return {}