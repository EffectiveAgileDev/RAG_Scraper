"""Step definitions for AI checkbox state defect testing."""

import json
import time
from unittest.mock import Mock, patch, MagicMock
import pytest
from pytest_bdd import given, when, then, scenario, parsers
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# Scenario loading
@scenario('../features/ai_checkbox_state_defect.feature', 'AI Enhancement checkbox checked state is properly recognized')
def test_ai_checkbox_checked_state():
    pass


@scenario('../features/ai_checkbox_state_defect.feature', 'AI Enhancement checkbox enables AI processing')
def test_ai_checkbox_enables_processing():
    pass


@scenario('../features/ai_checkbox_state_defect.feature', 'AI Enhancement checkbox state persists during scraping')
def test_ai_checkbox_state_persists():
    pass


@scenario('../features/ai_checkbox_state_defect.feature', 'AI Enhancement checkbox unchecked state is properly recognized')
def test_ai_checkbox_unchecked_state():
    pass


@scenario('../features/ai_checkbox_state_defect.feature', 'AI Enhancement checkbox state matches internal configuration')
def test_ai_checkbox_matches_internal_state():
    pass


@scenario('../features/ai_checkbox_state_defect.feature', 'AI Enhancement checkbox works in both single-page and multi-page modes')
def test_ai_checkbox_both_modes():
    pass


# Test context class
class UITestContext:
    def __init__(self):
        self.driver = None
        self.base_url = "http://localhost:8085"
        self.ai_checkbox = None
        self.ai_panel = None
        self.error_messages = []
        self.ai_config = None
        self.current_mode = "multi"
        self.scraping_request_data = None


@pytest.fixture
def ui_context():
    """UI test context fixture with Selenium WebDriver."""
    ctx = UITestContext()
    
    # Set up Chrome WebDriver with headless option for CI
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        ctx.driver = webdriver.Chrome(options=chrome_options)
        ctx.driver.implicitly_wait(10)
    except Exception as e:
        # If Chrome is not available, skip these tests
        pytest.skip(f"Chrome WebDriver not available: {e}")
    
    yield ctx
    
    # Cleanup
    if ctx.driver:
        ctx.driver.quit()


# Step definitions
@given('the RAG_Scraper web interface is loaded')
def web_interface_loaded(ui_context):
    """Load the RAG_Scraper web interface."""
    try:
        ui_context.driver.get(ui_context.base_url)
        
        # Wait for the page to load completely
        WebDriverWait(ui_context.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Verify the page title or a key element
        assert "RAG_Scraper" in ui_context.driver.title or \
               ui_context.driver.find_element(By.CLASS_NAME, "title"), \
               "RAG_Scraper interface did not load properly"
        
    except Exception as e:
        pytest.fail(f"Failed to load web interface: {e}")


@given('I am in multi-page scraping mode')
def in_multipage_mode(ui_context):
    """Ensure we are in multi-page scraping mode."""
    try:
        # Click on multi-page mode if not already selected
        multipage_radio = ui_context.driver.find_element(By.CSS_SELECTOR, "input[name='scrapingMode'][value='multi']")
        if not multipage_radio.is_selected():
            multipage_radio.click()
        
        ui_context.current_mode = "multi"
        
        # Wait for multi-page options to appear
        WebDriverWait(ui_context.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "multiPageHeader"))
        )
        
    except (NoSuchElementException, TimeoutException) as e:
        pytest.fail(f"Could not switch to multi-page mode: {e}")


