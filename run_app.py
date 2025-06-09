#!/usr/bin/env python3
"""Run the RAG_Scraper web application."""
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.web_interface.app import create_app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Starting RAG_Scraper web interface...")
    print("📍 Open your browser to: http://localhost:8080")
    print("⏹️  Press Ctrl+C to stop the server")
    
    try:
        app.run(host='localhost', port=8080, debug=False)
    except KeyboardInterrupt:
        print("\n👋 RAG_Scraper stopped")