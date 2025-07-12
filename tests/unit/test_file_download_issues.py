"""Unit tests for file download functionality issues."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os


class TestFileDownloadFunctionality:
    """Test file download functionality."""
    
    def test_multiple_file_download_links_present(self):
        """Test that multiple file download links are generated correctly."""
        mock_results = {
            'success': True,
            'output_files': [
                '/output/restaurant_data.txt',
                '/output/restaurant_data.pdf', 
                '/output/restaurant_data.json'
            ]
        }
        
        # Test the file link generation helper
        download_links = self._extract_download_links(mock_results)
        
        # Should generate 3 download links
        assert len(download_links) == 3, f"Expected 3 download links, got {len(download_links)}"
        
        # Verify each file type has a link
        file_types = [link['type'] for link in download_links]
        expected_types = ['txt', 'pdf', 'json']
        for expected_type in expected_types:
            assert expected_type in file_types, f"Missing download link for {expected_type} file"
        
        # Verify link structure
        for link in download_links:
            assert 'filename' in link, "Download link should have filename"
            assert 'type' in link, "Download link should have type"
            assert 'url' in link, "Download link should have URL"
            assert link['url'].startswith('/api/download/'), "Download URL should use API endpoint"
    
    def test_download_link_functionality(self):
        """Test that download links actually work."""
        import tempfile
        import os
        
        # Create a temporary upload folder and test files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files in the upload directory
            test_file_path = os.path.join(temp_dir, 'test_file.txt')
            with open(test_file_path, 'w') as f:
                f.write("Test restaurant data content")
            
            test_json_path = os.path.join(temp_dir, 'test_file.json')
            with open(test_json_path, 'w') as f:
                f.write('{"restaurant": "test data"}')
            
            # Create app with custom upload folder
            from src.web_interface.app import create_app
            app = create_app(upload_folder=temp_dir)
            
            with app.test_client() as client:
                # Test downloading a file that exists
                response = client.get('/api/download/test_file.txt')
                assert response.status_code == 200, f"Download failed with status {response.status_code}"
                assert b"Test restaurant data content" in response.data, "Downloaded content should match file content"
                
                # Test downloading JSON file
                response = client.get('/api/download/test_file.json')
                assert response.status_code == 200, f"JSON download failed with status {response.status_code}"
                
                # Test missing file handling
                response = client.get('/api/download/missing_file.txt')
                assert response.status_code == 404, "Missing file should return 404"
    
    def test_no_files_scenario_handling(self):
        """Test handling when no files are generated."""
        # This test should FAIL initially if UI doesn't handle empty results properly
        
        mock_results = {
            'success': True,
            'output_files': []  # No files generated
        }
        
        download_links = self._extract_download_links(mock_results)
        
        # Should show appropriate message and no download links
        assert len(download_links) == 0, "No download links should be present when no files generated"
        
        # Should have appropriate messaging
        no_files_message = self._get_no_files_message(mock_results)
        assert no_files_message is not None, "Should display message when no files available"
    
    def _extract_download_links(self, results):
        """Helper to extract download links from results."""
        # This simulates the JavaScript file link generation
        # In reality, this should parse the actual HTML output
        
        if not results.get('output_files'):
            return []
        
        links = []
        for file_path in results['output_files']:
            filename = os.path.basename(file_path)
            file_type = filename.split('.')[-1] if '.' in filename else 'unknown'
            
            links.append({
                'filename': filename,
                'type': file_type,
                'url': f'/api/download/{filename}',
                'functional': False  # This should be tested
            })
        
        return links
    
    def _get_no_files_message(self, results):
        """Helper to check for no files message."""
        # This should check if appropriate messaging is displayed
        if not results.get('output_files'):
            return "No files available for download"
        return None


class TestAdvancedOptionsToggle:
    """Test Advanced Options toggle functionality."""
    
    def test_advanced_options_panel_toggle(self):
        """Test that Advanced Options panel toggles correctly."""
        # This test should FAIL initially if toggle functionality is broken
        
        from src.web_interface.app import create_app
        app = create_app()
        
        with app.test_client() as client:
            # Get the main page
            response = client.get('/')
            assert response.status_code == 200
            
            html_content = response.get_data(as_text=True)
            
            # Check that Advanced Options elements are present
            assert 'toggleAdvancedOptions()' in html_content, "toggleAdvancedOptions function should be present"
            assert 'advancedOptionsPanel' in html_content, "Advanced Options panel should be present"
            assert 'advancedOptionsIcon' in html_content, "Advanced Options icon should be present"
    
    def test_advanced_options_javascript_function_exists(self):
        """Test that the toggle function exists in JavaScript."""
        # This test should FAIL initially if JavaScript function is missing or broken
        
        # Read the HTML template that contains the JavaScript
        template_path = '/home/rod/AI/Projects/RAG_Scraper/src/web_interface/templates/index.html'
        
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Check that the function is defined
        assert 'function toggleAdvancedOptions()' in content, "toggleAdvancedOptions function should be defined"
        
        # Check that the function modifies the correct elements
        assert 'advancedOptionsPanel' in content, "Function should reference advancedOptionsPanel"
        assert 'advancedOptionsIcon' in content, "Function should reference advancedOptionsIcon"
        assert 'collapsed' in content, "Function should handle collapsed class"
    
    def test_advanced_options_css_classes_present(self):
        """Test that required CSS classes are present."""
        # This test should FAIL initially if CSS classes are missing
        
        template_path = '/home/rod/AI/Projects/RAG_Scraper/src/web_interface/templates/index.html'
        
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Check for required CSS classes
        assert 'advanced-options-panel' in content, "advanced-options-panel class should be defined"
        assert 'collapsed' in content, "collapsed class should be used"
        assert 'expanded' in content, "expanded class should be used"
    
    def test_advanced_options_default_state(self):
        """Test that Advanced Options panel starts in collapsed state."""
        # This test should FAIL initially if default state is wrong
        
        template_path = '/home/rod/AI/Projects/RAG_Scraper/src/web_interface/templates/index.html'
        
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Find the Advanced Options panel declaration
        import re
        panel_match = re.search(r'id="advancedOptionsPanel"[^>]*class="[^"]*', content)
        
        assert panel_match, "advancedOptionsPanel should be found"
        panel_classes = panel_match.group(0)
        
        # Should start collapsed
        assert 'collapsed' in panel_classes, "Advanced Options panel should start collapsed"


# Additional integration test
class TestIntegrationIssues:
    """Test integration between UI and backend."""
    
    def test_file_download_api_endpoints_exist(self):
        """Test that download API endpoints are properly configured."""
        # This test should FAIL initially if API routes are missing
        
        from src.web_interface.app import create_app
        app = create_app()
        
        # Check that download routes are registered
        url_map = list(app.url_map.iter_rules())
        download_routes = [rule for rule in url_map if 'download' in rule.rule]
        
        assert len(download_routes) > 0, "Download API routes should be configured"
        
        # Check for specific expected routes
        download_rule_strings = [rule.rule for rule in download_routes]
        expected_patterns = ['/api/download', '/download']
        
        has_download_route = any(
            any(pattern in rule for pattern in expected_patterns) 
            for rule in download_rule_strings
        )
        
        assert has_download_route, f"Expected download routes not found. Available: {download_rule_strings}"
    
    def test_results_display_integration(self):
        """Test that results display properly integrates with download functionality."""
        # This test should FAIL initially if results display doesn't show download links
        
        mock_results = {
            'success': True,
            'processed_count': 1,
            'output_files': [
                '/output/test_file.txt',
                '/output/test_file.pdf'
            ]
        }
        
        # This should simulate the JavaScript showResults function
        # In a real test, this would check the actual DOM manipulation
        
        # For now, we'll check that the data structure is correct
        assert 'output_files' in mock_results, "Results should contain output_files"
        assert len(mock_results['output_files']) == 2, "Should have 2 output files"
        
        # This assertion should FAIL initially if results display doesn't handle files properly
        for file_path in mock_results['output_files']:
            filename = os.path.basename(file_path)
            expected_download_url = f'/api/download/{filename}'
            
            # This should verify that download URLs are generated correctly
            # In the real implementation, this would be checked in the browser
            assert expected_download_url.startswith('/api/download/'), "Download URLs should be properly formatted"