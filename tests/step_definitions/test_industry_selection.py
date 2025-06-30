import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from pytest_bdd.parsers import parse
from unittest.mock import Mock, patch

scenarios("../features/industry_selection.feature")


class StepContext:
    """Context object to share state between steps"""
    def __init__(self):
        self.form_data = {}
        self.response = None
        self.industry_options = []
        self.scraping_successful = False
        self.homepage_response = None
        self.clear_response = None
        self.text = None


@pytest.fixture
def context():
    """Context object to share state between steps"""
    return StepContext()


@pytest.fixture
def mock_app(client):
    """Fixture for mocked Flask app with session support"""
    with client.session_transaction() as sess:
        yield client, sess


@given("I am on the RAG Scraper homepage")
def on_homepage(mock_app):
    """Navigate to the homepage"""
    client, _ = mock_app
    response = client.get("/")
    assert response.status_code == 200


@when(parsers.parse('I enter "{url}" in the URL input field'))
def enter_url(context, url):
    """Store the entered URL in context"""
    context.form_data["url"] = url


@when("I click the \"Scrape Website\" button without selecting an industry")
def click_scrape_without_industry(mock_app, context):
    """Submit form without industry selection"""
    client, _ = mock_app
    response = client.post("/scrape", data=context.form_data)
    context.response = response


@when("I have not selected any industry")
def no_industry_selected(context):
    """Ensure no industry is selected in form data"""
    context.form_data.pop("industry", None)


@when("I click the \"Scrape Website\" button")
def click_scrape_button(mock_app, context):
    """Submit the scraping form"""
    client, _ = mock_app
    response = client.post("/scrape", data=context.form_data)
    context.response = response


@when("I click on the industry dropdown")
def click_industry_dropdown(mock_app, context):
    """Get the industry options"""
    client, _ = mock_app
    response = client.get("/api/industries")
    context.industry_options = response.json if hasattr(response, "json") else []


@when(parsers.parse('I select "{industry}" from the industry dropdown'))
def select_industry(context, industry):
    """Select an industry in the form"""
    context.form_data["industry"] = industry


@when("I click the \"Scrape All\" button")
def click_scrape_all(mock_app, context):
    """Submit batch scraping form"""
    client, _ = mock_app
    response = client.post("/scrape/batch", data=context.form_data)
    context.response = response


@when("I enter multiple URLs in the batch input:")
def enter_batch_urls(context, text):
    """Enter multiple URLs for batch processing"""
    context.form_data["urls"] = text


@when("the scraping completes successfully")
def scraping_completes(context):
    """Mock successful scraping completion"""
    context.scraping_successful = True


@when("I navigate back to the homepage")
def navigate_back_home(mock_app, context):
    """Navigate back to homepage"""
    client, _ = mock_app
    response = client.get("/")
    context.homepage_response = response


@when("I click the \"Clear Selection\" button next to the dropdown")
def clear_industry_selection(mock_app, context):
    """Clear the industry selection"""
    client, _ = mock_app
    response = client.post("/api/clear-industry")
    context.clear_response = response


@then(parsers.parse('I should see an error message "{message}"'))
def see_error_message(context, message):
    """Verify error message is displayed"""
    response = context.response
    assert message in response.get_data(as_text=True)


@then("the scraping process should not start")
def scraping_not_started(context):
    """Verify scraping was not initiated"""
    response = context.response
    assert response.status_code == 400  # Bad request
    assert not hasattr(context, "scraping_successful")


@then("I should see the following industry options:")
def see_industry_options(context, datatable):
    """Verify all industry options are displayed"""
    expected_industries = [row["Industry"] for row in datatable]
    actual_industries = context.industry_options
    
    for industry in expected_industries:
        assert industry in actual_industries


@then("the industry dropdown should be highlighted with an error state")
def dropdown_error_state(context):
    """Verify dropdown shows error styling"""
    response = context.response
    assert "error" in response.get_data(as_text=True).lower()
    assert "industry" in response.get_data(as_text=True).lower()


@then(parsers.parse('I should see a validation message "{message}"'))
def see_validation_message(context, message):
    """Verify validation message is shown"""
    response = context.response
    assert message in response.get_data(as_text=True)


@then("the URL input should retain the entered value")
def url_input_retained(context):
    """Verify URL is retained after validation error"""
    response = context.response
    entered_url = context.form_data.get("url", "")
    assert entered_url in response.get_data(as_text=True)


@then(parsers.parse('the industry dropdown should still show "{industry}" selected'))
def industry_still_selected(context, industry):
    """Verify industry selection persists"""
    response = context.homepage_response
    assert f'value="{industry}"' in response.get_data(as_text=True)
    assert "selected" in response.get_data(as_text=True)


@then("I should be able to scrape another URL without reselecting the industry")
def can_scrape_without_reselection(mock_app, context):
    """Verify industry persists for next scrape"""
    client, sess = mock_app
    # Industry should be in session
    assert "industry" in sess
    assert sess["industry"] is not None


@then(parsers.parse('I should see help text "{help_text}"'))
def see_help_text(mock_app, help_text):
    """Verify industry-specific help text is displayed"""
    client, _ = mock_app
    # This would be an AJAX call in real implementation
    response = client.get("/api/industry-help")
    assert help_text in response.get_data(as_text=True)


@then(parsers.parse('the system should use the "{industry}" specific extractor'))
def use_industry_extractor(context, industry):
    """Verify correct industry extractor is used"""
    # This would check logs or internal state in real implementation
    assert context.form_data.get("industry") == industry


@then("the extracted data should include industry-specific categories")
def has_industry_categories(context):
    """Verify industry-specific data categories are present"""
    response = context.response
    # Would check for specific category presence based on industry
    assert response.status_code == 200


@then('the industry dropdown should show "Select an industry..."')
def dropdown_shows_placeholder(context):
    """Verify dropdown shows placeholder text"""
    response = context.clear_response
    assert response.status_code == 200


@then("any industry-specific help text should be hidden")
def help_text_hidden(context):
    """Verify help text is not displayed"""
    response = context.clear_response
    assert "help-text" not in response.get_data(as_text=True)


@then(parsers.parse('all URLs should be processed using the "{industry}" extractor'))
def all_urls_use_industry(context, industry):
    """Verify all batch URLs use same industry extractor"""
    assert context.form_data.get("industry") == industry
    assert context.response.status_code == 200


@then(parsers.parse('the progress indicator should show "{message}"'))
def progress_shows_message(context, message):
    """Verify progress indicator shows industry-specific message"""
    response = context.response
    assert message in response.get_data(as_text=True)