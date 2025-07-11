#!/usr/bin/env python3
"""
Debug script to analyze restaurant data extraction for mettavern.com and other sites.
This script helps understand why certain restaurant pages might return "No restaurant data found".
"""

import sys
import requests
from bs4 import BeautifulSoup
from src.scraper.multi_strategy_scraper import MultiStrategyScraper
from src.scraper.restaurant_scraper import RestaurantScraper


def analyze_url(url: str, verbose: bool = True):
    """Analyze URL extraction step by step."""
    print(f"\n{'='*60}")
    print(f"ANALYZING: {url}")
    print(f"{'='*60}")
    
    try:
        # Step 1: Fetch HTML
        response = requests.get(url, timeout=30)
        html_content = response.text
        
        if verbose:
            print(f"\n1. HTML FETCH:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Content Length: {len(html_content):,} chars")
            print(f"   Content Type: {response.headers.get('content-type', 'Unknown')}")
            
            # Show first few lines to identify the site structure
            soup = BeautifulSoup(html_content, 'html.parser')
            title = soup.find('title')
            if title:
                print(f"   Page Title: {title.get_text().strip()[:100]}")
        
        # Step 2: Test individual extractors
        scraper = MultiStrategyScraper()
        
        print(f"\n2. EXTRACTION METHODS:")
        
        # JSON-LD
        json_ld_results = scraper.json_ld_extractor.extract_from_html(html_content)
        print(f"   JSON-LD: {len(json_ld_results)} results")
        for i, result in enumerate(json_ld_results):
            print(f"     [{i+1}] Name: '{result.name}' | Valid: {result.is_valid()} | Confidence: {result.confidence}")
            if verbose and result.address:
                print(f"         Address: {result.address}")
        
        # Microdata
        microdata_results = scraper.microdata_extractor.extract_from_html(html_content)
        print(f"   Microdata: {len(microdata_results)} results")
        for i, result in enumerate(microdata_results):
            print(f"     [{i+1}] Name: '{result.name}' | Valid: {result.is_valid()} | Confidence: {result.confidence}")
            if verbose and result.address:
                print(f"         Address: {result.address}")
        
        # Heuristic
        soup = BeautifulSoup(html_content, 'html.parser')
        is_restaurant_page = scraper.heuristic_extractor._is_restaurant_page(soup)
        print(f"   Heuristic - Is Restaurant Page: {is_restaurant_page}")
        
        heuristic_results = scraper.heuristic_extractor.extract_from_html(html_content, url)
        print(f"   Heuristic: {len(heuristic_results)} results")
        for i, result in enumerate(heuristic_results):
            print(f"     [{i+1}] Name: '{result.name}' | Valid: {result.is_valid()} | Confidence: {result.confidence}")
            if verbose:
                print(f"         Address: {result.address}")
                print(f"         Phone: {result.phone}")
                print(f"         Hours: {result.hours[:100]}..." if len(result.hours) > 100 else f"         Hours: {result.hours}")
                print(f"         Cuisine: {result.cuisine}")
                if result.menu_items:
                    menu_count = sum(len(items) for items in result.menu_items.values())
                    print(f"         Menu Items: {menu_count} items in {len(result.menu_items)} sections")
        
        # Step 3: Test final extraction
        print(f"\n3. FINAL EXTRACTION:")
        final_result = scraper.scrape_url(url)
        
        if final_result:
            print(f"   ✅ SUCCESS: Restaurant data extracted")
            print(f"   Name: {final_result.name}")
            print(f"   Address: {final_result.address}")
            print(f"   Phone: {final_result.phone}")
            print(f"   Confidence: {final_result.confidence}")
            print(f"   Sources: {', '.join(final_result.sources)}")
            print(f"   Website: {final_result.website}")
            
            if final_result.menu_items:
                total_items = sum(len(items) for items in final_result.menu_items.values())
                print(f"   Menu: {total_items} items in {len(final_result.menu_items)} sections")
            
            if final_result.social_media:
                print(f"   Social Media: {len(final_result.social_media)} links")
                
        else:
            print(f"   ❌ FAILED: No restaurant data found")
            
            # Debug why it failed
            print(f"\n   FAILURE ANALYSIS:")
            if not json_ld_results and not microdata_results and not heuristic_results:
                print(f"   - No extraction methods found valid data")
                if not is_restaurant_page:
                    print(f"   - Page not identified as restaurant website")
                    # Check for restaurant keywords
                    text_content = soup.get_text().lower()
                    restaurant_keywords = ['restaurant', 'menu', 'food', 'dining', 'cuisine']
                    found_keywords = [kw for kw in restaurant_keywords if kw in text_content]
                    print(f"   - Found keywords: {found_keywords}")
            else:
                print(f"   - Some extraction methods found data but validation failed")
                
        return final_result
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        if verbose:
            traceback.print_exc()
        return None


def main():
    """Main function to test multiple URLs."""
    test_urls = [
        "https://mettavern.com",  # Working example
        # Add other URLs to test here
    ]
    
    if len(sys.argv) > 1:
        # Allow passing URL as command line argument
        test_urls = [sys.argv[1]]
    
    print("Restaurant Data Extraction Debug Tool")
    print("====================================")
    
    results = {}
    for url in test_urls:
        result = analyze_url(url)
        results[url] = result
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    success_count = sum(1 for r in results.values() if r is not None)
    total_count = len(results)
    
    print(f"Successfully extracted: {success_count}/{total_count} URLs")
    
    for url, result in results.items():
        status = "✅ SUCCESS" if result else "❌ FAILED"
        name = f" - {result.name}" if result else ""
        print(f"  {status}: {url}{name}")


if __name__ == "__main__":
    main()