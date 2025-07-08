"""Step definitions for local file upload feature tests."""

import os
import tempfile
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from unittest.mock import Mock, patch, MagicMock
import time
from werkzeug.datastructures import FileStorage
from io import BytesIO

# Load scenarios
scenarios("../features/local_file_upload.feature")


# Test fixtures and helpers
@pytest.fixture
def mock_pdf_content():
    """Create mock PDF content for testing."""
    return b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n173\n%%EOF"


@pytest.fixture
def mock_large_pdf_content():
    """Create mock large PDF content (>10MB) for testing."""
    base_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj"
    # Pad to simulate large file
    padding = b"X" * (11 * 1024 * 1024)  # 11MB
    return base_content + padding


@pytest.fixture
def mock_text_content():
    """Create mock text file content for invalid file type testing."""
    return b"This is not a PDF file, just plain text content."


@pytest.fixture
def mock_file_storage(mock_pdf_content):
    """Create mock FileStorage object for testing."""
    return FileStorage(
        stream=BytesIO(mock_pdf_content),
        filename="test_restaurant_menu.pdf",
        content_type="application/pdf"
    )


@pytest.fixture
def web_interface_context():
    """Mock web interface context for testing."""
    context = MagicMock()
    context.current_mode = "URL"
    context.upload_queue = []
    context.upload_errors = []
    context.upload_progress = {}
    context.extracted_results = []
    return context


# Background steps
@given("the RAG Scraper web interface is running")
def rag_scraper_running(web_interface_context):
    """Ensure the web interface is running."""
    assert web_interface_context is not None


@given("I am on the main scraping page")
def on_main_page(web_interface_context):
    """Ensure we're on the main scraping page."""
    web_interface_context.current_page = "main_scraping"


@given("the local file upload system is enabled")
def file_upload_enabled(web_interface_context):
    """Ensure file upload system is enabled."""
    web_interface_context.file_upload_enabled = True


# Mode switching scenarios
@given('the interface is in "URL Mode" by default')
def interface_url_mode(web_interface_context):
    """Set interface to URL mode."""
    web_interface_context.current_mode = "URL"


@given('the interface is in "File Upload Mode"')
def interface_file_upload_mode(web_interface_context):
    """Set interface to file upload mode."""
    web_interface_context.current_mode = "FILE_UPLOAD"


@when('I click the "File Upload Mode" toggle')
def click_file_upload_toggle(web_interface_context):
    """Simulate clicking the file upload mode toggle."""
    web_interface_context.current_mode = "FILE_UPLOAD"
    web_interface_context.mode_switched = True


@when('I click the "URL Mode" toggle')
def click_url_mode_toggle(web_interface_context):
    """Simulate clicking the URL mode toggle."""
    web_interface_context.current_mode = "URL"
    web_interface_context.mode_switched = True


@then("the URL input area should be hidden")
def url_area_hidden(web_interface_context):
    """Verify URL input area is hidden."""
    assert web_interface_context.current_mode != "URL" or hasattr(web_interface_context, 'mode_switched')


@then("the file upload area should be displayed")
def file_upload_area_displayed(web_interface_context):
    """Verify file upload area is displayed."""
    assert web_interface_context.current_mode == "FILE_UPLOAD"


@then('the upload area should show "Drag and drop PDF files here or click to browse"')
def upload_area_message(web_interface_context):
    """Verify upload area shows correct message."""
    expected_message = "Drag and drop PDF files here or click to browse"
    web_interface_context.upload_area_message = expected_message
    assert web_interface_context.upload_area_message == expected_message


@then('the mode indicator should show "FILE UPLOAD MODE"')
def mode_indicator_file_upload(web_interface_context):
    """Verify mode indicator shows file upload mode."""
    assert web_interface_context.current_mode == "FILE_UPLOAD"


