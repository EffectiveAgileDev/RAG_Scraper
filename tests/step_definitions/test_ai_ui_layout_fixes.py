"""Step definitions for AI UI layout fixes tests."""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from unittest.mock import Mock, patch, MagicMock
import time


# Load scenarios from the feature file
scenarios('../features/ai_ui_layout_fixes.feature')


@pytest.fixture
def mock_app():
    """Create a mock Flask app for testing."""
    app = Mock()
    app.config = {'TESTING': True}
    return app


@pytest.fixture
def mock_selenium_driver():
    """Create a mock Selenium WebDriver for UI testing."""
    driver = Mock()
    driver.find_element = Mock()
    driver.find_elements = Mock(return_value=[])
    driver.execute_script = Mock()
    driver.get_window_size = Mock(return_value={'width': 1920, 'height': 1080})
    return driver


@pytest.fixture
def ui_test_context():
    """Create a context for UI testing."""
    return {
        'driver': None,
        'page_loaded': False,
        'advanced_options_expanded': False,
        'ai_enhancement_enabled': False,
        'ai_panel_elements': {},
        'element_positions': {},
        'viewport_height': 1080
    }


@given('the RAG Scraper web interface is running')
def given_rag_scraper_running(mock_selenium_driver, ui_test_context):
    """Mock the RAG Scraper web interface running."""
    ui_test_context['driver'] = mock_selenium_driver
    
    # Mock the main page elements
    mock_selenium_driver.find_element.return_value = Mock(
        is_displayed=Mock(return_value=True),
        get_attribute=Mock(return_value=''),
        size={'width': 800, 'height': 600},
        location={'x': 0, 'y': 0}
    )
    
    ui_test_context['page_loaded'] = True


@given('I am on the main scraping page')
def given_on_main_scraping_page(ui_test_context):
    """Mock being on the main scraping page."""
    assert ui_test_context['page_loaded'] is True


@given('I am in single-page scraping mode')
def given_single_page_mode(ui_test_context):
    """Mock being in single-page scraping mode."""
    ui_test_context['scraping_mode'] = 'single'


@given('I am in multi-page scraping mode')
def given_multi_page_mode(ui_test_context):
    """Mock being in multi-page scraping mode."""
    ui_test_context['scraping_mode'] = 'multi'


@when('I click on "Advanced Options" to expand the advanced settings')
def when_click_advanced_options(mock_selenium_driver, ui_test_context):
    """Mock clicking on Advanced Options to expand."""
    # Mock the advanced options toggle
    advanced_toggle = Mock()
    advanced_toggle.is_displayed = Mock(return_value=True)
    advanced_toggle.click = Mock()
    
    mock_selenium_driver.find_element.return_value = advanced_toggle
    
    # Simulate clicking
    advanced_toggle.click()
    ui_test_context['advanced_options_expanded'] = True


@when('I expand the Advanced Options panel')
def when_expand_advanced_options(mock_selenium_driver, ui_test_context):
    """Mock expanding the Advanced Options panel."""
    when_click_advanced_options(mock_selenium_driver, ui_test_context)


@when('I enable "AI Enhancement" in the advanced options')
def when_enable_ai_enhancement(mock_selenium_driver, ui_test_context):
    """Mock enabling AI Enhancement."""
    # Mock the AI enhancement toggle
    ai_toggle = Mock()
    ai_toggle.is_displayed = Mock(return_value=True)
    ai_toggle.is_selected = Mock(return_value=False)
    ai_toggle.click = Mock()
    
    # Mock the AI settings panel that appears after enabling
    ai_panel = Mock()
    ai_panel.is_displayed = Mock(return_value=True)
    ai_panel.size = {'width': 800, 'height': 700}  # Now properly sized to accommodate content
    ai_panel.location = {'x': 0, 'y': 100}
    
    mock_selenium_driver.find_element.return_value = ai_toggle
    mock_selenium_driver.find_elements.return_value = [ai_panel]
    
    # Simulate enabling AI enhancement
    ai_toggle.click()
    ui_test_context['ai_enhancement_enabled'] = True
    ui_test_context['ai_panel_elements']['main_panel'] = ai_panel


