"""Integration test for UI fixes: Advanced Options toggle and file download functionality."""

import pytest
import tempfile
import os
import subprocess
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class TestUIFixesIntegration:
    """Integration test for both UI fixes working together."""
    
    @pytest.fixture(scope="class")
    def server_and_files(self):
        """Start server with test files for download testing."""
        # Create test files in Downloads directory
        downloads_dir = os.path.expanduser("~/Downloads")
        test_files = {
            'integration_test.txt': 'Integration test content for download',
            'integration_test.json': '{"test": "integration data"}',
            'integration_test.pdf': 'PDF content placeholder'
        }
        
        created_files = []
        for filename, content in test_files.items():
            file_path = os.path.join(downloads_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
            created_files.append(file_path)
        
        # Start server
        env = os.environ.copy()
        env['PYTHONPATH'] = '/home/rod/AI/Projects/RAG_Scraper'
        process = subprocess.Popen(
            ['python', '/home/rod/AI/Projects/RAG_Scraper/run_app.py'],
            cwd='/home/rod/AI/Projects/RAG_Scraper',
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(3)  # Wait for server to start
        
        yield process, created_files
        
        # Cleanup
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        
        # Remove test files
        for file_path in created_files:
            if os.path.exists(file_path):
                os.remove(file_path)
    
    @pytest.fixture
    def browser(self, server_and_files):
        """Create browser for testing."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        yield driver
        
        driver.quit()
    
    def test_advanced_options_and_file_download_integration(self, browser, server_and_files):
        """Test that both Advanced Options toggle and file downloads work together."""
        server_process, test_files = server_and_files
        
        # Navigate to the application
        browser.get("http://192.168.12.187:8085")
        
        # Wait for page to load
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Test 1: Advanced Options Toggle Functionality
        print("Testing Advanced Options toggle...")
        
        # Find Advanced Options elements
        panel = browser.find_element(By.ID, "advancedOptionsPanel")
        icon = browser.find_element(By.ID, "advancedOptionsIcon")
        toggle_header = browser.find_element(By.CSS_SELECTOR, '[onclick="toggleAdvancedOptions()"]')
        
        # Verify initial state (collapsed)
        initial_classes = panel.get_attribute("class")
        initial_icon = icon.get_attribute("innerHTML")
        assert "collapsed" in initial_classes, "Panel should start collapsed"
        assert initial_icon == "▼", "Icon should start as down arrow"
        
        # Click to expand
        browser.execute_script("arguments[0].click();", toggle_header)
        time.sleep(0.5)
        
        # Verify expanded state
        expanded_classes = panel.get_attribute("class")
        expanded_icon = icon.get_attribute("innerHTML")
        assert "collapsed" not in expanded_classes, "Panel should be expanded"
        assert expanded_icon == "▲", "Icon should be up arrow when expanded"
        
        # Click to collapse again
        browser.execute_script("arguments[0].click();", toggle_header)
        time.sleep(0.5)
        
        # Verify collapsed state
        collapsed_classes = panel.get_attribute("class")
        collapsed_icon = icon.get_attribute("innerHTML")
        assert "collapsed" in collapsed_classes, "Panel should be collapsed again"
        assert collapsed_icon == "▼", "Icon should be down arrow when collapsed"
        
        print("✓ Advanced Options toggle working correctly")
        
        # Test 2: File Download Functionality
        print("Testing file download functionality...")
        
        # Test downloading each test file through direct API calls
        import requests
        
        base_url = "http://192.168.12.187:8085"
        
        for file_path in test_files:
            filename = os.path.basename(file_path)
            download_url = f"{base_url}/api/download/{filename}"
            
            try:
                response = requests.get(download_url)
                assert response.status_code == 200, f"Download failed for {filename} with status {response.status_code}"
                
                # Verify content matches what we wrote
                with open(file_path, 'r') as f:
                    expected_content = f.read()
                assert expected_content in response.text, f"Downloaded content doesn't match for {filename}"
                
                print(f"✓ Successfully downloaded and verified {filename}")
                
            except Exception as e:
                pytest.fail(f"Failed to download {filename}: {e}")
        
        print("✓ File download functionality working correctly")
        
        # Test 3: Integration - Advanced Options with Multiple File Scenario
        print("Testing integration scenario...")
        
        # Expand Advanced Options
        browser.execute_script("arguments[0].click();", toggle_header)
        time.sleep(0.5)
        
        # Verify we can see Advanced Options controls
        page_discovery = browser.find_element(By.ID, "pageDiscoveryEnabled")
        request_timeout = browser.find_element(By.ID, "requestTimeout")
        
        assert page_discovery.is_displayed(), "Page discovery control should be visible when expanded"
        assert request_timeout.is_displayed(), "Request timeout control should be visible when expanded"
        
        # Test that file downloads still work with Advanced Options expanded
        test_filename = os.path.basename(test_files[0])
        download_url = f"{base_url}/api/download/{test_filename}"
        response = requests.get(download_url)
        assert response.status_code == 200, "File download should work with Advanced Options expanded"
        
        print("✓ Integration test passed - both features work together")
        
        # Summary
        print("\n" + "="*60)
        print("INTEGRATION TEST SUMMARY")
        print("="*60)
        print("✓ Advanced Options toggle: WORKING")
        print("✓ File download functionality: WORKING") 
        print("✓ Integration compatibility: WORKING")
        print("✓ All UI fixes verified successfully")
        print("="*60)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])