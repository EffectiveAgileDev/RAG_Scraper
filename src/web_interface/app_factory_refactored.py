"""
Refactored application factory with separated concerns.

This refactored version addresses the brittleness issues by:
- Separating configuration, service initialization, and route registration
- Using dependency injection for better testability
- Reducing coupling between components
- Enabling better integration testing
"""

import os
import tempfile
import secrets
from flask import Flask
from typing import Optional, Dict, Any

from src.web_interface.application_state import get_app_state
from src.web_interface.api_routes import register_api_routes
from src.web_interface.routes.main_routes import main_routes
from src.web_interface.file_upload_routes import register_file_upload_routes
from src.web_interface.ai_api_routes import ai_api
from src.file_generator.file_generator_service import FileGeneratorService


class AppConfig:
    """Application configuration container."""
    
    def __init__(self, testing=False, upload_folder=None):
        """Initialize application configuration."""
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


class AppConfigurationService:
    """Service responsible for configuring Flask applications."""
    
    def configure_app(self, app: Flask, config: AppConfig):
        """Apply configuration to Flask app.
        
        Args:
            app: Flask application instance
            config: Configuration object
        """
        app.config["SECRET_KEY"] = config.secret_key
        app.config["TESTING"] = config.testing
        app.config["DEBUG"] = config.debug
        app.config["MAX_CONTENT_LENGTH"] = config.max_content_length
        app.config["UPLOAD_FOLDER"] = config.upload_folder


class ServiceContainer:
    """Container for managing application services and dependencies."""
    
    def __init__(self, config: AppConfig):
        """Initialize service container with configuration."""
        self.config = config
        self.services = {}
        
    def register_services(self):
        """Register and initialize all application services."""
        # Initialize application state
        app_state = get_app_state()
        
        # Initialize file generator service
        config_file = os.path.join(self.config.upload_folder, "rag_scraper_config.json")
        file_generator_service = FileGeneratorService(config_file)
        app_state.file_generator_service = file_generator_service
        
        # Store services in container
        self.services['app_state'] = app_state
        self.services['file_generator_service'] = file_generator_service
        self.services['advanced_monitor'] = app_state.advanced_monitor
        
        return self.services
    
    def get_service(self, service_name: str):
        """Get a service by name."""
        return self.services.get(service_name)


class RouteRegistrar:
    """Service responsible for registering routes with Flask applications."""
    
    def register_routes(self, app: Flask, services: Dict[str, Any]):
        """Register all routes with the Flask application.
        
        Args:
            app: Flask application instance
            services: Dictionary of available services
        """
        # Register main blueprint
        app.register_blueprint(main_routes)
        
        # Register API routes with dependencies
        register_api_routes(
            app, 
            services['advanced_monitor'], 
            services['file_generator_service']
        )
        
        # Register file upload routes
        register_file_upload_routes(app)
        
        # Register AI API routes
        app.register_blueprint(ai_api)


class SecurityHeadersService:
    """Service responsible for adding security headers."""
    
    def configure_security_headers(self, app: Flask):
        """Add security headers to all responses.
        
        Args:
            app: Flask application instance
        """
        @app.after_request
        def add_security_headers(response):
            """Add security headers to all responses."""
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            return response


class RefactoredAppFactory:
    """
    Refactored application factory using separation of concerns.
    
    This factory separates concerns into dedicated services:
    - Configuration management
    - Service initialization
    - Route registration
    - Security configuration
    """
    
    def __init__(self):
        """Initialize the application factory."""
        self.config_service = AppConfigurationService()
        self.security_service = SecurityHeadersService()
        self.route_registrar = RouteRegistrar()
    
    def create_app(self, 
                   testing: bool = False, 
                   upload_folder: Optional[str] = None,
                   config_service: Optional[AppConfigurationService] = None,
                   service_container: Optional[ServiceContainer] = None,
                   route_registrar: Optional[RouteRegistrar] = None) -> Flask:
        """
        Create and configure Flask application using dependency injection.
        
        Args:
            testing: Whether this is a testing environment
            upload_folder: Custom upload folder path
            config_service: Injectable configuration service
            service_container: Injectable service container
            route_registrar: Injectable route registrar
            
        Returns:
            Configured Flask application
        """
        # Create Flask app
        app = Flask(__name__)
        
        # Create configuration
        config = AppConfig(testing=testing, upload_folder=upload_folder)
        
        # Use injected services or defaults
        config_svc = config_service or self.config_service
        route_reg = route_registrar or self.route_registrar
        
        # Apply configuration
        config_svc.configure_app(app, config)
        
        # Initialize services
        if service_container is None:
            service_container = ServiceContainer(config)
        services = service_container.register_services()
        
        # Register routes
        route_reg.register_routes(app, services)
        
        # Configure security
        self.security_service.configure_security_headers(app)
        
        return app


# Create factory instance
refactored_factory = RefactoredAppFactory()


def create_app_refactored(testing=False, upload_folder=None):
    """
    Create app using the refactored factory.
    
    This function maintains backward compatibility while using
    the new separated architecture.
    """
    return refactored_factory.create_app(testing=testing, upload_folder=upload_folder)


# Backward compatibility - this will be used to replace the original
def create_app(testing=False, upload_folder=None):
    """Create and configure Flask application with refactored architecture."""
    return create_app_refactored(testing=testing, upload_folder=upload_folder)