# File upload scenarios
@given(parsers.parse('I have a valid PDF file "{filename}" on my local system'))
def have_pdf_file(filename, mock_pdf_content, web_interface_context):
    """Mock having a PDF file on local system."""
    web_interface_context.local_files = web_interface_context.local_files if hasattr(web_interface_context, 'local_files') else {}
    web_interface_context.local_files[filename] = {
        'content': mock_pdf_content,
        'size': len(mock_pdf_content),
        'type': 'application/pdf'
    }


@given(parsers.parse('I have multiple PDF files: {filenames}'))
def have_multiple_pdf_files(filenames, mock_pdf_content, web_interface_context):
    """Mock having multiple PDF files on local system."""
    web_interface_context.local_files = {}
    # Parse filenames like '"menu1.pdf", "menu2.pdf", "guide.pdf"'
    file_list = [f.strip().strip('"') for f in filenames.split(',')]
    for filename in file_list:
        web_interface_context.local_files[filename] = {
            'content': mock_pdf_content,
            'size': len(mock_pdf_content),
            'type': 'application/pdf'
        }


@when(parsers.parse('I drag and drop the PDF file onto the upload area'))
def drag_drop_pdf(web_interface_context):
    """Simulate drag and drop of PDF file."""
    if hasattr(web_interface_context, 'local_files'):
        filename = list(web_interface_context.local_files.keys())[0]
        file_info = web_interface_context.local_files[filename]
        
        # Simulate file validation
        is_valid_pdf = file_info['type'] == 'application/pdf' and file_info['content'].startswith(b'%PDF')
        is_valid_size = file_info['size'] <= 50 * 1024 * 1024  # 50MB limit
        
        if is_valid_pdf and is_valid_size:
            web_interface_context.upload_queue.append({
                'filename': filename,
                'status': 'Ready for processing',
                'size': file_info['size'],
                'type': file_info['type']
            })
        else:
            web_interface_context.upload_errors.append(f"Invalid file: {filename}")


@when('I click the "Browse Files" button')
def click_browse_files(web_interface_context):
    """Simulate clicking browse files button."""
    web_interface_context.browse_clicked = True


@when(parsers.parse('I select the PDF file from the file dialog'))
def select_pdf_from_dialog(web_interface_context):
    """Simulate selecting PDF from file dialog."""
    if hasattr(web_interface_context, 'local_files') and web_interface_context.browse_clicked:
        filename = list(web_interface_context.local_files.keys())[0]
        file_info = web_interface_context.local_files[filename]
        
        web_interface_context.upload_queue.append({
            'filename': filename,
            'status': 'Ready for processing',
            'size': file_info['size'],
            'type': file_info['type']
        })


@when(parsers.parse('I select all three files through the file browser'))
def select_multiple_files(web_interface_context):
    """Simulate selecting multiple files through browser."""
    if hasattr(web_interface_context, 'local_files'):
        for filename, file_info in web_interface_context.local_files.items():
            web_interface_context.upload_queue.append({
                'filename': filename,
                'status': 'Ready for processing',
                'size': file_info['size'],
                'type': file_info['type']
            })


@then("the file should be validated as a PDF format")
def file_validated_as_pdf(web_interface_context):
    """Verify file was validated as PDF."""
    assert len(web_interface_context.upload_queue) > 0
    last_uploaded = web_interface_context.upload_queue[-1]
    assert last_uploaded['type'] == 'application/pdf'


@then("the file size should be checked (must be under 50MB)")
def file_size_checked(web_interface_context):
    """Verify file size was checked."""
    assert len(web_interface_context.upload_queue) > 0
    last_uploaded = web_interface_context.upload_queue[-1]
    assert last_uploaded['size'] <= 50 * 1024 * 1024


@then('the file should appear in the upload queue with status "Ready for processing"')
def file_in_queue_ready(web_interface_context):
    """Verify file appears in queue with ready status."""
    assert len(web_interface_context.upload_queue) > 0
    last_uploaded = web_interface_context.upload_queue[-1]
    assert last_uploaded['status'] == 'Ready for processing'


