"""
Application factory for creating Flask applications with proper configuration.

This module now uses the refactored implementation internally while maintaining
backward compatibility with existing code.
"""

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

# Import the refactored implementation
from src.web_interface.app_factory_refactored import (
    RefactoredAppFactory,
    AppConfig,
    AppConfigurationService,
    ServiceContainer,
    RouteRegistrar,
    SecurityHeadersService
)


def create_app(testing=False, upload_folder=None):
    """
    Create and configure Flask application using refactored architecture.
    
    This function maintains backward compatibility while using the new
    separated concerns architecture internally.
    
    Args:
        testing: Whether this is a testing environment
        upload_folder: Custom upload folder path
        
    Returns:
        Configured Flask application
    """
    # Use the refactored factory
    factory = RefactoredAppFactory()
    return factory.create_app(testing=testing, upload_folder=upload_folder)