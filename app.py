#!/usr/bin/env python3
"""Production entry point for RAG_Scraper web application."""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.web_interface.app_factory_refactored import create_app

def create_production_app():
    """Create Flask app for production deployment."""
    # Set production environment variables
    os.environ.setdefault('FLASK_ENV', 'production')
    os.environ.setdefault('DEBUG', 'false')
    
    # Get configuration from environment
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8085))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    app = create_app()
    
    # Configure for production
    app.config.update(
        DEBUG=debug,
        SECRET_KEY=os.environ.get('SECRET_KEY', os.urandom(24)),
        MAX_CONTENT_LENGTH=50 * 1024 * 1024,  # 50MB max file size
        UPLOAD_FOLDER=os.environ.get('UPLOAD_FOLDER', '/app/uploads'),
        OUTPUT_DIRECTORY=os.environ.get('OUTPUT_DIRECTORY', '/app/output')
    )
    
    return app

# For Gunicorn
app = create_production_app()

if __name__ == '__main__':
    # For direct execution (development)
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8085))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    print("🚀 Starting RAG_Scraper web interface...")
    print(f"📍 Server: http://{host}:{port}")
    print("⏹️  Press Ctrl+C to stop the server")
    
    app.run(host=host, port=port, debug=debug)