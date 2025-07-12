"""Debug Advanced Options toggle issue."""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import subprocess
import os


def test_advanced_options_debug():
    """Debug Advanced Options toggle functionality."""
    
    # Start server
    env = os.environ.copy()
    env['PYTHONPATH'] = '/home/rod/AI/Projects/RAG_Scraper'
    server_process = subprocess.Popen(
        ['python', '/home/rod/AI/Projects/RAG_Scraper/run_app.py'],
        cwd='/home/rod/AI/Projects/RAG_Scraper',
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give server time to start
    time.sleep(3)
    
    # Configure Chrome to capture console logs
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--log-level=0")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    
    try:
        driver.get("http://192.168.12.187:8085")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "advancedOptionsPanel"))
        )
        
        print("Page loaded successfully")
        
        # Check if elements exist
        panel = driver.find_element(By.ID, "advancedOptionsPanel")
        icon = driver.find_element(By.ID, "advancedOptionsIcon")
        toggle_header = driver.find_element(By.CSS_SELECTOR, '[onclick="toggleAdvancedOptions()"]')
        
        print(f"Panel classes: {panel.get_attribute('class')}")
        print(f"Icon text: '{icon.text}'")
        print(f"Icon innerHTML: '{icon.get_attribute('innerHTML')}'")
        
        # Execute the JavaScript function directly
        driver.execute_script("toggleAdvancedOptions();")
        
        time.sleep(0.5)
        
        # Try to get console logs (may not work in headless mode)
        try:
            logs = driver.get_log('browser')
            print("\nConsole logs:")
            for log in logs:
                print(f"  {log['level']}: {log['message']}")
        except:
            print("\nConsole logs not available")
        
        # Check state after click
        print(f"\nAfter click:")
        print(f"Panel classes: {panel.get_attribute('class')}")
        print(f"Icon text: '{icon.text}'")
        print(f"Icon innerHTML: '{icon.get_attribute('innerHTML')}'")
        
        # Try clicking the header element instead
        print("\nTrying header click...")
        driver.execute_script("arguments[0].click();", toggle_header)
        
        time.sleep(0.5)
        
        # Try to get console logs again
        try:
            logs = driver.get_log('browser')
            print("\nConsole logs after header click:")
            for log in logs:
                print(f"  {log['level']}: {log['message']}")
        except:
            print("\nConsole logs not available after header click")
        
        print(f"\nAfter header click:")
        print(f"Panel classes: {panel.get_attribute('class')}")
        print(f"Icon text: '{icon.text}'")
        print(f"Icon innerHTML: '{icon.get_attribute('innerHTML')}'")
        
        # Check if the icon element is being replaced or modified
        icon_id = icon.get_attribute('id')
        icon_classes = icon.get_attribute('class')
        print(f"Icon ID: {icon_id}")
        print(f"Icon classes: {icon_classes}")
        
        # Try to directly modify the icon
        driver.execute_script("document.getElementById('advancedOptionsIcon').textContent = '▲';")
        time.sleep(0.1)
        
        print(f"\nAfter direct modification:")
        print(f"Icon text: '{icon.text}'")
        print(f"Icon innerHTML: '{icon.get_attribute('innerHTML')}'")
        
    finally:
        driver.quit()
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()


if __name__ == "__main__":
    test_advanced_options_debug()