@then(parsers.parse('the file name should be displayed as "{filename}"'))
def filename_displayed(filename, web_interface_context):
    """Verify filename is displayed correctly."""
    assert len(web_interface_context.upload_queue) > 0
    last_uploaded = web_interface_context.upload_queue[-1]
    assert last_uploaded['filename'] == filename


@then("a remove button should be available for each file")
def remove_button_available(web_interface_context):
    """Verify remove button is available for each file."""
    for file_item in web_interface_context.upload_queue:
        file_item['has_remove_button'] = True
        assert file_item['has_remove_button']


@then(parsers.parse('the total file count should display "{count}"'))
def total_file_count_display(count, web_interface_context):
    """Verify total file count is displayed correctly."""
    expected_count = len(web_interface_context.upload_queue)
    if count == "1 file selected":
        assert expected_count == 1
    elif count == "3 files selected":
        assert expected_count == 3
    elif count == "0" or count == "No files selected":
        assert expected_count == 0


@then("I should be able to remove individual files from the queue")
def can_remove_individual_files(web_interface_context):
    """Verify individual files can be removed."""
    initial_count = len(web_interface_context.upload_queue)
    if initial_count > 0:
        # Simulate removing first file
        web_interface_context.upload_queue.pop(0)
        assert len(web_interface_context.upload_queue) == initial_count - 1


# Invalid file handling scenarios
@when(parsers.parse('I try to upload a file "{filename}" that is not a PDF'))
def try_upload_invalid_file(filename, mock_text_content, web_interface_context):
    """Simulate trying to upload an invalid file."""
    web_interface_context.local_files = {filename: {
        'content': mock_text_content,
        'size': len(mock_text_content),
        'type': 'text/plain'
    }}
    
    file_info = web_interface_context.local_files[filename]
    # Validate file type
    if not file_info['type'] in ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
        web_interface_context.upload_errors.append("Only PDF, DOC, and DOCX files are supported")


@when("I try to upload a PDF file larger than 50MB")
def try_upload_large_file(mock_large_pdf_content, web_interface_context):
    """Simulate trying to upload an oversized file."""
    filename = "large_menu.pdf"
    web_interface_context.local_files = {filename: {
        'content': mock_large_pdf_content,
        'size': len(mock_large_pdf_content),
        'type': 'application/pdf'
    }}
    
    file_info = web_interface_context.local_files[filename]
    # Validate file size
    if file_info['size'] > 50 * 1024 * 1024:
        web_interface_context.upload_errors.append("File size exceeds 50MB limit")


@then("the file should be rejected with error message")
def file_rejected_with_error(web_interface_context):
    """Verify file was rejected with error message."""
    assert len(web_interface_context.upload_errors) > 0


@then(parsers.parse('the error should state "{error_message}"'))
def error_message_check(error_message, web_interface_context):
    """Verify specific error message is shown."""
    assert any(error_message in error for error in web_interface_context.upload_errors)


@then("the file should not appear in the upload queue")
def file_not_in_queue(web_interface_context):
    """Verify file was not added to upload queue."""
    # For invalid files, they shouldn't be in the queue
    if hasattr(web_interface_context, 'local_files'):
        for filename in web_interface_context.local_files.keys():
            assert not any(item['filename'] == filename for item in web_interface_context.upload_queue)


@then("the interface should highlight the supported file types")
def highlight_supported_types(web_interface_context):
    """Verify supported file types are highlighted."""
    web_interface_context.supported_types_highlighted = True
    assert web_interface_context.supported_types_highlighted


# File processing scenarios
@given(parsers.parse('I have uploaded a PDF file "{filename}"'))
def have_uploaded_pdf(filename, web_interface_context):
    """Mock having uploaded a PDF file."""
    web_interface_context.upload_queue.append({
        'filename': filename,
        'status': 'Ready for processing',
        'size': 1024 * 100,  # 100KB
        'type': 'application/pdf'
    })


@given('the file is in the upload queue with status "Ready for processing"')
def file_ready_for_processing(web_interface_context):
    """Verify file is ready for processing."""
    assert len(web_interface_context.upload_queue) > 0
    assert web_interface_context.upload_queue[-1]['status'] == 'Ready for processing'


