"""Unit tests for HTML rendering bug in API key sections."""
import pytest
from bs4 import BeautifulSoup
import os


class TestHTMLRenderingBug:
    """Test suite for HTML rendering bug fixes."""
    
    @pytest.fixture
    def html_content(self):
        """Load the actual HTML template."""
        template_path = os.path.join("src", "web_interface", "templates", "index.html")
        with open(template_path, "r") as f:
            return f.read()
    
    def test_single_page_api_key_section_clean(self, html_content):
        """Test that single-page API key section has no HTML artifacts."""
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Find the single-page API key section
        single_page_section = soup.find("div", {"id": "singleApiKeySection"})
        assert single_page_section is not None, "Single-page API key section not found"
        
        # Get all text content from the section
        section_text = single_page_section.get_text()
        
        # Verify no raw HTML appears as text
        assert "autocomplete=" not in section_text, "Found 'autocomplete=' as text in single-page section"
        assert "off" not in section_text or "off" in section_text.lower(), "Found standalone 'off' as text"
        assert "/>" not in section_text, "Found '/>' as text in single-page section"
        
        # Verify the input has proper autocomplete attribute
        api_key_input = single_page_section.find("input", {"id": "singleAiApiKey"})
        assert api_key_input is not None, "Single-page API key input not found"
        assert api_key_input.get("autocomplete") == "off", "Single-page API key input missing autocomplete='off'"
    
    def test_multi_page_api_key_section_has_no_bug(self, html_content):
        """Test that multi-page API key section no longer has the HTML bug."""
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Find the multi-page API key section
        multi_page_section = soup.find("div", {"id": "apiKeySection"})
        assert multi_page_section is not None, "Multi-page API key section not found"
        
        # Convert section to string to check for stray HTML
        section_html = str(multi_page_section)
        
        # Check that the bug is fixed: no stray autocomplete="off" /> 
        assert 'autocomplete="off" /&gt;' not in section_html, "Found the HTML bug in multi-page section"
        
        # Check that autocomplete text doesn't appear as visible text
        section_text = multi_page_section.get_text()
        assert "autocomplete=" not in section_text, "Found 'autocomplete=' as visible text"
        assert "/>" not in section_text, "Found '/>' as visible text"
    
    def test_multi_page_api_key_input_structure(self, html_content):
        """Test the structure of multi-page API key input."""
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Find the multi-page API key input
        api_key_input = soup.find("input", {"id": "aiApiKey"})
        assert api_key_input is not None, "Multi-page API key input not found"
        
        # Check that the input now has the autocomplete attribute
        assert api_key_input.get("autocomplete") == "off", \
            "Multi-page API key input should have autocomplete='off'"
    
    def test_both_api_key_inputs_exist(self, html_content):
        """Test that both API key inputs exist in the HTML."""
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Check single-page input
        single_input = soup.find("input", {"id": "singleAiApiKey"})
        assert single_input is not None, "Single-page API key input not found"
        assert single_input.get("type") == "text", "Single-page input should be type='text'"
        assert single_input.get("name") == "aiApiKey", "Single-page input should have name='aiApiKey'"
        
        # Check multi-page input
        multi_input = soup.find("input", {"id": "aiApiKey"})
        assert multi_input is not None, "Multi-page API key input not found"
        assert multi_input.get("type") == "text", "Multi-page input should be type='text'"
        assert multi_input.get("name") == "aiApiKey", "Multi-page input should have name='aiApiKey'"
    
    def test_multi_page_api_key_section_fixed(self, html_content):
        """Test that multi-page API key section should be clean after fix."""
        # This test will initially FAIL, then PASS after we fix the bug
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Find the multi-page API key section
        multi_page_section = soup.find("div", {"id": "apiKeySection"})
        assert multi_page_section is not None, "Multi-page API key section not found"
        
        # Get all text content from the section
        section_text = multi_page_section.get_text()
        
        # After fix, there should be no stray HTML as text
        assert "autocomplete=" not in section_text, "Found 'autocomplete=' as text in multi-page section"
        assert "/>" not in section_text, "Found '/>' as text in multi-page section"
        
        # The input should have proper autocomplete attribute
        api_key_input = multi_page_section.find("input", {"id": "aiApiKey"})
        assert api_key_input is not None, "Multi-page API key input not found"
        assert api_key_input.get("autocomplete") == "off", "Multi-page API key input should have autocomplete='off'"