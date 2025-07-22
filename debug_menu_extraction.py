#!/usr/bin/env python3
"""Debug script to test menu extraction from JavaScript-rendered content."""

import sys
import os
from bs4 import BeautifulSoup

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

from src.scraper.heuristic_extractor import HeuristicExtractor

def create_test_html():
    """Create test HTML that mimics the structure from piattinopdx.com with JavaScript-rendered content."""
    return '''
    <html>
    <head>
        <title>Piattino Italian Restaurant</title>
    </head>
    <body>
        <div id="content">
            <h1>Piattino Italian Restaurant</h1>
            
            <!-- Simulate JavaScript-rendered menu content -->
            <div class="menu-section">
                <h2>Pizza</h2>
                <div class="menu-item">
                    <h3>Pepperoni Plus $19.9</h3>
                    <p>Traditional pepperoni pizza with extra cheese</p>
                </div>
                <div class="menu-item">
                    <h3>Margherita $18.0</h3>
                    <p>Fresh mozzarella, basil, and tomato</p>
                </div>
            </div>
            
            <div class="menu-section">
                <h2>Main Dishes</h2>
                <div class="menu-item">
                    <h3>House Meatballs $23.0</h3>
                    <p>Homemade meatballs in marinara sauce</p>
                </div>
                <div class="menu-item">
                    <h3>Chicken Parmigiana $25.5</h3>
                    <p>Breaded chicken breast with marinara and mozzarella</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

def debug_menu_extraction():
    """Debug the menu extraction process step by step."""
    print("=== DEBUG: Menu Extraction Analysis ===\n")
    
    # Create test HTML content
    html_content = create_test_html()
    print("1. Test HTML created with menu items containing prices like:")
    print("   - Pepperoni Plus $19.9")
    print("   - House Meatballs $23.0")
    print("   - Margherita $18.0")
    print("   - Chicken Parmigiana $25.5\n")
    
    # Initialize the heuristic extractor
    extractor = HeuristicExtractor()
    print("2. HeuristicExtractor initialized\n")
    
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    print("3. HTML parsed with BeautifulSoup\n")
    
    # Test the _extract_menu_items method directly
    print("4. Testing _extract_menu_items method:\n")
    menu_items = extractor._extract_menu_items(soup)
    
    print(f"   Found {len(menu_items)} menu sections:")
    for section_name, items in menu_items.items():
        print(f"   - {section_name}: {len(items)} items")
        for item in items:
            print(f"     * {item}")
    print()
    
    # Check what headers are found
    print("5. Analyzing header structure:")
    all_headers = soup.find_all(["h1", "h2", "h3"])
    for header in all_headers:
        print(f"   - {header.name}: '{header.get_text().strip()}'")
    print()
    
    # Check menu section patterns
    print("6. Testing menu section pattern matching:")
    section_patterns = [
        r"appetizers?", r"entrees?", r"desserts?", r"beverages?", r"mains?", r"drinks?", r"cocktails?",
        r"shared plates?", r"small plates?", r"starters?", r"salads?", r"greens?", r"soups?",
        r"burgers?", r"sandwiches?", r"pizza", r"pasta", r"main plates?", r"brunch", r"lunch", 
        r"dinner", r"sides?", r"kids?", r"wine", r"beer", r"favorites?", r"specials?", r"classics?"
    ]
    
    import re
    h2_headers = soup.find_all("h2")
    for header_elem in h2_headers:
        header_text = header_elem.get_text().strip()
        print(f"   Header: '{header_text}'")
        
        is_menu_section = False
        for pattern in section_patterns:
            if re.search(pattern, header_text, re.I):
                print(f"     ✓ Matches pattern: {pattern}")
                is_menu_section = True
                break
        
        if not is_menu_section:
            # Check for common menu-related words
            menu_keywords = ["menu", "food", "plate", "item", "dish"]
            for keyword in menu_keywords:
                if keyword in header_text.lower():
                    print(f"     ✓ Contains menu keyword: {keyword}")
                    is_menu_section = True
                    break
        
        if not is_menu_section:
            print(f"     ✗ No pattern match found")
    print()
    
    # Test full extraction pipeline
    print("7. Testing full heuristic extraction:")
    results = extractor.extract_from_html(html_content, "https://piattinopdx.com")
    
    if results:
        result = results[0]
        print(f"   Restaurant name: '{result.name}'")
        print(f"   Confidence: {result.confidence}")
        print(f"   Source: {result.source}")
        print(f"   Menu items found: {len(result.menu_items)} sections")
        for section_name, items in result.menu_items.items():
            print(f"     - {section_name}: {items}")
    else:
        print("   ✗ No results returned from extraction")
    print()

if __name__ == "__main__":
    debug_menu_extraction()