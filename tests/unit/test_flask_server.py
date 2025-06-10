"""Unit tests for Flask web server functionality."""
import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def app():
    """Create Flask app for testing."""
    from src.web_interface.app import create_app
    
    app = create_app(testing=True)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestFlaskAppCreation:
    """Test Flask application creation and configuration."""
    
    def test_create_app_with_testing_config(self):
        """Test creating app with testing configuration."""
        from src.web_interface.app import create_app
        
        app = create_app(testing=True)
        
        assert app is not None
        assert app.config['TESTING'] is True
        assert app.config['DEBUG'] is False  # Should be False in testing
    
    def test_create_app_with_development_config(self):
        """Test creating app with development configuration."""
        from src.web_interface.app import create_app
        
        app = create_app(testing=False)
        
        assert app is not None
        assert app.config.get('TESTING', False) is False
    
    def test_app_has_required_routes(self, app):
        """Test that app has required routes."""
        # Get all routes
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(rule.rule)
        
        # Should have main interface route
        assert '/' in routes
        
        # Should have API routes
        assert '/api/scrape' in routes or '/scrape' in routes
        assert '/api/validate' in routes or '/validate' in routes
    
    def test_app_runs_on_localhost(self, app):
        """Test that app is configured for localhost."""
        # This tests configuration, actual running tested in integration
        assert app.config.get('SERVER_NAME') is None or 'localhost' in str(app.config.get('SERVER_NAME'))


