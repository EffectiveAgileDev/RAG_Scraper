#!/usr/bin/env python3
"""Test script to monitor progress API during actual scraping."""

import requests
import json
import time
import threading

def monitor_progress():
    """Monitor progress API while scraping."""
    print("Starting progress monitoring...")
    
    for i in range(60):  # Monitor for 60 seconds
        try:
            response = requests.get("http://localhost:8085/api/progress")
            data = response.json()
            
            if data.get('status') == 'processing' or data.get('progress_percentage', 0) > 0:
                print(f"\n[{i+1}s] ACTIVE PROCESSING:")
                print(f"  - Status: {data.get('status')}")
                print(f"  - Progress: {data.get('progress_percentage')}%")
                print(f"  - URLs: {data.get('urls_completed')}/{data.get('urls_total')}")
                print(f"  - Current URL: {data.get('current_url', 'None')}")
                print(f"  - Operation: '{data.get('current_operation', 'None')}'")
            else:
                print(".", end="", flush=True)
                
        except Exception as e:
            print(f"\n[{i+1}s] Error: {e}")
            
        time.sleep(1)

def start_scraping():
    """Start a scraping request."""
    print("\nStarting scraping request...")
    
    url = "http://localhost:8085/api/scrape"
    payload = {
        "urls": ["https://mettavern.com/"],
        "output_dir": "/tmp/test_output",
        "file_mode": "single",
        "file_format": "text",
        "json_field_selections": {},
        "scraping_mode": "single",
        "multi_page_config": {},
        "enableJavaScript": False,
        "jsTimeout": 30,
        "enablePopupHandling": True,
        "industry": "Restaurant"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Scraping Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Processed: {data.get('processed_count')}")
            print(f"Failed: {data.get('failed_count')}")
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Scraping Error: {e}")

if __name__ == "__main__":
    print("Testing progress display during scraping")
    print("=" * 50)
    
    # Start progress monitoring in background
    monitor_thread = threading.Thread(target=monitor_progress, daemon=True)
    monitor_thread.start()
    
    # Wait a moment then start scraping
    time.sleep(2)
    start_scraping()
    
    # Wait for monitoring to finish
    monitor_thread.join()
    print("\nMonitoring complete.")