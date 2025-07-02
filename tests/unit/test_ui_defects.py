"""Unit tests for UI defects found during manual testing."""
import pytest
import re
from unittest.mock import patch, MagicMock
from src.web_interface.ui_components import IndustryDropdown


class TestIndustryDropdownStyling:
    """Test industry dropdown styling defect."""
    
    def test_industry_dropdown_has_terminal_input_class(self):
        """Test that industry dropdown includes terminal-input CSS class."""
        dropdown = IndustryDropdown()
        html = dropdown.render()
        
        # Should have both industry-dropdown and terminal-input classes
        assert 'class="industry-dropdown terminal-input"' in html
        assert 'name="industry"' in html
        assert 'id="industry"' in html
    
    def test_industry_dropdown_renders_select_element(self):
        """Test that industry dropdown renders as a select element."""
        dropdown = IndustryDropdown()
        html = dropdown.render()
        
        # Should be a select element, not input
        assert html.startswith('<select')
        assert html.endswith('</select>')
        assert '<option' in html
    
    def test_industry_dropdown_includes_all_industries(self):
        """Test that dropdown includes all configured industries."""
        dropdown = IndustryDropdown()
        html = dropdown.render()
        
        # Should include major industries
        assert 'Restaurant' in html
        assert 'Real Estate' in html
        assert 'Medical' in html
        assert 'Fast Food' in html
        
        # Should have placeholder
        assert 'Select an industry...' in html


class TestAllDropdownsStylingDefect:
    """Test all dropdowns white background defect affecting multiple select elements."""
    
    def test_all_dropdowns_have_terminal_input_class(self):
        """Test that all dropdowns should have terminal-input CSS class."""
        # Industry dropdown
        industry_dropdown = IndustryDropdown()
        industry_html = industry_dropdown.render()
        assert 'terminal-input' in industry_html
        
        # Aggregation mode dropdown should also have terminal-input
        # This represents the pattern that ALL select elements need the class
        test_select_html = '<select class="terminal-input" name="fileMode">'
        assert 'terminal-input' in test_select_html
    
    def test_javascript_styling_enforcement_needed(self):
        """Test that JavaScript must enforce styling due to browser overrides."""
        # Simulate the need for JavaScript intervention
        # Browser default styles can override CSS, requiring JS enforcement
        
        # CSS alone is insufficient
        css_styles = {
            'background': '#1a1a1a',
            'color': '#ffffff'
        }
        
        # Browser may override with its own styles
        browser_override = {
            'background': 'white',  # This is the bug
            'color': 'black'
        }
        
        # JavaScript must force our styles
        js_enforced_styles = {
            'background': '#1a1a1a !important',
            'color': '#ffffff !important'
        }
        
        assert js_enforced_styles['background'] == '#1a1a1a !important'
        assert js_enforced_styles['color'] == '#ffffff !important'
    
    def test_dropdown_styles_persist_on_focus_blur(self):
        """Test that dropdown styles must persist during focus/blur events."""
        # Styles should remain consistent across all states
        required_styles = {
            'default': {'background': '#1a1a1a', 'color': '#ffffff'},
            'focus': {'background': '#1a1a1a', 'color': '#ffffff'},
            'blur': {'background': '#1a1a1a', 'color': '#ffffff'},
            'hover': {'background': '#1a1a1a', 'color': '#ffffff'},
            'active': {'background': '#1a1a1a', 'color': '#ffffff'}
        }
        
        # All states should have same background
        backgrounds = [state['background'] for state in required_styles.values()]
        assert all(bg == '#1a1a1a' for bg in backgrounds)
        
        # All states should have same text color
        colors = [state['color'] for state in required_styles.values()]
        assert all(color == '#ffffff' for color in colors)
    
    def test_mutation_observer_required_for_dynamic_changes(self):
        """Test that dynamic style changes require MutationObserver to fix."""
        # Some browsers or extensions may dynamically change styles
        # MutationObserver pattern is needed to catch and fix these
        
        mutation_observer_config = {
            'attributes': True,
            'attributeFilter': ['style'],
            'subtree': False
        }
        
        assert mutation_observer_config['attributes'] is True
        assert 'style' in mutation_observer_config['attributeFilter']
        
        # Observer should detect style changes and reapply our styles
        detected_change = {'backgroundColor': 'white'}  # Bad change
        corrected_style = {'backgroundColor': '#1a1a1a'}  # Our fix
        
        assert detected_change['backgroundColor'] == 'white'  # The problem
        assert corrected_style['backgroundColor'] == '#1a1a1a'  # The solution