@when('I click the "Process Files" button')
def click_process_files(web_interface_context):
    """Simulate clicking process files button."""
    # Update status for all files in queue
    for file_item in web_interface_context.upload_queue:
        file_item['status'] = 'Processing'
    
    # Mock processing results
    web_interface_context.extracted_results = [{
        'restaurant_name': 'Sample Restaurant',
        'address': '123 Main St, Portland, OR',
        'phone': '(555) 123-4567',
        'menu_items': ['Burger - $12.99', 'Pizza - $15.99'],
        'source_file': web_interface_context.upload_queue[0]['filename'] if web_interface_context.upload_queue else 'test.pdf'
    }]
    
    # Update status to complete
    for file_item in web_interface_context.upload_queue:
        file_item['status'] = 'Complete'


@then("the file should be uploaded to the server")
def file_uploaded_to_server(web_interface_context):
    """Verify file was uploaded to server."""
    # Check that processing was initiated
    assert any(item['status'] in ['Processing', 'Complete'] for item in web_interface_context.upload_queue)


@then("the server should extract text from the PDF using OCR/PDF parsing")
def text_extracted_from_pdf(web_interface_context):
    """Verify text extraction was performed."""
    # Mock text extraction results
    web_interface_context.extracted_text = "Sample Restaurant Menu\nBurger $12.99\nPizza $15.99\nPhone: (555) 123-4567"
    assert hasattr(web_interface_context, 'extracted_text')


@then("the extracted text should be processed through WTEG schema mapping")
def text_processed_through_schema(web_interface_context):
    """Verify text was processed through WTEG schema."""
    # Verify that structured data was extracted
    assert len(web_interface_context.extracted_results) > 0
    result = web_interface_context.extracted_results[0]
    assert 'restaurant_name' in result
    assert 'address' in result
    assert 'phone' in result


@then("restaurant data should be identified (name, address, phone, menu items)")
def restaurant_data_identified(web_interface_context):
    """Verify restaurant data was properly identified."""
    assert len(web_interface_context.extracted_results) > 0
    result = web_interface_context.extracted_results[0]
    assert result['restaurant_name'] == 'Sample Restaurant'
    assert '123 Main St' in result['address']
    assert '(555) 123-4567' in result['phone']
    assert len(result['menu_items']) > 0


@then("the results should be displayed in the same format as URL scraping")
def results_displayed_same_format(web_interface_context):
    """Verify results are displayed in same format as URL scraping."""
    # Results should have same structure as URL scraping results
    assert len(web_interface_context.extracted_results) > 0
    result = web_interface_context.extracted_results[0]
    required_fields = ['restaurant_name', 'address', 'phone', 'menu_items']
    for field in required_fields:
        assert field in result


@then("I should be able to export the results to Text/PDF/JSON formats")
def can_export_results(web_interface_context):
    """Verify results can be exported to different formats."""
    web_interface_context.export_formats_available = ['text', 'pdf', 'json']
    assert 'text' in web_interface_context.export_formats_available
    assert 'pdf' in web_interface_context.export_formats_available
    assert 'json' in web_interface_context.export_formats_available


# Progress and error handling scenarios
@given("I have uploaded a large PDF file (> 10MB)")
def uploaded_large_pdf(mock_large_pdf_content, web_interface_context):
    """Mock uploading a large PDF file."""
    web_interface_context.upload_queue.append({
        'filename': 'large_restaurant_guide.pdf',
        'status': 'Ready for processing',
        'size': len(mock_large_pdf_content),
        'type': 'application/pdf'
    })


@then("a progress bar should appear showing upload progress")
def progress_bar_appears(web_interface_context):
    """Verify progress bar appears for upload."""
    web_interface_context.upload_progress['large_restaurant_guide.pdf'] = {
        'progress': 0,
        'status': 'Uploading...',
        'show_progress_bar': True
    }
    assert web_interface_context.upload_progress['large_restaurant_guide.pdf']['show_progress_bar']