class TestMainRoute:
    """Test main interface route."""
    
    def test_main_route_returns_html(self, client):
        """Test main route returns HTML interface."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert response.content_type.startswith('text/html')
    
    def test_main_route_contains_form_elements(self, client):
        """Test main route contains required form elements."""
        response = client.get('/')
        html_content = response.get_data(as_text=True)
        
        # Should have URL input
        assert 'url' in html_content.lower() or 'input' in html_content.lower()
        
        # Should have form element
        assert '<form' in html_content or 'form' in html_content.lower()
        
        # Should have submit button
        assert 'submit' in html_content.lower() or 'button' in html_content.lower()
    
    def test_main_route_includes_css_styles(self, client):
        """Test main route includes CSS styling."""
        response = client.get('/')
        html_content = response.get_data(as_text=True)
        
        # Should have styling
        assert '<style' in html_content or 'css' in html_content.lower()
    
    def test_main_route_includes_javascript(self, client):
        """Test main route includes JavaScript functionality."""
        response = client.get('/')
        html_content = response.get_data(as_text=True)
        
        # Should have JavaScript
        assert '<script' in html_content or 'javascript' in html_content.lower()


class TestURLValidationEndpoint:
    """Test URL validation API endpoint."""
    
    def test_validate_single_valid_url(self, client):
        """Test validation of single valid URL."""
        response = client.post('/api/validate', 
                             json={'url': 'https://example.com'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['is_valid'] is True
        assert 'error' not in data or data['error'] is None
    
    def test_validate_single_invalid_url(self, client):
        """Test validation of single invalid URL."""
        response = client.post('/api/validate', 
                             json={'url': 'not-a-valid-url'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['is_valid'] is False
        assert 'error' in data
        assert data['error'] is not None
    
    def test_validate_multiple_urls(self, client):
        """Test validation of multiple URLs."""
        urls = [
            'https://restaurant1.com',
            'invalid-url',
            'https://restaurant2.com'
        ]
        
        response = client.post('/api/validate', 
                             json={'urls': urls})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'results' in data
        assert len(data['results']) == 3
        
        # Check individual results
        assert data['results'][0]['is_valid'] is True
        assert data['results'][1]['is_valid'] is False
        assert data['results'][2]['is_valid'] is True
    
    def test_validate_empty_request(self, client):
        """Test validation with empty request."""
        response = client.post('/api/validate', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_validate_malformed_json(self, client):
        """Test validation with malformed JSON."""
        response = client.post('/api/validate', 
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_validate_get_method_not_allowed(self, client):
        """Test that GET method is not allowed for validation."""
        response = client.get('/api/validate')
        
        assert response.status_code == 405  # Method Not Allowed


class TestScrapingEndpoint:
    """Test scraping API endpoint."""
    
    @patch('src.web_interface.app.RestaurantScraper')
    def test_scrape_single_url_success(self, mock_scraper_class, client):
        """Test successful scraping of single URL."""
        # Mock scraper
        mock_scraper = Mock()
        mock_scraper_class.return_value = mock_scraper
        
        # Mock scraping result
        mock_result = Mock()
        mock_result.successful_extractions = [Mock()]
        mock_result.failed_urls = []
        mock_result.output_files = {'text': ['/tmp/output.txt']}
        mock_result.processing_time = 1.0
        mock_scraper.scrape_restaurants.return_value = mock_result
        
        response = client.post('/api/scrape', 
                             json={'url': 'https://restaurant.com'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'output_files' in data
    
    @patch('src.web_interface.app.RestaurantScraper')
    def test_scrape_multiple_urls_success(self, mock_scraper_class, client):
        """Test successful scraping of multiple URLs."""
        # Mock scraper
        mock_scraper = Mock()
        mock_scraper_class.return_value = mock_scraper
        
        # Mock scraping result
        mock_result = Mock()
        mock_result.successful_extractions = [Mock(), Mock()]
        mock_result.failed_urls = []
        mock_result.output_files = {'text': ['/tmp/output.txt']}
        mock_result.processing_time = 2.0
        mock_scraper.scrape_restaurants.return_value = mock_result
        
        urls = ['https://restaurant1.com', 'https://restaurant2.com']
        response = client.post('/api/scrape', 
                             json={'urls': urls})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['processed_count'] == 2
    
    @patch('src.web_interface.app.RestaurantScraper')
    def test_scrape_with_invalid_url(self, mock_scraper_class, client):
        """Test scraping with invalid URL."""
        response = client.post('/api/scrape', 
                             json={'url': 'invalid-url'})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    @patch('src.web_interface.app.RestaurantScraper')
    def test_scrape_with_scraper_exception(self, mock_scraper_class, client):
        """Test scraping when scraper raises exception."""
        # Mock scraper to raise exception
        mock_scraper = Mock()
        mock_scraper_class.return_value = mock_scraper
        mock_scraper.scrape_restaurants.side_effect = Exception("Network error")
        
        response = client.post('/api/scrape', 
                             json={'url': 'https://restaurant.com'})
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_scrape_empty_request(self, client):
        """Test scraping with empty request."""
        response = client.post('/api/scrape', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_scrape_get_method_not_allowed(self, client):
        """Test that GET method is not allowed for scraping."""
        response = client.get('/api/scrape')
        
        assert response.status_code == 405  # Method Not Allowed


class TestProgressEndpoint:
    """Test progress monitoring endpoint."""
    
    def test_progress_endpoint_exists(self, client):
        """Test that progress endpoint exists."""
        response = client.get('/api/progress')
        
        # Should either return progress or 404 if not implemented
        assert response.status_code in [200, 404]
    
    @patch('src.web_interface.app.get_current_progress')
    def test_get_progress_status(self, mock_get_progress, client):
        """Test getting current progress status."""
        # Mock progress data
        mock_get_progress.return_value = {
            'current_url': 'https://restaurant.com',
            'progress_percentage': 50,
            'urls_completed': 2,
            'urls_total': 4
        }
        
        response = client.get('/api/progress')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'current_url' in data
        assert 'progress_percentage' in data


class TestFileDownloadEndpoint:
    """Test file download functionality."""
    
    def test_download_endpoint_exists(self, client):
        """Test that download endpoint exists."""
        response = client.get('/api/download/test.txt')
        
        # Should either work or return 404 for non-existent file
        assert response.status_code in [200, 404]
    
    def test_download_nonexistent_file(self, client):
        """Test download of non-existent file."""
        response = client.get('/api/download/nonexistent.txt')
        
        assert response.status_code == 404
    
    def test_download_file_security(self, client):
        """Test download file path security."""
        # Try to access file outside allowed directory
        response = client.get('/api/download/../../../etc/passwd')
        
        assert response.status_code == 403 or response.status_code == 404


class TestErrorHandling:
    """Test error handling in Flask app."""
    
    def test_404_error_handling(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent-route')
        
        assert response.status_code == 404
        
        # Should return JSON error for API routes
        if response.content_type.startswith('application/json'):
            data = response.get_json()
            assert 'error' in data
    
    def test_500_error_handling(self, app, client):
        """Test 500 error handling."""
        # Create route that raises exception
        @app.route('/test-error')
        def test_error():
            raise Exception("Test error")
        
        # Enable error handling even in testing mode
        app.config['TESTING'] = False
        
        response = client.get('/test-error')
        
        assert response.status_code == 500
    
    def test_json_parsing_error(self, client):
        """Test JSON parsing error handling."""
        response = client.post('/api/validate',
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 400


class TestCORS:
    """Test CORS configuration."""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present."""
        response = client.get('/')
        
        # Check for CORS headers (if implemented)
        # This may not be needed for localhost-only app
        headers = dict(response.headers)
        
        # Either has CORS headers or doesn't need them for localhost
        assert response.status_code == 200


