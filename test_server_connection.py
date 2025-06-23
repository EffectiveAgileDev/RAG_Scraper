#!/usr/bin/env python3
"""Test script to verify server connection."""
import requests
import time
import subprocess
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.app_config import get_app_config

def test_server_connection():
    """Test if the server is accessible."""
    config = get_app_config()
    server_url = config.get_server_url()
    
    print(f"Testing connection to: {server_url}")
    
    try:
        # Try to connect
        response = requests.get(server_url, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ SUCCESS: Server is running and accessible at {server_url}")
            print(f"   Response status: {response.status_code}")
            print(f"   Response size: {len(response.content)} bytes")
            return True
        else:
            print(f"⚠️  WARNING: Server responded with status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: Could not connect to {server_url}")
        print("   Make sure the server is running with:")
        print("   python start_server.py")
        return False
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        return False

def start_server_and_test():
    """Start the server and test connection."""
    print("Starting server in background...")
    
    # Start server in background
    server_process = subprocess.Popen(
        [sys.executable, "start_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    try:
        # Test connection
        success = test_server_connection()
        
        if success:
            print("\n📋 To access the server:")
            print(f"   1. Open your web browser")
            print(f"   2. Go to: http://localhost:8085")
            print(f"   3. Make sure to include 'http://' at the beginning")
            
    finally:
        # Stop the server
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()
        
    return success

if __name__ == "__main__":
    print("=" * 60)
    print("RAG Scraper Server Connection Test")
    print("=" * 60)
    
    # First, try to connect to existing server
    if test_server_connection():
        print("\nServer is already running!")
    else:
        print("\nServer not running. Starting it now...")
        print("-" * 60)
        start_server_and_test()
    
    print("\n" + "=" * 60)