@given('I can see the AI Enhancement checkbox in the Advanced Options')
def can_see_ai_checkbox(ui_context):
    """Verify AI Enhancement checkbox is visible in Advanced Options."""
    try:
        # First, open Advanced Options if not already open
        try:
            advanced_toggle = ui_context.driver.find_element(By.CSS_SELECTOR, "[onclick*='toggleAdvancedOptions']")
            advanced_panel = ui_context.driver.find_element(By.ID, "advancedOptionsPanel")
            
            if "collapsed" in advanced_panel.get_attribute("class"):
                advanced_toggle.click()
                time.sleep(0.5)  # Wait for animation
        except (NoSuchElementException, TimeoutException):
            pass  # Advanced options might already be open
        
        # Then open AI Enhancement panel if not already open
        try:
            ai_toggle = ui_context.driver.find_element(By.CSS_SELECTOR, "[onclick*='toggleAIEnhancementOptions']")
            ai_panel = ui_context.driver.find_element(By.ID, "aiEnhancementPanel")
            
            if "collapsed" in ai_panel.get_attribute("class"):
                ai_toggle.click()
                time.sleep(0.5)  # Wait for animation
        except (NoSuchElementException, TimeoutException):
            pass  # AI panel might already be open
        
        # Now find the AI Enhancement checkbox
        ui_context.ai_checkbox = WebDriverWait(ui_context.driver, 10).until(
            EC.presence_of_element_located((By.ID, "aiEnhancementEnabled"))
        )
        
        # Verify checkbox is visible
        assert ui_context.ai_checkbox.is_displayed(), "AI Enhancement checkbox is not visible"
        
    except (NoSuchElementException, TimeoutException) as e:
        pytest.fail(f"Could not find AI Enhancement checkbox: {e}")


@when('I check the AI Enhancement checkbox')
def check_ai_checkbox(ui_context):
    """Check the AI Enhancement checkbox."""
    try:
        if not ui_context.ai_checkbox.is_selected():
            # Click the checkbox to check it
            ui_context.ai_checkbox.click()
            time.sleep(0.5)  # Wait for any JavaScript event handlers
        
        # Verify it's now checked
        assert ui_context.ai_checkbox.is_selected(), "AI Enhancement checkbox was not checked successfully"
        
    except Exception as e:
        pytest.fail(f"Failed to check AI Enhancement checkbox: {e}")


@then('the checkbox should appear visually checked')
def checkbox_visually_checked(ui_context):
    """Verify the checkbox appears visually checked."""
    try:
        # Check the HTML checked attribute
        checked_attribute = ui_context.ai_checkbox.get_attribute("checked")
        assert checked_attribute is not None, "Checkbox checked attribute is not set"
        
        # Check if the checkbox is selected according to Selenium
        assert ui_context.ai_checkbox.is_selected(), "Checkbox does not appear selected to Selenium"
        
        # Additional visual check - look for checked CSS classes if any
        checkbox_classes = ui_context.ai_checkbox.get_attribute("class")
        print(f"Checkbox classes: {checkbox_classes}")
        
    except Exception as e:
        pytest.fail(f"Checkbox does not appear visually checked: {e}")


@then('the system should recognize AI enhancement as enabled')
def system_recognizes_ai_enabled(ui_context):
    """Verify the system recognizes AI enhancement as enabled."""
    try:
        # Execute JavaScript to check the internal state
        ai_config_result = ui_context.driver.execute_script("""
            try {
                var config = getAIConfiguration();
                return {
                    success: true,
                    ai_enhancement_enabled: config.ai_enhancement_enabled,
                    config: config
                };
            } catch (error) {
                return {
                    success: false,
                    error: error.message
                };
            }
        """)
        
        assert ai_config_result['success'], f"Failed to get AI configuration: {ai_config_result.get('error')}"
        assert ai_config_result['ai_enhancement_enabled'] is True, \
            f"System does not recognize AI enhancement as enabled. Config: {ai_config_result['config']}"
        
        ui_context.ai_config = ai_config_result['config']
        
    except Exception as e:
        pytest.fail(f"System does not recognize AI enhancement as enabled: {e}")


@then('the AI configuration panel should become visible')
def ai_config_panel_visible(ui_context):
    """Verify the AI configuration panel becomes visible."""
    try:
        # Find the AI configuration options panel
        ai_config_panel = ui_context.driver.find_element(By.ID, "aiConfigOptions")
        
        # Wait for it to become visible (in case there's an animation)
        WebDriverWait(ui_context.driver, 5).until(
            lambda driver: ai_config_panel.is_displayed()
        )
        
        # Verify it's not collapsed
        panel_classes = ai_config_panel.get_attribute("class")
        assert "collapsed" not in panel_classes, f"AI config panel is still collapsed: {panel_classes}"
        
    except (NoSuchElementException, TimeoutException) as e:
        pytest.fail(f"AI configuration panel is not visible: {e}")


