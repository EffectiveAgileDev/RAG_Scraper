"""API routes for RAG_Scraper web application."""
import os
import json
import tempfile
from flask import Flask, request, jsonify, send_file
from werkzeug.exceptions import BadRequest
from urllib.parse import urlparse

from src.config.url_validator import URLValidator
from src.config.scraping_config import ScrapingConfig
from src.scraper.restaurant_scraper import RestaurantScraper
from src.scraper.advanced_progress_monitor import AdvancedProgressMonitor
from src.file_generator.file_generator_service import (
    FileGeneratorService,
    FileGenerationRequest,
)


def register_api_routes(app, advanced_monitor, file_generator_service):
    """Register all API routes with the Flask app."""
    
    # Global scraper instance for progress tracking
    active_scraper = None

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
            if not data:
                return jsonify({"success": False, "error": "No data provided"}), 400

            # Extract URLs
            urls = []
            if "url" in data:
                urls = [data["url"]]
            elif "urls" in data:
                urls = data["urls"]
            else:
                return jsonify({"success": False, "error": "No URLs provided"}), 400

            # Validate URLs first
            validator = URLValidator()
            validation_results = validator.validate_urls(urls)

            invalid_urls = [
                result for result in validation_results if not result.is_valid
            ]
            if invalid_urls:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"Invalid URLs provided: {len(invalid_urls)} of {len(urls)} URLs are invalid",
                        }
                    ),
                    400,
                )

            # Configure scraping
            output_dir = data.get("output_dir") or app.config["UPLOAD_FOLDER"]
            file_mode = data.get("file_mode", "single")
            file_format = data.get("file_format", "text")  # text, pdf, or both
            scraping_mode = data.get("scraping_mode", "single")  # single or multi
            multi_page_config = data.get("multi_page_config", {})

            # Extract JavaScript rendering configuration
            enable_javascript = data.get("enableJavaScript", False)
            js_timeout = data.get("jsTimeout", 30)
            enable_popup_handling = data.get("enablePopupHandling", True)
            
            config = ScrapingConfig(
                urls=urls, 
                output_directory=output_dir, 
                file_mode=file_mode
            )

            # Simple progress callback for basic functionality
            def progress_callback(message, percentage=None, time_estimate=None):
                pass

            # Create and run scraper with progress tracking
            enable_multi_page = (scraping_mode == "multi")
            
            # Configure multi-page scraper with UI settings
            max_pages = 10  # default
            if enable_multi_page and multi_page_config:
                max_pages = multi_page_config.get("maxPages", 50)
                
            scraper = RestaurantScraper(enable_multi_page=enable_multi_page)
            
            # Update the multi-page scraper with UI configuration
            if enable_multi_page and scraper.multi_page_scraper and multi_page_config:
                # Update the max_pages setting
                scraper.multi_page_scraper.max_pages = max_pages
                # Update the crawl depth setting
                scraper.multi_page_scraper.max_crawl_depth = multi_page_config.get("crawlDepth", 2)
                # Update the page discovery max_pages as well
                if hasattr(scraper.multi_page_scraper, 'page_discovery') and scraper.multi_page_scraper.page_discovery:
                    scraper.multi_page_scraper.page_discovery.max_pages = max_pages
            
            active_scraper = scraper

            # Set multi-page mode on config for RestaurantScraper logic
            config.enable_multi_page = enable_multi_page
            
            # Add multi-page config to the scraping config if available
            if enable_multi_page and multi_page_config:
                config.max_crawl_depth = multi_page_config.get("crawlDepth", 2)
                config.max_pages_per_site = multi_page_config.get("maxPages", 50)
                config.rate_limit_delay = multi_page_config.get("rateLimit", 1000) / 1000.0  # Convert ms to seconds
                
                # Set link patterns
                include_patterns = multi_page_config.get("includePatterns", "").split(",")
                exclude_patterns = multi_page_config.get("excludePatterns", "").split(",") 
                config.link_patterns = {
                    "include": [p.strip() for p in include_patterns if p.strip()],
                    "exclude": [p.strip() for p in exclude_patterns if p.strip()]
                }
            
            # Only force batch processing for single-page mode with multiple URLs
            if scraping_mode == "single" and len(urls) > 5:
                config.force_batch_processing = True

            result = scraper.scrape_restaurants(
                config, progress_callback=progress_callback
            )

            # Disable Advanced Progress Monitor updates to avoid interference
            # successful_urls = set()
            # if result.successful_extractions:
            #     successful_count = min(len(result.successful_extractions), len(urls))
            #     successful_urls = set(urls[:successful_count])
            # for i, url in enumerate(urls):
            #     if url in successful_urls:
            #         processing_time = 3.0 + (i * 0.5)
            #         advanced_monitor.update_url_completion(url, processing_time, success=True)
            #     elif url in result.failed_urls:
            #         error_msg = "Failed to extract data"
            #         advanced_monitor.add_error_notification(url, "extraction_error", error_msg)
            #         advanced_monitor.update_url_completion(url, 1.0, success=False)
            #     else:
            #         processing_time = 2.0 + (i * 0.3)
            #         advanced_monitor.update_url_completion(url, processing_time, success=True)

            # Clear active scraper
            active_scraper = None

            # Generate files asynchronously to avoid frontend timeout
            generated_files = []
            file_generation_errors = []

            if result.successful_extractions:
                try:
                    import threading
                    from src.file_generator.file_generator_service import (
                        FileGenerationRequest,
                    )

                    def generate_files_async():
                        """Generate files in background thread."""
                        formats_to_generate = [file_format]
                        
                        for fmt in formats_to_generate:
                            try:
                                file_request = FileGenerationRequest(
                                    restaurant_data=result.successful_extractions,
                                    file_format=fmt,
                                    output_directory=output_dir,
                                    allow_overwrite=True,
                                    save_preferences=False,
                                )

                                file_result = file_generator_service.generate_file(file_request)
                                # File generation results will be available for next request
                                
                            except Exception as e:
                                # Log error but don't block response
                                pass

                    # Start file generation in background
                    file_thread = threading.Thread(target=generate_files_async, daemon=True)
                    file_thread.start()
                    
                    # Generate at least one file synchronously for immediate response
                    try:
                        file_request = FileGenerationRequest(
                            restaurant_data=result.successful_extractions,
                            file_format=file_format,
                            output_directory=output_dir,
                            allow_overwrite=True,
                            save_preferences=False,
                        )

                        file_result = file_generator_service.generate_file(file_request)

                        if file_result["success"]:
                            generated_files.append(file_result["file_path"])
                        else:
                            file_generation_errors.append(
                                f"{file_format.upper()} generation failed: {file_result['error']}"
                            )

                    except Exception as e:
                        file_generation_errors.append(
                            f"{file_format.upper()} generation error: {str(e)}"
                        )
                        
                except Exception as e:
                    # If threading fails, fall back to synchronous generation
                    file_generation_errors.append(f"File generation setup error: {str(e)}")

            # Generate enhanced results data for UI display
            sites_data = generate_sites_data(result, scraping_mode, urls)
            
            # Return results with actual file paths
            response_data = {
                "success": True,
                "processed_count": len(result.successful_extractions),
                "failed_count": len(result.failed_urls),
                "output_files": generated_files,
                "processing_time": getattr(result, "processing_time", 0),
                "sites_data": sites_data,
            }

            # Include file generation errors if any occurred
            if file_generation_errors:
                response_data["file_generation_warnings"] = file_generation_errors

            return jsonify(response_data)

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

            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            if not os.path.exists(file_path):
                return jsonify({"error": "File not found"}), 404

            return send_file(file_path, as_attachment=True)

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


