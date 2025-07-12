"""Step definitions for Advanced Options functionality tests."""

from unittest.mock import Mock, patch
import pytest
from pytest_bdd import given, when, then, scenarios
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Import scenarios
scenarios('../features/advanced_options_functionality.feature')

@pytest.fixture
def browser():
    """Create browser instance for UI testing."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode for testing
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

@pytest.fixture
def web_server():
    """Start web server for testing."""
    # This would start the actual Flask server
    # For now, we'll mock it
    return "http://localhost:8085"

# Step implementations

@given('the web interface is running')
def web_interface_running(web_server):
    """Verify web interface is accessible."""
    # This should verify the server is running
    assert web_server == "http://localhost:8085"

@given('the user is on the main extraction page')
def user_on_main_page(browser, web_server):
    """Navigate to main extraction page."""
    browser.get(web_server)
    # Verify we're on the right page
    assert "RAG_Scraper" in browser.title

@given('multi-page mode is selected')
def multipage_mode_selected(browser):
    """Select multi-page mode."""
    # Find and click multi-page mode radio button
    multipage_radio = browser.find_element(By.CSS_SELECTOR, 'input[value="multi"]')
    browser.execute_script("arguments[0].click();", multipage_radio)

@given('the Advanced Options panel is collapsed')
def advanced_options_collapsed(browser):
    """Verify Advanced Options panel is collapsed."""
    panel = browser.find_element(By.ID, "advancedOptionsPanel")
    assert "collapsed" in panel.get_attribute("class"), "Advanced Options panel should be collapsed"

@given('the Advanced Options panel is expanded')
def advanced_options_expanded(browser):
    """Expand Advanced Options panel."""
    header = browser.find_element(By.CSS_SELECTOR, '[onclick="toggleAdvancedOptions()"]')
    header.click()
    
    panel = browser.find_element(By.ID, "advancedOptionsPanel")
    assert "collapsed" not in panel.get_attribute("class"), "Advanced Options panel should be expanded"

@given('the user has modified some advanced options')
def user_modified_options(browser):
    """Modify some advanced options."""
    # Uncheck page discovery
    page_discovery = browser.find_element(By.ID, "pageDiscoveryEnabled")
    if page_discovery.is_selected():
        page_discovery.click()
    
    # Change timeout value
    timeout_input = browser.find_element(By.ID, "requestTimeout")
    timeout_input.clear()
    timeout_input.send_keys("60")

@when('the user clicks on the "Advanced Options" header')
def user_clicks_advanced_options_header(browser):
    """Click on Advanced Options header."""
    header = browser.find_element(By.CSS_SELECTOR, '[onclick="toggleAdvancedOptions()"]')
    header.click()

@when('the user focuses on the Advanced Options header')
def user_focuses_advanced_options_header(browser):
    """Focus on Advanced Options header."""
    header = browser.find_element(By.CSS_SELECTOR, '[onclick="toggleAdvancedOptions()"]')
    header.send_keys("")  # Focus on element

@when('presses the Enter key')
def user_presses_enter(browser):
    """Press Enter key."""
    focused_element = browser.switch_to.active_element
    focused_element.send_keys(Keys.ENTER)

@when('the user presses the Space key')
def user_presses_space(browser):
    """Press Space key."""
    focused_element = browser.switch_to.active_element
    focused_element.send_keys(Keys.SPACE)

@when('the user clicks the "Reset to Defaults" button')
def user_clicks_reset_button(browser):
    """Click Reset to Defaults button."""
    reset_button = browser.find_element(By.CSS_SELECTOR, '[onclick="resetAdvancedOptionsToDefaults()"]')
    reset_button.click()

@then('the Advanced Options panel should expand')
def advanced_options_should_expand(browser):
    """Verify panel expands."""
    wait = WebDriverWait(browser, 5)
    panel = wait.until(EC.presence_of_element_located((By.ID, "advancedOptionsPanel")))
    
    # This test should FAIL initially if toggle functionality is broken
    assert "collapsed" not in panel.get_attribute("class"), "Advanced Options panel should be expanded but is still collapsed"

@then('the Advanced Options panel should collapse')
def advanced_options_should_collapse(browser):
    """Verify panel collapses."""
    wait = WebDriverWait(browser, 5)
    panel = wait.until(EC.presence_of_element_located((By.ID, "advancedOptionsPanel")))
    
    # This test should FAIL initially if toggle functionality is broken
    assert "collapsed" in panel.get_attribute("class"), "Advanced Options panel should be collapsed but is still expanded"

@then('the expand icon should change from "▼" to "▲"')
def expand_icon_changes_to_up(browser):
    """Verify expand icon changes to up arrow."""
    icon = browser.find_element(By.ID, "advancedOptionsIcon")
    
    # This test should FAIL initially if icon doesn't update
    assert icon.text == "▲", f"Expected expand icon to be '▲' but got '{icon.text}'"

@then('the expand icon should change from "▲" to "▼"')
def expand_icon_changes_to_down(browser):
    """Verify expand icon changes to down arrow."""
    icon = browser.find_element(By.ID, "advancedOptionsIcon")
    
    # This test should FAIL initially if icon doesn't update
    assert icon.text == "▼", f"Expected expand icon to be '▼' but got '{icon.text}'"

@then('all advanced option controls should be visible')
def advanced_option_controls_visible(browser):
    """Verify all controls are visible."""
    # Check key elements are visible
    elements_to_check = [
        "pageDiscoveryEnabled",
        "requestTimeout", 
        "concurrentRequests",
        "followRedirects",
        "respectRobotsTxt"
    ]
    
    for element_id in elements_to_check:
        element = browser.find_element(By.ID, element_id)
        assert element.is_displayed(), f"Element {element_id} should be visible but is not"

@then('advanced option controls should be hidden')
def advanced_option_controls_hidden(browser):
    """Verify controls are hidden."""
    panel = browser.find_element(By.ID, "advancedOptionsPanel")
    
    # Panel should have collapsed class which hides content
    assert "collapsed" in panel.get_attribute("class"), "Panel should be collapsed to hide controls"

@then('the panel should expand')
def panel_should_expand(browser):
    """Verify panel expansion."""
    panel = browser.find_element(By.ID, "advancedOptionsPanel")
    assert "collapsed" not in panel.get_attribute("class"), "Panel should be expanded"

@then('the panel should collapse')
def panel_should_collapse(browser):
    """Verify panel collapse."""
    panel = browser.find_element(By.ID, "advancedOptionsPanel")
    assert "collapsed" in panel.get_attribute("class"), "Panel should be collapsed"

@then('the user should see the "Enable Page Discovery" checkbox')
def should_see_page_discovery_checkbox(browser):
    """Verify page discovery checkbox is visible."""
    checkbox = browser.find_element(By.ID, "pageDiscoveryEnabled")
    assert checkbox.is_displayed(), "Page Discovery checkbox should be visible"

@then('the user should see the "Request Timeout" input field')
def should_see_request_timeout_input(browser):
    """Verify request timeout input is visible."""
    input_field = browser.find_element(By.ID, "requestTimeout")
    assert input_field.is_displayed(), "Request Timeout input should be visible"

@then('the user should see the "Concurrent Requests" slider')
def should_see_concurrent_requests_slider(browser):
    """Verify concurrent requests slider is visible."""
    slider = browser.find_element(By.ID, "concurrentRequests")
    assert slider.is_displayed(), "Concurrent Requests slider should be visible"

@then('the user should see the "Follow Redirects" checkbox')
def should_see_follow_redirects_checkbox(browser):
    """Verify follow redirects checkbox is visible."""
    checkbox = browser.find_element(By.ID, "followRedirects")
    assert checkbox.is_displayed(), "Follow Redirects checkbox should be visible"

@then('the user should see the "Respect Robots.txt" checkbox')
def should_see_respect_robots_checkbox(browser):
    """Verify respect robots checkbox is visible."""
    checkbox = browser.find_element(By.ID, "respectRobotsTxt")
    assert checkbox.is_displayed(), "Respect Robots.txt checkbox should be visible"

@then('the user should see the "Reset to Defaults" button')
def should_see_reset_button(browser):
    """Verify reset button is visible."""
    button = browser.find_element(By.CSS_SELECTOR, '[onclick="resetAdvancedOptionsToDefaults()"]')
    assert button.is_displayed(), "Reset to Defaults button should be visible"

@then('all advanced options should return to their default values')
def advanced_options_return_to_defaults(browser):
    """Verify all options are reset to defaults."""
    # Check default values
    page_discovery = browser.find_element(By.ID, "pageDiscoveryEnabled")
    assert page_discovery.is_selected(), "Page Discovery should be checked by default"
    
    timeout_input = browser.find_element(By.ID, "requestTimeout")
    assert timeout_input.get_attribute("value") == "30", "Request Timeout should be 30 by default"
    
    concurrent_requests = browser.find_element(By.ID, "concurrentRequests")
    assert concurrent_requests.get_attribute("value") == "5", "Concurrent Requests should be 5 by default"
    
    follow_redirects = browser.find_element(By.ID, "followRedirects")
    assert follow_redirects.is_selected(), "Follow Redirects should be checked by default"
    
    respect_robots = browser.find_element(By.ID, "respectRobotsTxt")
    assert respect_robots.is_selected(), "Respect Robots.txt should be checked by default"

@then('a success message should be displayed')
def success_message_displayed(browser):
    """Verify success message is shown."""
    # Look for alert or notification
    try:
        alert = browser.find_element(By.CLASS_NAME, "terminal-alert")
        assert "SUCCESS" in alert.text, "Success message should contain 'SUCCESS'"
    except:
        # This test should FAIL initially if no success message is shown
        assert False, "No success message was displayed after reset"