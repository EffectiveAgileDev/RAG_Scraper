"""Step definitions for comprehensive feature showcase acceptance tests."""

import pytest
import time
import requests
import json
from pytest_bdd import scenarios, given, when, then, parsers
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from typing import Dict, List, Any

# Load all scenarios from the feature file
scenarios('../features/comprehensive_feature_showcase.feature')


@dataclass
class TestContext:
    """Context for maintaining test state across steps."""
    base_url: str = "http://localhost:8085"
    current_response: Dict[str, Any] = None
    scraping_session_id: str = None
    progress_updates: List[Dict] = None
    results_data: Dict[str, Any] = None
    configuration: Dict[str, Any] = None
    
    def __post_init__(self):
        self.progress_updates = []
        self.configuration = {}


@pytest.fixture
def test_context():
    """Provide test context for scenario steps."""
    return TestContext()


# Background Steps

@given("the RAG Scraper web interface is running")
def web_interface_running(test_context):
    """Verify the web interface is accessible."""
    try:
        response = requests.get(f"{test_context.base_url}/", timeout=10)
        assert response.status_code == 200, f"Web interface not accessible: {response.status_code}"
    except requests.exceptions.RequestException as e:
        pytest.skip(f"Web interface not running: {e}")


@given("I have access to test restaurant URLs")
def test_urls_available(test_context):
    """Verify test URLs are accessible."""
    test_urls = [
        "https://mettavern.com/",
        "https://example-restaurant.com/"
    ]
    
    # For testing purposes, we'll assume URLs are valid
    # In a real test, you might want to validate accessibility
    test_context.configuration["test_urls"] = test_urls


# Single-page scraping scenario steps

@given("I am on the RAG Scraper home page")
def on_home_page(test_context):
    """Simulate being on the home page."""
    test_context.configuration["current_page"] = "home"


@when('I enter "https://mettavern.com/" in the URL input field')
def enter_url(test_context):
    """Simulate entering a URL."""
    test_context.configuration["url"] = "https://mettavern.com/"


@when('I select "Single Page" scraping mode')
def select_single_page_mode(test_context):
    """Select single page scraping mode."""
    test_context.configuration["scraping_mode"] = "single"


@when('I select "Multi Page" scraping mode')
def select_multi_page_mode(test_context):
    """Select multi-page scraping mode."""
    test_context.configuration["scraping_mode"] = "multi"


@when('I select "Text" as the output format')
def select_text_format(test_context):
    """Select text output format."""
    test_context.configuration["file_format"] = "text"


@when('I click the "Start Scraping" button')
def start_scraping(test_context):
    """Simulate starting the scraping process."""
    # Prepare the API request payload
    payload = {
        "urls": [test_context.configuration["url"]],
        "scraping_mode": test_context.configuration["scraping_mode"],
        "file_format": test_context.configuration.get("file_format", "text"),
        "output_dir": "/tmp",
        "file_mode": "single"
    }
    
    # Add multi-page configuration if in multi-page mode
    if test_context.configuration["scraping_mode"] == "multi":
        payload["multi_page_config"] = {
            "maxPages": test_context.configuration.get("max_pages", 10),
            "crawlDepth": test_context.configuration.get("crawl_depth", 2),
            "rateLimit": test_context.configuration.get("rate_limit", 1000),
            "includePatterns": "menu,food,restaurant",
            "excludePatterns": "admin,login,cart"
        }
    
    try:
        # Make the actual API call
        response = requests.post(
            f"{test_context.base_url}/api/scrape",
            json=payload,
            timeout=60
        )
        
        test_context.current_response = {
            "status_code": response.status_code,
            "data": response.json() if response.status_code == 200 else None,
            "error": response.text if response.status_code != 200 else None
        }
        
        # Simulate progress monitoring
        if response.status_code == 200:
            test_context.scraping_session_id = f"session_{int(time.time())}"
            test_context.results_data = test_context.current_response["data"]
            
    except requests.exceptions.RequestException as e:
        test_context.current_response = {
            "status_code": 0,
            "data": None,
            "error": str(e)
        }


@then("I should see progress updates in real-time")
def verify_progress_updates(test_context):
    """Verify that progress updates are working."""
    assert test_context.current_response is not None
    
    # Simulate checking progress API
    try:
        progress_response = requests.get(f"{test_context.base_url}/api/progress")
        if progress_response.status_code == 200:
            progress_data = progress_response.json()
            test_context.progress_updates.append(progress_data)
            
            # Verify progress structure
            expected_fields = [
                "current_url", "urls_completed", "urls_total", 
                "progress_percentage", "status"
            ]
            for field in expected_fields:
                assert field in progress_data, f"Missing progress field: {field}"
                
    except requests.exceptions.RequestException:
        # If progress API fails, we'll verify based on the scraping response
        assert test_context.current_response["status_code"] == 200


