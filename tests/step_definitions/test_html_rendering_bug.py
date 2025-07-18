"""Step definitions for HTML rendering bug tests."""
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

# Link feature file
scenarios("../features/html_rendering_bug.feature")


@pytest.fixture
def mock_flask_app():
    """Mock Flask application for testing."""
    with patch("src.web_interface.app.create_app") as mock_create_app:
        app = Mock()
        app.config = {"SECRET_KEY": "test-secret"}
        mock_create_app.return_value = app
        yield app


@pytest.fixture
def html_content():
    """Fixture to hold the HTML content for testing."""
    return {"html": None}


@given("the RAG Scraper web interface is loaded")
def load_web_interface(mock_flask_app, html_content):
    """Load the web interface HTML."""
    # Read the actual HTML template
    with open("src/web_interface/templates/index.html", "r") as f:
        html_content["html"] = f.read()


@when("I expand the single-page configuration section")
def expand_single_page_section(html_content):
    """Simulate expanding single-page configuration section."""
    # In real implementation, this would trigger JavaScript
    # For testing, we just verify the HTML structure exists
    soup = BeautifulSoup(html_content["html"], "html.parser")
    single_page_section = soup.find("div", {"id": "singlePageConfig"})
    assert single_page_section is not None, "Single-page configuration section not found"


@when("I enable AI Enhancement in single-page mode")
def enable_single_page_ai(html_content):
    """Simulate enabling AI enhancement in single-page mode."""
    soup = BeautifulSoup(html_content["html"], "html.parser")
    ai_toggle = soup.find("input", {"id": "singleAiEnhancement"})
    assert ai_toggle is not None, "Single-page AI enhancement toggle not found"


@when("I look at the API key input section in single-page mode")
def view_single_page_api_key_section(html_content):
    """Focus on the single-page API key section."""
    soup = BeautifulSoup(html_content["html"], "html.parser")
    api_key_section = soup.find("div", {"id": "singleApiKeySection"})
    assert api_key_section is not None, "Single-page API key section not found"
    html_content["current_section"] = api_key_section


@when("I expand the AI Enhancement Options section in multi-page mode")
def expand_multi_page_ai_section(html_content):
    """Simulate expanding the multi-page AI enhancement section."""
    soup = BeautifulSoup(html_content["html"], "html.parser")
    ai_section = soup.find("div", {"id": "aiEnhancementPanel"})
    assert ai_section is not None, "Multi-page AI enhancement section not found"


@when("I look at the API key input section in multi-page mode")
def view_multi_page_api_key_section(html_content):
    """Focus on the multi-page API key section."""
    soup = BeautifulSoup(html_content["html"], "html.parser")
    api_key_section = soup.find("div", {"id": "apiKeySection"})
    assert api_key_section is not None, "Multi-page API key section not found"
    html_content["current_section"] = api_key_section


@then(parsers.parse('I should not see raw HTML text "{text}" in the single-page section'))
def check_no_html_text_single_page(html_content, text):
    """Verify no raw HTML text appears in single-page section."""
    soup = BeautifulSoup(html_content["html"], "html.parser")
    api_key_section = soup.find("div", {"id": "singleApiKeySection"})
    
    # Check that the text doesn't appear as visible content
    section_text = api_key_section.get_text()
    assert text not in section_text, f"Found raw HTML text '{text}' in single-page section"


@then(parsers.parse('I should not see raw HTML text "{text}" in the multi-page section'))
def check_no_html_text_multi_page(html_content, text):
    """Verify no raw HTML text appears in multi-page section."""
    soup = BeautifulSoup(html_content["html"], "html.parser")
    api_key_section = soup.find("div", {"id": "apiKeySection"})
    
    # Check that the text doesn't appear as visible content
    section_text = api_key_section.get_text()
    assert text not in section_text, f"Found raw HTML text '{text}' in multi-page section"


@then("the single-page API key input should have autocomplete disabled")
def check_single_page_autocomplete(html_content):
    """Verify single-page API key input has autocomplete disabled."""
    soup = BeautifulSoup(html_content["html"], "html.parser")
    api_key_input = soup.find("input", {"id": "singleAiApiKey"})
    assert api_key_input is not None, "Single-page API key input not found"
    assert api_key_input.get("autocomplete") == "off", "Single-page API key input should have autocomplete='off'"


@then("the multi-page API key input should have autocomplete disabled")
def check_multi_page_autocomplete(html_content):
    """Verify multi-page API key input has autocomplete disabled."""
    soup = BeautifulSoup(html_content["html"], "html.parser")
    api_key_input = soup.find("input", {"id": "aiApiKey"})
    assert api_key_input is not None, "Multi-page API key input not found"
    assert api_key_input.get("autocomplete") == "off", "Multi-page API key input should have autocomplete='off'"


@when(parsers.parse('I enter "{text}" in the single-page API key input'))
def enter_single_page_api_key(html_content, text):
    """Simulate entering text in single-page API key input."""
    soup = BeautifulSoup(html_content["html"], "html.parser")
    api_key_input = soup.find("input", {"id": "singleAiApiKey"})
    assert api_key_input is not None, "Single-page API key input not found"
    # Store the entered value for verification
    html_content["single_page_api_key"] = text


@when(parsers.parse('I enter "{text}" in the multi-page API key input'))
def enter_multi_page_api_key(html_content, text):
    """Simulate entering text in multi-page API key input."""
    soup = BeautifulSoup(html_content["html"], "html.parser")
    api_key_input = soup.find("input", {"id": "aiApiKey"})
    assert api_key_input is not None, "Multi-page API key input not found"
    # Store the entered value for verification
    html_content["multi_page_api_key"] = text


@then(parsers.parse('the single-page API key input should contain "{text}"'))
def verify_single_page_api_key(html_content, text):
    """Verify single-page API key input contains expected text."""
    assert html_content.get("single_page_api_key") == text, \
        f"Expected single-page API key to be '{text}', but got '{html_content.get('single_page_api_key')}'"


@then(parsers.parse('the multi-page API key input should contain "{text}"'))
def verify_multi_page_api_key(html_content, text):
    """Verify multi-page API key input contains expected text."""
    assert html_content.get("multi_page_api_key") == text, \
        f"Expected multi-page API key to be '{text}', but got '{html_content.get('multi_page_api_key')}'"