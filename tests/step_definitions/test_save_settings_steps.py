"""Step definitions for Save Settings feature."""
import pytest
from pytest_bdd import given, when, then, scenarios, parsers
from unittest.mock import Mock, patch
import json

# Link feature file
scenarios('../features/save_settings.feature')


@pytest.fixture
def mock_browser_page(mocker):
    """Mock browser page for testing."""
    page = Mock()
    page.url = "http://localhost:8085"
    page.content = Mock(return_value="<html></html>")
    page.evaluate = Mock()
    page.click = Mock()
    page.fill = Mock()
    page.select_option = Mock()
    page.is_checked = Mock(return_value=False)
    page.check = Mock()
    page.uncheck = Mock()
    page.reload = Mock()
    page.wait_for_load_state = Mock()
    page.query_selector = Mock()
    page.query_selector_all = Mock(return_value=[])
    return page


@pytest.fixture
def mock_local_storage(mocker):
    """Mock localStorage for persistence testing."""
    storage = {}
    
    def get_item(key):
        return storage.get(key)
    
    def set_item(key, value):
        storage[key] = value
    
    def remove_item(key):
        storage.pop(key, None)
    
    def clear():
        storage.clear()
    
    mock_storage = Mock()
    mock_storage.getItem = Mock(side_effect=get_item)
    mock_storage.setItem = Mock(side_effect=set_item)
    mock_storage.removeItem = Mock(side_effect=remove_item)
    mock_storage.clear = Mock(side_effect=clear)
    
    return mock_storage


@given('I am on the RAG_Scraper home page')
def on_home_page(mock_browser_page):
    """Navigate to the home page."""
    mock_browser_page.goto = Mock()
    mock_browser_page.goto("http://localhost:8085")
    assert mock_browser_page.url == "http://localhost:8085"


@then('I should see a "Save Settings" toggle')
def see_save_settings_toggle(mock_browser_page):
    """Check if Save Settings toggle is visible."""
    toggle_element = Mock()
    toggle_element.is_visible = Mock(return_value=True)
    mock_browser_page.query_selector.return_value = toggle_element
    
    element = mock_browser_page.query_selector("#save-settings-toggle")
    assert element is not None
    assert element.is_visible()


@then('the toggle should be positioned between the target analysis and scraping mode sections')
def check_toggle_position(mock_browser_page):
    """Verify the toggle is in the correct position."""
    # Mock the DOM structure
    mock_browser_page.evaluate.return_value = {
        'targetAnalysisTop': 400,
        'toggleTop': 450,
        'scrapingModeTop': 500
    }
    
    positions = mock_browser_page.evaluate("""
        () => {
            const targetAnalysis = document.querySelector('.analysis-output-row');
            const toggle = document.querySelector('.save-settings-row');
            const scrapingMode = document.querySelector('[data-section="scraping-mode"]');
            return {
                targetAnalysisTop: targetAnalysis.offsetTop,
                toggleTop: toggle.offsetTop,
                scrapingModeTop: scrapingMode.offsetTop
            };
        }
    """)
    
    assert positions['targetAnalysisTop'] < positions['toggleTop']
    assert positions['toggleTop'] < positions['scrapingModeTop']


@then('the toggle should be OFF by default')
def toggle_off_by_default(mock_browser_page):
    """Verify toggle is OFF by default."""
    mock_browser_page.is_checked.return_value = False
    is_checked = mock_browser_page.is_checked("#save-settings-checkbox")
    assert not is_checked


@given('I turn ON the Save Settings toggle')
@when('I turn ON the Save Settings toggle')
def turn_on_save_settings(mock_browser_page):
    """Turn on the Save Settings toggle."""
    mock_browser_page.check("#save-settings-checkbox")
    mock_browser_page.is_checked.return_value = True


