"""Flask web application for RAG_Scraper - Refactored version."""
import os
import tempfile
import secrets
from flask import Flask

try:
    from src.scraper.advanced_progress_monitor import AdvancedProgressMonitor
    from src.file_generator.file_generator_service import FileGeneratorService
    from .routes.main_routes import main_bp
    from .api_routes import register_api_routes
except ImportError as e:
    # Fallback for testing
    print(f"Import warning: {e}")
    AdvancedProgressMonitor = None
    FileGeneratorService = None
    main_bp = None
    register_api_routes = None


# Global Advanced Progress Monitor instance
advanced_monitor = AdvancedProgressMonitor()

# Global scraper instance for progress tracking
active_scraper = None

# Global file generator service for persistent configuration
file_generator_service = None


def create_app(testing=False):
    """Create and configure Flask application."""
    app = Flask(__name__)

    # Configuration
    app.config["SECRET_KEY"] = secrets.token_hex(16)
    app.config["TESTING"] = testing
    app.config["DEBUG"] = False  # Always False for security
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max request size

    # Upload folder configuration
    if testing:
        app.config["UPLOAD_FOLDER"] = tempfile.gettempdir()
    else:
        app.config["UPLOAD_FOLDER"] = os.path.join(os.path.expanduser("~"), "Downloads")

    # Initialize file generator service
    global file_generator_service
    config_file = os.path.join(app.config["UPLOAD_FOLDER"], "rag_scraper_config.json")
    file_generator_service = FileGeneratorService(config_file)

    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

    # Register blueprints and routes
    app.register_blueprint(main_bp)
    
    # Register API routes
    register_api_routes(app, advanced_monitor, file_generator_service)

    return app


def get_current_progress():
    """Get current progress from the global monitor."""
    if advanced_monitor:
        return advanced_monitor.get_status()
    return {
        "status": "idle",
        "progress": {"percentage": 0, "message": "Ready"},
        "time_estimate": None,
        "current_url": None,
        "total_pages": 0,
        "completed_pages": 0,
        "failed_pages": 0,
        "rate_limit_active": False,
        "memory_usage": {"current": 0, "peak": 0}
    }


# For backward compatibility
app = create_app()

if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=8085, debug=False)