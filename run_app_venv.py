#!/usr/bin/env python3
"""Run the RAG_Scraper web application with automatic virtual environment activation."""
import sys
import os
import subprocess
from pathlib import Path

def main():
    """Main entry point that ensures virtual environment is used."""
    # Get project root directory
    project_root = Path(__file__).parent.absolute()
    venv_path = project_root / "venv"
    
    # Check if we're already running in the virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # We're already in a virtual environment, just run the app
        print("✅ Virtual environment already active")
        run_app()
    else:
        # We're not in a virtual environment, check if venv exists
        if not venv_path.exists():
            print(f"❌ Virtual environment not found at {venv_path}")
            print("Please create the virtual environment first:")
            print(f"  python -m venv {venv_path}")
            print("  source venv/bin/activate")
            print("  pip install -r requirements.txt")
            sys.exit(1)
        
        # Determine the correct Python executable in the virtual environment
        if os.name == 'nt':  # Windows
            venv_python = venv_path / "Scripts" / "python.exe"
        else:  # Unix/Linux/macOS
            venv_python = venv_path / "bin" / "python"
        
        if not venv_python.exists():
            print(f"❌ Virtual environment Python not found at {venv_python}")
            print("Please recreate the virtual environment")
            sys.exit(1)
        
        print("🔄 Activating virtual environment and starting server...")
        
        # Run this script again using the virtual environment Python
        try:
            subprocess.run([str(venv_python), __file__], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start server: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n👋 RAG_Scraper stopped")

def run_app():
    """Run the actual Flask application."""
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Check if OpenAI is available (this was the original issue)
    try:
        import openai
        print(f"✅ OpenAI package available (version {openai.__version__})")
    except ImportError:
        print("❌ OpenAI package not available - install with: pip install openai")
        sys.exit(1)
    
    from src.web_interface.app_factory import create_app
    from src.config.app_config import get_app_config
    
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

if __name__ == '__main__':
    main()