"""API routes for RAG_Scraper web application."""
import os
import json
import logging
import tempfile
from flask import Flask, request, jsonify, send_file, session
from werkzeug.exceptions import BadRequest
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

from src.config.url_validator import URLValidator
from src.config.scraping_config import ScrapingConfig
from src.config.industry_config import IndustryConfig
from src.scraper.restaurant_scraper import RestaurantScraper
from src.scraper.advanced_progress_monitor import AdvancedProgressMonitor
from src.file_generator.file_generator_service import (
    FileGeneratorService,
    FileGenerationRequest,
)
from src.web_interface.session_manager import IndustrySessionManager
from src.web_interface.handlers import (
    ScrapingRequestHandler,
    FileGenerationHandler,
    ValidationHandler
)
from src.web_interface.validators.industry_validator import IndustryValidator
from src.web_interface.settings_storage import SettingsStorage, SinglePageSettingsStorage, MultiPageSettingsStorage


def register_api_routes(app, advanced_monitor, file_generator_service):
    """Register all API routes with the Flask app."""
    
    # Initialize validators and handlers
    industry_validator = IndustryValidator()
    validation_handler = ValidationHandler()
    file_generation_handler = FileGenerationHandler(file_generator_service)
    scraping_handler = ScrapingRequestHandler(
        validation_handler=validation_handler,
        file_generation_handler=file_generation_handler,
        upload_folder=app.config["UPLOAD_FOLDER"]
    )
    
    # Global scraper instance for progress tracking
    active_scraper = None

    # Industry Selection API Routes
    @app.route("/api/industries", methods=["GET"])
    def get_industries():
        """Get list of available industries."""
        try:
            config = IndustryConfig()
            industries = config.get_industry_list()
            return jsonify(industries)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/industry-help", methods=["GET"])
    def get_industry_help():
        """Get help text for selected industry."""
        try:
            session_manager = IndustrySessionManager()
            industry = session_manager.get_industry()
            
            if not industry:
                return "", 200
            
            config = IndustryConfig()
            help_text = config.get_help_text(industry)
            return help_text, 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/clear-industry", methods=["POST"])
    def clear_industry():
        """Clear industry selection from session."""
        try:
            session_manager = IndustrySessionManager()
            session_manager.clear_industry()
            return "", 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Form-based routes for industry validation
    @app.route("/scrape", methods=["POST"])
    def scrape_form():
        """Handle form-based scraping requests with industry validation."""
        try:
            form_data = request.form.to_dict()
            
            # Validate industry using centralized validator
            industry_result = industry_validator.validate_and_store_industry(form_data)
            if not industry_result.is_valid:
                return f"<html><body><h1>Error</h1><p>{industry_result.error_message}</p></body></html>", 400
            
            # Redirect to API endpoint with JSON data
            import json
            json_data = {
                "url": form_data.get("url"),
                "industry": industry_result.industry
            }
            
            # For now, return success - full implementation would redirect to API
            return jsonify({"success": True, "industry": industry_result.industry})
            
        except Exception as e:
            return f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>", 500

    @app.route("/scrape/batch", methods=["POST"])
    def scrape_batch_form():
        """Handle form-based batch scraping requests with industry validation."""
        try:
            form_data = request.form.to_dict()
            
            # Validate industry using centralized validator
            industry_result = industry_validator.validate_and_store_industry(form_data)
            if not industry_result.is_valid:
                return f"<html><body><h1>Error</h1><p>{industry_result.error_message}</p></body></html>", 400
            
            # For now, return success - full implementation would process batch
            return jsonify({"success": True, "industry": industry_result.industry})
            
        except Exception as e:
            return f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>", 500

    @app.route("/api/validate", methods=["POST"])
    def validate_urls():
        """Validate URLs endpoint."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400

            validator = URLValidator()

            # Handle single URL
            if "url" in data:
                result = validator.validate_url(data["url"])
                return jsonify(
                    {"is_valid": result.is_valid, "error": result.error_message}
                )

            # Handle multiple URLs
            elif "urls" in data:
                results = validator.validate_urls(data["urls"])
                return jsonify(
                    {
                        "results": [
                            {"is_valid": result.is_valid, "error": result.error_message}
                            for result in results
                        ]
                    }
                )

            else:
                return jsonify({"error": "No URL or URLs provided"}), 400

        except BadRequest:
            return jsonify({"error": "Invalid JSON"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/scrape", methods=["POST"])
    def scrape_restaurants():
        """Scrape restaurants endpoint."""
        nonlocal active_scraper
        
        try:
            data = request.get_json()
            logger.debug(f"API scrape route received data keys: {list(data.keys()) if data else 'None'}")
            
            # Handle AI configuration if provided
            if 'ai_config' in data and 'session_id' in data:
                from src.web_interface.ai_config_manager import AIConfigManager
                ai_config_manager = AIConfigManager()
                
                # Store AI configuration in session if AI is enabled
                ai_config = data['ai_config']
                logger.debug(f"AI config received: {ai_config}")
                if ai_config and ai_config.get('ai_enhancement_enabled', False):
                    logger.debug(f"AI enhancement enabled, saving to session {data['session_id']}")
                    ai_config_manager.set_session_config(data['session_id'], ai_config)
                else:
                    logger.debug(f"AI enhancement disabled or config missing")
            
            # Use handler to process the request
            response = scraping_handler.handle_scraping_request(data)
            
            # Update active_scraper for progress tracking compatibility
            active_scraper = scraping_handler.active_scraper
            
            # Convert response to JSON format
            response_data = {
                "success": response.success,
                "processed_count": response.processed_count,
                "failed_count": response.failed_count,
                "output_files": response.output_files,
                "processing_time": response.processing_time,
                "sites_data": response.sites_data,
            }
            
            # Add optional fields
            if response.error:
                response_data["error"] = response.error
            if response.warnings:
                response_data["file_generation_warnings"] = response.warnings
            if response.ai_analysis:
                response_data["ai_analysis"] = response.ai_analysis
            
            return jsonify(response_data), (200 if response.success else 400)

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/progress", methods=["GET"])
    def get_progress():
        """Get current scraping progress with advanced monitoring."""
        nonlocal active_scraper

        try:
            # Get real-time progress from Advanced Progress Monitor
            current_status = advanced_monitor.get_current_status()
            ui_state = advanced_monitor.get_ui_state()

            # Get additional monitoring data
            progress_data = {
                "current_url": current_status.current_url,
                "urls_completed": current_status.urls_completed,
                "urls_total": current_status.urls_total,
                "progress_percentage": current_status.progress_percentage,
                "estimated_time_remaining": current_status.estimated_time_remaining,
                "current_operation": current_status.current_operation,
                "memory_usage_mb": current_status.memory_usage_mb,
                "status": "processing"
                if advanced_monitor.active_session_id
                else "idle",
                "processing_time": len(advanced_monitor.url_processing_times),
                # Advanced monitoring features
                "session_id": advanced_monitor.active_session_id,
                "progress_bar_percentage": ui_state.get("progress_bar_percentage", 0),
                "status_message": ui_state.get("status_message", "Ready"),
                # Multi-page progress if enabled
                "page_progress": None,
                "notifications": [],
                "error_notifications": [],
                "completion_events": [],
            }

            # Add multi-page progress if session exists
            if advanced_monitor.active_session_id:
                try:
                    page_progress = advanced_monitor.get_page_progress()
                    if page_progress.total_pages > 1:
                        progress_data["page_progress"] = {
                            "current_page": page_progress.current_page,
                            "total_pages": page_progress.total_pages,
                            "progress_message": advanced_monitor.get_current_progress_message(),
                        }

                    # Add notifications safely
                    progress_data[
                        "notifications"
                    ] = advanced_monitor.get_page_notifications()[
                        -5:
                    ]  # Last 5

                    # Add error notifications safely
                    error_notifications = []
                    for err in advanced_monitor.get_error_notifications()[
                        -3:
                    ]:  # Last 3
                        try:
                            error_notifications.append(
                                {
                                    "url": err.url,
                                    "error_type": err.error_type,
                                    "message": err.error_message,
                                    "timestamp": err.timestamp.isoformat(),
                                }
                            )
                        except:
                            pass  # Skip malformed error notifications
                    progress_data["error_notifications"] = error_notifications

                    progress_data[
                        "completion_events"
                    ] = advanced_monitor.get_completion_events()[
                        -3:
                    ]  # Last 3
                except Exception as e:
                    # If there's an error getting advanced data, continue with basic data
                    pass

            return jsonify(progress_data)

        except Exception as e:
            # Fallback to basic progress data
            return jsonify(
                {
                    "current_url": "",
                    "urls_completed": 0,
                    "urls_total": 0,
                    "progress_percentage": 0,
                    "estimated_time_remaining": 0,
                    "current_operation": "",
                    "memory_usage_mb": 0,
                    "status": "idle",
                    "processing_time": 0,
                    "session_id": None,
                    "progress_bar_percentage": 0,
                    "status_message": "Ready",
                    "page_progress": None,
                    "notifications": [],
                    "error_notifications": [],
                    "completion_events": [],
                }
            )

    @app.route("/api/download/<filename>")
    def download_file(filename):
        """Download generated file."""
        try:
            # Security: ensure filename is safe
            if ".." in filename or "/" in filename or "\\" in filename:
                return jsonify({"error": "Invalid filename"}), 403

            # Try to find the file in the upload folder
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            
            # If file doesn't exist in upload folder, check if it exists elsewhere
            # This handles cases where files are generated with full paths
            if not os.path.exists(file_path):
                # Look for files with this filename in the upload folder first
                for root, dirs, files in os.walk(app.config["UPLOAD_FOLDER"]):
                    if filename in files:
                        file_path = os.path.join(root, filename)
                        break
                else:
                    # If still not found, search in common output directories
                    search_paths = [
                        "/tmp/test_output",
                        "/tmp/output",
                        os.path.expanduser("~/Downloads"),
                        tempfile.gettempdir()
                    ]
                    
                    for search_path in search_paths:
                        if os.path.exists(search_path):
                            for root, dirs, files in os.walk(search_path):
                                if filename in files:
                                    file_path = os.path.join(root, filename)
                                    break
                            if os.path.exists(file_path):
                                break
                    else:
                        return jsonify({"error": "File not found"}), 404

            return send_file(file_path, as_attachment=True)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/view-file/<filename>")
    def view_file(filename):
        """View generated text file in browser."""
        try:
            # Security: ensure filename is safe
            if ".." in filename or "/" in filename or "\\" in filename:
                return jsonify({"error": "Invalid filename"}), 403

            # Try to find the file in the upload folder
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            
            # If file doesn't exist in upload folder, check if it exists elsewhere
            # This handles cases where files are generated with full paths
            if not os.path.exists(file_path):
                # Look for files with this filename in the upload folder first
                for root, dirs, files in os.walk(app.config["UPLOAD_FOLDER"]):
                    if filename in files:
                        file_path = os.path.join(root, filename)
                        break
                else:
                    # If still not found, search in common output directories
                    search_paths = [
                        "/tmp/test_output",
                        "/tmp/output",
                        os.path.expanduser("~/Downloads"),
                        tempfile.gettempdir()
                    ]
                    
                    for search_path in search_paths:
                        if os.path.exists(search_path):
                            for root, dirs, files in os.walk(search_path):
                                if filename in files:
                                    file_path = os.path.join(root, filename)
                                    break
                            if os.path.exists(file_path):
                                break
                    else:
                        return jsonify({"error": "File not found"}), 404

            # Determine content type based on file extension
            file_extension = filename.split('.')[-1].lower()
            if file_extension == 'json':
                mimetype = 'application/json'
            elif file_extension == 'txt':
                mimetype = 'text/plain'
            else:
                mimetype = 'text/plain'  # Default to plain text

            # Send file to be displayed in browser (not as attachment)
            return send_file(file_path, as_attachment=False, mimetype=mimetype)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/generate-file", methods=["POST"])
    def generate_file():
        """Generate text file from scraped restaurant data."""
        try:
            data = request.get_json(force=True)
            if data is None:
                return (
                    jsonify({"success": False, "error": "No JSON data provided"}),
                    400,
                )
            if not data:
                return (
                    jsonify({"success": False, "error": "No restaurant data provided"}),
                    400,
                )
        except Exception as json_error:
            return (
                jsonify({"success": False, "error": "Invalid JSON data provided"}),
                400,
            )

        try:
            # Validate required fields
            if "restaurant_data" not in data:
                return (
                    jsonify({"success": False, "error": "No restaurant data provided"}),
                    400,
                )

            # Parse restaurant data from JSON
            from src.scraper.multi_strategy_scraper import RestaurantData

            restaurant_objects = []

            for restaurant_dict in data["restaurant_data"]:
                restaurant = RestaurantData(
                    name=restaurant_dict.get("name", ""),
                    address=restaurant_dict.get("address", ""),
                    phone=restaurant_dict.get("phone", ""),
                    hours=restaurant_dict.get("hours", ""),
                    price_range=restaurant_dict.get("price_range", ""),
                    cuisine=restaurant_dict.get("cuisine", ""),
                    menu_items=restaurant_dict.get("menu_items", {}),
                    social_media=restaurant_dict.get("social_media", []),
                    confidence=restaurant_dict.get("confidence", "medium"),
                    sources=restaurant_dict.get("sources", ["web_interface"]),
                    ai_analysis=restaurant_dict.get("ai_analysis"),
                )
                restaurant_objects.append(restaurant)

            # Create file generation request
            request_obj = FileGenerationRequest(
                restaurant_data=restaurant_objects,
                output_directory=data.get("output_directory"),
                file_format=data.get("file_format", "text"),
                allow_overwrite=data.get("allow_overwrite", True),
                save_preferences=data.get("save_preferences", False),
            )

            # Generate file
            result = file_generator_service.generate_file(request_obj)

            return jsonify(result)

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/file-config", methods=["GET"])
    def get_file_config():
        """Get current file generation configuration."""
        try:
            config = file_generator_service.get_current_config()
            supported_formats = file_generator_service.get_supported_formats()
            directory_options = file_generator_service.get_output_directory_options()

            return jsonify(
                {
                    "success": True,
                    "config": config,
                    "supported_formats": supported_formats,
                    "directory_options": directory_options,
                }
            )

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/file-config", methods=["POST"])
    def update_file_config():
        """Update file generation configuration."""
        try:
            data = request.get_json(force=True)
            if data is None or not data:
                return (
                    jsonify(
                        {"success": False, "error": "No configuration data provided"}
                    ),
                    400,
                )
        except Exception as json_error:
            return (
                jsonify({"success": False, "error": "Invalid JSON data provided"}),
                400,
            )

        try:
            result = file_generator_service.update_config(data)
            return jsonify(result)

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/validate-directory", methods=["POST"])
    def validate_directory():
        """Validate directory permissions for file generation."""
        try:
            data = request.get_json(force=True)
            if data is None or not data or "directory_path" not in data:
                return (
                    jsonify({"success": False, "error": "No directory path provided"}),
                    400,
                )
        except Exception as json_error:
            return (
                jsonify({"success": False, "error": "Invalid JSON data provided"}),
                400,
            )

        try:
            result = file_generator_service.validate_directory_permissions(
                data["directory_path"]
            )
            return jsonify({"success": True, "validation": result})

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/create-directory", methods=["POST"])
    def create_directory():
        """Create custom directory for file output."""
        try:
            data = request.get_json(force=True)
            if (
                data is None
                or not data
                or "parent_directory" not in data
                or "directory_name" not in data
            ):
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Parent directory and directory name required",
                        }
                    ),
                    400,
                )
        except Exception as json_error:
            return (
                jsonify({"success": False, "error": "Invalid JSON data provided"}),
                400,
            )

        try:
            result = file_generator_service.create_custom_directory(
                data["parent_directory"], data["directory_name"]
            )
            return jsonify(result)

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route("/api/save-settings", methods=["POST"])
    def save_settings():
        """Save user settings."""
        try:
            data = request.get_json(force=True)
            if not data or 'settings' not in data:
                return jsonify({"success": False, "error": "No settings provided"}), 400
            
            settings_storage = SettingsStorage()
            
            # Validate settings
            if not settings_storage.validate_settings(data['settings']):
                return jsonify({"success": False, "error": "Invalid settings"}), 400
            
            # Save to session (for server-side persistence)
            session['saved_settings'] = data['settings']
            session['save_enabled'] = data.get('saveEnabled', True)
            
            return jsonify({
                "success": True,
                "message": "Settings saved successfully"
            })
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route("/api/get-saved-settings", methods=["GET"])
    def get_saved_settings():
        """Get saved user settings."""
        try:
            settings_storage = SettingsStorage()
            
            # Check if save is enabled
            if not session.get('save_enabled', False):
                return jsonify({
                    "success": True,
                    "settings": None
                })
            
            # Get settings from session
            saved_settings = session.get('saved_settings')
            if not saved_settings:
                saved_settings = settings_storage.get_default_settings()
            
            return jsonify({
                "success": True,
                "settings": saved_settings
            })
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route("/api/save-single-page-settings", methods=["POST"])
    def save_single_page_settings():
        """Save single-page mode settings."""
        try:
            data = request.get_json(force=True)
            if not data or 'settings' not in data:
                return jsonify({"success": False, "error": "No settings provided"}), 400
            
            storage = SinglePageSettingsStorage()
            
            # Validate settings
            if not storage.validate_settings(data['settings']):
                return jsonify({"success": False, "error": "Invalid single-page settings"}), 400
            
            # Save settings
            if storage.save_settings(data['settings']):
                # Also save the enabled state
                session['single_page_save_enabled'] = data.get('saveEnabled', True)
                
                return jsonify({
                    "success": True,
                    "message": "Single-page settings saved successfully"
                })
            else:
                return jsonify({"success": False, "error": "Failed to save settings"}), 500
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route("/api/save-multi-page-settings", methods=["POST"])
    def save_multi_page_settings():
        """Save multi-page mode settings."""
        try:
            data = request.get_json(force=True)
            if not data or 'settings' not in data:
                return jsonify({"success": False, "error": "No settings provided"}), 400
            
            storage = MultiPageSettingsStorage()
            
            # Validate settings
            if not storage.validate_settings(data['settings']):
                return jsonify({"success": False, "error": "Invalid multi-page settings"}), 400
            
            # Save settings
            if storage.save_settings(data['settings']):
                # Also save the enabled state
                session['multi_page_save_enabled'] = data.get('saveEnabled', True)
                
                return jsonify({
                    "success": True,
                    "message": "Multi-page settings saved successfully"
                })
            else:
                return jsonify({"success": False, "error": "Failed to save settings"}), 500
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route("/api/get-single-page-settings", methods=["GET"])
    def get_single_page_settings():
        """Get saved single-page settings."""
        try:
            storage = SinglePageSettingsStorage()
            
            # Check if save is enabled
            if not session.get('single_page_save_enabled', False):
                return jsonify({
                    "success": True,
                    "settings": None,
                    "saveEnabled": False
                })
            
            # Get settings
            saved_settings = storage.load_settings()
            if not saved_settings:
                saved_settings = storage.get_default_settings()
            
            return jsonify({
                "success": True,
                "settings": saved_settings,
                "saveEnabled": True
            })
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route("/api/get-multi-page-settings", methods=["GET"])
    def get_multi_page_settings():
        """Get saved multi-page settings."""
        try:
            storage = MultiPageSettingsStorage()
            
            # Check if save is enabled
            if not session.get('multi_page_save_enabled', False):
                return jsonify({
                    "success": True,
                    "settings": None,
                    "saveEnabled": False
                })
            
            # Get settings
            saved_settings = storage.load_settings()
            if not saved_settings:
                saved_settings = storage.get_default_settings()
            
            return jsonify({
                "success": True,
                "settings": saved_settings,
                "saveEnabled": True
            })
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