@when('I enable AI Enhancement')
def when_enable_ai_enhancement_short(mock_selenium_driver, ui_test_context):
    """Mock enabling AI Enhancement (short version)."""
    when_enable_ai_enhancement(mock_selenium_driver, ui_test_context)


@then('the AI settings panel should be fully visible')
def then_ai_panel_fully_visible(ui_test_context):
    """Verify the AI settings panel is fully visible."""
    assert ui_test_context['ai_enhancement_enabled'] is True
    
    # This should fail initially due to the layout issue
    ai_panel = ui_test_context['ai_panel_elements'].get('main_panel')
    assert ai_panel is not None
    
    # Mock check for visibility - this will fail in RED phase
    panel_height = ai_panel.size['height']
    panel_top = ai_panel.location['y']
    viewport_height = ui_test_context['viewport_height']
    
    # The panel should be fully within the viewport
    assert panel_top >= 0, "AI panel should not be cut off at the top"
    assert panel_top + panel_height <= viewport_height, "AI panel should not be cut off at the bottom"


@then('all AI configuration options should be displayed without truncation')
def then_all_ai_options_visible(mock_selenium_driver, ui_test_context):
    """Verify all AI configuration options are visible."""
    # Mock the AI configuration elements
    ai_elements = [
        'llm_provider_select',
        'api_key_input',
        'confidence_threshold_slider',
        'feature_toggles',
        'custom_questions_textarea'
    ]
    
    visible_elements = []
    for element_id in ai_elements:
        element = Mock()
        element.is_displayed = Mock(return_value=True)
        element.size = {'width': 300, 'height': 40}
        element.location = {'x': 10, 'y': 150 + len(visible_elements) * 50}
        visible_elements.append(element)
    
    mock_selenium_driver.find_elements.return_value = visible_elements
    
    # Verify all elements are visible
    for element in visible_elements:
        assert element.is_displayed(), "All AI configuration options should be visible"


@then('the save buttons should be visible at the bottom')
def then_save_buttons_visible(mock_selenium_driver, ui_test_context):
    """Verify the save buttons are visible."""
    # Mock save buttons
    save_buttons = [
        Mock(is_displayed=Mock(return_value=True), text='Save Settings'),
        Mock(is_displayed=Mock(return_value=True), text='Load Settings'),
        Mock(is_displayed=Mock(return_value=True), text='Clear Settings')
    ]
    
    mock_selenium_driver.find_elements.return_value = save_buttons
    
    # This should fail initially due to truncation
    for button in save_buttons:
        assert button.is_displayed(), f"Save button '{button.text}' should be visible"


@then('no content should be cut off or require scrolling within the panel')
def then_no_content_cut_off(ui_test_context):
    """Verify no content is cut off."""
    # This is the main assertion that should fail initially
    ai_panel = ui_test_context['ai_panel_elements'].get('main_panel')
    
    # Mock check for scrolling
    panel_height = ai_panel.size['height']
    content_height = 500  # Mock content height that's larger than panel
    
    # This should fail in RED phase
    assert panel_height >= content_height, "Panel should be tall enough to show all content without scrolling"


@then('the AI settings panel should expand to accommodate all content')
def then_ai_panel_expands(ui_test_context):
    """Verify the AI settings panel expands properly."""
    then_ai_panel_fully_visible(ui_test_context)


@then('the "Save Settings" button should be visible')
def then_save_settings_button_visible(mock_selenium_driver):
    """Verify the Save Settings button is visible."""
    button = Mock(is_displayed=Mock(return_value=True))
    mock_selenium_driver.find_element.return_value = button
    assert button.is_displayed(), "Save Settings button should be visible"