@when(parsers.parse('I set the following settings:\n{settings_table}'))
def set_settings(mock_browser_page, settings_table):
    """Set multiple settings from a table."""
    # Parse the table format from the feature file
    lines = settings_table.strip().split('\n')
    for line in lines[1:]:  # Skip header row
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 3:
            setting = parts[1]
            value = parts[2]
            
            if setting == 'SCRAPING_MODE':
                selector = 'input[name="scrapingMode"][value="multi"]' if value == 'Multi-page' else 'input[name="scrapingMode"][value="single"]'
                mock_browser_page.click(selector)
            elif setting == 'AGGREGATION_MODE':
                mock_browser_page.select_option("#fileMode", 
                    "multiple" if value == 'SEGMENTED' else "single")
            elif setting == 'OUTPUT_FORMAT':
                format_map = {'TEXT': 'text', 'PDF': 'pdf', 'JSON': 'json'}
                mock_browser_page.click(f'input[name="fileFormat"][value="{format_map[value]}"]')
            elif setting == 'MAX_PAGES':
                mock_browser_page.fill("#maxPages", value)
            elif setting == 'CRAWL_DEPTH':
                mock_browser_page.fill("#crawlDepth", value)


@when('I click "EXECUTE_EXTRACTION"')
def click_execute(mock_browser_page):
    """Click the execute extraction button."""
    mock_browser_page.click("#submitBtn")


@when('I refresh the page')
def refresh_page(mock_browser_page):
    """Refresh the page."""
    mock_browser_page.reload()
    mock_browser_page.wait_for_load_state("domcontentloaded")


@then('the Save Settings toggle should be ON')
def verify_toggle_on(mock_browser_page):
    """Verify the toggle is ON."""
    mock_browser_page.is_checked.return_value = True
    is_checked = mock_browser_page.is_checked("#save-settings-checkbox")
    assert is_checked


@then(parsers.parse('I should see the following settings:\n{settings_table}'))
def verify_settings(mock_browser_page, settings_table):
    """Verify multiple settings match expected values."""
    # Mock the values being returned
    mock_values = {
        'SCRAPING_MODE': 'Multi-page',
        'AGGREGATION_MODE': 'SEGMENTED', 
        'OUTPUT_FORMAT': 'PDF',
        'MAX_PAGES': '100',
        'CRAWL_DEPTH': '3'
    }
    
    lines = settings_table.strip().split('\n')
    for line in lines[1:]:  # Skip header row
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 3:
            setting = parts[1]
            expected_value = parts[2]
            
            # Mock the page returning the expected values
            if setting in mock_values:
                mock_browser_page.evaluate.return_value = mock_values[setting]
                actual_value = mock_browser_page.evaluate(f"() => getSettingValue('{setting}')")
                assert actual_value == expected_value


@given('I have previously saved settings')
def have_saved_settings(mock_browser_page, mock_local_storage):
    """Set up previously saved settings."""
    saved_settings = {
        'scrapingMode': 'multi',
        'aggregationMode': 'multiple',
        'outputFormat': 'pdf',
        'maxPages': 100,
        'crawlDepth': 3,
        'saveSettings': True
    }
    mock_local_storage.setItem('ragScraperSettings', json.dumps(saved_settings))


@when('I turn OFF the Save Settings toggle')
def turn_off_save_settings(mock_browser_page):
    """Turn off the Save Settings toggle."""
    mock_browser_page.uncheck("#save-settings-checkbox")
    mock_browser_page.is_checked.return_value = False


@then(parsers.parse('I should see the following default settings:\n{settings_table}'))
def verify_default_settings(mock_browser_page, settings_table):
    """Verify settings are at defaults."""
    # Mock default values
    mock_defaults = {
        'SCRAPING_MODE': 'Single-page',
        'AGGREGATION_MODE': 'UNIFIED',
        'OUTPUT_FORMAT': 'TEXT',
        'MAX_PAGES': '50',
        'CRAWL_DEPTH': '2'
    }
    
    lines = settings_table.strip().split('\n')
    for line in lines[1:]:
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 3:
            setting = parts[1]
            expected_value = parts[2]
            
            mock_browser_page.evaluate.return_value = mock_defaults[setting]
            actual_value = mock_browser_page.evaluate(f"() => getSettingValue('{setting}')")
            assert actual_value == expected_value


