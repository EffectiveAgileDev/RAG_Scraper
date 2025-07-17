#!/usr/bin/env python3
"""Test OpenAI API connectivity and functionality."""

import os
import sys
from openai import OpenAI

# Test API key from environment or hardcoded
api_key = "sk-proj-kc55Co_Xx2rus01oIhtaDwShNsl-i3zouqC2tGGbcBk06YKCNZZI0KPTqEDGKAr5JB4kEKt7T3BlbkFJYCCQcf0eHrGjCjO5UUbxBTKZjHDPRNhMcN1s8OPPqGOC0A"

if not api_key:
    print("ERROR: No API key found!")
    sys.exit(1)

try:
    client = OpenAI(api_key=api_key)
    print(f"✓ OpenAI client created successfully")
    
    # Test a simple API call
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello and confirm you're working."}
        ],
        max_tokens=50,
        temperature=0.3
    )
    
    print(f"✓ API call successful!")
    print(f"Response: {response.choices[0].message.content}")
    
    # Check usage
    if hasattr(response, 'usage') and response.usage:
        print(f"Tokens used: {response.usage.total_tokens}")
    
except Exception as e:
    print(f"✗ API call failed: {e}")
    print(f"Error type: {type(e)}")
    import traceback
    traceback.print_exc()