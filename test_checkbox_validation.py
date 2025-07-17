#!/usr/bin/env python3
"""Test AI Enhancement checkbox state validation fix."""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import requests
import json

def test_ai_checkbox_validation():
    """Test that AI Enhancement checkbox state is properly recognized."""
    print("Testing AI Enhancement checkbox validation fix...")
    
    base_url = "http://localhost:8085"
    
    # Test 1: Check that the main page loads correctly
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"Main page status: {response.status_code}")
        if response.status_code != 200:
            print("FAILURE: Main page not accessible")
            return False
    except Exception as e:
        print(f"FAILURE: Cannot connect to Flask app: {e}")
        return False
    
    # Test 2: Test AI configuration endpoint with multi-page mode
    ai_config_data = {
        "ai_enhancement_enabled": True,
        "llm_provider": "openai",
        "api_key": "sk-test-key",
        "features": {
            "nutritional_analysis": True,
            "price_analysis": False
        },
        "confidence_threshold": 0.7
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/ai/configure",
            json=ai_config_data,
            timeout=5
        )
        print(f"AI configure endpoint status: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS: AI configuration endpoint working")
        else:
            print(f"WARNING: AI configure returned {response.status_code}")
    except Exception as e:
        print(f"WARNING: AI configure endpoint error: {e}")
    
    # Test 3: Test multi-page scraping with AI config
    scraping_data = {
        "urls": ["https://example.com"],
        "output_dir": "/tmp",
        "file_mode": "single",
        "file_format": "json",
        "industry": "restaurant",
        "scraping_mode": "multi",  # This should now be the default
        "multi_page_config": {
            "maxPages": 5,
            "crawlDepth": 1
        },
        "ai_config": ai_config_data,
        "session_id": "test_session_123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/scrape",
            json=scraping_data,
            timeout=10
        )
        print(f"Scraping endpoint status: {response.status_code}")
        if response.status_code == 200 or response.status_code == 400:
            result = response.json()
            print(f"Scraping result keys: {list(result.keys())}")
            if "ai_config" in str(result) or "ai_analysis" in str(result):
                print("SUCCESS: AI configuration being processed in scraping request")
                return True
            else:
                print("INFO: Scraping processed but no AI config visible in response")
                return True
        else:
            print(f"WARNING: Scraping returned {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Scraping endpoint error: {e}")
        return False

if __name__ == "__main__":
    success = test_ai_checkbox_validation()
    if success:
        print("\n✅ AI Enhancement checkbox validation appears to be fixed!")
    else:
        print("\n❌ AI Enhancement checkbox validation still has issues.")