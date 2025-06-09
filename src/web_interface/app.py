"""Flask web application for RAG_Scraper."""
import os
import json
import tempfile
from flask import Flask, render_template_string, request, jsonify, send_file
from werkzeug.exceptions import BadRequest
import secrets

from src.config.url_validator import URLValidator
from src.config.scraping_config import ScrapingConfig


# Global variable to store current progress
current_progress = {
    'current_url': None,
    'progress_percentage': 0,
    'urls_completed': 0,
    'urls_total': 0,
    'status': 'idle'
}


def create_app(testing=False):
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = secrets.token_hex(16)
    app.config['TESTING'] = testing
    app.config['DEBUG'] = False  # Always False for security
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size
    
    # Upload folder configuration
    if testing:
        app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
    else:
        app.config['UPLOAD_FOLDER'] = os.path.join(os.path.expanduser('~'), 'Downloads')
    
    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    # Main interface route
    @app.route('/')
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
    @app.route('/api/validate', methods=['POST'])
    def validate_urls():
        """Validate URLs endpoint."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            validator = URLValidator()
            
            # Handle single URL
            if 'url' in data:
                result = validator.validate_url(data['url'])
                return jsonify({
                    'is_valid': result.is_valid,
                    'error': result.error_message
                })
            
            # Handle multiple URLs
            elif 'urls' in data:
                results = validator.validate_urls(data['urls'])
                return jsonify({
                    'results': [
                        {
                            'is_valid': result.is_valid,
                            'error': result.error_message
                        }
                        for result in results
                    ]
                })
            
            else:
                return jsonify({'error': 'No URL or URLs provided'}), 400
                
        except BadRequest:
            return jsonify({'error': 'Invalid JSON'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Scraping endpoint
    @app.route('/api/scrape', methods=['POST'])
    def scrape_restaurants():
        """Scrape restaurants endpoint."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            # Extract URLs
            urls = []
            if 'url' in data:
                urls = [data['url']]
            elif 'urls' in data:
                urls = data['urls']
            else:
                return jsonify({'success': False, 'error': 'No URLs provided'}), 400
            
            # Validate URLs first
            validator = URLValidator()
            validation_results = validator.validate_urls(urls)
            
            invalid_urls = [result for result in validation_results if not result.is_valid]
            if invalid_urls:
                return jsonify({
                    'success': False,
                    'error': f'Invalid URLs provided: {len(invalid_urls)} of {len(urls)} URLs are invalid'
                }), 400
            
            # Configure scraping
            output_dir = data.get('output_dir') or app.config['UPLOAD_FOLDER']
            file_mode = data.get('file_mode', 'single')
            
            config = ScrapingConfig(
                urls=urls,
                output_directory=output_dir,
                file_mode=file_mode
            )
            
            # Progress callback
            def progress_callback(message, percentage=None, current_url=None):
                global current_progress
                current_progress.update({
                    'status': message,
                    'progress_percentage': percentage or current_progress['progress_percentage'],
                    'current_url': current_url or current_progress['current_url'],
                    'urls_total': len(urls)
                })
            
            # Import and run scraper
            from src.scraper.restaurant_scraper import RestaurantScraper
            scraper = RestaurantScraper()
            
            result = scraper.scrape_restaurants(config, progress_callback=progress_callback)
            
            # Return results
            return jsonify({
                'success': True,
                'processed_count': len(result.successful_extractions),
                'failed_count': len(result.failed_urls),
                'output_files': result.output_files.get('text', []),
                'processing_time': getattr(result, 'processing_time', 0)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # Progress endpoint
    @app.route('/api/progress', methods=['GET'])
    def get_progress():
        """Get current scraping progress."""
        global current_progress
        return jsonify(current_progress)
    
    # File download endpoint
    @app.route('/api/download/<filename>')
    def download_file(filename):
        """Download generated file."""
        try:
            # Security: ensure filename is safe
            if '..' in filename or '/' in filename or '\\' in filename:
                return jsonify({'error': 'Invalid filename'}), 403
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            if not os.path.exists(file_path):
                return jsonify({'error': 'File not found'}), 404
            
            return send_file(file_path, as_attachment=True)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Endpoint not found'}), 404
        return render_template_string('<h1>Page Not Found</h1><p>The requested page does not exist.</p>'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template_string('<h1>Server Error</h1><p>An internal error occurred.</p>'), 500
    
    return app


def get_current_progress():
    """Get current progress for testing."""
    global current_progress
    return current_progress


if __name__ == '__main__':
    app = create_app()
    app.run(host='localhost', port=8080, debug=False)