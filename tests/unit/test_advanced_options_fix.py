"""Test Advanced Options toggle fix."""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
import subprocess
import signal


class TestAdvancedOptionsToggleFix:
    """Test the Advanced Options toggle functionality fix."""
    
    @pytest.fixture(scope="class")
    def server_process(self):
        """Start the Flask server for testing."""
        # Start the server in background
        env = os.environ.copy()
        env['PYTHONPATH'] = '/home/rod/AI/Projects/RAG_Scraper'
        process = subprocess.Popen(
            ['python', '/home/rod/AI/Projects/RAG_Scraper/run_app.py'],
            cwd='/home/rod/AI/Projects/RAG_Scraper',
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give server time to start
        time.sleep(3)
        
        yield process
        
        # Cleanup
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    
    @pytest.fixture
    def browser(self, server_process):
        """Create browser instance for testing."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        yield driver
        
        driver.quit()
    
    def test_advanced_options_elements_present(self, browser):
        """Test that Advanced Options elements are present on page."""
        browser.get("http://192.168.12.187:8085")
        
        # Wait for page to load
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Check that required elements exist
        toggle_header = browser.find_elements(By.CSS_SELECTOR, '[onclick="toggleAdvancedOptions()"]')
        assert len(toggle_header) > 0, "Advanced Options toggle header should be present"
        
        panel = browser.find_elements(By.ID, "advancedOptionsPanel")
        assert len(panel) > 0, "Advanced Options panel should be present"
        
        icon = browser.find_elements(By.ID, "advancedOptionsIcon")
        assert len(icon) > 0, "Advanced Options icon should be present"
    
    def test_advanced_options_default_state(self, browser):
        """Test that Advanced Options panel starts collapsed."""
        browser.get("http://192.168.12.187:8085")
        
        # Wait for page to load
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "advancedOptionsPanel"))
        )
        
        panel = browser.find_element(By.ID, "advancedOptionsPanel")
        panel_classes = panel.get_attribute("class")
        
        # Panel should start collapsed
        assert "collapsed" in panel_classes, f"Panel should start collapsed, but classes are: {panel_classes}"
    
    def test_advanced_options_toggle_functionality(self, browser):
        """Test that clicking Advanced Options actually toggles the panel."""
        browser.get("http://192.168.12.187:8085")
        
        # Wait for page to load
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "advancedOptionsPanel"))
        )
        
        # First select multi-page mode to enable Advanced Options
        try:
            multipage_option = browser.find_element(By.CSS_SELECTOR, 'input[value="multi"]')
            if not multipage_option.is_selected():
                # Find the parent label or container and click it
                multipage_container = browser.find_element(By.CSS_SELECTOR, 'label:has(input[value="multi"]), .mode-option:has(input[value="multi"])')
                browser.execute_script("arguments[0].click();", multipage_container)
                time.sleep(0.5)
        except:
            # If we can't find the multi-page option, continue with the test
            pass
        
        # Get initial state
        panel = browser.find_element(By.ID, "advancedOptionsPanel")
        icon = browser.find_element(By.ID, "advancedOptionsIcon")
        
        initial_panel_classes = panel.get_attribute("class")
        initial_icon_content = icon.get_attribute("innerHTML")
        
        # Click the toggle header
        toggle_header = browser.find_element(By.CSS_SELECTOR, '[onclick="toggleAdvancedOptions()"]')
        browser.execute_script("arguments[0].click();", toggle_header)
        
        # Wait a moment for animation
        time.sleep(0.5)
        
        # Check if state changed
        new_panel_classes = panel.get_attribute("class")
        new_icon_content = icon.get_attribute("innerHTML")
        
        # If panel was collapsed, it should now be expanded
        if "collapsed" in initial_panel_classes:
            assert "collapsed" not in new_panel_classes, f"Panel should be expanded after click. Initial: {initial_panel_classes}, New: {new_panel_classes}"
            assert new_icon_content == "▲", f"Icon should change to up arrow, but got: {new_icon_content}"
        else:
            # If panel was expanded, it should now be collapsed
            assert "collapsed" in new_panel_classes, f"Panel should be collapsed after click. Initial: {initial_panel_classes}, New: {new_panel_classes}"
            assert new_icon_content == "▼", f"Icon should change to down arrow, but got: {new_icon_content}"
        
        # Test toggle again
        browser.execute_script("arguments[0].click();", toggle_header)
        time.sleep(0.5)
        
        # Should return to original state
        final_panel_classes = panel.get_attribute("class")
        final_icon_content = icon.get_attribute("innerHTML")
        
        assert final_panel_classes == initial_panel_classes, f"Panel should return to initial state. Initial: {initial_panel_classes}, Final: {final_panel_classes}"
        assert final_icon_content == initial_icon_content, f"Icon should return to initial state. Initial: {initial_icon_content}, Final: {final_icon_content}"
    
    def test_advanced_options_content_visibility(self, browser):
        """Test that Advanced Options content is properly hidden/shown."""
        browser.get("http://192.168.12.187:8085")
        
        # Wait for page to load
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "advancedOptionsPanel"))
        )
        
        # First select multi-page mode to enable Advanced Options
        try:
            multipage_option = browser.find_element(By.CSS_SELECTOR, 'input[value="multi"]')
            if not multipage_option.is_selected():
                multipage_container = browser.find_element(By.CSS_SELECTOR, 'label:has(input[value="multi"]), .mode-option:has(input[value="multi"])')
                browser.execute_script("arguments[0].click();", multipage_container)
                time.sleep(0.5)
        except:
            pass
        
        panel = browser.find_element(By.ID, "advancedOptionsPanel")
        
        # If panel is collapsed, content should not be visible
        if "collapsed" in panel.get_attribute("class"):
            # Try to find a control inside the panel
            controls = panel.find_elements(By.CSS_SELECTOR, "input, button, select")
            
            # Content might be present but not visible due to CSS
            # Check if panel has zero or very small height
            panel_height = panel.size['height']
            assert panel_height <= 10, f"Collapsed panel should have minimal height, but got: {panel_height}px"
        
        # Click to expand
        toggle_header = browser.find_element(By.CSS_SELECTOR, '[onclick="toggleAdvancedOptions()"]')
        browser.execute_script("arguments[0].click();", toggle_header)
        time.sleep(0.5)
        
        # Now panel should be visible with proper height
        if "collapsed" not in panel.get_attribute("class"):
            panel_height = panel.size['height']
            assert panel_height > 50, f"Expanded panel should have substantial height, but got: {panel_height}px"
            
            # Should be able to find controls
            controls = panel.find_elements(By.CSS_SELECTOR, "input, button")
            assert len(controls) > 0, "Expanded panel should contain interactive controls"