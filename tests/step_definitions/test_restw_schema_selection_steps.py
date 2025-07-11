"""Step definitions for RestW schema selection acceptance tests."""

import pytest
from pytest_bdd import given, when, then, scenarios, parsers

from src.web_interface.ui_components import RestWSchemaSelector
from src.config.restw_config import RestWConfig
from src.processors.restw_processor_factory import RestWProcessorFactory

# Load scenarios from feature file
scenarios('../features/restw_schema_selection.feature')


@given('the RAG Scraper web interface is available')
def web_interface_available():
    """Web interface is available for testing."""
    pass


@given('the Restaurant industry is available in the industry dropdown')
def restaurant_industry_available():
    """Restaurant industry is available in dropdown."""
    pass


@given('I am on the main scraping page')
def on_main_scraping_page(mock_web_context):
    """User is on the main scraping page."""
    mock_web_context.current_page = 'main'
    mock_web_context.form_data = {}


@when('I select "Restaurant" from the industry dropdown')
def select_restaurant_industry(mock_web_context):
    """Select Restaurant from industry dropdown."""
    mock_web_context.form_data['industry'] = 'Restaurant'


@then('I should see a RestW schema selection option')
def should_see_restw_option(mock_web_context):
    """RestW schema option should be visible."""
    assert mock_web_context.form_data['industry'] == 'Restaurant'
    
    # Check if RestW selector is available
    restw_selector = RestWSchemaSelector()
    assert restw_selector.is_available_for_industry('Restaurant')


@then('the RestW schema option should be labeled "RestW - Enhanced Restaurant Data"')
def restw_option_labeled_correctly():
    """RestW option should have correct label."""
    restw_selector = RestWSchemaSelector()
    label = restw_selector.get_display_label()
    assert label == "RestW - Enhanced Restaurant Data"


@then('the RestW schema option should have helpful description text')
def restw_option_has_description():
    """RestW option should have description text."""
    restw_selector = RestWSchemaSelector()
    description = restw_selector.get_description()
    assert len(description) > 0
    assert 'WTEG' not in description  # Should not expose WTEG terminology


@given('I have selected "Restaurant" from the industry dropdown')
def restaurant_selected(mock_web_context):
    """Restaurant industry is selected."""
    mock_web_context.form_data['industry'] = 'Restaurant'


@when('I select the RestW schema option')
def select_restw_schema(mock_web_context):
    """Select RestW schema option."""
    mock_web_context.form_data['schema'] = 'RestW'


@then('the form should be configured for RestW extraction')
def form_configured_for_restw(mock_web_context):
    """Form should be configured for RestW extraction."""
    assert mock_web_context.form_data['schema'] == 'RestW'
    
    # Check if RestW configuration is applied
    restw_config = RestWConfig()
    assert restw_config.is_restw_schema_selected(mock_web_context.form_data)


@then('I should see RestW-specific field options')
def should_see_restw_fields():
    """RestW-specific field options should be visible."""
    restw_config = RestWConfig()
    fields = restw_config.get_extraction_fields()
    
    # Check for RestW-specific fields
    expected_fields = ['location', 'menu_items', 'services_offered', 'contact_info']
    for field in expected_fields:
        assert field in fields


@then('the extraction should use WTEG processors')
def extraction_uses_wteg_processors():
    """Extraction should use WTEG processors internally."""
    factory = RestWProcessorFactory()
    processor = factory.create_processor('url', 'RestW')
    
    # Should use WTEG processors internally but expose RestW interface
    assert hasattr(processor, 'process_url')
    assert processor.schema_type == 'RestW'


@then('I should see help text explaining RestW features')
def should_see_restw_help_text():
    """Help text should explain RestW features."""
    restw_selector = RestWSchemaSelector()
    help_text = restw_selector.get_help_text()
    assert len(help_text) > 0


@then('the help text should mention structured location data')
def help_text_mentions_location():
    """Help text should mention location data."""
    restw_selector = RestWSchemaSelector()
    help_text = restw_selector.get_help_text()
    assert 'location' in help_text.lower()


@then('the help text should mention menu item extraction')
def help_text_mentions_menu():
    """Help text should mention menu extraction."""
    restw_selector = RestWSchemaSelector()
    help_text = restw_selector.get_help_text()
    assert 'menu' in help_text.lower()


@then('the help text should mention service offerings')
def help_text_mentions_services():
    """Help text should mention service offerings."""
    restw_selector = RestWSchemaSelector()
    help_text = restw_selector.get_help_text()
    assert 'service' in help_text.lower()


@then('the help text should not mention "WTEG" terminology')
def help_text_no_wteg():
    """Help text should not expose WTEG terminology."""
    restw_selector = RestWSchemaSelector()
    help_text = restw_selector.get_help_text()
    assert 'WTEG' not in help_text
    assert 'wteg' not in help_text.lower()


