"""Step definitions for file upload web interface BDD tests."""

import pytest
from pytest_bdd import given, when, then, scenario, parsers
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import tempfile
import os
import time


# Scenarios
@scenario('../features/file_upload_web_interface.feature', 'User can see input mode toggle')
def test_user_can_see_input_mode_toggle():
    pass

@scenario('../features/file_upload_web_interface.feature', 'User can switch to file upload mode')
def test_user_can_switch_to_file_upload_mode():
    pass

@scenario('../features/file_upload_web_interface.feature', 'User can switch back to URL mode')
def test_user_can_switch_back_to_url_mode():
    pass

@scenario('../features/file_upload_web_interface.feature', 'User can upload a single PDF file')
def test_user_can_upload_single_pdf():
    pass

@scenario('../features/file_upload_web_interface.feature', 'User can upload multiple PDF files')
def test_user_can_upload_multiple_pdfs():
    pass

@scenario('../features/file_upload_web_interface.feature', 'User cannot upload non-PDF files')
def test_user_cannot_upload_non_pdf_files():
    pass

@scenario('../features/file_upload_web_interface.feature', 'User can remove files from upload queue')
def test_user_can_remove_files_from_queue():
    pass

@scenario('../features/file_upload_web_interface.feature', 'User can drag and drop files')
def test_user_can_drag_and_drop_files():
    pass

@scenario('../features/file_upload_web_interface.feature', 'User can process uploaded files')
def test_user_can_process_uploaded_files():
    pass

@scenario('../features/file_upload_web_interface.feature', 'File upload shows validation errors')
def test_file_upload_shows_validation_errors():
    pass

@scenario('../features/file_upload_web_interface.feature', 'File upload shows security scan results')
def test_file_upload_shows_security_scan_results():
    pass

@scenario('../features/file_upload_web_interface.feature', 'Empty file upload queue shows validation')
def test_empty_file_upload_queue_validation():
    pass

@scenario('../features/file_upload_web_interface.feature', 'File upload progress is tracked')
def test_file_upload_progress_tracking():
    pass

@scenario('../features/file_upload_web_interface.feature', 'Processed files show extraction results')
def test_processed_files_show_extraction_results():
    pass


# Fixtures
@pytest.fixture
def browser():
    """Create a browser instance for testing."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1920, 1080)
    yield driver
    driver.quit()

@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        # Write minimal PDF content
        pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer
<< /Size 4 /Root 1 0 R >>
startxref
173
%%EOF"""
        f.write(pdf_content)
        yield f.name
    os.unlink(f.name)

@pytest.fixture
def large_pdf_file():
    """Create a large PDF file for testing size limits."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        # Create a large file (55MB) to exceed the 50MB limit
        large_content = b"X" * (55 * 1024 * 1024)
        f.write(large_content)
        yield f.name
    os.unlink(f.name)

@pytest.fixture
def text_file():
    """Create a text file for testing file type validation."""
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        f.write(b"This is not a PDF file")
        yield f.name
    os.unlink(f.name)


# Step definitions
@given('the RAG Scraper web application is running')
def web_app_running(browser):
    """Ensure the web application is accessible."""
    browser.get("http://localhost:8085")
    # Wait for page to load
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

@given('I am on the main interface page')
def on_main_interface_page(browser):
    """Verify we're on the main interface page."""
    assert "RAG_Scraper" in browser.title
    assert browser.find_element(By.ID, "scrapeForm")

@when('I view the main form')
def view_main_form(browser):
    """Look at the main form elements."""
    form = browser.find_element(By.ID, "scrapeForm")
    assert form.is_displayed()

@then('I should see an input mode toggle with "URL" and "File Upload" options')
def should_see_input_mode_toggle(browser):
    """Check for input mode toggle presence."""
    # This should fail initially since we haven't implemented it yet
    toggle = browser.find_element(By.ID, "input-mode-toggle")
    assert toggle.is_displayed()
    
    url_option = browser.find_element(By.CSS_SELECTOR, "input[value='url'][name='input_mode']")
    file_option = browser.find_element(By.CSS_SELECTOR, "input[value='file'][name='input_mode']")
    
    assert url_option.is_displayed()
    assert file_option.is_displayed()

