#!/usr/bin/env python3
"""Test script to verify mode switching behavior in the browser."""

import requests
from bs4 import BeautifulSoup
import time


def test_mode_switching():
    """Test that mode switching works correctly."""
    
    try:
        response = requests.get('http://localhost:8085', timeout=5)
        html_content = response.text
        print("✅ Successfully connected to server")
    except:
        print("❌ Server not running on localhost:8085")
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Test 1: Check initial state
    print("\n🔍 Testing initial state:")
    single_page_header = soup.find(id='singlePageHeader')
    multi_page_header = soup.find(id='multiPageHeader')
    
    print(f"Single page header style: {single_page_header.get('style', '')}")
    print(f"Multi page header style: {multi_page_header.get('style', '')}")
    
    # Test 2: Check JavaScript function exists
    print("\n🔍 Testing JavaScript function:")
    if 'setupModeSelection' in html_content:
        print("✅ setupModeSelection function found")
    else:
        print("❌ setupModeSelection function NOT found")
        
    # Test 3: Check that the function properly handles both headers
    print("\n🔍 Testing header control logic:")
    
    # Look for the specific lines that control singlePageHeader
    if 'singlePageHeader.style.display' in html_content:
        print("✅ singlePageHeader visibility control found")
    else:
        print("❌ singlePageHeader visibility control NOT found")
        
    if 'multiPageHeader.style.display' in html_content:
        print("✅ multiPageHeader visibility control found")
    else:
        print("❌ multiPageHeader visibility control NOT found")
        
    # Test 4: Check specific fix implementation
    print("\n🔍 Testing specific fix implementation:")
    if 'singlePageHeader.style.display = \'none\'' in html_content:
        print("✅ Code to hide singlePageHeader found")
    else:
        print("❌ Code to hide singlePageHeader NOT found")
        
    if 'multiPageHeader.style.display = \'block\'' in html_content:
        print("✅ Code to show multiPageHeader found")
    else:
        print("❌ Code to show multiPageHeader NOT found")
        
    # Test 5: Print the actual JavaScript code for verification
    print("\n🔍 Extracting relevant JavaScript code:")
    lines = html_content.split('\n')
    in_setup_function = False
    
    for line in lines:
        if 'function setupModeSelection()' in line:
            in_setup_function = True
            print("Found setupModeSelection function:")
            
        if in_setup_function:
            if 'singlePageHeader.style.display' in line or 'multiPageHeader.style.display' in line:
                print(f"  {line.strip()}")
                
            if line.strip() == '}' and 'setupModeSelection' in line:
                break
                
    print("\n📝 EXPECTED BEHAVIOR:")
    print("1. By default: singlePageHeader visible, multiPageHeader hidden")
    print("2. When MULTI_PAGE clicked: singlePageHeader hidden, multiPageHeader visible")
    print("3. When SINGLE_PAGE clicked: singlePageHeader visible, multiPageHeader hidden")
    
    print("\n📝 MANUAL TESTING:")
    print("1. Open http://localhost:8085")
    print("2. Look for SCRAPING_MODE section")
    print("3. Click MULTI_PAGE radio button")
    print("4. Verify only MULTI_PAGE_CONFIG header is visible")
    print("5. Click SINGLE_PAGE radio button")
    print("6. Verify only SINGLE_PAGE_CONFIG header is visible")


if __name__ == "__main__":
    test_mode_switching()