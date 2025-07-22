#!/usr/bin/env python3
"""Debug script to compare multi-page scraper reporting vs actual extraction."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scraper.multi_page_scraper import MultiPageScraper
from src.scraper.multi_strategy_scraper import MultiStrategyScraper
from src.web_interface.handlers.scraping_request_handler import ScrapingRequestHandler
import requests

def debug_multipage_vs_actual():
    """Debug the disconnect between multi-page reporting and actual extraction."""
    
    print("=== MULTI-PAGE SCRAPER vs ACTUAL EXTRACTION COMPARISON ===\n")
    
    url = "https://piattinopdx.com/"
    menu_url = "https://piattinopdx.com/menus/"
    
    print("1. ACTUAL EXTRACTION WITH HEURISTIC EXTRACTOR:")
    print("=" * 50)
    
    # Test direct multi-strategy extraction
    extractor = MultiStrategyScraper(enable_ethical_scraping=False)
    
    # Test home page
    print(f"Testing home page: {url}")
    result = extractor.scrape_url(url)
    if result:
        print(f"   Home page menu items: {len(result.menu_items)} sections")
        if result.menu_items:
            total_items = sum(len(items) for items in result.menu_items.values())
            print(f"   Total items found: {total_items}")
            for section, items in result.menu_items.items():
                print(f"   - {section}: {len(items)} items")
        else:
            print("   No menu items found")
    else:
        print("   No data extracted from home page")
    
    # Test menu page if it exists
    print(f"\nTesting menu page: {menu_url}")
    try:
        result = extractor.scrape_url(menu_url)
        if result:
            print(f"   Menu page menu items: {len(result.menu_items)} sections")
            if result.menu_items:
                total_items = sum(len(items) for items in result.menu_items.values())
                print(f"   Total items found: {total_items}")
                for section, items in result.menu_items.items():
                    print(f"   - {section}: {len(items)} items")
            else:
                print("   No menu items found")
        else:
            print("   No data extracted from menu page")
    except Exception as e:
        print(f"   Error accessing menu page: {e}")
    
    print("\n\n2. MULTI-PAGE SCRAPER RESULTS:")
    print("=" * 50)
    
    # Test multi-page scraper
    scraper = MultiPageScraper(max_pages=5, enable_ethical_scraping=True)
    result = scraper.scrape_website(url)
    
    print(f"Pages processed: {len(result.pages_processed)}")
    print(f"Pages discovered: {result.pages_processed}")
    print(f"Successful pages: {len(result.successful_pages)}")
    print(f"Failed pages: {len(result.failed_pages)}")
    
    if result.aggregated_data:
        print(f"\nAggregated data:")
        print(f"   Restaurant: {result.aggregated_data.name}")
        print(f"   Menu sections: {len(result.aggregated_data.menu_items)} sections")
        if result.aggregated_data.menu_items:
            total_items = sum(len(items) for items in result.aggregated_data.menu_items.values())
            print(f"   Total aggregated items: {total_items}")
            for section, items in result.aggregated_data.menu_items.items():
                print(f"   - {section}: {len(items)} items")
        print(f"   Confidence: {result.aggregated_data.confidence}")
        print(f"   Sources: {result.aggregated_data.sources}")
    
    print(f"\nData sources summary:")
    if result.data_sources_summary:
        print(f"   Total pages in summary: {result.data_sources_summary.get('total_pages', 0)}")
        print(f"   Sources: {result.data_sources_summary.get('sources', {})}")
        print(f"   Page types: {result.data_sources_summary.get('page_types', {})}")
        print(f"   Fields found: {result.data_sources_summary.get('fields_found', [])}")
    
    print("\n\n3. SCRAPING REQUEST HANDLER UI ESTIMATION:")
    print("=" * 50)
    
    # Simulate what the scraping request handler would calculate
    total_menu_items = 0
    if result.aggregated_data and result.aggregated_data.menu_items:
        for section, items in result.aggregated_data.menu_items.items():
            if isinstance(items, list):
                total_menu_items += len(items)
    
    print(f"Total menu items for estimation: {total_menu_items}")
    
    # This is the logic from scraping_request_handler.py lines 676-678
    for page_url in result.pages_processed:
        if 'food-menu' in page_url.lower() or ('menu' in page_url.lower() and 'drink' not in page_url.lower()):
            # Food menus typically have more items
            page_items = max(45, int(total_menu_items * 0.5)) if total_menu_items > 0 else 0
            print(f"   {page_url} -> Estimated UI display: {page_items} items")
        elif page_url.endswith('/') or page_url.endswith('/#'):
            # Home page might have overview items  
            page_items = max(10, int(total_menu_items * 0.05)) if total_menu_items > 0 else 0
            print(f"   {page_url} -> Estimated UI display: {page_items} items")
        else:
            page_items = 0
            print(f"   {page_url} -> Estimated UI display: {page_items} items")
    
    print("\n\n4. ANALYSIS:")
    print("=" * 50)
    
    print("The disconnect occurs because:")
    print("1. Multi-page scraper discovers multiple pages (including /menus/)")
    print("2. Actual extraction finds limited items (8 items from home page)")
    print("3. UI estimation logic assigns minimum 45 items to menu URLs")
    print("4. User sees '45 items found' but actual extraction only has 8 items")
    print("\nThe '45 items found' is a UI estimation, not actual extraction results!")

if __name__ == "__main__":
    debug_multipage_vs_actual()