def generate_sites_data(result, scraping_mode, urls):
    """Generate enhanced sites data for results display."""
    sites_data = []
    
    if scraping_mode == 'single':
        # In single-page mode, each URL is treated as a separate site
        total_time = getattr(result, 'processing_time', 0.0)
        num_urls = len(urls) if urls else 1
        avg_time_per_url = total_time / num_urls if num_urls > 0 else 1.0
        
        for i, extraction in enumerate(result.successful_extractions):
            # RestaurantData doesn't have URL, so we use the corresponding URL from input
            url = urls[i] if i < len(urls) else 'Unknown URL'
            # Vary timing slightly for each URL
            processing_time = round(avg_time_per_url * (0.9 + (i % 3) * 0.1), 1)
            
            sites_data.append({
                'site_url': url,
                'pages_processed': 1,
                'pages': [{
                    'url': url,
                    'status': 'success',
                    'processing_time': processing_time
                }]
            })
        
        for failed_url in result.failed_urls:
            # failed_urls is a list of URL strings
            url = failed_url if isinstance(failed_url, str) else 'Unknown URL'
            
            sites_data.append({
                'site_url': url,
                'pages_processed': 1,
                'pages': [{
                    'url': url,
                    'status': 'failed',
                    'processing_time': 0.5  # Show minimal time for failed URLs
                }]
            })
    
    else:  # multi-page mode
        # Use multi-page results if available
        if hasattr(result, 'multi_page_results') and result.multi_page_results:
            # Use actual multi-page scraping results
            for i, mp_result in enumerate(result.multi_page_results):
                # Get the correct URL for this result (not always the first one)
                site_url = urls[i] if i < len(urls) else 'Unknown URL'
                
                # If we have pages_processed, try to extract the base URL from the first page
                if mp_result.pages_processed:
                    # Use the first processed page as the site URL if available
                    first_page = mp_result.pages_processed[0]
                    # Extract base domain from the first page URL
                    parsed = urlparse(first_page)
                    site_url = f"{parsed.scheme}://{parsed.netloc}/"
                
                pages = []
                # Calculate approximate per-page timing
                total_time = getattr(mp_result, 'processing_time', 0.0)
                num_pages = len(mp_result.pages_processed) if mp_result.pages_processed else 1
                avg_time_per_page = total_time / num_pages if num_pages > 0 else 0.0
                
                for i, page_url in enumerate(mp_result.pages_processed):
                    status = 'success' if page_url in mp_result.successful_pages else 'failed'
                    # Vary the time slightly for each page for more realistic display
                    page_time = avg_time_per_page * (0.8 + (i % 5) * 0.1) if avg_time_per_page > 0 else 0.1
                    pages.append({
                        'url': page_url,
                        'status': status,
                        'processing_time': round(page_time, 1)
                    })
                
                sites_data.append({
                    'site_url': site_url,
                    'pages_processed': len(mp_result.pages_processed),
                    'pages': pages
                })
        else:
            # Fallback: Group pages by site (original logic)
            sites = {}
            
            # Process successful extractions
            for i, extraction in enumerate(result.successful_extractions):
                # RestaurantData doesn't have URL, so we use the corresponding URL from input
                url = urls[i] if i < len(urls) else 'Unknown URL'
                processing_time = 0.0  # Default processing time
                
                # Extract base site URL
                site_url = extract_site_url(url)
                
                if site_url not in sites:
                    sites[site_url] = {
                        'site_url': site_url,
                        'pages_processed': 0,
                        'pages': []
                    }
                
                # Generate relationship data based on URL patterns (mock implementation)
                relationship_data = generate_mock_relationship_data(url, site_url)
                
                sites[site_url]['pages'].append({
                    'url': url,
                    'status': 'success',
                    'processing_time': processing_time,
                    'relationship': relationship_data
                })
                sites[site_url]['pages_processed'] += 1
            
            # Process failed URLs
            for failed_url in result.failed_urls:
                # failed_urls is a list of URL strings
                url = failed_url if isinstance(failed_url, str) else 'Unknown URL'
                
                # Extract base site URL
                site_url = extract_site_url(url)
                
                if site_url not in sites:
                    sites[site_url] = {
                        'site_url': site_url,
                        'pages_processed': 0,
                        'pages': []
                    }
                
                # Generate relationship data for failed URLs too
                relationship_data = generate_mock_relationship_data(url, site_url)
                
                sites[site_url]['pages'].append({
                    'url': url,
                    'status': 'failed',
                    'processing_time': 0.0,
                    'relationship': relationship_data
                })
                sites[site_url]['pages_processed'] += 1
            
            sites_data = list(sites.values())
    
    return sites_data


