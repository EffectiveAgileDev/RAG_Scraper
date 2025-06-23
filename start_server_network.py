#!/usr/bin/env python3
"""Start server with network access enabled - USE WITH CAUTION"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.web_interface.app import create_app
from src.config.app_config import get_app_config
import socket

def get_local_ip():
    """Get the local IP address of this machine."""
    try:
        # Create a socket to external address (doesn't actually connect)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "unknown"

if __name__ == "__main__":
    config = get_app_config()
    config.host = "0.0.0.0"  # Accept connections from any IP
    config.debug = True  # Enable debug for development
    
    local_ip = get_local_ip()
    
    app = create_app()
    print("=" * 60)
    print("⚠️  WARNING: Starting server with NETWORK ACCESS ENABLED")
    print("=" * 60)
    print(f"The server will accept connections from other computers!")
    print()
    print(f"Access from this computer:")
    print(f"  - http://localhost:{config.port}")
    print(f"  - http://127.0.0.1:{config.port}")
    print()
    print(f"Access from other computers on your network:")
    print(f"  - http://{local_ip}:{config.port}")
    print()
    print("To find this computer's IP on other systems, use ifconfig or ipconfig")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(host=config.host, port=config.port, debug=config.debug)