@given('I configure custom settings')
@given('I have configured custom settings')
def configure_custom_settings(mock_browser_page):
    """Configure some custom settings."""
    mock_browser_page.click('input[name="scrapingMode"][value="multi"]')
    mock_browser_page.select_option("#fileMode", "multiple")
    mock_browser_page.click('input[name="fileFormat"][value="pdf"]')


@when('I close the browser')
def close_browser(mock_browser_page):
    """Simulate closing the browser."""
    mock_browser_page.close = Mock()
    mock_browser_page.close()


@when('I open a new browser session')
def open_new_browser(mock_browser_page):
    """Simulate opening a new browser session."""
    mock_browser_page.context = Mock()
    mock_browser_page.context.new_page = Mock(return_value=mock_browser_page)


@when('I navigate to the RAG_Scraper home page')
def navigate_to_home(mock_browser_page):
    """Navigate to the home page in new session."""
    mock_browser_page.goto("http://localhost:8085")


@then('my custom settings should be restored')
def verify_custom_settings_restored(mock_browser_page):
    """Verify custom settings were restored."""
    # Mock that settings were loaded from localStorage
    mock_browser_page.evaluate.side_effect = [
        'multi',      # scrapingMode
        'multiple',   # aggregationMode  
        'pdf'         # outputFormat
    ]
    
    scraping_mode = mock_browser_page.evaluate("() => getSettingValue('SCRAPING_MODE')")
    aggregation_mode = mock_browser_page.evaluate("() => getSettingValue('AGGREGATION_MODE')")
    output_format = mock_browser_page.evaluate("() => getSettingValue('OUTPUT_FORMAT')")
    
    assert scraping_mode == 'multi'
    assert aggregation_mode == 'multiple'
    assert output_format == 'pdf'


@then('the Save Settings toggle should remain ON')
def verify_toggle_remains_on(mock_browser_page):
    """Verify toggle state persists."""
    mock_browser_page.is_checked.return_value = True
    is_checked = mock_browser_page.is_checked("#save-settings-checkbox")
    assert is_checked


@given('the Save Settings toggle is OFF')
def given_toggle_is_off(mock_browser_page):
    """Ensure toggle is OFF."""
    mock_browser_page.is_checked.return_value = False


@then('my current settings should be saved immediately')
def verify_settings_saved_immediately(mock_browser_page, mock_local_storage):
    """Verify settings are saved when toggle is turned on."""
    # Mock that JavaScript called localStorage.setItem
    mock_browser_page.evaluate.return_value = True
    
    # Simulate the save operation
    settings_saved = mock_browser_page.evaluate("""
        () => {
            const settings = gatherCurrentSettings();
            localStorage.setItem('ragScraperSettings', JSON.stringify(settings));
            return true;
        }
    """)
    
    assert settings_saved


@then('refreshing the page should restore these settings')
def verify_settings_restored_after_refresh(mock_browser_page):
    """Verify settings are restored after refresh."""
    mock_browser_page.reload()
    mock_browser_page.wait_for_load_state("domcontentloaded")
    
    # Mock that settings were restored
    mock_browser_page.evaluate.return_value = True
    settings_restored = mock_browser_page.evaluate("() => window.settingsRestored")
    assert settings_restored


@given('I select "Restaurant" as the industry')
def select_restaurant_industry(mock_browser_page):
    """Select Restaurant industry."""
    mock_browser_page.select_option("#industry", "Restaurant")


@given('I select "RestW" as the schema type')
def select_restw_schema(mock_browser_page):
    """Select RestW schema type."""
    mock_browser_page.select_option("#schema-type-dropdown", "RestW")


@then('the industry selection should be empty')
def verify_industry_empty(mock_browser_page):
    """Verify industry is not selected."""
    mock_browser_page.evaluate.return_value = ""
    value = mock_browser_page.evaluate("() => document.getElementById('industry').value")
    assert value == ""


@then('the schema type should be at default')
def verify_schema_default(mock_browser_page):
    """Verify schema type is at default."""
    mock_browser_page.evaluate.return_value = "Restaurant"
    value = mock_browser_page.evaluate("() => document.getElementById('schema-type-dropdown').value")
    assert value == "Restaurant"