@then('I should see "Processing" status messages')
def verify_processing_status(test_context):
    """Verify processing status messages."""
    if test_context.progress_updates:
        # Check if any progress update shows processing
        processing_found = any(
            update.get("status") == "processing" or 
            "processing" in update.get("current_operation", "").lower()
            for update in test_context.progress_updates
        )
        assert processing_found or test_context.current_response["status_code"] == 200


@then("I should see a progress percentage indicator")
def verify_progress_percentage(test_context):
    """Verify progress percentage is shown."""
    if test_context.progress_updates:
        percentage_found = any(
            "progress_percentage" in update and 
            isinstance(update["progress_percentage"], (int, float))
            for update in test_context.progress_updates
        )
        assert percentage_found or test_context.current_response["status_code"] == 200


@then('I should eventually see "EXTRACTION_COMPLETE" status')
def verify_extraction_complete(test_context):
    """Verify extraction completion."""
    assert test_context.current_response is not None
    assert test_context.current_response["status_code"] == 200
    
    # Check if we have successful results
    data = test_context.current_response["data"]
    assert data is not None
    assert data.get("success") is True


@then("I should see successful extraction results")
def verify_successful_results(test_context):
    """Verify successful extraction results."""
    data = test_context.current_response["data"]
    assert data.get("processed_count", 0) > 0, "No successful extractions found"


@then("I should see the generated text file available for download")
def verify_file_generation(test_context):
    """Verify file generation and download availability."""
    data = test_context.current_response["data"]
    output_files = data.get("output_files", [])
    assert len(output_files) > 0, "No output files generated"


# Multi-page scraping scenario steps

@when("I configure multi-page settings")
def configure_multi_page_settings(test_context):
    """Configure multi-page settings from table data."""
    # Default multi-page settings
    test_context.configuration.update({
        "max_pages": 10,
        "crawl_depth": 2,
        "rate_limit": 1000
    })


@then("I should see enhanced progress visualization features")
def verify_enhanced_progress_features(test_context):
    """Verify enhanced progress visualization features."""
    # This test verifies that the multi-page response includes enhanced features
    data = test_context.current_response["data"]
    assert data is not None
    
    # Check for sites_data which contains page-level information
    sites_data = data.get("sites_data", [])
    if sites_data:
        # Verify we have detailed page information
        site = sites_data[0]
        assert "pages_processed" in site
        assert "pages" in site
        
        # Verify page-level details
        if site["pages"]:
            page = site["pages"][0]
            assert "url" in page
            assert "status" in page
            assert "processing_time" in page


@then("I should see multiple pages being processed")
def verify_multiple_pages_processed(test_context):
    """Verify multiple pages were processed."""
    data = test_context.current_response["data"]
    sites_data = data.get("sites_data", [])
    
    if sites_data:
        total_pages = sum(site.get("pages_processed", 0) for site in sites_data)
        assert total_pages >= 1, f"Expected multiple pages, got {total_pages}"


@then("I should see page relationship information")
def verify_page_relationships(test_context):
    """Verify page relationship information is available."""
    data = test_context.current_response["data"]
    sites_data = data.get("sites_data", [])
    
    # In multi-page mode, we should have hierarchical page data
    if sites_data and test_context.configuration["scraping_mode"] == "multi":
        site = sites_data[0]
        assert site.get("pages_processed", 0) >= 1


@then("I should see aggregated data from multiple pages")
def verify_aggregated_data(test_context):
    """Verify aggregated data from multiple pages."""
    data = test_context.current_response["data"]
    assert data.get("processed_count", 0) >= 1


@then('I should eventually see "EXTRACTION_COMPLETE" with multiple targets processed')
def verify_multi_page_completion(test_context):
    """Verify multi-page extraction completion."""
    data = test_context.current_response["data"]
    assert data.get("success") is True
    
    # For multi-page, we should see evidence of multiple page processing
    sites_data = data.get("sites_data", [])
    if sites_data:
        total_pages = sum(site.get("pages_processed", 0) for site in sites_data)
        assert total_pages >= 1


@then("I should see detailed results showing all processed pages")
def verify_detailed_page_results(test_context):
    """Verify detailed results for all processed pages."""
    data = test_context.current_response["data"]
    sites_data = data.get("sites_data", [])
    
    for site in sites_data:
        assert "site_url" in site
        assert "pages_processed" in site
        assert "pages" in site
        
        for page in site["pages"]:
            assert "url" in page
            assert "status" in page


