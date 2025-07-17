#!/usr/bin/env python3
"""Quick test to check if URL scraping is working."""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.scraper.multi_strategy_scraper import MultiStrategyScraper
from src.config.scraping_config import ScrapingConfig

def test_url_scraping():
    """Test basic URL scraping functionality."""
    print("Testing URL scraping functionality...")
    
    # Create a simple config
    config = ScrapingConfig(
        urls=["https://example.com"]
    )
    
    # Create scraper
    scraper = MultiStrategyScraper(config)
    
    # Test with a simple restaurant website
    test_url = "https://www.fullers.co.uk/pubs/"
    
    print(f"Testing URL: {test_url}")
    
    try:
        # Test basic HTTP request first
        print("Testing basic HTTP request...")
        import requests
        try:
            response = requests.get(test_url, timeout=10)
            print(f"HTTP Status: {response.status_code}")
            print(f"Content length: {len(response.text)}")
            print(f"Content preview: {response.text[:200]}...")
        except Exception as req_e:
            print(f"HTTP request failed: {req_e}")
            return
        
        # Now test scraping
        print("\nTesting scraping...")
        result = scraper.scrape_url(test_url)
        print(f"Scraping result: {result}")
        
        if result:
            print("SUCCESS: URL scraping is working!")
            print(f"Restaurant name: {result.name}")
            print(f"Address: {result.address}")
            print(f"Sources: {result.sources}")
        else:
            print("FAILURE: No data extracted from URL")
            
    except Exception as e:
        print(f"ERROR: Exception during scraping: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_url_scraping()