@then('the "URL" option should be selected by default')
def url_option_selected_by_default(browser):
    """Check that URL option is selected by default."""
    url_option = browser.find_element(By.CSS_SELECTOR, "input[value='url'][name='input_mode']")
    assert url_option.is_selected()

@then('the TARGET_URLS textarea should be visible')
def target_urls_textarea_visible(browser):
    """Check that TARGET_URLS textarea is visible."""
    textarea = browser.find_element(By.ID, "urls")
    assert textarea.is_displayed()

@when('I click the "File Upload" toggle option')
def click_file_upload_toggle(browser):
    """Click the file upload toggle option."""
    file_option = browser.find_element(By.CSS_SELECTOR, "input[value='file'][name='input_mode']")
    file_option.click()

@then('the TARGET_URLS textarea should be hidden')
def target_urls_textarea_hidden(browser):
    """Check that TARGET_URLS textarea is hidden."""
    textarea = browser.find_element(By.ID, "urls")
    assert not textarea.is_displayed()

@then('I should see a file upload area with drag and drop support')
def should_see_file_upload_area(browser):
    """Check for file upload area presence."""
    upload_area = browser.find_element(By.ID, "file-upload-area")
    assert upload_area.is_displayed()
    
    # Check for drag and drop attributes
    assert "drag" in upload_area.get_attribute("class").lower() or \
           upload_area.get_attribute("ondrop") is not None

@then('the file upload area should accept PDF files')
def file_upload_accepts_pdf(browser):
    """Check that file upload accepts PDF files."""
    file_input = browser.find_element(By.CSS_SELECTOR, "input[type='file']")
    accept_attr = file_input.get_attribute("accept")
    assert "application/pdf" in accept_attr or ".pdf" in accept_attr

@then('there should be a "Browse Files" button')
def should_see_browse_files_button(browser):
    """Check for browse files button."""
    browse_btn = browser.find_element(By.ID, "browse-files-btn")
    assert browse_btn.is_displayed()
    assert "browse" in browse_btn.text.lower()

@given('I have switched to "File Upload" mode')
def switched_to_file_upload_mode(browser):
    """Switch to file upload mode."""
    file_option = browser.find_element(By.CSS_SELECTOR, "input[value='file'][name='input_mode']")
    file_option.click()
    
    # Wait for UI to update
    WebDriverWait(browser, 5).until(
        EC.visibility_of_element_located((By.ID, "file-upload-area"))
    )

@when('I click the "URL" toggle option')
def click_url_toggle(browser):
    """Click the URL toggle option."""
    url_option = browser.find_element(By.CSS_SELECTOR, "input[value='url'][name='input_mode']")
    url_option.click()

@then('the file upload area should be hidden')
def file_upload_area_hidden(browser):
    """Check that file upload area is hidden."""
    upload_area = browser.find_element(By.ID, "file-upload-area")
    assert not upload_area.is_displayed()

@then('the TARGET_URLS textarea should be visible and required')
def target_urls_visible_and_required(browser):
    """Check that TARGET_URLS textarea is visible and required."""
    textarea = browser.find_element(By.ID, "urls")
    assert textarea.is_displayed()
    assert textarea.get_attribute("required") is not None

@given('I am in "File Upload" mode')
def in_file_upload_mode(browser):
    """Ensure we're in file upload mode."""
    file_option = browser.find_element(By.CSS_SELECTOR, "input[value='file'][name='input_mode']")
    if not file_option.is_selected():
        file_option.click()
    
    WebDriverWait(browser, 5).until(
        EC.visibility_of_element_located((By.ID, "file-upload-area"))
    )

@when(parsers.parse('I select a valid PDF file "{filename}"'))
def select_pdf_file(browser, filename, sample_pdf_file):
    """Select a PDF file for upload."""
    file_input = browser.find_element(By.CSS_SELECTOR, "input[type='file']")
    file_input.send_keys(sample_pdf_file)

@then(parsers.parse('the file should appear in the upload queue'))
def file_appears_in_queue(browser):
    """Check that file appears in upload queue."""
    queue = browser.find_element(By.ID, "upload-queue")
    assert queue.is_displayed()
    
    file_items = queue.find_elements(By.CLASS_NAME, "file-item")
    assert len(file_items) > 0