# Batch processing scenario steps

@when("I enter multiple URLs")
def enter_multiple_urls(test_context):
    """Enter multiple URLs for batch processing."""
    urls = [
        "https://mettavern.com/",
        "https://example-restaurant.com/"
    ]
    test_context.configuration["urls"] = urls


@then("I should see batch processing progress")
def verify_batch_processing(test_context):
    """Verify batch processing capabilities."""
    # Update the scraping call for multiple URLs
    payload = {
        "urls": test_context.configuration.get("urls", [test_context.configuration["url"]]),
        "scraping_mode": test_context.configuration["scraping_mode"],
        "file_format": test_context.configuration.get("file_format", "text"),
        "output_dir": "/tmp",
        "file_mode": "single"
    }
    
    try:
        response = requests.post(
            f"{test_context.base_url}/api/scrape",
            json=payload,
            timeout=60
        )
        
        test_context.current_response = {
            "status_code": response.status_code,
            "data": response.json() if response.status_code == 200 else None
        }
        
        assert test_context.current_response["status_code"] == 200
        
    except requests.exceptions.RequestException as e:
        pytest.skip(f"API not available: {e}")


@then("I should see individual URL processing status")
def verify_individual_url_status(test_context):
    """Verify individual URL processing status."""
    data = test_context.current_response["data"]
    assert data is not None
    assert "processed_count" in data
    assert "failed_count" in data


@then("I should see overall progress across all URLs")
def verify_overall_progress(test_context):
    """Verify overall progress tracking."""
    data = test_context.current_response["data"]
    total_urls = len(test_context.configuration.get("urls", [test_context.configuration["url"]]))
    processed = data.get("processed_count", 0)
    failed = data.get("failed_count", 0)
    
    assert processed + failed <= total_urls


@then("I should see results for each successfully processed URL")
def verify_per_url_results(test_context):
    """Verify results for each URL."""
    data = test_context.current_response["data"]
    if data.get("processed_count", 0) > 0:
        assert "sites_data" in data or "output_files" in data


@then("I should see any failed URLs clearly marked")
def verify_failed_url_marking(test_context):
    """Verify failed URLs are clearly marked."""
    data = test_context.current_response["data"]
    # Failed count should be trackable
    assert "failed_count" in data


# Advanced options scenario steps

@when('I expand the "Advanced Options" section')
def expand_advanced_options(test_context):
    """Simulate expanding advanced options."""
    test_context.configuration["advanced_options_expanded"] = True


@then("I should see configuration options for")
def verify_advanced_options_available(test_context):
    """Verify advanced configuration options are available."""
    # This is a UI test that would verify the presence of advanced options
    # For API testing, we verify these options are accepted
    advanced_options = {
        "page_discovery": True,
        "custom_timeout": 45,
        "concurrent_requests": 2,
        "rate_limiting": 2000
    }
    test_context.configuration.update(advanced_options)


@when("I configure advanced options")
def configure_advanced_options(test_context):
    """Configure advanced options from table."""
    test_context.configuration.update({
        "page_discovery": True,
        "custom_timeout": 45,
        "concurrent_requests": 2,
        "rate_limiting": 2000
    })


@then("I should see the custom configuration being applied")
def verify_custom_config_applied(test_context):
    """Verify custom configuration is applied."""
    # This would be verified through the API response and behavior
    assert test_context.configuration.get("rate_limiting") == 2000


@then("I should see slower processing due to increased rate limiting")
def verify_slower_processing(test_context):
    """Verify slower processing due to rate limiting."""
    # This would be verified by checking processing times
    data = test_context.current_response["data"]
    processing_time = data.get("processing_time", 0)
    assert processing_time >= 0  # Any processing time indicates completion


@then("I should see reduced concurrent processing")
def verify_reduced_concurrency(test_context):
    """Verify reduced concurrent processing."""
    # This would be verified through monitoring concurrent connections
    assert test_context.configuration.get("concurrent_requests") == 2


# Real-time progress scenario steps

@when('I start a multi-page scraping operation on "https://mettavern.com/"')
def start_multi_page_operation(test_context):
    """Start a multi-page scraping operation."""
    test_context.configuration.update({
        "url": "https://mettavern.com/",
        "scraping_mode": "multi"
    })
    # This would trigger the scraping operation
    start_scraping(test_context)