@then('saving AI settings should not show "AI enhancement is disabled" message')
def saving_no_disabled_message(ui_context):
    """Verify saving AI settings doesn't show disabled message."""
    try:
        # Execute JavaScript to trigger save AI settings
        save_result = ui_context.driver.execute_script("""
            try {
                // Capture console messages
                var messages = [];
                var originalLog = console.log;
                console.log = function(msg) {
                    messages.push(msg);
                    originalLog.apply(console, arguments);
                };
                
                // Try to save AI settings
                saveAISettings();
                
                // Restore console.log
                console.log = originalLog;
                
                return {
                    success: true,
                    messages: messages
                };
            } catch (error) {
                return {
                    success: false,
                    error: error.message
                };
            }
        """)
        
        # Check for disabled messages in console output or alerts
        if save_result['success']:
            messages = save_result.get('messages', [])
            disabled_messages = [msg for msg in messages if 'disabled' in str(msg).lower()]
            assert len(disabled_messages) == 0, f"Found disabled messages: {disabled_messages}"
        
        # Also check for any alert dialogs that might show the error
        try:
            alert = ui_context.driver.switch_to.alert
            alert_text = alert.text
            assert 'disabled' not in alert_text.lower(), f"Alert shows disabled message: {alert_text}"
            alert.accept()
        except:
            pass  # No alert present, which is expected for successful save
        
    except Exception as e:
        pytest.fail(f"Error checking for disabled message: {e}")


@given('I have checked the AI Enhancement checkbox')
def have_checked_ai_checkbox(ui_context):
    """Given that AI Enhancement checkbox is already checked."""
    # Reuse the existing steps
    can_see_ai_checkbox(ui_context)
    check_ai_checkbox(ui_context)


@given('I have configured a valid API key')
def have_configured_api_key(ui_context):
    """Configure a valid API key."""
    try:
        # Find and fill in the API key field
        api_key_input = ui_context.driver.find_element(By.ID, "aiApiKey")
        api_key_input.clear()
        api_key_input.send_keys("sk-test-valid-api-key-for-testing")
        
    except NoSuchElementException as e:
        pytest.fail(f"Could not find API key input field: {e}")


@given('I have selected AI features')
def have_selected_ai_features(ui_context):
    """Select some AI features."""
    try:
        # Find and check some AI feature checkboxes
        feature_checkboxes = ui_context.driver.find_elements(By.CSS_SELECTOR, "input[name='aiFeatures']")
        
        # Select the first two features if available
        for i, checkbox in enumerate(feature_checkboxes[:2]):
            if not checkbox.is_selected():
                checkbox.click()
        
    except Exception as e:
        pytest.fail(f"Could not select AI features: {e}")


@when('I attempt to save AI settings')
def attempt_save_ai_settings(ui_context):
    """Attempt to save AI settings."""
    try:
        # Execute JavaScript to trigger save
        save_result = ui_context.driver.execute_script("""
            try {
                saveAISettings();
                return { success: true };
            } catch (error) {
                return { success: false, error: error.message };
            }
        """)
        
        ui_context.save_result = save_result
        
    except Exception as e:
        pytest.fail(f"Failed to attempt saving AI settings: {e}")


@then('the system should save the AI configuration successfully')
def system_saves_successfully(ui_context):
    """Verify the system saves AI configuration successfully."""
    try:
        save_result = getattr(ui_context, 'save_result', {})
        assert save_result.get('success') is True, f"Save was not successful: {save_result.get('error')}"
        
    except Exception as e:
        pytest.fail(f"System did not save AI configuration successfully: {e}")


@then('should not display "No AI settings to save" error message')
def no_error_message_displayed(ui_context):
    """Verify no error message is displayed."""
    try:
        # Check for error messages in various places
        error_elements = ui_context.driver.find_elements(By.CSS_SELECTOR, ".error, .alert-danger, .terminal-alert")
        
        error_messages = []
        for element in error_elements:
            if element.is_displayed():
                text = element.text
                if "no ai settings" in text.lower() or "disabled" in text.lower():
                    error_messages.append(text)
        
        assert len(error_messages) == 0, f"Found error messages: {error_messages}"
        
    except Exception as e:
        pytest.fail(f"Error checking for error messages: {e}")