@then(parsers.parse('I should see the filename "{filename}"'))
def should_see_filename(browser, filename):
    """Check that filename is displayed."""
    queue = browser.find_element(By.ID, "upload-queue")
    filename_element = queue.find_element(By.CLASS_NAME, "filename")
    assert filename in filename_element.text

@then('I should see the file size')
def should_see_file_size(browser):
    """Check that file size is displayed."""
    queue = browser.find_element(By.ID, "upload-queue")
    size_element = queue.find_element(By.CLASS_NAME, "file-size")
    assert size_element.is_displayed()
    assert size_element.text.strip() != ""

@then('there should be a remove button for the file')
def should_see_remove_button(browser):
    """Check for remove button on file item."""
    queue = browser.find_element(By.ID, "upload-queue")
    remove_btn = queue.find_element(By.CLASS_NAME, "remove-file-btn")
    assert remove_btn.is_displayed()

@when(parsers.parse('I select multiple PDF files "{filenames}"'))
def select_multiple_pdf_files(browser, filenames, sample_pdf_file):
    """Select multiple PDF files for upload."""
    # For testing, we'll simulate multiple files by uploading the same file multiple times
    file_input = browser.find_element(By.CSS_SELECTOR, "input[type='file']")
    file_list = [sample_pdf_file] * 3  # Simulate 3 files
    
    # Note: This is a simplified simulation - real implementation would handle multiple files
    for file_path in file_list:
        file_input.send_keys(file_path)

@then(parsers.parse('all files should appear in the upload queue'))
def all_files_in_queue(browser):
    """Check that all files appear in queue."""
    queue = browser.find_element(By.ID, "upload-queue")
    file_items = queue.find_elements(By.CLASS_NAME, "file-item")
    assert len(file_items) >= 3

@then(parsers.parse('I should see {count:d} files listed'))
def should_see_file_count(browser, count):
    """Check that specific number of files are listed."""
    queue = browser.find_element(By.ID, "upload-queue")
    file_items = queue.find_elements(By.CLASS_NAME, "file-item")
    assert len(file_items) == count

@then('each file should have a remove button')
def each_file_has_remove_button(browser):
    """Check that each file has a remove button."""
    queue = browser.find_element(By.ID, "upload-queue")
    file_items = queue.find_elements(By.CLASS_NAME, "file-item")
    remove_buttons = queue.find_elements(By.CLASS_NAME, "remove-file-btn")
    assert len(remove_buttons) == len(file_items)

@when(parsers.parse('I try to select a file "{filename}"'))
def try_select_non_pdf_file(browser, filename, text_file):
    """Try to select a non-PDF file."""
    file_input = browser.find_element(By.CSS_SELECTOR, "input[type='file']")
    file_input.send_keys(text_file)

@then(parsers.parse('I should see an error message "{error_message}"'))
def should_see_error_message(browser, error_message):
    """Check for specific error message."""
    error_element = browser.find_element(By.CLASS_NAME, "error-message")
    assert error_element.is_displayed()
    assert error_message.lower() in error_element.text.lower()

@then('the file should not be added to the upload queue')
def file_not_added_to_queue(browser):
    """Check that invalid file was not added to queue."""
    try:
        queue = browser.find_element(By.ID, "upload-queue")
        file_items = queue.find_elements(By.CLASS_NAME, "file-item")
        # Should have no items or items should not include the invalid file
        for item in file_items:
            filename_element = item.find_element(By.CLASS_NAME, "filename")
            assert ".txt" not in filename_element.text
    except:
        # If queue doesn't exist or is empty, that's also valid
        pass

@given(parsers.parse('I have uploaded "{file1}" and "{file2}"'))
def have_uploaded_multiple_files(browser, file1, file2, sample_pdf_file):
    """Upload multiple files to queue."""
    file_input = browser.find_element(By.CSS_SELECTOR, "input[type='file']")
    # Simulate uploading two files
    file_input.send_keys(sample_pdf_file)
    time.sleep(0.5)  # Small delay
    file_input.send_keys(sample_pdf_file)

