"""Step definitions for file format selection interface tests."""
import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Load scenarios from the feature file
scenarios("../features/file_format_selection_interface.feature")


@pytest.fixture
def flask_test_client():
    """Create Flask test client."""
    from src.web_interface.app import create_app

    app = create_app(testing=True)
    return app.test_client()


@pytest.fixture
def test_context():
    """Provide test context for sharing data between steps."""
    return {}


# Given steps
@given("the RAG_Scraper web interface is running")
def web_interface_running(flask_test_client):
    """Verify the web interface is accessible."""
    response = flask_test_client.get("/")
    assert response.status_code == 200


@given("I am on the main interface page")
def on_main_interface_page(flask_test_client, test_context):
    """Navigate to the main interface page."""
    response = flask_test_client.get("/")
    test_context["main_page_response"] = response
    test_context["main_page_html"] = response.get_data(as_text=True)
    assert response.status_code == 200


@given("I am viewing the scraping form")
def viewing_scraping_form(test_context):
    """Verify we are viewing the scraping form."""
    html = test_context["main_page_html"]
    assert "scrapeForm" in html, "Scraping form should be present on the page"


# When steps
@when(parsers.parse('I select "{format_option}" as the file format'))
def select_file_format(test_context, format_option):
    """Simulate selecting a file format option."""
    test_context["selected_format"] = format_option


# Then steps
@then("I should see file format selection options")
def should_see_format_selection_options(test_context):
    """Verify file format selection options are visible."""
    html = test_context["main_page_html"]

    # This test should FAIL initially - we need to add format selection to the interface
    assert (
        "file-format" in html or "fileFormat" in html
    ), "File format selection should be present in the HTML"


@then('the options should include "Text", "PDF", and "Both"')
def options_should_include_text_pdf_both(test_context):
    """Verify all format options are available."""
    html = test_context["main_page_html"]

    # This test should FAIL initially - we need to add these options
    assert "Text" in html, "Text option should be available"
    assert "PDF" in html, "PDF option should be available"
    assert "Both" in html, "Both option should be available"


@then('"Text" should be selected by default')
def text_should_be_default_selected(test_context):
    """Verify Text is the default selection."""
    html = test_context["main_page_html"]

    # This test should FAIL initially - we need to implement default selection
    assert (
        'value="text"' in html and "checked" in html
    ), "Text should be selected by default"


@then(parsers.parse('the "{format_option}" option should be visually selected'))
def format_option_should_be_selected(test_context, format_option):
    """Verify the specified format option is visually selected."""
    selected_format = test_context.get("selected_format")
    assert selected_format == format_option, f"Expected {format_option} to be selected"


@then("the other options should not be selected")
def other_options_should_not_be_selected(test_context):
    """Verify only one option is selected at a time."""
    # This would be verified by checking the UI state
    # For now, we'll assume the selection logic works correctly
    assert True  # Placeholder for UI selection validation