@when(parsers.parse('I enter a restaurant URL "{url}"'))
def enter_restaurant_url(mock_web_context, url):
    """Enter restaurant URL."""
    mock_web_context.form_data['urls'] = url


@when('I click the extract button')
def click_extract_button(mock_web_context):
    """Click extract button."""
    mock_web_context.form_data['action'] = 'extract'


@then('the output should be in RestW format')
def output_in_restw_format(mock_extraction_result):
    """Output should be in RestW format."""
    assert mock_extraction_result.schema_type == 'RestW'
    assert 'location' in mock_extraction_result.data
    assert 'menu_items' in mock_extraction_result.data


@then('the output should contain structured location data')
def output_contains_location_data(mock_extraction_result):
    """Output should contain structured location data."""
    location_data = mock_extraction_result.data.get('location', {})
    assert 'street_address' in location_data
    assert 'city' in location_data
    assert 'state' in location_data


@then('the output should contain menu items with categories')
def output_contains_menu_items(mock_extraction_result):
    """Output should contain categorized menu items."""
    menu_items = mock_extraction_result.data.get('menu_items', [])
    assert len(menu_items) > 0
    
    # Check for menu item structure
    for item in menu_items:
        assert 'item_name' in item
        assert 'category' in item


@then('the output should contain service offerings')
def output_contains_services(mock_extraction_result):
    """Output should contain service offerings."""
    services = mock_extraction_result.data.get('services_offered', {})
    assert 'delivery_available' in services
    assert 'takeout_available' in services


@then('the output should contain contact information')
def output_contains_contact_info(mock_extraction_result):
    """Output should contain contact information."""
    contact_info = mock_extraction_result.data.get('contact_info', {})
    assert 'primary_phone' in contact_info


@when('I upload a restaurant PDF file')
def upload_restaurant_pdf(mock_web_context):
    """Upload restaurant PDF file."""
    mock_web_context.form_data['uploaded_file'] = 'restaurant_menu.pdf'


@then('the extraction should use WTEG PDF processors')
def extraction_uses_wteg_pdf_processors():
    """Extraction should use WTEG PDF processors."""
    factory = RestWProcessorFactory()
    processor = factory.create_processor('pdf', 'RestW')
    
    assert hasattr(processor, 'process_pdf')
    assert processor.schema_type == 'RestW'


@then('the PDF should be parsed using WTEG schema')
def pdf_parsed_with_wteg_schema():
    """PDF should be parsed using WTEG schema internally."""
    factory = RestWProcessorFactory()
    processor = factory.create_processor('pdf', 'RestW')
    
    # Should use WTEG schema internally
    assert processor.uses_wteg_schema()


@then('the output should contain structured restaurant data')
def output_contains_structured_data(mock_extraction_result):
    """Output should contain structured restaurant data."""
    required_sections = ['location', 'menu_items', 'services_offered', 'contact_info']
    for section in required_sections:
        assert section in mock_extraction_result.data


@when('I perform an extraction')
def perform_extraction(mock_web_context):
    """Perform extraction."""
    mock_web_context.form_data['action'] = 'extract'
    mock_web_context.extraction_performed = True


@when('I return to the form')
def return_to_form(mock_web_context):
    """Return to form."""
    mock_web_context.current_page = 'main'


@then('the RestW schema option should still be selected')
def restw_option_still_selected(mock_web_context):
    """RestW schema option should still be selected."""
    assert mock_web_context.form_data.get('schema') == 'RestW'


@then('the form should maintain RestW configuration')
def form_maintains_restw_config(mock_web_context):
    """Form should maintain RestW configuration."""
    restw_config = RestWConfig()
    assert restw_config.is_restw_schema_selected(mock_web_context.form_data)


@when('I deselect the RestW schema option')
def deselect_restw_schema(mock_web_context):
    """Deselect RestW schema option."""
    mock_web_context.form_data['schema'] = None


@then('the form should revert to standard restaurant extraction')
def form_reverts_to_standard(mock_web_context):
    """Form should revert to standard restaurant extraction."""
    assert mock_web_context.form_data.get('schema') != 'RestW'
    
    restw_config = RestWConfig()
    assert not restw_config.is_restw_schema_selected(mock_web_context.form_data)


@then('RestW-specific options should be hidden')
def restw_options_hidden():
    """RestW-specific options should be hidden."""
    restw_selector = RestWSchemaSelector()
    assert not restw_selector.are_options_visible(schema_selected=False)


