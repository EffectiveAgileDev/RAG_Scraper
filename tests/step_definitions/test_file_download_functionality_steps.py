"""Step definitions for file download functionality tests."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
from pytest_bdd import given, when, then, scenarios
from flask import Flask
from werkzeug.test import Client

# Import scenarios
scenarios('../features/file_download_functionality.feature')

# Test fixtures and data
@pytest.fixture
def test_files():
    """Create temporary test files for download testing."""
    temp_dir = tempfile.mkdtemp()
    files = {
        'restaurant_data.txt': os.path.join(temp_dir, 'restaurant_data.txt'),
        'restaurant_data.pdf': os.path.join(temp_dir, 'restaurant_data.pdf'), 
        'restaurant_data.json': os.path.join(temp_dir, 'restaurant_data.json')
    }
    
    # Create test files with sample content
    for filename, filepath in files.items():
        with open(filepath, 'w') as f:
            if filename.endswith('.txt'):
                f.write("Sample restaurant data in text format")
            elif filename.endswith('.json'):
                f.write('{"restaurant": "test data"}')
            elif filename.endswith('.pdf'):
                f.write("PDF content placeholder")
    
    yield files
    
    # Cleanup
    for filepath in files.values():
        if os.path.exists(filepath):
            os.remove(filepath)
    os.rmdir(temp_dir)

@pytest.fixture
def extraction_results():
    """Mock extraction results with multiple files."""
    return {
        'success': True,
        'processed_count': 1,
        'output_files': [
            '/output/restaurant_data.txt',
            '/output/restaurant_data.pdf', 
            '/output/restaurant_data.json'
        ]
    }

@pytest.fixture
def web_client():
    """Create test client for web interface."""
    from src.web_interface.app import create_app
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client()

# Step implementations

@given('the web interface is running')
def web_interface_running(web_client):
    """Verify web interface is accessible."""
    response = web_client.get('/')
    assert response.status_code == 200

@given('the user has performed a successful extraction that generated multiple files')
def successful_extraction_with_files(context, extraction_results):
    """Set up context with successful extraction results."""
    context.extraction_results = extraction_results

@given('the extraction process generated the following files:')
def extraction_generated_files(context, table):
    """Set up specific files based on table data."""
    files = []
    for row in table:
        files.append({
            'filename': row['filename'],
            'type': row['type']
        })
    context.generated_files = files

@given('the extraction generated files of different types')
def extraction_different_file_types(context):
    """Set up files of different types."""
    context.file_types = ['txt', 'pdf', 'json']

@given('the extraction generated files')
def extraction_generated_basic_files(context):
    """Set up basic file generation."""
    context.has_files = True

@given('one of the files was deleted from the server')
def file_deleted_from_server(context):
    """Simulate a file being deleted."""
    context.deleted_file = 'restaurant_data.txt'

@given('the extraction process completed')
def extraction_process_completed(context):
    """Mark extraction as completed."""
    context.extraction_completed = True

@given('no files were generated due to processing errors')
def no_files_generated(context):
    """Set up scenario with no files generated."""
    context.generated_files = []
    context.has_files = False

@when('the user views the results page')
def user_views_results_page(context, web_client):
    """Simulate user viewing results page."""
    # Mock the results display
    with patch('src.web_interface.routes.main_routes.showResults') as mock_show:
        context.results_response = web_client.get('/results')

@when('the user clicks on a text file download link')
def user_clicks_text_download(context, web_client):
    """Simulate clicking text file download."""
    context.text_download_response = web_client.get('/api/download/restaurant_data.txt')

@when('the user clicks on a PDF file download link')
def user_clicks_pdf_download(context, web_client):
    """Simulate clicking PDF file download."""
    context.pdf_download_response = web_client.get('/api/download/restaurant_data.pdf')

@when('the user clicks on a JSON file download link')
def user_clicks_json_download(context, web_client):
    """Simulate clicking JSON file download."""
    context.json_download_response = web_client.get('/api/download/restaurant_data.json')

@when('the user tries to download the missing file')
def user_downloads_missing_file(context, web_client):
    """Simulate downloading missing file."""
    missing_file = getattr(context, 'deleted_file', 'missing_file.txt')
    context.missing_file_response = web_client.get(f'/api/download/{missing_file}')

@then('they should see download links for all 3 files')
def should_see_three_download_links(context):
    """Verify 3 download links are present."""
    # This test should FAIL initially since download functionality may not work
    assert hasattr(context, 'download_links')
    assert len(context.download_links) == 3, "Expected 3 download links but got different number"

@then('each download link should be functional')
def download_links_functional(context):
    """Verify all download links work."""
    # This test should FAIL initially  
    for link in getattr(context, 'download_links', []):
        assert link['status'] == 'functional', f"Download link {link['name']} is not functional"

@then('the file should download successfully')
def file_downloads_successfully(context):
    """Verify file download was successful."""
    # Check the most recent download response
    response = getattr(context, 'last_download_response', None)
    assert response is not None, "No download response found"
    assert response.status_code == 200, f"Download failed with status {response.status_code}"

@then('they should see an appropriate error message')
def should_see_error_message(context):
    """Verify error message is displayed."""
    response = getattr(context, 'missing_file_response', None)
    assert response is not None
    assert response.status_code == 404, "Expected 404 for missing file"

@then('the other files should still be downloadable')
def other_files_still_downloadable(context):
    """Verify remaining files can still be downloaded."""
    # This should verify that other files are still accessible
    remaining_files = ['restaurant_data.pdf', 'restaurant_data.json']
    for filename in remaining_files:
        # Simulate download attempt for remaining files
        context.file_available = True  # This should be verified by actual download test

@then('they should see a message indicating no files are available for download')
def should_see_no_files_message(context):
    """Verify no files available message."""
    assert hasattr(context, 'no_files_message')
    assert context.no_files_message == True, "Expected no files message but it was not displayed"

@then('no download links should be displayed')
def no_download_links_displayed(context):
    """Verify no download links are shown."""
    download_links = getattr(context, 'download_links', [])
    assert len(download_links) == 0, f"Expected no download links but found {len(download_links)}"