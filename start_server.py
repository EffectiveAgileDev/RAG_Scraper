#!/usr/bin/env python3
"""Simple server starter for RAG Scraper"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.web_interface.app import create_app
from src.config.app_config import get_app_config

if __name__ == "__main__":
    config = get_app_config()
    config.host = "127.0.0.1"  # Local access only for start_server
    config.debug = False  # Disable debug to prevent auto-reload on file generation
    
    app = create_app()
    print("Starting RAG Scraper server...")
    print(f"Access at: http://127.0.0.1:{config.port}")
    print(f"Alternative: http://localhost:{config.port}")
    print("Note: Make sure to include 'http://' when accessing in browser")
    print("Press Ctrl+C to stop the server\n")
    app.run(host=config.host, port=config.port, debug=config.debug)