@then('the AI configuration should be retrievable')
def ai_config_retrievable(ui_context):
    """Verify AI configuration can be retrieved."""
    try:
        config_result = ui_context.driver.execute_script("""
            try {
                var config = getAIConfiguration();
                return {
                    success: true,
                    config: config,
                    enabled: config.ai_enhancement_enabled
                };
            } catch (error) {
                return {
                    success: false,
                    error: error.message
                };
            }
        """)
        
        assert config_result['success'], f"Could not retrieve AI configuration: {config_result.get('error')}"
        assert config_result['enabled'] is True, "Retrieved configuration shows AI as disabled"
        
    except Exception as e:
        pytest.fail(f"AI configuration is not retrievable: {e}")


@given('I have configured AI settings properly')
def have_configured_ai_properly(ui_context):
    """Given AI settings are properly configured."""
    # Combine previous steps
    have_configured_api_key(ui_context)
    have_selected_ai_features(ui_context)


@when('I initiate a scraping operation')
def initiate_scraping_operation(ui_context):
    """Initiate a scraping operation."""
    try:
        # Mock the scraping request to capture the data being sent
        ui_context.driver.execute_script("""
            // Mock the fetch function to capture scraping requests
            window.capturedScrapingRequest = null;
            var originalFetch = window.fetch;
            window.fetch = function(url, options) {
                if (url.includes('/api/scrape')) {
                    window.capturedScrapingRequest = {
                        url: url,
                        options: options,
                        body: options.body ? JSON.parse(options.body) : null
                    };
                }
                return Promise.resolve({
                    ok: true,
                    json: function() {
                        return Promise.resolve({
                            success: true,
                            processed_count: 1,
                            sites_data: []
                        });
                    }
                });
            };
        """)
        
        # Fill in a test URL and start scraping
        url_input = ui_context.driver.find_element(By.ID, "url")
        url_input.clear()
        url_input.send_keys("https://example-restaurant.com")
        
        # Click the scrape button
        scrape_button = ui_context.driver.find_element(By.CSS_SELECTOR, "button[onclick*='startScraping']")
        scrape_button.click()
        
        # Wait a moment for the request to be captured
        time.sleep(1)
        
    except Exception as e:
        pytest.fail(f"Failed to initiate scraping operation: {e}")


@then('the AI configuration should be included in the scraping request')
def ai_config_in_scraping_request(ui_context):
    """Verify AI configuration is included in scraping request."""
    try:
        # Get the captured request data
        request_data = ui_context.driver.execute_script("return window.capturedScrapingRequest;")
        
        assert request_data is not None, "No scraping request was captured"
        
        request_body = request_data.get('body', {})
        assert 'ai_enhancement_enabled' in request_body, "AI enhancement enabled flag not in request"
        assert request_body['ai_enhancement_enabled'] is True, "AI enhancement is not enabled in request"
        
        ui_context.scraping_request_data = request_body
        
    except Exception as e:
        pytest.fail(f"AI configuration not included in scraping request: {e}")


@then('the system should not fall back to traditional extraction only')
def no_fallback_to_traditional(ui_context):
    """Verify system doesn't fall back to traditional extraction only."""
    try:
        request_body = ui_context.scraping_request_data
        
        # Check that AI-related fields are present and properly set
        assert request_body.get('ai_enhancement_enabled') is True, "AI enhancement is disabled in request"
        assert 'api_key' in request_body, "API key not included in request"
        assert 'ai_features' in request_body, "AI features not included in request"
        
    except Exception as e:
        pytest.fail(f"System is falling back to traditional extraction: {e}")


@then('the processing should attempt to use AI enhancement')
def processing_attempts_ai(ui_context):
    """Verify processing attempts to use AI enhancement."""
    # This is verified by the previous step - if AI config is in the request,
    # the backend will attempt to use AI enhancement
    assert ui_context.scraping_request_data.get('ai_enhancement_enabled') is True, \
           "Processing will not attempt AI enhancement"