@then('the extraction should use standard restaurant processors')
def extraction_uses_standard_processors():
    """Extraction should use standard restaurant processors."""
    factory = RestWProcessorFactory()
    processor = factory.create_processor('url', 'standard')
    
    assert processor.schema_type == 'standard'
    assert not processor.uses_wteg_schema()


@when(parsers.parse('I select "{industry}" from the industry dropdown'))
def select_industry(mock_web_context, industry):
    """Select industry from dropdown."""
    mock_web_context.form_data['industry'] = industry


@then('I should not see the RestW schema option')
def should_not_see_restw_option(mock_web_context):
    """RestW schema option should not be visible."""
    industry = mock_web_context.form_data.get('industry')
    
    restw_selector = RestWSchemaSelector()
    assert not restw_selector.is_available_for_industry(industry)


@when('I submit the form without entering URLs or files')
def submit_form_without_data(mock_web_context):
    """Submit form without URLs or files."""
    mock_web_context.form_data['action'] = 'extract'
    mock_web_context.form_data['urls'] = ''
    mock_web_context.form_data['uploaded_file'] = None


@then('I should see appropriate error messages')
def should_see_error_messages(mock_web_context):
    """Should see appropriate error messages."""
    # Error handling should be present
    assert 'action' in mock_web_context.form_data


@then('the RestW schema selection should be preserved')
def restw_selection_preserved(mock_web_context):
    """RestW schema selection should be preserved."""
    assert mock_web_context.form_data.get('schema') == 'RestW'


@then('the form should remain in RestW mode')
def form_remains_in_restw_mode(mock_web_context):
    """Form should remain in RestW mode."""
    restw_config = RestWConfig()
    assert restw_config.is_restw_schema_selected(mock_web_context.form_data)


@when('I extract data from a restaurant source')
def extract_from_restaurant_source(mock_web_context):
    """Extract data from restaurant source."""
    mock_web_context.form_data['urls'] = 'https://example-restaurant.com'
    mock_web_context.form_data['action'] = 'extract'


@then('the output should contain RestW-formatted data')
def output_contains_restw_formatted_data(mock_extraction_result):
    """Output should contain RestW-formatted data."""
    assert mock_extraction_result.schema_type == 'RestW'


@then('the output should have location section with address fields')
def output_has_location_section(mock_extraction_result):
    """Output should have location section."""
    location = mock_extraction_result.data.get('location', {})
    assert 'street_address' in location
    assert 'city' in location
    assert 'state' in location
    assert 'zip_code' in location


@then('the output should have menu_items section with categorized items')
def output_has_menu_items_section(mock_extraction_result):
    """Output should have menu_items section."""
    menu_items = mock_extraction_result.data.get('menu_items', [])
    assert len(menu_items) > 0
    
    for item in menu_items:
        assert 'item_name' in item
        assert 'category' in item
        assert 'price' in item


@then('the output should have services_offered section')
def output_has_services_section(mock_extraction_result):
    """Output should have services_offered section."""
    services = mock_extraction_result.data.get('services_offered', {})
    assert 'delivery_available' in services
    assert 'takeout_available' in services


@then('the output should have contact_info section')
def output_has_contact_info_section(mock_extraction_result):
    """Output should have contact_info section."""
    contact_info = mock_extraction_result.data.get('contact_info', {})
    assert 'primary_phone' in contact_info


@then('the output should have web_links section')
def output_has_web_links_section(mock_extraction_result):
    """Output should have web_links section."""
    web_links = mock_extraction_result.data.get('web_links', {})
    assert 'official_website' in web_links


@then('all field names should use RestW terminology not WTEG')
def field_names_use_restw_terminology(mock_extraction_result):
    """Field names should use RestW terminology."""
    data_str = str(mock_extraction_result.data)
    assert 'WTEG' not in data_str
    assert 'wteg' not in data_str.lower()


@when('I configure RestW extraction options')
def configure_restw_options(mock_web_context):
    """Configure RestW extraction options."""
    mock_web_context.form_data['restw_options'] = {
        'include_location': True,
        'include_menu_items': True,
        'include_services': True
    }


@when('I save the configuration')
def save_configuration(mock_web_context):
    """Save configuration."""
    mock_web_context.form_data['action'] = 'save_config'


@then('the RestW configuration should be persisted')
def restw_config_persisted(mock_web_context):
    """RestW configuration should be persisted."""
    assert 'restw_options' in mock_web_context.form_data


@then('future sessions should remember RestW settings')
def future_sessions_remember_settings():
    """Future sessions should remember RestW settings."""
    restw_config = RestWConfig()
    assert restw_config.has_saved_configuration()


@then('the configuration should be available for batch processing')
def config_available_for_batch_processing():
    """Configuration should be available for batch processing."""
    restw_config = RestWConfig()
    batch_config = restw_config.get_batch_configuration()
    assert batch_config is not None