def generate_mock_relationship_data(url, site_url):
    """Generate mock relationship data based on URL patterns."""
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    path_parts = path.split('/') if path else []
    
    # Determine relationship type based on URL structure
    if url == site_url or url == site_url + '/' or not path:
        # Root page
        return {
            'type': 'root',
            'depth': 0,
            'parent_url': None,
            'children_count': min(len(path_parts) + 2, 5),  # Mock children count
            'discovery_method': 'manual'
        }
    elif len(path_parts) == 1:
        # First level child (e.g., /menu, /contact)
        return {
            'type': 'child',
            'depth': 1,
            'parent_url': site_url,
            'children_count': 1 if 'menu' in path.lower() else 0,  # Menu might have subpages
            'discovery_method': 'link'
        }
    elif len(path_parts) >= 2:
        # Deeper child page (e.g., /menu/specials)
        parent_path = '/'.join(path_parts[:-1])
        parent_url = f"{site_url}/{parent_path}"
        
        return {
            'type': 'child',
            'depth': len(path_parts),
            'parent_url': parent_url,
            'children_count': 0,
            'discovery_method': 'link'
        }
    else:
        # Orphaned page (shouldn't happen with current logic, but for completeness)
        return {
            'type': 'orphaned',
            'depth': None,
            'parent_url': None,
            'children_count': 0,
            'discovery_method': 'unknown'
        }


def extract_site_url(page_url):
    """Extract site URL from page URL."""
    try:
        parsed = urlparse(page_url)
        return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        return page_url