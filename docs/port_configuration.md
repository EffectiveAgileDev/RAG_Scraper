# Port Configuration for Multi-Page RAG Scraper

## Overview

The multi-page version of RAG Scraper uses port **8085** by default, instead of port 8080 used by the single-page version. This prevents conflicts when running both versions on the same machine.

## Configuration Options

### Default Configuration
- **Port**: 8085
- **Host**: localhost (127.0.0.1)
- **Debug**: False

### Environment Variables

You can override the default configuration using environment variables:

```bash
# Change the port
export RAG_SCRAPER_PORT=9000

# Change the host (use 0.0.0.0 for network access)
export RAG_SCRAPER_HOST=0.0.0.0

# Enable debug mode
export RAG_SCRAPER_DEBUG=true
```

### Running the Server

The application provides three ways to start the server:

1. **For Development** (debug mode enabled):
   ```bash
   python start_server.py
   ```
   - Uses port 8085
   - Host: 127.0.0.1 (local access only)
   - Debug: True

2. **For Production** (debug mode disabled):
   ```bash
   python run_app.py
   ```
   - Uses port 8085
   - Host: localhost (local access only)
   - Debug: False

3. **Direct Module Execution**:
   ```bash
   python -m src.web_interface.app
   ```
   - Uses port 8085
   - Host: 0.0.0.0 (accessible from network)
   - Debug: False

### Configuration Module

The port configuration is managed by `src.config.app_config.py`, which provides:

- `AppConfig` class for configuration management
- Environment variable support
- Singleton pattern for consistent configuration
- Port validation (must be between 1024-65535)

### Example Usage

```python
from src.config.app_config import get_app_config

# Get the singleton configuration
config = get_app_config()

# Access configuration values
print(f"Server will run on: {config.get_server_url()}")
# Output: Server will run on: http://localhost:8085

# Override values if needed
config.port = 9000
config.host = "0.0.0.0"
```

### Testing

The port configuration is fully tested with unit tests in:
- `tests/unit/test_app_config.py`
- `tests/unit/test_app_integration_with_config.py`

Run the tests with:
```bash
pytest tests/unit/test_app_config.py -v
```

### Migration Notes

If you're migrating from the single-page version (port 8080) to the multi-page version (port 8085):

1. Update any bookmarks or scripts that reference `localhost:8080`
2. Update any integration tests that hardcode port 8080
3. Ensure no other services are using port 8085
4. Set the `RAG_SCRAPER_PORT` environment variable if you need a different port

### Troubleshooting

If you encounter port conflicts:

1. Check if another service is using port 8085:
   ```bash
   lsof -i :8085  # On macOS/Linux
   netstat -an | grep 8085  # On Windows
   ```

2. Set a different port using environment variable:
   ```bash
   export RAG_SCRAPER_PORT=9090
   python run_app.py
   ```

3. Or modify the default in `src/config/app_config.py`