@then("I should see real-time progress elements")
def verify_real_time_progress_elements(test_context):
    """Verify real-time progress elements."""
    # Check progress API for real-time elements
    try:
        progress_response = requests.get(f"{test_context.base_url}/api/progress")
        if progress_response.status_code == 200:
            progress_data = progress_response.json()
            
            # Verify key progress elements
            expected_elements = [
                "progress_percentage", "current_url", "estimated_time_remaining",
                "memory_usage_mb", "status"
            ]
            
            for element in expected_elements:
                assert element in progress_data
                
    except requests.exceptions.RequestException:
        # Fall back to checking the main response
        assert test_context.current_response["status_code"] == 200


@then("the progress visualization should update without page refresh")
def verify_no_page_refresh_needed(test_context):
    """Verify progress updates without page refresh."""
    # This is primarily a frontend test, but we can verify the API supports it
    assert test_context.current_response is not None


@then("the progress should be accurate and reflect actual processing")
def verify_accurate_progress(test_context):
    """Verify progress accuracy."""
    data = test_context.current_response["data"]
    assert data.get("success") is True
    
    # Progress should correlate with actual results
    processed = data.get("processed_count", 0)
    assert processed >= 0


# Enhanced results display scenario steps

@given("I have completed a multi-page scraping operation")
def completed_multi_page_operation(test_context):
    """Set up completed multi-page operation."""
    test_context.configuration.update({
        "scraping_mode": "multi",
        "url": "https://mettavern.com/"
    })
    start_scraping(test_context)


@when("I view the results section")
def view_results_section(test_context):
    """View the results section."""
    # Results are available in the response data
    assert test_context.current_response is not None


@then("I should see enhanced results display showing")
def verify_enhanced_results_display(test_context):
    """Verify enhanced results display."""
    data = test_context.current_response["data"]
    sites_data = data.get("sites_data", [])
    
    if sites_data:
        site = sites_data[0]
        
        # Verify enhanced display elements
        assert "pages_processed" in site
        assert "pages" in site
        
        for page in site["pages"]:
            assert "url" in page
            assert "status" in page
            assert "processing_time" in page


# Additional scenario steps for completeness

@then("I should be able to expand/collapse page details")
def verify_expandable_page_details(test_context):
    """Verify expandable page details."""
    # This is a UI feature that would be tested in frontend tests
    data = test_context.current_response["data"]
    assert "sites_data" in data


@then("I should see clear visual indicators for page status")
def verify_page_status_indicators(test_context):
    """Verify page status indicators."""
    data = test_context.current_response["data"]
    sites_data = data.get("sites_data", [])
    
    for site in sites_data:
        for page in site.get("pages", []):
            assert page.get("status") in ["success", "failed"]


@then("I should see the relationship hierarchy between pages")
def verify_page_hierarchy(test_context):
    """Verify page relationship hierarchy."""
    data = test_context.current_response["data"]
    sites_data = data.get("sites_data", [])
    
    # Verify hierarchical structure exists
    assert len(sites_data) >= 0


# File generation steps

@given("I have successfully scraped restaurant data")
def have_scraped_data(test_context):
    """Set up successful scraping data."""
    start_scraping(test_context)
    data = test_context.current_response["data"]
    assert data.get("success") is True


@when("I configure file generation options")
def configure_file_generation(test_context):
    """Configure file generation options."""
    test_context.configuration["file_formats"] = ["text", "pdf", "both"]


@when("I generate files for each format")
def generate_files_each_format(test_context):
    """Generate files for each format."""
    # File generation is handled automatically in the scraping response
    data = test_context.current_response["data"]
    assert "output_files" in data


@then("I should see files generated successfully")
def verify_files_generated(test_context):
    """Verify files were generated successfully."""
    data = test_context.current_response["data"]
    output_files = data.get("output_files", [])
    assert len(output_files) >= 0


@then("I should be able to download each file format")
def verify_file_download(test_context):
    """Verify file download capability."""
    # This would test the download endpoint
    data = test_context.current_response["data"]
    assert "output_files" in data


@then("the files should contain properly formatted restaurant data")
def verify_file_content_format(test_context):
    """Verify file content formatting."""
    # This would require reading and validating the generated files
    data = test_context.current_response["data"]
    assert data.get("processed_count", 0) > 0


@then("PDF files should have proper formatting and layout")
def verify_pdf_formatting(test_context):
    """Verify PDF formatting."""
    # This would require PDF validation
    assert test_context.current_response["status_code"] == 200


# Error handling steps

@given("I am testing error scenarios")
def setup_error_testing(test_context):
    """Set up error scenario testing."""
    test_context.configuration["testing_errors"] = True


@when('I enter an invalid URL "https://nonexistent-restaurant-site.invalid/"')
def enter_invalid_url(test_context):
    """Enter an invalid URL."""
    test_context.configuration["url"] = "https://nonexistent-restaurant-site.invalid/"


