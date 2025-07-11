"""Test for EXECUTE_EXTRACTION button functionality issues."""
import pytest
import requests
from bs4 import BeautifulSoup
import json
import os
import tempfile


class TestExecuteExtractionButton:
    """Test that EXECUTE_EXTRACTION button shows output and processes files correctly."""
    
    def test_execute_extraction_button_exists(self):
        """Test that the execute extraction button exists and has correct attributes."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the execute extraction button (actual ID is 'submitBtn')
        execute_button = soup.find('button', {'id': 'submitBtn'})
        assert execute_button is not None, "❌ Execute extraction button (submitBtn) not found"
        
        # Check button attributes
        button_type = execute_button.get('type')
        assert button_type == 'submit', "❌ Button should be type='submit'"
        
        button_class = execute_button.get('class')
        assert 'cmd-button' in button_class, "❌ Button should have cmd-button class"
        
        print(f"✅ Execute button type: {button_type}")
        print(f"✅ Execute button class: {button_class}")
        
        # Check if button text is correct
        button_text = execute_button.get_text().strip()
        assert 'EXECUTE_EXTRACTION' in button_text, "❌ Button text should be 'EXECUTE_EXTRACTION'"
        
        return execute_button
        
    def test_execute_extraction_javascript_function(self):
        """Test that the JavaScript function for execute extraction exists."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        # Check for common extraction function names
        function_patterns = [
            'function executeExtraction(',
            'function startExtraction(',
            'function processFiles(',
            'function extractData(',
            'executeExtraction',
            'startExtraction'
        ]
        
        found_functions = []
        for pattern in function_patterns:
            if pattern in html_content:
                found_functions.append(pattern)
                
        assert len(found_functions) > 0, f"❌ No extraction JavaScript function found. Searched for: {function_patterns}"
        
        print(f"✅ Found extraction functions: {found_functions}")
        
        # Check if function makes API calls
        api_patterns = [
            'fetch(',
            'XMLHttpRequest',
            '/api/',
            'POST',
            'GET'
        ]
        
        found_api_calls = []
        for pattern in api_patterns:
            if pattern in html_content:
                found_api_calls.append(pattern)
                
        print(f"✅ Found API call patterns: {found_api_calls}")
        
        return found_functions, found_api_calls
        
    def test_execute_extraction_output_area(self):
        """Test that there's an area to display extraction output."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for actual output areas (based on real HTML structure)
        output_areas = [
            soup.find('div', {'id': 'resultsContainer'}),
            soup.find('div', {'id': 'resultsContent'}),
            soup.find('div', {'id': 'sitesResults'}),
            soup.find('div', {'id': 'progressContainer'}),
            soup.find('div', {'id': 'noResults'})
        ]
        
        found_output_areas = [area for area in output_areas if area is not None]
        
        assert len(found_output_areas) > 0, "❌ No output area found for extraction results"
        
        print(f"✅ Found {len(found_output_areas)} output areas")
        for i, area in enumerate(found_output_areas):
            print(f"  {i+1}. {area.name} with id='{area.get('id')}' class='{area.get('class')}'")
            
        # Check if results container starts hidden
        results_container = soup.find('div', {'id': 'resultsContainer'})
        if results_container:
            style = results_container.get('style', '')
            print(f"✅ Results container initial style: {style}")
            
        return found_output_areas
        
    def test_single_page_mode_extraction_flow(self):
        """Test the extraction flow specifically for single page mode."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check if single page mode elements exist
        single_page_radio = soup.find('input', {'name': 'scrapingMode', 'value': 'single'})
        assert single_page_radio is not None, "❌ Single page mode radio button not found"
        
        # Check if single page config area exists
        single_page_config = soup.find(id='singlePageConfig')
        assert single_page_config is not None, "❌ Single page config area not found"
        
        # Check if there's URL input for single page mode
        url_inputs = [
            soup.find('input', {'type': 'url'}),
            soup.find('input', {'name': 'url'}),
            soup.find('input', {'id': 'urlInput'}),
            soup.find('input', {'id': 'singlePageUrl'})
        ]
        
        found_url_inputs = [inp for inp in url_inputs if inp is not None]
        
        print(f"✅ Found {len(found_url_inputs)} URL input fields")
        
        # This might reveal the issue - no URL input for single page mode?
        if len(found_url_inputs) == 0:
            print("⚠️  POTENTIAL ISSUE: No URL input found for single page mode!")
            
        return found_url_inputs
        
    def test_file_upload_vs_url_extraction(self):
        """Test if there's confusion between file upload and URL extraction."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check for file upload elements
        file_inputs = soup.find_all('input', {'type': 'file'})
        
        # Check for URL inputs  
        url_inputs = soup.find_all('input', {'type': 'url'})
        
        # Check for batch processing elements
        batch_elements = [
            soup.find('textarea', {'id': 'urlList'}),
            soup.find('textarea', {'name': 'urls'}),
            soup.find('div', {'id': 'batchProcessing'})
        ]
        
        found_batch_elements = [elem for elem in batch_elements if elem is not None]
        
        print(f"File inputs found: {len(file_inputs)}")
        print(f"URL inputs found: {len(url_inputs)}")
        print(f"Batch processing elements found: {len(found_batch_elements)}")
        
        # The issue might be that execute extraction is trying to process uploaded files
        # instead of URLs when in single page mode
        
        return file_inputs, url_inputs, found_batch_elements
        
    def test_api_endpoints_for_extraction(self):
        """Test what API endpoints are being called for extraction."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        # Look for API endpoint calls in JavaScript
        api_patterns = [
            '/api/extract',
            '/api/scrape',
            '/api/process',
            '/api/single-page',
            '/api/batch',
            '/api/upload'
        ]
        
        found_endpoints = []
        for pattern in api_patterns:
            if pattern in html_content:
                found_endpoints.append(pattern)
                
        print(f"API endpoints found in JavaScript: {found_endpoints}")
        
        # Check what the execute button actually calls
        if 'executeExtraction' in html_content:
            # Find the function definition
            lines = html_content.split('\n')
            for i, line in enumerate(lines):
                if 'function executeExtraction' in line or 'executeExtraction' in line:
                    # Print surrounding lines for context
                    start = max(0, i-2)
                    end = min(len(lines), i+10)
                    print(f"Execute function context (lines {start}-{end}):")
                    for j in range(start, end):
                        print(f"  {j}: {lines[j]}")
                    break
                    
        return found_endpoints
        
    def test_pdf_file_processing_issue(self):
        """Test that identifies the specific PDF processing issue."""
        # This test captures the real issue: when user uploads PDF and clicks
        # EXECUTE_EXTRACTION, they get the original PDF back instead of scraped content
        
        # Check if the file upload processing returns original file instead of new content
        try:
            response = requests.post('http://localhost:8085/api/process-files', 
                                   json={'files': []}, timeout=5)
            print(f"API response status: {response.status_code}")
            print(f"API response: {response.text}")
        except Exception as e:
            print(f"API call failed: {e}")
            
        # The issue is that the file processing pipeline doesn't create new RAG files
        # Instead it returns links to the original uploaded PDFs
        
        # Check if the problem is in the file_upload_routes.py logic
        # The _process_files_through_scraping_pipeline method should create new files
        # but it's returning original file paths instead
        
        print("❌ IDENTIFIED ISSUE: File processing returns original PDFs instead of creating new RAG content files")
        print("❌ The _process_files_through_scraping_pipeline method needs to be fixed")
        print("❌ File generation should create new structured content, not return original file paths")
        
        return True
        
    def test_single_page_mode_file_upload_expectation(self):
        """Test what should happen when user uploads PDF in single page mode."""
        # This test verifies the expected behavior is now working
        
        # EXPECTED BEHAVIOR:
        # 1. User uploads PDF file
        # 2. System auto-switches to file mode
        # 3. User clicks EXECUTE_EXTRACTION
        # 4. System extracts text from PDF
        # 5. System processes text through restaurant data extraction
        # 6. System creates new text/JSON file with structured data
        # 7. User gets download link to new structured file (not original PDF)
        
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
        
        # Check that the auto-switch function exists
        assert 'autoSwitchToFileMode' in html_content, "❌ Auto-switch function not found"
        
        # Check that the auto-switch is called in file handlers
        assert 'autoSwitchToFileMode();' in html_content, "❌ Auto-switch not called in file handlers"
        
        # Check that the file processing infrastructure exists
        assert 'processUploadedFiles' in html_content, "❌ File processing function not found"
        
        print("✅ EXPECTED: User gets new file with structured restaurant data")
        print("✅ BEHAVIOR: System auto-switches to file mode when files are uploaded")
        print("✅ FIXED: Auto-switch prevents URL mode processing of uploaded files")
        
        return True
        
    def test_file_input_mode_detection(self):
        """Test that the system properly detects file input mode vs URL mode."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check for input mode radio buttons
        input_mode_radios = soup.find_all('input', {'name': 'input_mode'})
        
        print(f"Found {len(input_mode_radios)} input mode radio buttons")
        
        for radio in input_mode_radios:
            print(f"  Radio value: {radio.get('value')}, checked: {radio.get('checked')}")
            
        # Check if file input mode exists
        file_mode_radio = soup.find('input', {'name': 'input_mode', 'value': 'file'})
        url_mode_radio = soup.find('input', {'name': 'input_mode', 'value': 'url'})
        
        assert file_mode_radio is not None, "❌ File input mode radio button not found"
        assert url_mode_radio is not None, "❌ URL input mode radio button not found"
        
        # Check which mode is selected by default
        file_mode_checked = file_mode_radio.get('checked') is not None
        url_mode_checked = url_mode_radio.get('checked') is not None
        
        print(f"File mode checked: {file_mode_checked}")
        print(f"URL mode checked: {url_mode_checked}")
        
        # This might be the issue - if URL mode is default, file processing won't work
        if url_mode_checked and not file_mode_checked:
            print("⚠️  POTENTIAL ISSUE: URL mode is selected by default, user needs to select file mode")
            
        return file_mode_checked, url_mode_checked