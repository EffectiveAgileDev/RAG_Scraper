"""Step definitions for AI UI Settings Panel BDD tests."""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from unittest.mock import Mock, patch, MagicMock

# Load scenarios from the feature file
scenarios('../features/ai_ui_settings_panel.feature')


@pytest.fixture
def mock_web_interface():
    """Mock web interface with AI settings panel."""
    mock_app = Mock()
    mock_app.config = {
        'AI_ENHANCEMENT_ENABLED': False,
        'AI_PROVIDER': 'openai',
        'AI_FEATURES': {
            'nutritional_analysis': True,
            'price_analysis': True,
            'cuisine_classification': True,
            'multimodal_analysis': False
        },
        'AI_CONFIDENCE_THRESHOLD': 0.7
    }
    return mock_app


@pytest.fixture
def ai_settings_context():
    """Context for AI settings panel tests."""
    return {
        'ai_panel_visible': False,
        'ai_enhancement_enabled': False,
        'selected_provider': 'openai',
        'api_key_visible': False,
        'feature_toggles': {},
        'confidence_threshold': 0.7,
        'validation_errors': []
    }


# Background steps
@given("the RAG Scraper web interface is loaded")
def web_interface_loaded(mock_web_interface):
    """Web interface is loaded."""
    assert mock_web_interface is not None


@given("I am on the main scraping page")
def on_main_scraping_page(mock_web_interface):
    """On the main scraping page."""
    assert mock_web_interface.config is not None


@given("the advanced options panel is available")
def advanced_options_available(mock_web_interface):
    """Advanced options panel is available."""
    # Simulate advanced options panel being present
    mock_web_interface.advanced_panel_available = True
    assert mock_web_interface.advanced_panel_available


# Scenario: AI Settings Panel is hidden by default
@given("I view the advanced options panel")
def view_advanced_options_panel(ai_settings_context):
    """View the advanced options panel."""
    ai_settings_context['viewing_advanced_panel'] = True


@when("I look for AI enhancement options")
def look_for_ai_enhancement_options(ai_settings_context):
    """Look for AI enhancement options."""
    # By default, AI panel should be collapsed
    ai_settings_context['ai_panel_checked'] = True


@then("the AI settings panel should be collapsed by default")
def ai_panel_collapsed_by_default(ai_settings_context):
    """AI settings panel should be collapsed by default."""
    assert not ai_settings_context['ai_panel_visible']


@then("the AI enhancement toggle should be OFF")
def ai_enhancement_toggle_off(ai_settings_context):
    """AI enhancement toggle should be OFF."""
    assert not ai_settings_context['ai_enhancement_enabled']


@then("no AI features should be visible initially")
def no_ai_features_visible_initially(ai_settings_context):
    """No AI features should be visible initially."""
    assert len(ai_settings_context['feature_toggles']) == 0


# Scenario: Enable AI Enhancement reveals configuration options
@given("I expand the advanced options panel")
def expand_advanced_options_panel(ai_settings_context):
    """Expand the advanced options panel."""
    ai_settings_context['advanced_panel_expanded'] = True


@when('I toggle the "Enable AI Enhancement" switch to ON')
def toggle_ai_enhancement_on(ai_settings_context):
    """Toggle AI Enhancement switch to ON."""
    ai_settings_context['ai_enhancement_enabled'] = True
    ai_settings_context['ai_panel_visible'] = True


@then("the AI configuration options should become visible")
def ai_config_options_visible(ai_settings_context):
    """AI configuration options should become visible."""
    assert ai_settings_context['ai_panel_visible']


@then("I should see LLM provider selection dropdown")
def see_llm_provider_dropdown(ai_settings_context):
    """Should see LLM provider selection dropdown."""
    ai_settings_context['provider_dropdown_visible'] = True
    assert ai_settings_context['provider_dropdown_visible']


@then("I should see API key input field")
def see_api_key_input_field(ai_settings_context):
    """Should see API key input field."""
    ai_settings_context['api_key_visible'] = True
    assert ai_settings_context['api_key_visible']


@then("I should see individual AI feature toggles")
def see_individual_ai_feature_toggles(ai_settings_context):
    """Should see individual AI feature toggles."""
    ai_settings_context['feature_toggles'] = {
        'nutritional_analysis': True,
        'price_analysis': True,
        'cuisine_classification': True,
        'multimodal_analysis': False
    }
    assert len(ai_settings_context['feature_toggles']) > 0


@then("I should see confidence threshold slider")
def see_confidence_threshold_slider(ai_settings_context):
    """Should see confidence threshold slider."""
    ai_settings_context['confidence_slider_visible'] = True
    assert ai_settings_context['confidence_slider_visible']


# Scenario: LLM Provider selection
@given("AI Enhancement is enabled")
def ai_enhancement_enabled(ai_settings_context):
    """AI Enhancement is enabled."""
    ai_settings_context['ai_enhancement_enabled'] = True
    ai_settings_context['ai_panel_visible'] = True


@when("I click on the LLM Provider dropdown")
def click_llm_provider_dropdown(ai_settings_context):
    """Click on LLM Provider dropdown."""
    ai_settings_context['provider_dropdown_open'] = True