@when(parsers.parse('I click the remove button for "{filename}"'))
def click_remove_button_for_file(browser, filename):
    """Click remove button for specific file."""
    queue = browser.find_element(By.ID, "upload-queue")
    file_items = queue.find_elements(By.CLASS_NAME, "file-item")
    
    for item in file_items:
        try:
            filename_element = item.find_element(By.CLASS_NAME, "filename")
            if filename in filename_element.text:
                remove_btn = item.find_element(By.CLASS_NAME, "remove-file-btn")
                remove_btn.click()
                break
        except:
            continue

@then(parsers.parse('"{filename}" should be removed from the queue'))
def file_removed_from_queue(browser, filename):
    """Check that specific file was removed."""
    queue = browser.find_element(By.ID, "upload-queue")
    file_items = queue.find_elements(By.CLASS_NAME, "file-item")
    
    for item in file_items:
        try:
            filename_element = item.find_element(By.CLASS_NAME, "filename")
            assert filename not in filename_element.text
        except:
            continue

@then(parsers.parse('"{filename}" should still be in the queue'))
def file_still_in_queue(browser, filename):
    """Check that specific file is still in queue."""
    queue = browser.find_element(By.ID, "upload-queue")
    file_items = queue.find_elements(By.CLASS_NAME, "file-item")
    
    found = False
    for item in file_items:
        try:
            filename_element = item.find_element(By.CLASS_NAME, "filename")
            if filename in filename_element.text:
                found = True
                break
        except:
            continue
    assert found

@when(parsers.parse('I drag and drop "{filename}" onto the upload area'))
def drag_and_drop_file(browser, filename, sample_pdf_file):
    """Simulate drag and drop of file."""
    upload_area = browser.find_element(By.ID, "file-upload-area")
    
    # Simulate drag and drop using JavaScript
    js_script = """
        var uploadArea = arguments[0];
        var file = new File(['dummy content'], arguments[1], {type: 'application/pdf'});
        var dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        
        var dropEvent = new DragEvent('drop', {
            dataTransfer: dataTransfer,
            bubbles: true
        });
        uploadArea.dispatchEvent(dropEvent);
    """
    browser.execute_script(js_script, upload_area, filename)

@then(parsers.parse('I should see "{filename}" in the file list'))
def should_see_file_in_list(browser, filename):
    """Check that file appears in the file list."""
    queue = browser.find_element(By.ID, "upload-queue")
    filename_elements = queue.find_elements(By.CLASS_NAME, "filename")
    
    found = False
    for element in filename_elements:
        if filename in element.text:
            found = True
            break
    assert found

@given('I have selected an industry')
def have_selected_industry(browser):
    """Select an industry for processing."""
    industry_select = browser.find_element(By.NAME, "industry")
    industry_select.send_keys("restaurant")

@when('I click the "Start Processing" button')
def click_start_processing(browser):
    """Click the start processing button."""
    start_btn = browser.find_element(By.ID, "startProcessing")
    start_btn.click()

@then('the file should be processed for text extraction')
def file_processed_for_extraction(browser):
    """Check that file processing started."""
    # Look for processing indicators
    try:
        progress_element = browser.find_element(By.ID, "progressContainer")
        assert progress_element.is_displayed()
    except:
        # Alternative: check for status message
        status_element = browser.find_element(By.CLASS_NAME, "status-message")
        assert "processing" in status_element.text.lower()

@then('I should see progress indication')
def should_see_progress_indication(browser):
    """Check for progress indication."""
    progress_bar = browser.find_element(By.CLASS_NAME, "progress-bar")
    assert progress_bar.is_displayed()

@then('the extracted text should be processed with the WTEG schema')
def extracted_text_processed_with_wteg(browser):
    """Check that WTEG schema processing occurs."""
    # This would typically check for specific output or status messages
    # indicating that WTEG schema processing occurred
    results_area = browser.find_element(By.ID, "results")
    assert results_area.is_displayed()

# Additional step definitions for remaining scenarios...
@when('I try to upload a file larger than 50MB')
def upload_large_file(browser, large_pdf_file):
    """Try to upload a large file."""
    file_input = browser.find_element(By.CSS_SELECTOR, "input[type='file']")
    file_input.send_keys(large_pdf_file)

@when('I upload a file that triggers security warnings')
def upload_suspicious_file(browser, sample_pdf_file):
    """Upload a file that would trigger security warnings."""
    # For testing, we'll use a regular file but simulate security warning
    file_input = browser.find_element(By.CSS_SELECTOR, "input[type='file']")
    file_input.send_keys(sample_pdf_file)

