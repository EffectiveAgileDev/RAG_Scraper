"""Application factory for creating Flask applications with proper configuration."""

import os
import tempfile
import secrets
from flask import Flask

from src.web_interface.application_state import get_app_state
from src.web_interface.api_routes import register_api_routes
from src.web_interface.routes.main_routes import main_routes
from src.web_interface.file_upload_routes import register_file_upload_routes
from src.web_interface.ai_api_routes import ai_api
from src.file_generator.file_generator_service import FileGeneratorService


class AppConfig:
    """Application configuration container."""
    
    def __init__(self, testing=False, upload_folder=None):
        """Initialize application configuration.
        
        Args:
            testing: Whether this is a testing environment
            upload_folder: Custom upload folder path
        """
        self.testing = testing
        self.secret_key = secrets.token_hex(16)
        self.debug = False  # Always False for security
        self.max_content_length = 16 * 1024 * 1024  # 16MB max request size
        
        # Set upload folder
        if upload_folder:
            self.upload_folder = upload_folder
        elif testing:
            self.upload_folder = tempfile.gettempdir()
        else:
            self.upload_folder = os.path.join(os.path.expanduser("~"), "Downloads")


def create_app(testing=False, upload_folder=None):
    """Create and configure Flask application.
    
    Args:
        testing: Whether this is a testing environment
        upload_folder: Custom upload folder path
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    config = AppConfig(testing=testing, upload_folder=upload_folder)
    
    # Apply configuration
    app.config["SECRET_KEY"] = config.secret_key
    app.config["TESTING"] = config.testing
    app.config["DEBUG"] = config.debug
    app.config["MAX_CONTENT_LENGTH"] = config.max_content_length
    app.config["UPLOAD_FOLDER"] = config.upload_folder
    
    # Initialize application state
    app_state = get_app_state()
    config_file = os.path.join(config.upload_folder, "rag_scraper_config.json")
    app_state.file_generator_service = FileGeneratorService(config_file)
    
    # Register routes
    app.register_blueprint(main_routes)
    register_api_routes(app, app_state.advanced_monitor, app_state.file_generator_service)
    register_file_upload_routes(app)
    app.register_blueprint(ai_api)  # Register AI API routes
    
    # Add security headers
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response
    
    return app