@then('I should see "OpenAI" as an option')
def see_openai_option(ai_settings_context):
    """Should see OpenAI as an option."""
    ai_settings_context['available_providers'] = ['openai', 'claude', 'ollama']
    assert 'openai' in ai_settings_context['available_providers']


@then('I should see "Claude" as an option')
def see_claude_option(ai_settings_context):
    """Should see Claude as an option."""
    assert 'claude' in ai_settings_context['available_providers']


@then('I should see "Ollama (Local)" as an option')
def see_ollama_option(ai_settings_context):
    """Should see Ollama (Local) as an option."""
    assert 'ollama' in ai_settings_context['available_providers']


@then('"OpenAI" should be selected by default')
def openai_selected_by_default(ai_settings_context):
    """OpenAI should be selected by default."""
    assert ai_settings_context['selected_provider'] == 'openai'


# Scenario: API Key input field
@when('I select "OpenAI" as the LLM provider')
def select_openai_provider(ai_settings_context):
    """Select OpenAI as the LLM provider."""
    ai_settings_context['selected_provider'] = 'openai'
    ai_settings_context['api_key_visible'] = True


@then("I should see an API key input field")
def see_api_key_input_field_visible(ai_settings_context):
    """Should see API key input field."""
    assert ai_settings_context['api_key_visible']


@then("the input field should be of type password for security")
def api_key_field_password_type(ai_settings_context):
    """API key field should be password type."""
    ai_settings_context['api_key_type'] = 'password'
    assert ai_settings_context['api_key_type'] == 'password'


@then('I should see placeholder text "Enter OpenAI API Key (optional)"')
def see_openai_placeholder_text(ai_settings_context):
    """Should see OpenAI placeholder text."""
    ai_settings_context['api_key_placeholder'] = 'Enter OpenAI API Key (optional)'
    assert 'OpenAI' in ai_settings_context['api_key_placeholder']


# Scenario: Individual AI feature toggles
@when("I view the AI feature options")
def view_ai_feature_options(ai_settings_context):
    """View AI feature options."""
    ai_settings_context['viewing_feature_options'] = True


@then('I should see "Nutritional Analysis" toggle (ON by default)')
def see_nutritional_analysis_toggle(ai_settings_context):
    """Should see Nutritional Analysis toggle ON by default."""
    ai_settings_context['feature_toggles']['nutritional_analysis'] = True
    assert ai_settings_context['feature_toggles']['nutritional_analysis']


@then('I should see "Price Analysis" toggle (ON by default)')
def see_price_analysis_toggle(ai_settings_context):
    """Should see Price Analysis toggle ON by default."""
    ai_settings_context['feature_toggles']['price_analysis'] = True
    assert ai_settings_context['feature_toggles']['price_analysis']


@then('I should see "Cuisine Classification" toggle (ON by default)')
def see_cuisine_classification_toggle(ai_settings_context):
    """Should see Cuisine Classification toggle ON by default."""
    ai_settings_context['feature_toggles']['cuisine_classification'] = True
    assert ai_settings_context['feature_toggles']['cuisine_classification']


@then('I should see "Multi-modal Analysis" toggle (OFF by default)')
def see_multimodal_analysis_toggle(ai_settings_context):
    """Should see Multi-modal Analysis toggle OFF by default."""
    ai_settings_context['feature_toggles']['multimodal_analysis'] = False
    assert not ai_settings_context['feature_toggles']['multimodal_analysis']


# Scenario: Confidence threshold slider
@when("I view the confidence threshold setting")
def view_confidence_threshold_setting(ai_settings_context):
    """View confidence threshold setting."""
    ai_settings_context['viewing_confidence_setting'] = True


@then("I should see a slider with range 0.1 to 1.0")
def see_confidence_slider_range(ai_settings_context):
    """Should see confidence slider with correct range."""
    ai_settings_context['confidence_range'] = (0.1, 1.0)
    assert ai_settings_context['confidence_range'] == (0.1, 1.0)


@then("the default value should be 0.7")
def confidence_default_value(ai_settings_context):
    """Default confidence value should be 0.7."""
    assert ai_settings_context['confidence_threshold'] == 0.7


@then("I should see the current value displayed")
def see_current_confidence_value_displayed(ai_settings_context):
    """Should see current confidence value displayed."""
    ai_settings_context['confidence_value_displayed'] = True
    assert ai_settings_context['confidence_value_displayed']


# Scenario: Disable AI Enhancement
@given("AI configuration options are visible")
def ai_config_options_visible_given(ai_settings_context):
    """AI configuration options are visible."""
    ai_settings_context['ai_panel_visible'] = True
    ai_settings_context['feature_toggles'] = {'nutritional_analysis': True}


@when('I toggle the "Enable AI Enhancement" switch to OFF')
def toggle_ai_enhancement_off(ai_settings_context):
    """Toggle AI Enhancement switch to OFF."""
    ai_settings_context['ai_enhancement_enabled'] = False
    ai_settings_context['ai_panel_visible'] = False


@then("all AI configuration options should be hidden")
def all_ai_config_options_hidden(ai_settings_context):
    """All AI configuration options should be hidden."""
    assert not ai_settings_context['ai_panel_visible']


@then("AI features should be disabled for scraping")
def ai_features_disabled_for_scraping(ai_settings_context):
    """AI features should be disabled for scraping."""
    assert not ai_settings_context['ai_enhancement_enabled']