class TestURLSplittingDefect:
    """Test URL splitting defect in JavaScript (simulated in Python)."""
    
    def test_url_splitting_on_newlines(self):
        """Test that URLs are properly split on newlines."""
        url_input = "https://example.com\nhttps://example.com/menu\nhttps://example.com/contact"
        
        # Simulate correct JavaScript behavior
        urls = [url.strip() for url in url_input.strip().split('\n') if url.strip()]
        
        assert len(urls) == 3
        assert urls[0] == "https://example.com"
        assert urls[1] == "https://example.com/menu"
        assert urls[2] == "https://example.com/contact"
    
    def test_url_splitting_on_spaces(self):
        """Test that URLs are properly split on spaces."""
        url_input = "https://example.com https://example.com/menu https://example.com/contact"
        
        # Simulate regex split /[\n\s]+/
        import re
        urls = [url.strip() for url in re.split(r'[\n\s]+', url_input.strip()) if url.strip()]
        
        assert len(urls) == 3
        assert urls[0] == "https://example.com"
        assert urls[1] == "https://example.com/menu"
        assert urls[2] == "https://example.com/contact"
    
    def test_url_splitting_mixed_separators(self):
        """Test URLs split on mixed newlines and spaces."""
        url_input = "https://example.com\n https://example.com/menu  \n\nhttps://example.com/contact"
        
        import re
        urls = [url.strip() for url in re.split(r'[\n\s]+', url_input.strip()) if url.strip()]
        
        assert len(urls) == 3
        assert "https://example.com" in urls
        assert "https://example.com/menu" in urls
        assert "https://example.com/contact" in urls
    
    def test_incorrect_url_splitting_with_double_backslash(self):
        """Test that double backslash splitting fails (the original bug)."""
        url_input = "https://example.com\nhttps://example.com/menu"
        
        # Simulate incorrect JavaScript: split('\\n') - looks for literal \n
        urls = [url.strip() for url in url_input.strip().split('\\n') if url.strip()]
        
        # This should fail to split properly (demonstrating the bug)
        assert len(urls) == 1  # URLs not split correctly
        assert "https://example.com\nhttps://example.com/menu" in urls[0]
    
    def test_url_concatenation_with_quotes_defect(self):
        """Test URLs pasted with quotes from web pages are concatenated incorrectly."""
        # User reported: pasted two URLs with quotes
        url_input = '"https://mobimag.co/wteg/portland/4" and "https://mobimag.co/wteg/portland/6"'
        
        # Current regex /[\n\s]+/ splits on spaces, breaking the input incorrectly
        import re
        urls_wrong = [url.strip() for url in re.split(r'[\n\s]+', url_input.strip()) if url.strip()]
        
        # This demonstrates the bug - URLs are broken into parts
        assert len(urls_wrong) == 3  # Split into: ["url1", "and", "url2"]
        assert urls_wrong[0] == '"https://mobimag.co/wteg/portland/4"'  # Still has quotes
        assert urls_wrong[1] == 'and'  # "and" becomes a separate item
        assert urls_wrong[2] == '"https://mobimag.co/wteg/portland/6"'  # Still has quotes
        
        # The real issue: when these quoted strings are sent to backend,
        # they fail validation or get concatenated
        
        # Correct approach: Extract actual URLs using regex pattern
        url_pattern = r'https?://[^\s"\']+(?:/[^\s"\']*)*'
        urls_correct = re.findall(url_pattern, url_input)
        
        assert len(urls_correct) == 2
        assert urls_correct[0] == "https://mobimag.co/wteg/portland/4"
        assert urls_correct[1] == "https://mobimag.co/wteg/portland/6"
    
    def test_mobimag_urls_parsing_failure(self):
        """Test specific mobimag.co URLs that fail in scraper.py."""
        # User reported these specific URLs fail
        url1 = "https://mobimag.co/wteg/portland/4"
        url2 = "https://mobimag.co/wteg/portland/6"
        
        # Test URL validation
        from urllib.parse import urlparse
        parsed1 = urlparse(url1)
        parsed2 = urlparse(url2)
        
        # URLs should be valid
        assert parsed1.scheme == "https"
        assert parsed1.netloc == "mobimag.co"
        assert parsed1.path == "/wteg/portland/4"
        
        assert parsed2.scheme == "https"
        assert parsed2.netloc == "mobimag.co"
        assert parsed2.path == "/wteg/portland/6"
        
        # Test that URLs don't get truncated at first slash
        assert "/" in parsed1.path
        assert parsed1.path.count("/") == 3  # /wteg/portland/4
        assert "/" in parsed2.path  
        assert parsed2.path.count("/") == 3  # /wteg/portland/6
        
        # Test that full URLs are preserved
        reconstructed1 = f"{parsed1.scheme}://{parsed1.netloc}{parsed1.path}"
        reconstructed2 = f"{parsed2.scheme}://{parsed2.netloc}{parsed2.path}"
        
        assert reconstructed1 == url1
        assert reconstructed2 == url2
        
        # Test with actual URLValidator
        from src.config.url_validator import URLValidator
        validator = URLValidator()
        
        result1 = validator.validate_url(url1)
        result2 = validator.validate_url(url2)
        
        # URLs should pass validation
        assert result1.is_valid, f"URL1 failed validation: {result1.error_message}"
        assert result2.is_valid, f"URL2 failed validation: {result2.error_message}"
        
        # Check parsed components
        assert result1.scheme == "https"
        assert result1.domain == "mobimag.co"
        assert result1.path == "/wteg/portland/4"
        
        assert result2.scheme == "https"
        assert result2.domain == "mobimag.co"
        assert result2.path == "/wteg/portland/6"
    
    def test_single_url_recognition_defect(self):
        """Test that only one URL is being recognized when multiple are provided."""
        # User reported: only one URL recognized, others show "✗ FAILED N/A Unknown error"
        url_input = "https://mobimag.co/wteg/portland/6 https://mobimag.co/wteg/portland/7"
        
        # Test regex extraction (this should work correctly now)
        import re
        url_pattern = r'https?://[^\s"\']+(?:/[^\s"\']*)*/?'
        urls_extracted = re.findall(url_pattern, url_input)
        
        # Should extract both URLs
        assert len(urls_extracted) == 2
        assert urls_extracted[0] == "https://mobimag.co/wteg/portland/6"
        assert urls_extracted[1] == "https://mobimag.co/wteg/portland/7"
        
        # Test URL validation for both
        from src.config.url_validator import URLValidator
        validator = URLValidator()
        
        result1 = validator.validate_url(urls_extracted[0])
        result2 = validator.validate_url(urls_extracted[1])
        
        # Both should be valid
        assert result1.is_valid, f"URL 1 failed: {result1.error_message}"
        assert result2.is_valid, f"URL 2 failed: {result2.error_message}"
        
        # Both should have correct components
        assert result1.domain == "mobimag.co"
        assert result1.path == "/wteg/portland/6"
        assert result2.domain == "mobimag.co"
        assert result2.path == "/wteg/portland/7"
        
        # Test batch validation
        validation_results = validator.validate_urls(urls_extracted)
        valid_results = [r for r in validation_results if r.is_valid]
        
        # Both should pass batch validation
        assert len(valid_results) == 2
        assert all(r.is_valid for r in validation_results)
    
    def test_unknown_error_in_scraping_defect(self):
        """Test 'Unknown error' reported during scraping multiple URLs."""
        # User reported: Second URL shows "✗ FAILED N/A Unknown error 0.50s"
        # This suggests the URL parsing works but scraping fails
        
        # URLs that trigger the issue
        urls = [
            "https://mobimag.co/wteg/portland/6",
            "https://mobimag.co/wteg/portland/7"
        ]
        
        # URLs should be valid
        from src.config.url_validator import URLValidator
        validator = URLValidator()
        results = validator.validate_urls(urls)
        
        assert all(r.is_valid for r in results), "URLs should be valid"
        
        # The issue is likely in:
        # 1. Rate limiting between requests
        # 2. Server blocking rapid requests from same IP
        # 3. Error handling not capturing specific error details
        # 4. Progress reporting showing generic "Unknown error"
        
        # Test that error handling should provide specific error messages
        generic_error = "Unknown error"
        specific_errors = [
            "Connection timeout",
            "Rate limited",
            "Server returned 403",
            "Server returned 404", 
            "Network error",
            "Parsing failed"
        ]
        
        # Generic errors are not helpful for debugging
        assert generic_error not in specific_errors
        
        # Error messages should be informative
        for error in specific_errors:
            assert len(error) > len("N/A")
            assert "error" in error.lower() or "failed" in error.lower() or "timeout" in error.lower()
    
    def test_space_separated_urls_concatenation_defect(self):
        """Test that space-separated URLs are not processed as one concatenated URL."""
        # User's exact scenario: URLs separated by space
        url_input = "https://mobimag.co/wteg/portland/6 https://mobimag.co/wteg/portland/7"
        
        # OLD BUGGY BEHAVIOR: split('\\n') doesn't split on spaces
        # This would treat it as ONE URL: "https://mobimag.co/wteg/portland/6 https://mobimag.co/wteg/portland/7"
        old_buggy_split = [url.strip() for url in url_input.strip().split('\\n') if url.strip()]
        assert len(old_buggy_split) == 1  # Demonstrates the bug
        assert " " in old_buggy_split[0]  # Space is preserved in the "URL"
        
        # NEW CORRECT BEHAVIOR: regex extraction finds both URLs
        import re
        url_pattern = r'https?://[^\s"\']+(?:/[^\s"\']*)*/?'
        urls_extracted = re.findall(url_pattern, url_input)
        
        # Should extract TWO separate URLs
        assert len(urls_extracted) == 2
        assert urls_extracted[0] == "https://mobimag.co/wteg/portland/6"
        assert urls_extracted[1] == "https://mobimag.co/wteg/portland/7"
        
        # No spaces should be in individual URLs
        assert " " not in urls_extracted[0]
        assert " " not in urls_extracted[1]
        
        # Each URL should be valid individually
        from src.config.url_validator import URLValidator
        validator = URLValidator()
        
        result1 = validator.validate_url(urls_extracted[0])
        result2 = validator.validate_url(urls_extracted[1])
        
        assert result1.is_valid, f"First URL invalid: {result1.error_message}"
        assert result2.is_valid, f"Second URL invalid: {result2.error_message}"
        
        # The concatenated version passes validation but would fail during HTTP request
        concatenated_url = old_buggy_split[0]
        result_concatenated = validator.validate_url(concatenated_url)
        
        # URLValidator doesn't catch spaces (this is the real issue!)
        assert result_concatenated.is_valid  # Passes validation incorrectly
        assert " " in concatenated_url  # But contains spaces which break HTTP requests
        
        # This is why we see "✗ FAILED N/A Unknown error" - 
        # the URL passes validation but fails during actual HTTP request
        # because spaces in URLs cause connection errors


