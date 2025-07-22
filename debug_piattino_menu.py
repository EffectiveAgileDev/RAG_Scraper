#!/usr/bin/env python3
"""Debug script specifically for piattinopdx.com menu extraction."""

import sys
import requests
import re
from bs4 import BeautifulSoup
from src.scraper.heuristic_extractor import HeuristicExtractor

def debug_piattino_menu():
    """Debug menu extraction for piattinopdx.com specifically."""
    url = "https://piattinopdx.com/"
    
    print("=== PIATTINO PDX MENU EXTRACTION DEBUG ===\n")
    
    # Fetch the HTML
    print("1. Fetching HTML...")
    response = requests.get(url, timeout=30)
    html_content = response.text
    print(f"   Status: {response.status_code}")
    print(f"   Content length: {len(html_content):,} chars\n")
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Search for text containing the menu items we know exist
    print("2. Searching for known menu items in text content:")
    full_text = soup.get_text()
    
    menu_items_to_find = [
        "Pepperoni Plus",
        "House Meatballs", 
        "$19.9",
        "$23.0"
    ]
    
    for item in menu_items_to_find:
        if item in full_text:
            print(f"   ✓ Found: '{item}'")
        else:
            print(f"   ✗ Missing: '{item}'")
    
    print(f"\n3. Looking for any text containing dollar amounts:")
    price_matches = re.findall(r'\$\d+(?:\.\d+)?', full_text)
    print(f"   Found {len(price_matches)} price patterns: {price_matches[:10]}...")
    
    # Check what headers exist
    print(f"\n4. Analyzing header structure:")
    headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    print(f"   Found {len(headers)} headers:")
    
    for i, header in enumerate(headers[:20]):  # Limit to first 20
        text = header.get_text().strip()
        if text and len(text) < 100:  # Only show reasonably short headers
            print(f"   [{i+1}] {header.name}: '{text}'")
            
            # Check if this might be a menu section
            menu_patterns = ['pizza', 'pasta', 'appetizer', 'entree', 'dessert', 'drink', 'main', 'starter']
            is_menu_related = any(pattern in text.lower() for pattern in menu_patterns)
            if is_menu_related:
                print(f"       ^ Menu-related header!")
    
    print(f"\n5. Looking for elements that might contain menu items:")
    
    # Look for divs that might contain menu items
    divs_with_prices = []
    for div in soup.find_all('div'):
        div_text = div.get_text()
        if '$' in div_text and any(item in div_text for item in ['pepperoni', 'meatball', 'pizza']):
            divs_with_prices.append(div)
    
    print(f"   Found {len(divs_with_prices)} divs containing prices and menu keywords")
    
    for i, div in enumerate(divs_with_prices[:5]):  # Show first 5
        text = div.get_text().strip()
        if len(text) < 200:  # Don't show huge blocks of text
            print(f"   [{i+1}] {text}")
    
    # Test the actual menu extraction
    print(f"\n6. Testing HeuristicExtractor._extract_menu_items:")
    extractor = HeuristicExtractor()
    menu_items = extractor._extract_menu_items(soup)
    
    print(f"   Menu sections found: {len(menu_items)}")
    for section_name, items in menu_items.items():
        print(f"   - {section_name}: {len(items)} items")
        for item in items:
            print(f"     * {item}")
    
    # Check for JavaScript-rendered content clues
    print(f"\n7. Checking for JavaScript-rendered content indicators:")
    scripts = soup.find_all('script')
    print(f"   Found {len(scripts)} script tags")
    
    # Look for common JS frameworks/patterns
    js_indicators = ['react', 'vue', 'angular', 'jquery', 'ajax', 'fetch']
    for script in scripts:
        if script.string:
            script_text = script.string.lower()
            for indicator in js_indicators:
                if indicator in script_text:
                    print(f"   ✓ Found {indicator} in JavaScript")
                    break
    
    # Look for menu-related JavaScript variables
    print(f"\n8. Searching for menu data in JavaScript:")
    menu_js_patterns = [
        r'menu\s*[=:]',
        r'pizza\s*[=:]', 
        r'item\s*[=:]',
        r'price\s*[=:]'
    ]
    
    for script in scripts:
        if script.string:
            script_text = script.string
            for pattern in menu_js_patterns:
                matches = re.findall(pattern, script_text, re.IGNORECASE)
                if matches:
                    print(f"   Found menu-related JS pattern: {pattern} ({len(matches)} matches)")
                    
                    # Show context around the match
                    for match_obj in re.finditer(pattern, script_text, re.IGNORECASE):
                        start = max(0, match_obj.start() - 50)
                        end = min(len(script_text), match_obj.end() + 50)
                        context = script_text[start:end].replace('\n', ' ').strip()
                        print(f"     Context: ...{context}...")
                        break  # Just show first match
    
    print(f"\n9. Final heuristic extraction test:")
    results = extractor.extract_from_html(html_content, url)
    
    if results:
        result = results[0]
        print(f"   Restaurant: {result.name}")
        print(f"   Menu sections: {len(result.menu_items)}")
        
        if result.menu_items:
            for section_name, items in result.menu_items.items():
                print(f"   - {section_name}: {items}")
        else:
            print("   ✗ No menu items found!")
    else:
        print("   ✗ No results from heuristic extraction!")

if __name__ == "__main__":
    debug_piattino_menu()