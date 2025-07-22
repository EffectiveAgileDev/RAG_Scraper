#!/usr/bin/env python3
"""Debug script to test enhanced menu extraction on Piattino content."""

import requests
from bs4 import BeautifulSoup
from src.scraper.heuristic_extractor import HeuristicExtractor

def test_piattino_menu_extraction():
    """Test the enhanced menu extraction on Piattino's actual menu page."""
    
    print("Testing enhanced menu extraction on Piattino...")
    
    # Test the main menu page that should have detailed content
    menu_url = "https://piattinopdx.com/menus/"
    
    try:
        # Fetch the menu page content
        response = requests.get(menu_url, timeout=10)
        response.raise_for_status()
        html_content = response.text
        
        print(f"Fetched {len(html_content)} characters from {menu_url}")
        
        # Debug: Find all section headers first
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        print(f"\\nAll h2 headers found:")
        for h2 in soup.find_all('h2'):
            print(f"  '{h2.get_text().strip()}'")
            
        print(f"\\nAll h3 headers found (first 20):")
        for i, h3 in enumerate(soup.find_all('h3')[:20]):
            classes = h3.get('class', [])
            print(f"  {i+1}. '{h3.get_text().strip()}' classes={classes}")
            
        print(f"\\nAll WordPress food-menu divs found (first 10):")
        wp_divs = soup.find_all('div', class_='food-menu-content-top-holder')
        print(f"Found {len(wp_divs)} WordPress food-menu divs")
        for i, div in enumerate(wp_divs[:10]):
            title_holder = div.find(class_='food-menu-content-title-holder')
            if title_holder:
                title_elem = title_holder.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                title_text = title_elem.get_text().strip() if title_elem else "No title"
            else:
                title_text = "No title holder"
            print(f"  {i+1}. {title_text}")

        # Test enhanced heuristic extraction
        extractor = HeuristicExtractor()
        results = extractor.extract_from_html(html_content, menu_url)
        
        if results:
            for result in results:
                print(f"\nExtraction Result:")
                print(f"  Name: {result.name}")
                print(f"  Confidence: {result.confidence}")
                print(f"  Menu sections: {len(result.menu_items) if result.menu_items else 0}")
                
                if result.menu_items:
                    total_items = sum(len(items) for items in result.menu_items.values())
                    print(f"  Total menu items: {total_items}")
                    
                    for section_name, items in result.menu_items.items():
                        print(f"\n  Section: {section_name} ({len(items)} items)")
                        for i, item in enumerate(items):  # Show ALL items to see what we're getting
                            item_preview = item[:150] + "..." if len(item) > 150 else item
                            print(f"    {i+1}. {item_preview}")
                            # Check if this looks like a detailed description
                            if ':' in item and len(item) > 50:
                                print(f"         *** This looks like a detailed description! ***")
                else:
                    print("  No menu items found")
        else:
            print("No extraction results returned")
            
    except Exception as e:
        print(f"Error testing extraction: {e}")

def test_with_sample_html():
    """Test with sample HTML that should work with enhanced extraction."""
    print("\nTesting with sample HTML...")
    
    sample_html = """
    <html>
    <body>
        <h3>Cheese Selection</h3>
        <p>Taleggio: cow milk, semi-soft, wash rind, strong, bold aroma with an unusual fruity tang</p>
        <p>Gorgonzola: cow milk, semi-soft, blue cheese with a creamy texture and tangy flavor</p>
        
        <h3>Antipasti</h3>
        <p>Bruschetta alla Napoletana: grilled bread with fresh tomatoes, basil, and garlic</p>
        <p>Carpaccio di Manzo: thin sliced raw beef with arugula, capers, and lemon</p>
    </body>
    </html>
    """
    
    extractor = HeuristicExtractor()
    results = extractor.extract_from_html(sample_html)
    
    if results:
        for result in results:
            print(f"Sample HTML Results:")
            print(f"  Menu sections: {len(result.menu_items) if result.menu_items else 0}")
            
            if result.menu_items:
                for section_name, items in result.menu_items.items():
                    print(f"  {section_name}: {len(items)} items")
                    for item in items:
                        print(f"    - {item}")
            else:
                print("  No menu items found")
    else:
        print("No results from sample HTML")

if __name__ == "__main__":
    test_with_sample_html()
    test_piattino_menu_extraction()