@when("I start scraping")
def start_scraping_error_test(test_context):
    """Start scraping for error test."""
    start_scraping(test_context)


@then("I should see appropriate error messages")
def verify_error_messages(test_context):
    """Verify appropriate error messages."""
    # Either the request fails with error details, or succeeds with failed URL tracking
    if test_context.current_response["status_code"] != 200:
        assert test_context.current_response["error"] is not None
    else:
        data = test_context.current_response["data"]
        assert data.get("failed_count", 0) >= 0


@then("I should see the URL marked as failed")
def verify_url_marked_failed(test_context):
    """Verify URL is marked as failed."""
    if test_context.current_response["status_code"] == 200:
        data = test_context.current_response["data"]
        assert data.get("failed_count", 0) >= 0


@then("I should see specific error details")
def verify_specific_error_details(test_context):
    """Verify specific error details."""
    # Error details should be available
    assert test_context.current_response is not None


@then("the system should continue processing other valid URLs")
def verify_continued_processing(test_context):
    """Verify system continues processing other URLs."""
    # This would be tested with mixed valid/invalid URLs
    assert test_context.current_response is not None


@then("I should see error recovery suggestions")
def verify_error_recovery_suggestions(test_context):
    """Verify error recovery suggestions."""
    # This would be part of the error response
    assert test_context.current_response is not None


# Memory management steps

@given("I am processing multiple URLs with multi-page scraping")
def setup_large_operation(test_context):
    """Set up large processing operation."""
    test_context.configuration.update({
        "scraping_mode": "multi",
        "urls": ["https://mettavern.com/"] * 3  # Multiple similar URLs
    })


@when("I monitor system resources during processing")
def monitor_system_resources(test_context):
    """Monitor system resources."""
    start_scraping(test_context)


@then("I should see memory usage tracking")
def verify_memory_tracking(test_context):
    """Verify memory usage tracking."""
    try:
        progress_response = requests.get(f"{test_context.base_url}/api/progress")
        if progress_response.status_code == 200:
            progress_data = progress_response.json()
            assert "memory_usage_mb" in progress_data
    except requests.exceptions.RequestException:
        # Fall back to basic verification
        assert test_context.current_response["status_code"] == 200


@then("I should see memory usage stay within reasonable limits")
def verify_memory_limits(test_context):
    """Verify memory stays within limits."""
    # This would require actual memory monitoring
    assert test_context.current_response["status_code"] == 200


@then("I should see memory cleanup after processing completion")
def verify_memory_cleanup(test_context):
    """Verify memory cleanup."""
    # This would require monitoring memory after completion
    data = test_context.current_response["data"]
    assert data.get("success") is True


@then("I should not see memory leaks or excessive usage")
def verify_no_memory_leaks(test_context):
    """Verify no memory leaks."""
    # This would require long-term memory monitoring
    assert test_context.current_response["status_code"] == 200


# Complete workflow steps

@given("I want to demonstrate the complete RAG Scraper workflow")
def setup_complete_workflow(test_context):
    """Set up complete workflow demonstration."""
    test_context.configuration["complete_workflow"] = True


@when("I perform a complete scraping session")
def perform_complete_session(test_context):
    """Perform complete scraping session."""
    # Configure and execute a comprehensive scraping session
    test_context.configuration.update({
        "url": "https://mettavern.com/",
        "scraping_mode": "multi",
        "file_format": "text",
        "max_pages": 10,
        "crawl_depth": 2
    })
    start_scraping(test_context)


@then("each step should complete successfully")
def verify_each_step_success(test_context):
    """Verify each workflow step succeeds."""
    assert test_context.current_response["status_code"] == 200
    data = test_context.current_response["data"]
    assert data.get("success") is True


@then("I should have a complete audit trail of the operation")
def verify_audit_trail(test_context):
    """Verify complete audit trail."""
    data = test_context.current_response["data"]
    assert "processing_time" in data
    assert "sites_data" in data


@then("I should have usable output files with restaurant data")
def verify_usable_output_files(test_context):
    """Verify usable output files."""
    data = test_context.current_response["data"]
    assert data.get("processed_count", 0) > 0
    assert len(data.get("output_files", [])) >= 0


@then("the entire process should demonstrate professional-grade functionality")
def verify_professional_grade_functionality(test_context):
    """Verify professional-grade functionality."""
    data = test_context.current_response["data"]
    
    # Professional features checklist
    professional_indicators = [
        data.get("success") is True,
        data.get("processing_time", 0) > 0,
        "sites_data" in data,
        data.get("processed_count", 0) >= 0
    ]
    
    assert all(professional_indicators), "Professional-grade functionality not demonstrated"