@given('AI enhancement is currently enabled')
def ai_enhancement_currently_enabled(ui_context):
    """Given AI enhancement is currently enabled."""
    # Verify current state
    system_recognizes_ai_enabled(ui_context)


@when('I uncheck the AI Enhancement checkbox')
def uncheck_ai_checkbox(ui_context):
    """Uncheck the AI Enhancement checkbox."""
    try:
        if ui_context.ai_checkbox.is_selected():
            ui_context.ai_checkbox.click()
            time.sleep(0.5)  # Wait for JavaScript handlers
        
        # Verify it's now unchecked
        assert not ui_context.ai_checkbox.is_selected(), "AI Enhancement checkbox was not unchecked successfully"
        
    except Exception as e:
        pytest.fail(f"Failed to uncheck AI Enhancement checkbox: {e}")


@then('the checkbox should appear visually unchecked')
def checkbox_visually_unchecked(ui_context):
    """Verify the checkbox appears visually unchecked."""
    try:
        # Check the HTML checked attribute
        checked_attribute = ui_context.ai_checkbox.get_attribute("checked")
        assert checked_attribute is None, "Checkbox checked attribute is still set"
        
        # Check if the checkbox is not selected according to Selenium
        assert not ui_context.ai_checkbox.is_selected(), "Checkbox still appears selected to Selenium"
        
    except Exception as e:
        pytest.fail(f"Checkbox does not appear visually unchecked: {e}")


@then('the system should recognize AI enhancement as disabled')
def system_recognizes_ai_disabled(ui_context):
    """Verify the system recognizes AI enhancement as disabled."""
    try:
        # Execute JavaScript to check the internal state
        ai_config_result = ui_context.driver.execute_script("""
            try {
                var config = getAIConfiguration();
                return {
                    success: true,
                    ai_enhancement_enabled: config.ai_enhancement_enabled,
                    config: config
                };
            } catch (error) {
                return {
                    success: false,
                    error: error.message
                };
            }
        """)
        
        assert ai_config_result['success'], f"Failed to get AI configuration: {ai_config_result.get('error')}"
        assert ai_config_result['ai_enhancement_enabled'] is False, \
            f"System still recognizes AI enhancement as enabled. Config: {ai_config_result['config']}"
        
    except Exception as e:
        pytest.fail(f"System does not recognize AI enhancement as disabled: {e}")


@then('the AI configuration panel should become hidden')
def ai_config_panel_hidden(ui_context):
    """Verify the AI configuration panel becomes hidden."""
    try:
        # Find the AI configuration options panel
        ai_config_panel = ui_context.driver.find_element(By.ID, "aiConfigOptions")
        
        # Wait for it to become hidden (in case there's an animation)
        WebDriverWait(ui_context.driver, 5).until(
            lambda driver: "collapsed" in ai_config_panel.get_attribute("class") or not ai_config_panel.is_displayed()
        )
        
    except (NoSuchElementException, TimeoutException) as e:
        pytest.fail(f"AI configuration panel is not hidden: {e}")


@then('attempting to save should show appropriate disabled message')
def save_shows_disabled_message(ui_context):
    """Verify attempting to save shows appropriate disabled message."""
    try:
        # Execute JavaScript to trigger save and capture any messages
        save_result = ui_context.driver.execute_script("""
            try {
                var messages = [];
                var originalAlert = window.alert;
                window.alert = function(msg) {
                    messages.push(msg);
                };
                
                saveAISettings();
                
                window.alert = originalAlert;
                
                return {
                    success: true,
                    messages: messages
                };
            } catch (error) {
                return {
                    success: false,
                    error: error.message
                };
            }
        """)
        
        if save_result['success']:
            messages = save_result.get('messages', [])
            disabled_found = any('disabled' in str(msg).lower() for msg in messages)
            assert disabled_found, f"Expected disabled message not found. Messages: {messages}"
        
    except Exception as e:
        pytest.fail(f"Error checking for disabled message: {e}")


@given('I am viewing the Advanced Options panel')
def viewing_advanced_options(ui_context):
    """Given I am viewing the Advanced Options panel."""
    can_see_ai_checkbox(ui_context)  # This step opens the panel if needed