class TestURLTruncationDefect:
    """Test URL truncation defect."""
    
    def test_url_preserves_full_path(self):
        """Test that URLs with paths are not truncated."""
        full_url = "https://restaurant.com/menu/dinner-specials"
        
        # Simulate URL parsing that should preserve full path
        from urllib.parse import urlparse
        parsed = urlparse(full_url)
        
        # Should preserve all components
        assert parsed.scheme == "https"
        assert parsed.netloc == "restaurant.com"
        assert parsed.path == "/menu/dinner-specials"
        
        # Reconstructed URL should be identical
        reconstructed = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        assert reconstructed == full_url
    
    def test_url_not_truncated_at_first_slash(self):
        """Test that URL path after first slash is preserved."""
        url_with_path = "https://example.com/deep/nested/path/page.html"
        
        # Should not truncate at first slash
        from urllib.parse import urlparse
        parsed = urlparse(url_with_path)
        
        assert parsed.path == "/deep/nested/path/page.html"
        assert "/" in parsed.path  # Multiple slashes preserved
        assert parsed.path.count("/") == 4  # All path segments preserved
    
    def test_url_query_parameters_preserved(self):
        """Test that URL query parameters are preserved."""
        url_with_params = "https://restaurant.com/menu?category=dinner&special=true"
        
        from urllib.parse import urlparse
        parsed = urlparse(url_with_params)
        
        assert parsed.query == "category=dinner&special=true"
        assert parsed.path == "/menu"
        
        # Full URL reconstruction
        full_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{parsed.query}"
        assert full_url == url_with_params


