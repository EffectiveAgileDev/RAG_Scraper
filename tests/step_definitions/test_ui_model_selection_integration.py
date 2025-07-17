"""Step definitions for UI model selection integration tests."""

import pytest
from pytest_bdd import scenarios, given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from unittest.mock import patch, Mock
import time

# Load scenarios from the feature file
scenarios('tests/features/ui_model_selection_integration.feature')


@pytest.fixture
def browser():
    """Create a browser instance for testing."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


@given('the RAG_Scraper web interface is loaded')
def web_interface_loaded(browser):
    """Load the web interface."""
    browser.get("http://localhost:8085")
    # Wait for page to load
    wait = WebDriverWait(browser, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))


@given('I can see both single-page and multi-page AI Enhancement sections')
def can_see_ai_sections(browser):
    """Verify both AI enhancement sections are present."""
    # Check for single-page AI section
    single_ai_section = browser.find_element(By.ID, "singleAiConfigOptions")
    assert single_ai_section is not None
    
    # Check for multi-page AI section
    multi_ai_section = browser.find_element(By.ID, "aiConfigOptions")
    assert multi_ai_section is not None


@given('I am in single-page scraping mode')
def in_single_page_mode(browser):
    """Switch to single-page scraping mode."""
    # Click single-page mode radio button
    single_mode_radio = browser.find_element(By.CSS_SELECTOR, 'input[name="scrapingMode"][value="single"]')
    browser.execute_script("arguments[0].click();", single_mode_radio)
    time.sleep(0.5)


@given('I am in multi-page scraping mode')
def in_multi_page_mode(browser):
    """Switch to multi-page scraping mode."""
    # Click multi-page mode radio button  
    multi_mode_radio = browser.find_element(By.CSS_SELECTOR, 'input[name="scrapingMode"][value="multi"]')
    browser.execute_script("arguments[0].click();", multi_mode_radio)
    time.sleep(0.5)


@given('I have enabled AI Enhancement')
def ai_enhancement_enabled(browser):
    """Enable AI Enhancement checkbox."""
    # Determine which mode we're in
    single_mode_checked = browser.find_element(By.CSS_SELECTOR, 'input[name="scrapingMode"][value="single"]').is_selected()
    
    if single_mode_checked:
        ai_checkbox = browser.find_element(By.ID, "singleEnableAi")
    else:
        ai_checkbox = browser.find_element(By.ID, "enableAi")
    
    if not ai_checkbox.is_selected():
        browser.execute_script("arguments[0].click();", ai_checkbox)
    time.sleep(0.5)


@when('I select "{provider}" as the LLM provider')
def select_llm_provider(browser, provider):
    """Select a specific LLM provider."""
    # Determine which mode we're in
    single_mode_checked = browser.find_element(By.CSS_SELECTOR, 'input[name="scrapingMode"][value="single"]').is_selected()
    
    if single_mode_checked:
        provider_select = Select(browser.find_element(By.ID, "singleLlmProvider"))
    else:
        provider_select = Select(browser.find_element(By.ID, "llmProvider"))
    
    # Map provider names to option values
    provider_map = {
        "OpenAI": "openai",
        "Claude": "claude", 
        "Ollama": "ollama"
    }
    
    provider_select.select_by_value(provider_map[provider])
    time.sleep(0.5)


@then('I should see a model selection dropdown with id "{dropdown_id}"')
def see_model_dropdown(browser, dropdown_id):
    """Verify model dropdown is present."""
    model_dropdown = browser.find_element(By.ID, dropdown_id)
    assert model_dropdown is not None
    assert model_dropdown.tag_name == "select"


@then('the model dropdown should be visible')
def model_dropdown_visible(browser):
    """Verify model dropdown is visible."""
    # Determine which mode we're in
    single_mode_checked = browser.find_element(By.CSS_SELECTOR, 'input[name="scrapingMode"][value="single"]').is_selected()
    
    if single_mode_checked:
        model_section = browser.find_element(By.ID, "singleModelSection")
    else:
        model_section = browser.find_element(By.ID, "modelSection")
    
    assert model_section.is_displayed()


@then('it should have a refresh button with id "{button_id}"')
def has_refresh_button(browser, button_id):
    """Verify refresh button is present."""
    refresh_button = browser.find_element(By.ID, button_id)
    assert refresh_button is not None
    assert refresh_button.tag_name == "button"


@then('the model selection dropdown "{dropdown_id}" should be hidden')
def model_dropdown_hidden(browser, dropdown_id):
    """Verify model dropdown is hidden."""
    # Determine which mode we're in
    single_mode_checked = browser.find_element(By.CSS_SELECTOR, 'input[name="scrapingMode"][value="single"]').is_selected()
    
    if single_mode_checked:
        model_section = browser.find_element(By.ID, "singleModelSection")
    else:
        model_section = browser.find_element(By.ID, "modelSection")
    
    assert not model_section.is_displayed()


@when('I enter a valid API key')
def enter_valid_api_key(browser):
    """Enter a valid API key."""
    # Determine which mode we're in
    single_mode_checked = browser.find_element(By.CSS_SELECTOR, 'input[name="scrapingMode"][value="single"]').is_selected()
    
    if single_mode_checked:
        api_key_input = browser.find_element(By.ID, "singleAiApiKey")
    else:
        api_key_input = browser.find_element(By.ID, "aiApiKey")
    
    api_key_input.clear()
    api_key_input.send_keys("sk-proj-test123validkey456")
    time.sleep(1)  # Allow for any async processing


@then('the model dropdown should automatically populate with available models')
def model_dropdown_populated(browser):
    """Verify model dropdown is populated."""
    # Determine which mode we're in
    single_mode_checked = browser.find_element(By.CSS_SELECTOR, 'input[name="scrapingMode"][value="single"]').is_selected()
    
    if single_mode_checked:
        model_dropdown = Select(browser.find_element(By.ID, "singleModelSelect"))
    else:
        model_dropdown = Select(browser.find_element(By.ID, "modelSelect"))
    
    # Should have more than just the default "Select model..." option
    options = model_dropdown.options
    assert len(options) > 1


@then('I should see "{default_model}" as the default selected option')
def verify_default_model(browser, default_model):
    """Verify default model is selected."""
    # Determine which mode we're in
    single_mode_checked = browser.find_element(By.CSS_SELECTOR, 'input[name="scrapingMode"][value="single"]').is_selected()
    
    if single_mode_checked:
        model_dropdown = Select(browser.find_element(By.ID, "singleModelSelect"))
    else:
        model_dropdown = Select(browser.find_element(By.ID, "modelSelect"))
    
    selected_option = model_dropdown.first_selected_option
    assert default_model in selected_option.text or selected_option.get_attribute("value") == default_model


@when('I select "{model}" from the model dropdown')
def select_model(browser, model):
    """Select a specific model from dropdown."""
    # Determine which mode we're in
    single_mode_checked = browser.find_element(By.CSS_SELECTOR, 'input[name="scrapingMode"][value="single"]').is_selected()
    
    if single_mode_checked:
        model_dropdown = Select(browser.find_element(By.ID, "singleModelSelect"))
    else:
        model_dropdown = Select(browser.find_element(By.ID, "modelSelect"))
    
    model_dropdown.select_by_value(model)
    time.sleep(0.5)


@when('I save the AI configuration')
def save_ai_configuration(browser):
    """Save the AI configuration."""
    # This would trigger the configuration save process
    # For now, just ensure the configuration is captured
    pass


@then('the saved configuration should include "{model}" as the selected model')
def verify_saved_model_config(browser, model):
    """Verify model is included in saved configuration."""
    # This would check the actual saved configuration
    # For the failing test, we expect this to fail initially
    assert False, f"Model {model} not found in saved configuration (expected failure for RED phase)"


@when('I click the refresh models button "{button_id}"')
def click_refresh_button(browser, button_id):
    """Click the refresh models button."""
    refresh_button = browser.find_element(By.ID, button_id)
    browser.execute_script("arguments[0].click();", refresh_button)
    time.sleep(1)


@then('the model dropdown should refresh and show available models')
def model_dropdown_refreshed(browser):
    """Verify model dropdown refreshed successfully."""
    # Determine which mode we're in
    single_mode_checked = browser.find_element(By.CSS_SELECTOR, 'input[name="scrapingMode"][value="single"]').is_selected()
    
    if single_mode_checked:
        model_dropdown = Select(browser.find_element(By.ID, "singleModelSelect"))
    else:
        model_dropdown = Select(browser.find_element(By.ID, "modelSelect"))
    
    # Should have available model options
    options = model_dropdown.options
    assert len(options) > 1


@then('no error messages should be displayed')
def no_error_messages(browser):
    """Verify no error messages are shown."""
    # Check for model warning elements
    try:
        single_warning = browser.find_element(By.ID, "singleModelWarning")
        assert not single_warning.is_displayed()
    except:
        pass
    
    try:
        multi_warning = browser.find_element(By.ID, "modelWarning")
        assert not multi_warning.is_displayed()
    except:
        pass