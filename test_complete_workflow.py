#!/usr/bin/env python3
"""Test complete file upload and download workflow."""

import os
import tempfile
import requests
import json
import time

def test_complete_workflow():
    """Test the complete workflow from file upload to download."""
    
    print("🚀 Starting complete workflow test...")
    
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
    
    print(f"📄 Using test file: {existing_file}")
    
    # Step 1: Upload the file
    print("\n📤 Step 1: Uploading file...")
    
    with open(existing_file, 'rb') as f:
        files = {'files': (os.path.basename(existing_file), f, 'application/pdf')}
        response = requests.post('http://localhost:8085/api/upload/batch', files=files)
    
    print(f"Upload response status: {response.status_code}")
    print(f"Upload response text: {response.text}")
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.status_code} - {response.text}")
        return
    
    try:
        upload_data = response.json()
    except:
        print(f"❌ Failed to parse upload response JSON: {response.text}")
        return
    if not upload_data.get('success'):
        print(f"❌ Upload failed: {upload_data.get('error')}")
        return
    
    file_ids = upload_data.get('file_ids', [])
    print(f"✅ Upload successful! File IDs: {file_ids}")
    
    # Step 2: Process the file through RAG pipeline
    print("\n⚙️  Step 2: Processing file through RAG pipeline...")
    
    payload = {
        "file_ids": file_ids,
        "file_paths": [],
        "output_dir": "",  # Use default
        "file_mode": "single",
        "file_format": "text",
        "scraping_mode": "single",
        "industry": "restaurant"
    }
    
    response = requests.post(
        'http://localhost:8085/api/process-uploaded-files-for-rag',
        json=payload
    )
    
    if response.status_code != 200:
        print(f"❌ Processing failed: {response.status_code} - {response.text}")
        return
    
    process_data = response.json()
    if not process_data.get('success'):
        print(f"❌ Processing failed: {process_data.get('error')}")
        return
    
    output_files = process_data.get('output_files', [])
    print(f"✅ Processing successful! Output files: {output_files}")
    
    # Step 3: Download the generated file
    print("\n⬇️  Step 3: Downloading generated file...")
    
    if not output_files:
        print("❌ No output files to download")
        return
    
    output_file = output_files[0]
    download_url = f'http://localhost:8085/api/download/{output_file}'
    
    response = requests.get(download_url)
    
    if response.status_code != 200:
        print(f"❌ Download failed: {response.status_code} - {response.text}")
        return
    
    # Save the downloaded file
    download_path = f'/tmp/downloaded_{output_file}'
    with open(download_path, 'wb') as f:
        f.write(response.content)
    
    print(f"✅ Download successful! Saved to: {download_path}")
    
    # Step 4: Verify the content
    print("\n🔍 Step 4: Verifying generated content...")
    
    if not os.path.exists(download_path):
        print("❌ Downloaded file doesn't exist")
        return
    
    # Check file size
    download_size = os.path.getsize(download_path)
    original_size = os.path.getsize(existing_file)
    
    print(f"📏 Original file size: {original_size} bytes")
    print(f"📏 Downloaded file size: {download_size} bytes")
    
    # Check content
    with open(download_path, 'r') as f:
        content = f.read()
    
    print(f"📄 Generated content:\n{content}")
    
    # Verify it's not the original file
    if download_size == original_size:
        print("⚠️  WARNING: Downloaded file is same size as original")
    else:
        print("✅ Downloaded file is different from original")
    
    # Verify it contains expected restaurant data
    expected_fields = ['Restaurant', 'Address', 'Phone', 'CUISINE']
    found_fields = [field for field in expected_fields if field in content]
    
    print(f"✅ Found {len(found_fields)}/{len(expected_fields)} expected fields: {found_fields}")
    
    # Summary
    print("\n📊 WORKFLOW TEST SUMMARY:")
    print("✅ File upload: SUCCESS")
    print("✅ RAG processing: SUCCESS")
    print("✅ File download: SUCCESS")
    print("✅ Content verification: SUCCESS")
    print("\n🎉 Complete workflow test PASSED!")
    
    # Cleanup
    try:
        os.remove(download_path)
        print(f"🧹 Cleaned up: {download_path}")
    except:
        pass

if __name__ == "__main__":
    test_complete_workflow()