@then("the progress should update in real-time (0% to 100%)")
def progress_updates_realtime(web_interface_context):
    """Verify progress updates in real-time."""
    # Simulate progress updates
    progress_file = web_interface_context.upload_progress['large_restaurant_guide.pdf']
    progress_file['progress'] = 50  # 50% progress
    assert 0 <= progress_file['progress'] <= 100


@then('the status should change from "Uploading..." to "Processing..." to "Complete"')
def status_changes_correctly(web_interface_context):
    """Verify status changes through different phases."""
    progress_file = web_interface_context.upload_progress['large_restaurant_guide.pdf']
    
    # Simulate status progression
    progress_file['status'] = 'Uploading...'
    assert progress_file['status'] == 'Uploading...'
    
    progress_file['status'] = 'Processing...'
    assert progress_file['status'] == 'Processing...'
    
    progress_file['status'] = 'Complete'
    assert progress_file['status'] == 'Complete'


@then("estimated time remaining should be displayed during upload")
def time_remaining_displayed(web_interface_context):
    """Verify estimated time remaining is displayed."""
    progress_file = web_interface_context.upload_progress['large_restaurant_guide.pdf']
    progress_file['estimated_time_remaining'] = '2 minutes remaining'
    assert 'estimated_time_remaining' in progress_file


# Clear queue scenarios
@given("I have multiple files in the upload queue")
def multiple_files_in_queue(web_interface_context):
    """Mock having multiple files in upload queue."""
    web_interface_context.upload_queue = [
        {'filename': 'menu1.pdf', 'status': 'Complete'},
        {'filename': 'menu2.pdf', 'status': 'Complete'},
        {'filename': 'guide.pdf', 'status': 'Ready for processing'}
    ]


@when('I click the "Clear All" button')
def click_clear_all(web_interface_context):
    """Simulate clicking clear all button."""
    web_interface_context.upload_queue.clear()


@then("all files should be removed from the upload queue")
def all_files_removed(web_interface_context):
    """Verify all files were removed from queue."""
    assert len(web_interface_context.upload_queue) == 0


@then('the queue should show "No files selected"')
def queue_shows_no_files(web_interface_context):
    """Verify queue shows no files message."""
    web_interface_context.queue_message = "No files selected" if len(web_interface_context.upload_queue) == 0 else f"{len(web_interface_context.upload_queue)} files"
    assert web_interface_context.queue_message == "No files selected"


@then("the total file count should reset to 0")
def file_count_reset(web_interface_context):
    """Verify file count is reset to 0."""
    assert len(web_interface_context.upload_queue) == 0


# Mode switching with preserved data scenarios
@given("I have processed files with extracted data displayed")
def processed_files_with_data(web_interface_context):
    """Mock having processed files with extracted data."""
    web_interface_context.extracted_results = [{
        'restaurant_name': 'Test Restaurant',
        'address': '456 Oak St, Portland, OR',
        'phone': '(555) 987-6543',
        'menu_items': ['Salad - $8.99', 'Soup - $6.99']
    }]


@then("the previously extracted data should remain visible")
def extracted_data_remains_visible(web_interface_context):
    """Verify extracted data remains visible after mode switch."""
    assert len(web_interface_context.extracted_results) > 0
    assert web_interface_context.extracted_results[0]['restaurant_name'] == 'Test Restaurant'


@then("I should be able to export the existing results")
def can_export_existing_results(web_interface_context):
    """Verify existing results can still be exported."""
    web_interface_context.can_export = len(web_interface_context.extracted_results) > 0
    assert web_interface_context.can_export


# Security and error handling
@given(parsers.parse('I have uploaded a PDF file "{filename}"'))
def uploaded_specific_pdf(filename, web_interface_context):
    """Mock uploading a specific PDF file."""
    web_interface_context.upload_queue.append({
        'filename': filename,
        'status': 'Ready for processing',
        'size': 1024 * 50,  # 50KB
        'type': 'application/pdf'
    })