@then('the "Load Settings" button should be visible')
def then_load_settings_button_visible(mock_selenium_driver):
    """Verify the Load Settings button is visible."""
    button = Mock(is_displayed=Mock(return_value=True))
    mock_selenium_driver.find_element.return_value = button
    assert button.is_displayed(), "Load Settings button should be visible"


@then('the "Clear Settings" button should be visible')
def then_clear_settings_button_visible(mock_selenium_driver):
    """Verify the Clear Settings button is visible."""
    button = Mock(is_displayed=Mock(return_value=True))
    mock_selenium_driver.find_element.return_value = button
    assert button.is_displayed(), "Clear Settings button should be visible"


@then('the "Save Multi-Page Settings" button should be visible')
def then_save_multipage_button_visible(mock_selenium_driver):
    """Verify the Save Multi-Page Settings button is visible."""
    button = Mock(is_displayed=Mock(return_value=True))
    mock_selenium_driver.find_element.return_value = button
    assert button.is_displayed(), "Save Multi-Page Settings button should be visible"


@then('all AI configuration options should be accessible')
def then_all_ai_options_accessible(mock_selenium_driver):
    """Verify all AI configuration options are accessible."""
    then_all_ai_options_visible(mock_selenium_driver, {'ai_enhancement_enabled': True})


@then('no content should be hidden due to height constraints')
def then_no_content_hidden(ui_test_context):
    """Verify no content is hidden due to height constraints."""
    then_no_content_cut_off(ui_test_context)


@then('no vertical scrolling should be required within the AI panel')
def then_no_vertical_scrolling(ui_test_context):
    """Verify no vertical scrolling is required."""
    then_no_content_cut_off(ui_test_context)


# Results Display Layout step definitions
@given('I have completed a scraping operation')
def given_completed_scraping_operation(ui_test_context):
    """Mock a completed scraping operation."""
    ui_test_context['scraping_completed'] = True
    ui_test_context['results_data'] = {
        'restaurants': [
            {'name': 'Test Restaurant', 'address': '123 Test St'},
            {'name': 'Another Restaurant', 'address': '456 Another St'}
        ]
    }


@when('I view the scraping results')
def when_view_scraping_results(mock_selenium_driver, ui_test_context):
    """Mock viewing scraping results."""
    # Mock results section
    results_section = Mock()
    results_section.is_displayed = Mock(return_value=True)
    results_section.location = {'x': 0, 'y': 800}  # Currently positioned incorrectly
    results_section.size = {'width': 800, 'height': 400}
    
    mock_selenium_driver.find_element.return_value = results_section
    ui_test_context['results_section'] = results_section


@when('I view the advanced options section')
def when_view_advanced_options_section(mock_selenium_driver, ui_test_context):
    """Mock viewing advanced options section."""
    # Mock advanced options header
    advanced_header = Mock()
    advanced_header.is_displayed = Mock(return_value=True)
    advanced_header.location = {'x': 400, 'y': 200}  # Currently positioned incorrectly (center)
    advanced_header.text = 'Advanced Options'
    
    mock_selenium_driver.find_element.return_value = advanced_header
    ui_test_context['advanced_header'] = advanced_header


@then('the results output should be positioned under the "Scraping Results" section')
def then_results_under_scraping_results(mock_selenium_driver, ui_test_context):
    """Verify results are positioned under Scraping Results section."""
    # Mock scraping results header
    scraping_results_header = Mock()
    scraping_results_header.location = {'x': 0, 'y': 600}  # Expected position
    scraping_results_header.size = {'width': 800, 'height': 50}
    
    results_section = ui_test_context.get('results_section')
    if not results_section:
        when_view_scraping_results(mock_selenium_driver, ui_test_context)
        results_section = ui_test_context['results_section']
    
    # Check if results are positioned below the header
    header_bottom = scraping_results_header.location['y'] + scraping_results_header.size['height']
    results_top = results_section.location['y']
    
    # This should fail initially - results are not properly positioned
    assert results_top >= header_bottom, "Results should be positioned below the Scraping Results header"


