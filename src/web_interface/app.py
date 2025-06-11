"""Flask web application for RAG_Scraper."""
import os
import json
import tempfile
from flask import Flask, render_template_string, request, jsonify, send_file
from werkzeug.exceptions import BadRequest
import secrets

from src.config.url_validator import URLValidator
from src.config.scraping_config import ScrapingConfig
from src.scraper.restaurant_scraper import RestaurantScraper
from src.file_generator.file_generator_service import (
    FileGeneratorService,
    FileGenerationRequest,
)


# Global variable to store current progress and scraper instance
current_progress = {
    "current_url": None,
    "progress_percentage": 0,
    "urls_completed": 0,
    "urls_total": 0,
    "status": "idle",
    "estimated_time_remaining": 0,
    "current_operation": "",
    "memory_usage_mb": 0,
    "processing_time": 0,
}

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

    # Main interface route
    @app.route("/")
    def index():
        """Serve main interface."""
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>RAG_Scraper - Restaurant Website Scraper</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    background-color: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #333;
                    text-align: center;
                    margin-bottom: 30px;
                }
                .form-group {
                    margin-bottom: 20px;
                }
                label {
                    display: block;
                    margin-bottom: 5px;
                    font-weight: bold;
                    color: #555;
                }
                textarea, input, select {
                    width: 100%;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 14px;
                }
                textarea {
                    height: 120px;
                    resize: vertical;
                }
                button {
                    background-color: #007bff;
                    color: white;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                    margin-right: 10px;
                }
                button:hover {
                    background-color: #0056b3;
                }
                button:disabled {
                    background-color: #6c757d;
                    cursor: not-allowed;
                }
                .progress-container {
                    display: none;
                    margin-top: 20px;
                    padding: 20px;
                    background-color: #f8f9fa;
                    border-radius: 4px;
                }
                .progress-bar {
                    width: 100%;
                    height: 20px;
                    background-color: #e9ecef;
                    border-radius: 10px;
                    overflow: hidden;
                }
                .progress-fill {
                    height: 100%;
                    background-color: #28a745;
                    width: 0%;
                    transition: width 0.3s ease;
                }
                .results-container {
                    display: none;
                    margin-top: 20px;
                    padding: 20px;
                    border-radius: 4px;
                }
                .success {
                    background-color: #d4edda;
                    border: 1px solid #c3e6cb;
                    color: #155724;
                }
                .error {
                    background-color: #f8d7da;
                    border: 1px solid #f5c6cb;
                    color: #721c24;
                }
                .url-validation {
                    margin-top: 10px;
                    font-size: 12px;
                }
                .valid-url {
                    color: #28a745;
                }
                .invalid-url {
                    color: #dc3545;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>RAG_Scraper</h1>
                <p style="text-align: center; color: #666; margin-bottom: 30px;">
                    Extract restaurant data from websites for RAG systems
                </p>
                
                <form id="scrapeForm">
                    <div class="form-group">
                        <label for="urls">Restaurant Website URLs (one per line):</label>
                        <textarea id="urls" name="urls" placeholder="https://restaurant1.com
https://restaurant2.com
https://restaurant3.com" required></textarea>
                        <div id="urlValidation" class="url-validation"></div>
                    </div>
                    
                    <div class="form-group">
                        <label for="outputDir">Output Directory:</label>
                        <input type="text" id="outputDir" name="outputDir" placeholder="Leave empty for default Downloads folder">
                    </div>
                    
                    <div class="form-group">
                        <label for="fileMode">File Mode:</label>
                        <select id="fileMode" name="fileMode">
                            <option value="single">Single file for all restaurants</option>
                            <option value="multiple">Separate file per restaurant</option>
                        </select>
                    </div>
                    
                    <button type="submit" id="submitBtn">Start Scraping</button>
                    <button type="button" id="validateBtn">Validate URLs</button>
                    <button type="button" id="clearBtn">Clear All</button>
                </form>
                
                <div id="progressContainer" class="progress-container">
                    <h3>Scraping Progress</h3>
                    <div class="progress-bar">
                        <div id="progressFill" class="progress-fill"></div>
                    </div>
                    <p id="progressText">Initializing...</p>
                    <p id="currentUrl"></p>
                    <p id="timeEstimate"></p>
                    <p id="memoryUsage"></p>
                </div>
                
                <div id="resultsContainer" class="results-container">
                    <h3>Results</h3>
                    <div id="resultsContent"></div>
                </div>
            </div>
            
            <script>
                const form = document.getElementById('scrapeForm');
                const urlsInput = document.getElementById('urls');
                const submitBtn = document.getElementById('submitBtn');
                const validateBtn = document.getElementById('validateBtn');
                const clearBtn = document.getElementById('clearBtn');
                const progressContainer = document.getElementById('progressContainer');
                const progressFill = document.getElementById('progressFill');
                const progressText = document.getElementById('progressText');
                const currentUrl = document.getElementById('currentUrl');
                const timeEstimate = document.getElementById('timeEstimate');
                const memoryUsage = document.getElementById('memoryUsage');
                const resultsContainer = document.getElementById('resultsContainer');
                const resultsContent = document.getElementById('resultsContent');
                const urlValidation = document.getElementById('urlValidation');
                
                let progressInterval;
                
                // Validate URLs on input
                urlsInput.addEventListener('input', debounce(validateURLsInput, 500));
                
                // Form submission
                form.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    
                    const urls = urlsInput.value.trim().split('\\n').filter(url => url.trim());
                    const outputDir = document.getElementById('outputDir').value.trim();
                    const fileMode = document.getElementById('fileMode').value;
                    
                    if (urls.length === 0) {
                        alert('Please enter at least one URL');
                        return;
                    }
                    
                    await startScraping(urls, outputDir, fileMode);
                });
                
                // Validate button
                validateBtn.addEventListener('click', validateURLsInput);
                
                // Clear button
                clearBtn.addEventListener('click', () => {
                    form.reset();
                    urlValidation.innerHTML = '';
                    hideResults();
                    hideProgress();
                });
                
                async function validateURLsInput() {
                    const urls = urlsInput.value.trim().split('\\n').filter(url => url.trim());
                    
                    if (urls.length === 0) {
                        urlValidation.innerHTML = '';
                        return;
                    }
                    
                    try {
                        const response = await fetch('/api/validate', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ urls: urls })
                        });
                        
                        const data = await response.json();
                        
                        if (data.results) {
                            displayValidationResults(data.results);
                        }
                    } catch (error) {
                        console.error('Validation error:', error);
                        urlValidation.innerHTML = '<span class="invalid-url">Validation failed</span>';
                    }
                }
                
                function displayValidationResults(results) {
                    const validCount = results.filter(r => r.is_valid).length;
                    const totalCount = results.length;
                    
                    let html = `<strong>${validCount}/${totalCount} URLs valid</strong><br>`;
                    
                    results.forEach((result, index) => {
                        const cssClass = result.is_valid ? 'valid-url' : 'invalid-url';
                        const status = result.is_valid ? '✓' : '✗';
                        const error = result.error ? ` (${result.error})` : '';
                        
                        html += `<span class="${cssClass}">${status} URL ${index + 1}${error}</span><br>`;
                    });
                    
                    urlValidation.innerHTML = html;
                }
                
                async function startScraping(urls, outputDir, fileMode) {
                    submitBtn.disabled = true;
                    showProgress();
                    hideResults();
                    
                    try {
                        const response = await fetch('/api/scrape', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                urls: urls,
                                output_dir: outputDir,
                                file_mode: fileMode
                            })
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            showResults(data, true);
                        } else {
                            showResults(data, false);
                        }
                    } catch (error) {
                        console.error('Scraping error:', error);
                        showResults({ error: 'Network error occurred' }, false);
                    } finally {
                        submitBtn.disabled = false;
                        hideProgress();
                    }
                }
                
                function showProgress() {
                    progressContainer.style.display = 'block';
                    progressFill.style.width = '0%';
                    progressText.textContent = 'Starting scraping...';
                    currentUrl.textContent = '';
                    timeEstimate.textContent = '';
                    memoryUsage.textContent = '';
                    
                    // Start progress polling
                    progressInterval = setInterval(updateProgress, 1000);
                }
                
                function hideProgress() {
                    progressContainer.style.display = 'none';
                    if (progressInterval) {
                        clearInterval(progressInterval);
                        progressInterval = null;
                    }
                }
                
                async function updateProgress() {
                    try {
                        const response = await fetch('/api/progress');
                        const data = await response.json();
                        
                        if (data.progress_percentage !== undefined) {
                            progressFill.style.width = data.progress_percentage + '%';
                            progressText.textContent = `${data.progress_percentage}% complete (${data.urls_completed}/${data.urls_total})`;
                            
                            if (data.current_url) {
                                currentUrl.textContent = `Processing: ${data.current_url}`;
                            }
                            
                            if (data.estimated_time_remaining > 0) {
                                const minutes = Math.floor(data.estimated_time_remaining / 60);
                                const seconds = Math.floor(data.estimated_time_remaining % 60);
                                timeEstimate.textContent = `Estimated time remaining: ${minutes}m ${seconds}s`;
                            } else if (data.urls_completed > 0) {
                                timeEstimate.textContent = 'Calculating time estimate...';
                            }
                            
                            if (data.memory_usage_mb > 0) {
                                memoryUsage.textContent = `Memory usage: ${data.memory_usage_mb.toFixed(1)} MB`;
                            }
                            
                            if (data.current_operation) {
                                progressText.textContent = data.current_operation;
                            }
                        }
                    } catch (error) {
                        console.error('Progress update error:', error);
                    }
                }
                
                function showResults(data, success) {
                    resultsContainer.style.display = 'block';
                    resultsContainer.className = 'results-container ' + (success ? 'success' : 'error');
                    
                    let html = '';
                    
                    if (success) {
                        html += '<h4>Scraping Completed Successfully!</h4>';
                        if (data.processed_count) {
                            html += `<p>Successfully processed ${data.processed_count} restaurant(s)</p>`;
                        }
                        if (data.output_files && data.output_files.length > 0) {
                            html += '<p>Generated files:</p><ul>';
                            data.output_files.forEach(file => {
                                html += `<li>${file}</li>`;
                            });
                            html += '</ul>';
                        }
                        if (data.failed_count && data.failed_count > 0) {
                            html += `<p>Failed URLs: ${data.failed_count}</p>`;
                        }
                    } else {
                        html += '<h4>Scraping Failed</h4>';
                        html += `<p>Error: ${data.error || 'Unknown error occurred'}</p>`;
                    }
                    
                    resultsContent.innerHTML = html;
                }
                
                function hideResults() {
                    resultsContainer.style.display = 'none';
                }
                
                function debounce(func, wait) {
                    let timeout;
                    return function executedFunction(...args) {
                        const later = () => {
                            clearTimeout(timeout);
                            func(...args);
                        };
                        clearTimeout(timeout);
                        timeout = setTimeout(later, wait);
                    };
                }
            </script>
        </body>
        </html>
        """
        return render_template_string(html_template)

    # URL validation endpoint
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

    # Scraping endpoint
    @app.route("/api/scrape", methods=["POST"])
    def scrape_restaurants():
        """Scrape restaurants endpoint."""
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

            config = ScrapingConfig(
                urls=urls, output_directory=output_dir, file_mode=file_mode
            )

            # Progress callback
            def progress_callback(message, percentage=None, time_estimate=None):
                global current_progress, active_scraper
                current_progress.update(
                    {
                        "status": message,
                        "progress_percentage": percentage
                        if percentage is not None
                        else current_progress["progress_percentage"],
                        "urls_total": len(urls),
                    }
                )

                if time_estimate is not None:
                    current_progress["estimated_time_remaining"] = time_estimate

                # Get detailed progress from batch processor if available
                if active_scraper and hasattr(active_scraper, "get_current_progress"):
                    batch_progress = active_scraper.get_current_progress()
                    if batch_progress:
                        current_progress.update(
                            {
                                "current_url": batch_progress.current_url,
                                "urls_completed": batch_progress.urls_completed,
                                "progress_percentage": batch_progress.progress_percentage,
                                "estimated_time_remaining": batch_progress.estimated_time_remaining,
                                "current_operation": batch_progress.current_operation,
                                "memory_usage_mb": batch_progress.memory_usage_mb,
                            }
                        )

            # Create and run scraper with progress tracking
            global active_scraper
            scraper = RestaurantScraper()
            active_scraper = scraper

            # Force batch processing for better progress tracking
            config.force_batch_processing = True

            result = scraper.scrape_restaurants(
                config, progress_callback=progress_callback
            )

            # Clear active scraper
            active_scraper = None

            # Automatically generate files after successful scraping
            generated_files = []
            file_generation_errors = []
            
            if result.successful_extractions:
                # Determine which formats to generate
                formats_to_generate = []
                if file_format == "both":
                    formats_to_generate = ["text", "pdf"]
                else:
                    formats_to_generate = [file_format]
                
                # Generate files for each requested format
                for fmt in formats_to_generate:
                    try:
                        from src.file_generator.file_generator_service import FileGenerationRequest
                        
                        file_request = FileGenerationRequest(
                            restaurant_data=result.successful_extractions,
                            file_format=fmt,
                            output_directory=output_dir,
                            allow_overwrite=True,
                            save_preferences=False
                        )
                        
                        file_result = file_generator_service.generate_file(file_request)
                        
                        if file_result["success"]:
                            generated_files.append(file_result["file_path"])
                        else:
                            file_generation_errors.append(f"{fmt.upper()} generation failed: {file_result['error']}")
                    
                    except Exception as e:
                        file_generation_errors.append(f"{fmt.upper()} generation error: {str(e)}")

            # Return results with actual file paths
            response_data = {
                "success": True,
                "processed_count": len(result.successful_extractions),
                "failed_count": len(result.failed_urls),
                "output_files": generated_files,
                "processing_time": getattr(result, "processing_time", 0),
            }
            
            # Include file generation errors if any occurred
            if file_generation_errors:
                response_data["file_generation_warnings"] = file_generation_errors
            
            return jsonify(response_data)

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    # Progress endpoint
    @app.route("/api/progress", methods=["GET"])
    def get_progress():
        """Get current scraping progress."""
        global current_progress, active_scraper

        # Get real-time progress from active scraper if available
        if active_scraper and hasattr(active_scraper, "get_current_progress"):
            batch_progress = active_scraper.get_current_progress()
            if batch_progress:
                # Update current_progress with latest batch processor data
                current_progress.update(
                    {
                        "current_url": batch_progress.current_url,
                        "urls_completed": batch_progress.urls_completed,
                        "progress_percentage": batch_progress.progress_percentage,
                        "estimated_time_remaining": batch_progress.estimated_time_remaining,
                        "current_operation": batch_progress.current_operation,
                        "memory_usage_mb": batch_progress.memory_usage_mb,
                    }
                )

        return jsonify(current_progress)

    # File download endpoint
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

    # File generation endpoints
    @app.route("/api/generate-file", methods=["POST"])
    def generate_file():
        """Generate text file from scraped restaurant data."""
        global file_generator_service

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
        global file_generator_service

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
        global file_generator_service

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
        global file_generator_service

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
        global file_generator_service

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

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Endpoint not found"}), 404
        return (
            render_template_string(
                "<h1>Page Not Found</h1><p>The requested page does not exist.</p>"
            ),
            404,
        )

    @app.errorhandler(500)
    def internal_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Internal server error"}), 500
        return (
            render_template_string(
                "<h1>Server Error</h1><p>An internal error occurred.</p>"
            ),
            500,
        )

    return app


def get_current_progress():
    """Get current progress for testing."""
    global current_progress
    return current_progress


if __name__ == "__main__":
    app = create_app()
    app.run(host="localhost", port=8080, debug=False)