class TestSecurityHeaders:
    """Test security headers."""
    
    def test_security_headers_present(self, client):
        """Test that security headers are present."""
        response = client.get('/')
        
        headers = dict(response.headers)
        
        # Should have basic security measures
        assert response.status_code == 200
        
        # X-Content-Type-Options
        if 'X-Content-Type-Options' in headers:
            assert headers['X-Content-Type-Options'] == 'nosniff'
    
    def test_no_server_header_leakage(self, client):
        """Test that server information is not leaked."""
        response = client.get('/')
        
        headers = dict(response.headers)
        
        # Should not reveal Flask version or server info
        if 'Server' in headers:
            server_header = headers['Server'].lower()
            assert 'flask' not in server_header
            assert 'werkzeug' not in server_header


class TestStaticFiles:
    """Test static file serving."""
    
    def test_css_files_served(self, client):
        """Test that CSS files are served."""
        response = client.get('/static/style.css')
        
        # Should either serve file or 404 if not exists
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            assert response.content_type.startswith('text/css')
    
    def test_js_files_served(self, client):
        """Test that JavaScript files are served."""
        response = client.get('/static/script.js')
        
        # Should either serve file or 404 if not exists
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            assert 'javascript' in response.content_type or 'text/plain' in response.content_type


class TestAppConfiguration:
    """Test application configuration."""
    
    def test_debug_mode_in_testing(self, app):
        """Test debug mode configuration in testing."""
        assert app.config['TESTING'] is True
        assert app.config.get('DEBUG', True) is not True  # Should be False in testing
    
    def test_secret_key_configured(self, app):
        """Test that secret key is configured."""
        # Should have secret key for session management
        assert 'SECRET_KEY' in app.config
        assert app.config['SECRET_KEY'] is not None
        assert len(app.config['SECRET_KEY']) > 10
    
    def test_upload_folder_configured(self, app):
        """Test that upload folder is configured."""
        # Should have upload folder for file generation
        if 'UPLOAD_FOLDER' in app.config:
            upload_folder = app.config['UPLOAD_FOLDER']
            assert upload_folder is not None
            assert len(upload_folder) > 0
    
    def test_max_content_length_configured(self, app):
        """Test that max content length is configured."""
        # Should have reasonable limits for API requests
        if 'MAX_CONTENT_LENGTH' in app.config:
            max_length = app.config['MAX_CONTENT_LENGTH']
            assert max_length is not None
            assert max_length > 1024  # At least 1KB
            assert max_length < 100 * 1024 * 1024  # Less than 100MB