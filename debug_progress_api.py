#!/usr/bin/env python3
"""Debug script to check what the progress API returns during scraping."""

import requests
import json
import time

def check_progress():
    """Check progress API response."""
    url = "http://localhost:8085/api/progress"
    
    print("Checking progress API response...")
    print("-" * 50)
    
    try:
        response = requests.get(url)
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Data:")
        print(json.dumps(data, indent=2))
        
        # Highlight key fields
        print("\nKey Fields:")
        print(f"- progress_percentage: {data.get('progress_percentage', 'NOT FOUND')}")
        print(f"- urls_total: {data.get('urls_total', 'NOT FOUND')}")
        print(f"- urls_completed: {data.get('urls_completed', 'NOT FOUND')}")
        print(f"- current_operation: {data.get('current_operation', 'NOT FOUND')}")
        print(f"- status: {data.get('status', 'NOT FOUND')}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Check immediately
    check_progress()
    
    print("\nMonitoring progress for 30 seconds...")
    print("Start a scraping operation to see changes.")
    print("-" * 50)
    
    # Monitor for 30 seconds
    for i in range(30):
        time.sleep(1)
        print(f"\n[{i+1}s] ", end="")
        
        try:
            response = requests.get("http://localhost:8085/api/progress")
            data = response.json()
            
            if data.get('status') == 'processing':
                print("PROCESSING DETECTED!")
                print(f"  - progress: {data.get('progress_percentage')}%")
                print(f"  - urls: {data.get('urls_completed')}/{data.get('urls_total')}")
                print(f"  - operation: {data.get('current_operation', 'None')}")
            else:
                print(f"Idle (status: {data.get('status')})")
                
        except Exception as e:
            print(f"Error: {e}")