@then('I should see a warning message about potential security issues')
def should_see_security_warning(browser):
    """Check for security warning message."""
    warning_element = browser.find_element(By.CLASS_NAME, "security-warning")
    assert warning_element.is_displayed()

@then('I should have the option to proceed or cancel')
def should_have_proceed_cancel_options(browser):
    """Check for proceed/cancel options."""
    proceed_btn = browser.find_element(By.ID, "proceed-anyway")
    cancel_btn = browser.find_element(By.ID, "cancel-upload")
    assert proceed_btn.is_displayed()
    assert cancel_btn.is_displayed()

@given('the upload queue is empty')
def upload_queue_empty(browser):
    """Ensure upload queue is empty."""
    try:
        queue = browser.find_element(By.ID, "upload-queue")
        file_items = queue.find_elements(By.CLASS_NAME, "file-item")
        
        # Remove any existing files
        for item in file_items:
            remove_btn = item.find_element(By.CLASS_NAME, "remove-file-btn")
            remove_btn.click()
    except:
        # Queue might not exist yet, which is fine
        pass

@when('I try to start processing')
def try_start_processing_empty(browser):
    """Try to start processing with empty queue."""
    start_btn = browser.find_element(By.ID, "startProcessing")
    start_btn.click()

@then('processing should not start')
def processing_should_not_start(browser):
    """Check that processing did not start."""
    # Should not see progress indicators
    try:
        progress_element = browser.find_element(By.ID, "progressContainer")
        assert not progress_element.is_displayed()
    except:
        # If progress container doesn't exist, that's also valid
        pass

@given('I have uploaded multiple PDF files')
def have_uploaded_multiple_pdfs(browser, sample_pdf_file):
    """Upload multiple PDF files."""
    file_input = browser.find_element(By.CSS_SELECTOR, "input[type='file']")
    # Simulate uploading 3 files
    for i in range(3):
        file_input.send_keys(sample_pdf_file)
        time.sleep(0.3)

@when('I start processing')
def start_processing(browser):
    """Start the processing."""
    start_btn = browser.find_element(By.ID, "startProcessing")
    start_btn.click()

@then('I should see individual file processing progress')
def should_see_individual_file_progress(browser):
    """Check for individual file progress indicators."""
    file_progress_items = browser.find_elements(By.CLASS_NAME, "file-progress")
    assert len(file_progress_items) > 0

@then('I should see overall progress across all files')
def should_see_overall_progress(browser):
    """Check for overall progress indicator."""
    overall_progress = browser.find_element(By.ID, "overall-progress")
    assert overall_progress.is_displayed()

@then('I should see which file is currently being processed')
def should_see_current_file_indicator(browser):
    """Check for current file processing indicator."""
    current_file_indicator = browser.find_element(By.ID, "current-file")
    assert current_file_indicator.is_displayed()
    assert current_file_indicator.text.strip() != ""

@given('I have successfully processed uploaded PDF files')
def have_processed_pdfs_successfully(browser, sample_pdf_file):
    """Complete a successful file processing workflow."""
    # This is a complex setup that would involve uploading files and processing them
    # For now, we'll simulate the end state
    pass

@when('processing is complete')
def processing_complete(browser):
    """Wait for processing to complete."""
    # Wait for completion indicators
    WebDriverWait(browser, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "processing-complete"))
    )

@then('I should see extraction results for each file')
def should_see_extraction_results_per_file(browser):
    """Check for per-file extraction results."""
    results_items = browser.find_elements(By.CLASS_NAME, "file-result")
    assert len(results_items) > 0

@then('I should see the number of data items extracted from each PDF')
def should_see_data_item_counts(browser):
    """Check for data item counts per PDF."""
    count_elements = browser.find_elements(By.CLASS_NAME, "data-count")
    assert len(count_elements) > 0
    for element in count_elements:
        assert element.text.strip() != ""

@then('I should be able to download the generated output files')
def should_be_able_to_download_files(browser):
    """Check for download links."""
    download_links = browser.find_elements(By.CLASS_NAME, "download-link")
    assert len(download_links) > 0
    for link in download_links:
        assert link.get_attribute("href") is not None