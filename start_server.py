#!/usr/bin/env python3
"""Simple server starter for RAG Scraper"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.web_interface.app import create_app

if __name__ == "__main__":
    app = create_app()
    print("Starting RAG Scraper server...")
    print("Access at: http://localhost:8080")
    app.run(host="127.0.0.1", port=8080, debug=True)