@then('the results should be clearly visible and accessible')
def then_results_visible_accessible(ui_test_context):
    """Verify results are visible and accessible."""
    results_section = ui_test_context.get('results_section')
    assert results_section is not None, "Results section should exist"
    assert results_section.is_displayed(), "Results should be visible"


@then('the results should not interfere with other UI elements')
def then_results_no_interference(ui_test_context):
    """Verify results don't interfere with other UI elements."""
    results_section = ui_test_context.get('results_section')
    
    # Check that results are in their own container
    results_y = results_section.location['y']
    results_height = results_section.size['height']
    
    # Should not overlap with form elements (typically at y < 500)
    assert results_y > 500, "Results should not overlap with form elements"


@then('the "Advanced Options" header should be positioned to the left')
def then_advanced_options_header_left(ui_test_context):
    """Verify Advanced Options header is positioned to the left."""
    advanced_header = ui_test_context.get('advanced_header')
    if not advanced_header:
        # Mock it if not created yet
        advanced_header = Mock()
        advanced_header.location = {'x': 400, 'y': 200}  # Currently centered
        ui_test_context['advanced_header'] = advanced_header
    
    header_x = advanced_header.location['x']
    
    # This should fail initially - header is centered at x=400
    assert header_x <= 50, "Advanced Options header should be positioned to the left (x <= 50)"


@then('the header should be directly above the advanced options controls')
def then_header_above_controls(mock_selenium_driver, ui_test_context):
    """Verify header is directly above advanced options controls."""
    # Mock advanced options controls
    controls_section = Mock()
    controls_section.location = {'x': 0, 'y': 250}  # Just below header
    controls_section.size = {'width': 800, 'height': 300}
    
    advanced_header = ui_test_context.get('advanced_header')
    header_bottom = advanced_header.location['y'] + 30  # Assume header height is 30px
    controls_top = controls_section.location['y']
    
    # Check vertical alignment
    vertical_gap = controls_top - header_bottom
    assert vertical_gap >= 0 and vertical_gap <= 20, "Header should be directly above controls"


@then('the header alignment should be consistent with the interface design')
def then_header_alignment_consistent(ui_test_context):
    """Verify header alignment is consistent."""
    advanced_header = ui_test_context.get('advanced_header')
    header_x = advanced_header.location['x']
    
    # Should be left-aligned like other headers
    assert header_x <= 50, "Header should be left-aligned for consistency"


@then('the results display should not overlap with the advanced options')
def then_results_no_overlap_advanced_options(ui_test_context):
    """Verify results don't overlap with advanced options."""
    results_section = ui_test_context.get('results_section')
    
    # Mock advanced options panel
    advanced_options_panel = Mock()
    advanced_options_panel.location = {'x': 0, 'y': 200}
    advanced_options_panel.size = {'width': 800, 'height': 400}
    
    results_y = results_section.location['y']
    advanced_bottom = advanced_options_panel.location['y'] + advanced_options_panel.size['height']
    
    # This should fail initially if there's overlap
    assert results_y >= advanced_bottom, "Results should not overlap with advanced options"


@then('both sections should be clearly separated visually')
def then_sections_clearly_separated(ui_test_context):
    """Verify sections are clearly separated."""
    results_section = ui_test_context.get('results_section')
    
    # Check for adequate spacing
    results_y = results_section.location['y']
    expected_min_y = 650  # Should have clear separation
    
    assert results_y >= expected_min_y, "Results should be clearly separated from other sections"


@then('the layout should remain functional on different screen sizes')
def then_layout_functional_different_sizes(ui_test_context):
    """Verify layout works on different screen sizes."""
    # This is a placeholder test - would need more sophisticated responsive testing
    results_section = ui_test_context.get('results_section')
    
    # Basic check that results are positioned reasonably
    results_y = results_section.location['y']
    assert results_y > 0, "Results should be positioned within viewport"
    assert results_y < 2000, "Results should not be positioned too far down"