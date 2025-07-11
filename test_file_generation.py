#!/usr/bin/env python3
"""Test script to verify file generation issue."""

import os
import tempfile
import requests
import json

def test_file_generation():
    """Test the file generation process with a real file."""
    
    # Find an existing test file
    test_files = [
        "/tmp/test_uploads/1752077956898_34672091_test_restaurant.pdf",
        "/tmp/test_uploads/1752077956904_f4c06a98_test_restaurant.pdf"
    ]
    
    existing_file = None
    for file_path in test_files:
        if os.path.exists(file_path):
            existing_file = file_path
            break
    
    if not existing_file:
        print("❌ No test files found")
        return
    
    print(f"📄 Testing with file: {existing_file}")
    
    # Create output directory
    output_dir = "/tmp/test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Test the RAG processing endpoint
    payload = {
        "file_ids": [],
        "file_paths": [existing_file],
        "output_dir": output_dir,
        "file_mode": "single",
        "file_format": "text",
        "scraping_mode": "single",
        "industry": "restaurant"
    }
    
    print(f"🔍 Making request to process-uploaded-files-for-rag...")
    print(f"📋 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            'http://localhost:8085/api/process-uploaded-files-for-rag',
            json=payload,
            timeout=30
        )
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📄 Response content: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                output_files = data.get('output_files', [])
                print(f"✅ Success! Output files: {output_files}")
                
                # Check if output files actually exist
                for file in output_files:
                    full_path = os.path.join(output_dir, file)
                    if os.path.exists(full_path):
                        print(f"✅ File exists: {full_path}")
                        # Check file size
                        size = os.path.getsize(full_path)
                        print(f"📏 File size: {size} bytes")
                        
                        # Check if it's different from original
                        orig_size = os.path.getsize(existing_file)
                        print(f"📏 Original file size: {orig_size} bytes")
                        
                        if size != orig_size:
                            print("✅ Generated file is different from original!")
                        else:
                            print("❌ Generated file is same size as original")
                    else:
                        print(f"❌ File does not exist: {full_path}")
            else:
                print(f"❌ API returned error: {data.get('error')}")
        else:
            print(f"❌ API call failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_file_generation()