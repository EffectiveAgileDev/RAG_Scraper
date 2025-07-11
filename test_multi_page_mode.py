#!/usr/bin/env python3
"""Test script to verify multi-page mode behavior."""

import requests
from bs4 import BeautifulSoup


def test_multi_page_mode():
    """Test the multi-page mode behavior."""
    
    try:
        response = requests.get('http://localhost:8085', timeout=5)
        html_content = response.text
    except:
        print("❌ Server not running on localhost:8085")
        return
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    print("🔍 Analyzing multi-page mode behavior...")
    
    # Check radio buttons
    single_page_radio = soup.find('input', {'name': 'scrapingMode', 'value': 'single'})
    multi_page_radio = soup.find('input', {'name': 'scrapingMode', 'value': 'multi'})
    
    print(f"📻 Single page radio checked: {single_page_radio.get('checked') is not None}")
    print(f"📻 Multi page radio checked: {multi_page_radio.get('checked') is not None}")
    
    # Check headers
    single_page_header = soup.find(id='singlePageHeader')
    multi_page_header = soup.find(id='multiPageHeader')
    
    print(f"📋 Single page header style: {single_page_header.get('style', '')}")
    print(f"📋 Multi page header style: {multi_page_header.get('style', '')}")
    
    # Check if JavaScript function exists
    if 'setupModeSelection' in html_content:
        print("✅ setupModeSelection function found in HTML")
    else:
        print("❌ setupModeSelection function NOT found in HTML")
        
    # Check if event listeners are properly set up
    if 'addEventListener' in html_content and 'mode-option' in html_content:
        print("✅ Event listeners for mode-option found")
    else:
        print("❌ Event listeners for mode-option NOT found")
    
    # Check the mode option labels
    mode_options = soup.find_all('label', {'class': 'mode-option'})
    print(f"🏷️  Found {len(mode_options)} mode option labels:")
    
    for i, option in enumerate(mode_options):
        data_mode = option.get('data-mode')
        classes = option.get('class', [])
        is_active = 'active' in classes
        print(f"  {i+1}. data-mode='{data_mode}' active={is_active} classes={classes}")
    
    # Check if both headers are visible (the reported issue)
    single_header_visible = 'display: block' in single_page_header.get('style', '')
    multi_header_visible = 'display: block' in multi_page_header.get('style', '')
    
    print(f"\n🔍 VISIBILITY ANALYSIS:")
    print(f"Single page header visible: {single_header_visible}")
    print(f"Multi page header visible: {multi_header_visible}")
    
    if single_header_visible and multi_header_visible:
        print("❌ BUG CONFIRMED: Both headers are visible!")
    elif single_header_visible and not multi_header_visible:
        print("✅ CORRECT: Only single page header is visible (default state)")
    elif not single_header_visible and multi_header_visible:
        print("✅ CORRECT: Only multi page header is visible")
    else:
        print("❌ ISSUE: No headers are visible")
        
    # Check if the issue is in the initial state
    print(f"\n🔍 INITIAL STATE:")
    print(f"Default mode should be single-page")
    print(f"Single page header should be visible: {single_header_visible}")
    print(f"Multi page header should be hidden: {not multi_header_visible}")
    
    # Provide instructions for manual testing
    print(f"\n📝 MANUAL TESTING INSTRUCTIONS:")
    print(f"1. Open http://localhost:8085 in browser")
    print(f"2. Look for SCRAPING_MODE section")
    print(f"3. Click on 'MULTI_PAGE' radio button")
    print(f"4. Check if:")
    print(f"   - SINGLE_PAGE_CONFIG header disappears")
    print(f"   - MULTI_PAGE_CONFIG header appears")
    print(f"   - Only ONE config section is visible")


if __name__ == "__main__":
    test_multi_page_mode()