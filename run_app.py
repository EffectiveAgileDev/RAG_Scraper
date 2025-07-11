#!/usr/bin/env python3
"""Run the RAG_Scraper web application."""
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.web_interface.app import create_app
from src.config.app_config import get_app_config

if __name__ == '__main__':
    config = get_app_config()
    config.host = "0.0.0.0"  # Listen on all interfaces for network access
    config.debug = False  # Disable debug for production
    
    app = create_app()
    print("🚀 Starting RAG_Scraper web interface...")
    print(f"📍 Open your browser to: http://localhost:{config.port}")
    print(f"📱 Network access: http://192.168.12.187:{config.port}")
    print("   (Make sure to include 'http://' in the URL)")
    print("⏹️  Press Ctrl+C to stop the server")
    
    try:
        app.run(host=config.host, port=config.port, debug=config.debug)
    except KeyboardInterrupt:
        print("\n👋 RAG_Scraper stopped")