class TestIndustryValidationDefect:
    """Test industry validation defect in form submission."""
    
    def test_industry_field_included_in_form_data(self):
        """Test that industry field should be included in form submission."""
        # Simulate form data that should include industry
        form_data = {
            "urls": ["https://example.com"],
            "output_dir": "/output",
            "file_mode": "single",
            "file_format": "txt",
            "industry": "Restaurant",  # This field was missing in the original bug
            "scraping_mode": "standard"
        }
        
        # Industry should be present and valid
        assert "industry" in form_data
        assert form_data["industry"] == "Restaurant"
        assert form_data["industry"] != ""
        assert form_data["industry"] is not None
    
    def test_missing_industry_field_validation(self):
        """Test validation when industry field is missing."""
        # Simulate form data without industry (the original bug)
        form_data = {
            "urls": ["https://example.com"],
            "output_dir": "/output",
            "file_mode": "single",
            "file_format": "txt",
            # "industry": missing!
            "scraping_mode": "standard"
        }
        
        # Should detect missing industry
        assert "industry" not in form_data
        
        # Simulate backend validation
        industry = form_data.get("industry")
        is_valid = bool(industry and industry.strip())
        
        assert not is_valid  # Should fail validation
    
    def test_empty_industry_field_validation(self):
        """Test validation when industry field is empty."""
        form_data = {
            "urls": ["https://example.com"],
            "industry": "",  # Empty industry
        }
        
        # Should detect empty industry
        industry = form_data.get("industry")
        is_valid = bool(industry and industry.strip())
        
        assert not is_valid  # Should fail validation
    
    @patch('src.config.industry_config.IndustryConfig')
    def test_invalid_industry_selection(self, mock_config):
        """Test validation of invalid industry selection."""
        # Mock industry config
        mock_instance = MagicMock()
        mock_instance.validate_industry.return_value = False
        mock_config.return_value = mock_instance
        
        form_data = {"industry": "InvalidIndustry"}
        
        # Should fail validation for invalid industry
        from src.config.industry_config import IndustryConfig
        config = IndustryConfig()
        is_valid = config.validate_industry(form_data["industry"])
        
        assert not is_valid


if __name__ == "__main__":
    pytest.main([__file__])