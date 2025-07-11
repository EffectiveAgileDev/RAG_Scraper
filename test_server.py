#!/usr/bin/env python3
"""Test server startup and route."""
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from src.web_interface.app import create_app
    print("✓ App import successful")
    
    app = create_app()
    print("✓ App creation successful")
    
    with app.test_client() as client:
        print("✓ Test client created")
        
        response = client.get('/')
        print(f"✓ Route test - Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"✗ Error response: {response.data.decode()}")
        else:
            print("✓ Index route working correctly")
            
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()