@then('the getAIConfiguration() function should return ai_enhancement_enabled: true')
def get_ai_config_returns_true(ui_context):
    """Verify getAIConfiguration() returns ai_enhancement_enabled: true."""
    system_recognizes_ai_enabled(ui_context)


@then('when I uncheck the AI Enhancement checkbox')
def when_uncheck_checkbox(ui_context):
    """When I uncheck the checkbox (step continuation)."""
    uncheck_ai_checkbox(ui_context)


@then('the getAIConfiguration() function should return ai_enhancement_enabled: false')
def get_ai_config_returns_false(ui_context):
    """Verify getAIConfiguration() returns ai_enhancement_enabled: false."""
    system_recognizes_ai_disabled(ui_context)


@then('the visual state should always match the internal state')
def visual_matches_internal_state(ui_context):
    """Verify visual state matches internal state."""
    try:
        # Get current visual state
        visual_checked = ui_context.ai_checkbox.is_selected()
        
        # Get current internal state
        internal_result = ui_context.driver.execute_script("""
            try {
                var config = getAIConfiguration();
                return config.ai_enhancement_enabled;
            } catch (error) {
                return null;
            }
        """)
        
        assert visual_checked == internal_result, \
            f"Visual state ({visual_checked}) does not match internal state ({internal_result})"
        
    except Exception as e:
        pytest.fail(f"Visual state does not match internal state: {e}")


@given('I am in multi-page mode')
def given_in_multipage_mode(ui_context):
    """Given I am in multi-page mode."""
    in_multipage_mode(ui_context)


@then('AI enhancement should be enabled for multi-page mode')
def ai_enabled_multipage_mode(ui_context):
    """Verify AI enhancement is enabled for multi-page mode."""
    system_recognizes_ai_enabled(ui_context)


@when('I switch to single-page mode')
def switch_to_single_page_mode(ui_context):
    """Switch to single-page mode."""
    try:
        # Click on single-page mode radio button
        single_page_radio = ui_context.driver.find_element(By.CSS_SELECTOR, "input[name='scrapingMode'][value='single']")
        single_page_radio.click()
        
        ui_context.current_mode = "single"
        
        # Wait for single-page options to appear
        WebDriverWait(ui_context.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "singlePageHeader"))
        )
        
    except (NoSuchElementException, TimeoutException) as e:
        pytest.fail(f"Could not switch to single-page mode: {e}")


@then('the single-page AI Enhancement checkbox should reflect the same state')
def single_page_checkbox_same_state(ui_context):
    """Verify single-page AI Enhancement checkbox reflects the same state."""
    try:
        # Find the single-page AI Enhancement checkbox
        single_page_checkbox = ui_context.driver.find_element(By.ID, "singleAiEnhancementEnabled")
        
        # Get the state of both checkboxes
        multi_page_state = ui_context.ai_checkbox.is_selected()
        single_page_state = single_page_checkbox.is_selected()
        
        assert multi_page_state == single_page_state, \
            f"Single-page checkbox state ({single_page_state}) does not match multi-page state ({multi_page_state})"
        
    except NoSuchElementException as e:
        pytest.fail(f"Could not find single-page AI Enhancement checkbox: {e}")


@then('AI enhancement should work consistently in both modes')
def ai_works_consistently_both_modes(ui_context):
    """Verify AI enhancement works consistently in both modes."""
    try:
        # Test AI configuration function works in single-page mode
        single_page_config = ui_context.driver.execute_script("""
            try {
                var config = getAIConfiguration();
                return {
                    success: true,
                    ai_enhancement_enabled: config.ai_enhancement_enabled,
                    mode: config.active_mode || 'unknown'
                };
            } catch (error) {
                return {
                    success: false,
                    error: error.message
                };
            }
        """)
        
        assert single_page_config['success'], f"AI configuration failed in single-page mode: {single_page_config.get('error')}"
        
        # The state should be consistent
        expected_state = ui_context.ai_checkbox.is_selected()
        actual_state = single_page_config['ai_enhancement_enabled']
        
        assert expected_state == actual_state, \
            f"AI configuration inconsistent between modes. Expected: {expected_state}, Actual: {actual_state}"
        
    except Exception as e:
        pytest.fail(f"AI enhancement does not work consistently in both modes: {e}")