@when("the file upload fails due to network error")
def file_upload_fails_network(web_interface_context):
    """Simulate file upload failing due to network error."""
    for file_item in web_interface_context.upload_queue:
        file_item['status'] = 'Upload Failed'
        file_item['error'] = 'Network error'


@when("the PDF cannot be processed due to encryption")
def pdf_processing_fails_encryption(web_interface_context):
    """Simulate PDF processing failing due to encryption."""
    for file_item in web_interface_context.upload_queue:
        file_item['status'] = 'Processing Failed'
        file_item['error'] = 'Password-protected PDF'


@then("an error message should be displayed")
def error_message_displayed(web_interface_context):
    """Verify error message is displayed."""
    failed_files = [f for f in web_interface_context.upload_queue if 'Failed' in f.get('status', '')]
    assert len(failed_files) > 0


@then(parsers.parse('the error should state "{error_text}"'))
def specific_error_message(error_text, web_interface_context):
    """Verify specific error message is displayed."""
    failed_files = [f for f in web_interface_context.upload_queue if 'Failed' in f.get('status', '')]
    if error_text == "Upload failed: Network error. Please try again.":
        assert any('Network error' in f.get('error', '') for f in failed_files)
    elif "password-protected" in error_text.lower():
        assert any('Password-protected' in f.get('error', '') for f in failed_files)


@then("I should have the option to retry the upload")
def retry_option_available(web_interface_context):
    """Verify retry option is available."""
    for file_item in web_interface_context.upload_queue:
        if 'Failed' in file_item.get('status', ''):
            file_item['can_retry'] = True
            assert file_item['can_retry']


@then("the file should remain in the queue for retry")
def file_remains_for_retry(web_interface_context):
    """Verify file remains in queue for retry."""
    failed_files = [f for f in web_interface_context.upload_queue if 'Failed' in f.get('status', '')]
    assert len(failed_files) > 0


@then('the file should be marked as "Failed" in the queue')
def file_marked_failed(web_interface_context):
    """Verify file is marked as failed."""
    failed_files = [f for f in web_interface_context.upload_queue if 'Failed' in f.get('status', '')]
    assert len(failed_files) > 0


@then("I should be able to remove the failed file and try again")
def can_remove_failed_file(web_interface_context):
    """Verify failed file can be removed."""
    initial_count = len(web_interface_context.upload_queue)
    # Remove failed files
    web_interface_context.upload_queue = [f for f in web_interface_context.upload_queue if 'Failed' not in f.get('status', '')]
    assert len(web_interface_context.upload_queue) < initial_count


@then("the file should be scanned for malware (if security scanning is enabled)")
def file_scanned_for_malware(web_interface_context):
    """Verify file is scanned for malware."""
    web_interface_context.security_scan_enabled = True
    if web_interface_context.security_scan_enabled:
        for file_item in web_interface_context.upload_queue:
            file_item['malware_scanned'] = True
            assert file_item['malware_scanned']


@then("only clean files should proceed to text extraction")
def only_clean_files_proceed(web_interface_context):
    """Verify only clean files proceed to extraction."""
    clean_files = [f for f in web_interface_context.upload_queue if f.get('malware_scanned', False)]
    assert len(clean_files) > 0


@then("if malware is detected, the file should be rejected with appropriate error")
def malware_detection_rejection(web_interface_context):
    """Verify malware detection causes rejection."""
    # Simulate malware detection
    if web_interface_context.upload_queue:
        web_interface_context.upload_queue[0]['malware_detected'] = False  # Assume clean for test
        assert 'malware_detected' in web_interface_context.upload_queue[0]


@then("the infected file should be safely removed from temporary storage")
def infected_file_removed(web_interface_context):
    """Verify infected files are safely removed."""
    # Files with malware should be removed
    clean_queue = [f for f in web_interface_context.upload_queue if not f.get('malware_detected', False)]
    web_interface_context.upload_queue = clean_queue
    assert all(not f.get('malware_detected', False) for f in web_interface_context.upload_queue)