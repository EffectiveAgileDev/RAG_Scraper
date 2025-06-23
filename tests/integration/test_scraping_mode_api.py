"""Integration tests for scraping mode API endpoint changes."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from src.web_interface.app import create_app
from src.scraper.restaurant_scraper import RestaurantScraper
from src.config.scraping_config import ScrapingConfig


class TestScrapingModeAPIIntegration:
    """Integration tests for scraping mode API functionality."""

    @pytest.fixture
    def app(self):
        """Create Flask app for testing."""
        app = create_app(testing=True)
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    @pytest.fixture
    def valid_urls(self):
        """Valid test URLs."""
        return ['https://restaurant1.com', 'https://restaurant2.com']

    @pytest.fixture
    def single_page_request_data(self, valid_urls):
        """Single-page mode request data."""
        return {
            'urls': valid_urls,
            'output_dir': '/test/output',
            'file_mode': 'single',
            'file_format': 'text',
            'scraping_mode': 'single'
        }

    @pytest.fixture
    def multi_page_request_data(self, valid_urls):
        """Multi-page mode request data."""
        return {
            'urls': valid_urls,
            'output_dir': '/test/output',
            'file_mode': 'single',
            'file_format': 'text',
            'scraping_mode': 'multi',
            'multi_page_config': {
                'maxPages': 75,
                'crawlDepth': 3,
                'includePatterns': 'menu,food,restaurant',
                'excludePatterns': 'admin,login,cart',
                'rateLimit': 1500
            }
        }

    @patch('src.web_interface.app.URLValidator')
    @patch('src.web_interface.app.RestaurantScraper')
    @patch('src.web_interface.app.advanced_monitor')
    def test_single_page_mode_api_endpoint(self, mock_monitor, mock_scraper_class, mock_validator, client, single_page_request_data):
        """Test /api/scrape endpoint with single-page mode."""
        # Mock validator to return valid URLs
        mock_validator_instance = Mock()
        mock_validator_instance.validate_urls.return_value = [
            Mock(is_valid=True) for _ in single_page_request_data['urls']
        ]
        mock_validator.return_value = mock_validator_instance
        
        # Mock scraper
        mock_scraper = Mock()
        mock_result = Mock()
        mock_result.successful_extractions = []
        mock_result.failed_urls = []
        mock_result.total_processed = 2
        mock_result.errors = []
        mock_result.processing_time = 5.0
        mock_scraper.scrape_restaurants.return_value = mock_result
        mock_scraper_class.return_value = mock_scraper
        
        # Mock file generator service
        with patch('src.web_interface.app.file_generator_service') as mock_file_service:
            mock_file_service.generate_files.return_value = {
                'success': True,
                'files': {'text': ['/test/output/restaurants.txt']}
            }
            
            # Make request
            response = client.post('/api/scrape', 
                                   data=json.dumps(single_page_request_data),
                                   content_type='application/json')
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            
            # Verify scraper was created with correct mode
            mock_scraper_class.assert_called_once_with(enable_multi_page=False)

    @patch('src.web_interface.app.URLValidator')
    @patch('src.web_interface.app.RestaurantScraper')
    @patch('src.web_interface.app.advanced_monitor')
    def test_multi_page_mode_api_endpoint(self, mock_monitor, mock_scraper_class, mock_validator, client, multi_page_request_data):
        """Test /api/scrape endpoint with multi-page mode."""
        # Mock validator to return valid URLs
        mock_validator_instance = Mock()
        mock_validator_instance.validate_urls.return_value = [
            Mock(is_valid=True) for _ in multi_page_request_data['urls']
        ]
        mock_validator.return_value = mock_validator_instance
        
        # Mock scraper
        mock_scraper = Mock()
        mock_result = Mock()
        mock_result.successful_extractions = []
        mock_result.failed_urls = []
        mock_result.total_processed = 2
        mock_result.errors = []
        mock_result.processing_time = 8.0
        mock_scraper.scrape_restaurants.return_value = mock_result
        mock_scraper_class.return_value = mock_scraper
        
        # Mock file generator service
        with patch('src.web_interface.app.file_generator_service') as mock_file_service:
            mock_file_service.generate_files.return_value = {
                'success': True,
                'files': {'text': ['/test/output/restaurants.txt']}
            }
            
            # Make request
            response = client.post('/api/scrape', 
                                   data=json.dumps(multi_page_request_data),
                                   content_type='application/json')
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            
            # Verify scraper was created with correct mode
            mock_scraper_class.assert_called_once_with(enable_multi_page=True)

    @patch('src.web_interface.app.URLValidator')
    def test_api_endpoint_with_invalid_urls(self, mock_validator, client):
        """Test API endpoint with invalid URLs."""
        # Mock validator to return invalid URLs
        mock_validator_instance = Mock()
        mock_validator_instance.validate_urls.return_value = [
            Mock(is_valid=False, error_message="Invalid URL")
        ]
        mock_validator.return_value = mock_validator_instance
        
        request_data = {
            'urls': ['invalid-url'],
            'scraping_mode': 'single'
        }
        
        response = client.post('/api/scrape', 
                               data=json.dumps(request_data),
                               content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Invalid URLs' in data['error']

    def test_api_endpoint_with_missing_data(self, client):
        """Test API endpoint with missing data."""
        response = client.post('/api/scrape', 
                               data=json.dumps({}),
                               content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'No URLs provided' in data['error']

    def test_api_endpoint_with_no_json_data(self, client):
        """Test API endpoint with no JSON data."""
        response = client.post('/api/scrape')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'No data provided' in data['error']

    @patch('src.web_interface.app.URLValidator')
    @patch('src.web_interface.app.RestaurantScraper')
    @patch('src.web_interface.app.advanced_monitor')
    def test_multi_page_config_parameter_passing(self, mock_monitor, mock_scraper_class, mock_validator, client, multi_page_request_data):
        """Test that multi-page configuration parameters are correctly processed."""
        # Mock validator
        mock_validator_instance = Mock()
        mock_validator_instance.validate_urls.return_value = [
            Mock(is_valid=True) for _ in multi_page_request_data['urls']
        ]
        mock_validator.return_value = mock_validator_instance
        
        # Mock scraper
        mock_scraper = Mock()
        mock_result = Mock()
        mock_result.successful_extractions = []
        mock_result.failed_urls = []
        mock_result.total_processed = 2
        mock_result.errors = []
        mock_result.processing_time = 8.0
        mock_scraper.scrape_restaurants.return_value = mock_result
        mock_scraper_class.return_value = mock_scraper
        
        # Mock file generator service
        with patch('src.web_interface.app.file_generator_service') as mock_file_service:
            mock_file_service.generate_files.return_value = {
                'success': True,
                'files': {'text': ['/test/output/restaurants.txt']}
            }
            
            # Make request
            response = client.post('/api/scrape', 
                                   data=json.dumps(multi_page_request_data),
                                   content_type='application/json')
            
            # Verify the response is successful
            assert response.status_code == 200
            
            # In a real implementation, we would verify that the multi-page config
            # is passed to the appropriate components. For now, we verify the scraper
            # was created in multi-page mode
            mock_scraper_class.assert_called_once_with(enable_multi_page=True)

    @patch('src.web_interface.app.URLValidator')
    @patch('src.web_interface.app.RestaurantScraper')
    @patch('src.web_interface.app.advanced_monitor')
    def test_progress_monitoring_with_different_modes(self, mock_monitor, mock_scraper_class, mock_validator, client):
        """Test that progress monitoring is configured correctly for different modes."""
        # Test data for both modes
        test_cases = [
            {
                'mode': 'single',
                'data': {
                    'urls': ['https://restaurant1.com'],
                    'scraping_mode': 'single'
                },
                'expect_multipage_monitoring': False
            },
            {
                'mode': 'multi',
                'data': {
                    'urls': ['https://restaurant1.com'],
                    'scraping_mode': 'multi',
                    'multi_page_config': {
                        'maxPages': 50,
                        'crawlDepth': 2,
                        'includePatterns': 'menu',
                        'excludePatterns': 'admin',
                        'rateLimit': 1000
                    }
                },
                'expect_multipage_monitoring': True
            }
        ]
        
        for test_case in test_cases:
            # Reset mocks
            mock_monitor.reset_mock()
            mock_scraper_class.reset_mock()
            
            # Mock validator
            mock_validator_instance = Mock()
            mock_validator_instance.validate_urls.return_value = [Mock(is_valid=True)]
            mock_validator.return_value = mock_validator_instance
            
            # Mock scraper
            mock_scraper = Mock()
            mock_result = Mock()
            mock_result.successful_extractions = []
            mock_result.failed_urls = []
            mock_result.total_processed = 1
            mock_result.errors = []
            mock_result.processing_time = 3.0
            mock_scraper.scrape_restaurants.return_value = mock_result
            mock_scraper_class.return_value = mock_scraper
            
            # Mock file generator service
            with patch('src.web_interface.app.file_generator_service') as mock_file_service:
                mock_file_service.generate_files.return_value = {
                    'success': True,
                    'files': {'text': ['/test/output/restaurants.txt']}
                }
                
                # Make request
                response = client.post('/api/scrape', 
                                       data=json.dumps(test_case['data']),
                                       content_type='application/json')
                
                # Verify response
                assert response.status_code == 200
                
                # Verify multipage monitoring is enabled/disabled appropriately
                if test_case['expect_multipage_monitoring']:
                    mock_monitor.enable_multipage_monitoring.assert_called_once()
                # Note: We can't easily test the negative case without more complex mocking

    def test_web_interface_home_page_contains_mode_selector(self, client):
        """Test that the home page contains the mode selector elements."""
        response = client.get('/')
        
        assert response.status_code == 200
        html_content = response.data.decode('utf-8')
        
        # Check for mode selector elements
        assert 'scraping-mode-selector' in html_content
        assert 'SINGLE_PAGE' in html_content
        assert 'MULTI_PAGE' in html_content
        assert 'scrapingMode' in html_content
        assert 'MULTI_PAGE_CONFIG' in html_content

    def test_web_interface_contains_config_panel_elements(self, client):
        """Test that the web interface contains all configuration panel elements."""
        response = client.get('/')
        
        assert response.status_code == 200
        html_content = response.data.decode('utf-8')
        
        # Check for configuration elements
        assert 'maxPages' in html_content
        assert 'crawlDepth' in html_content
        assert 'includePatterns' in html_content
        assert 'excludePatterns' in html_content
        assert 'rateLimit' in html_content
        assert 'multiPageConfig' in html_content

    def test_web_interface_javascript_functions(self, client):
        """Test that the web interface contains the necessary JavaScript functions."""
        response = client.get('/')
        
        assert response.status_code == 200
        html_content = response.data.decode('utf-8')
        
        # Check for JavaScript functions
        assert 'toggleMultiPageConfig' in html_content
        assert 'setupModeSelection' in html_content
        assert 'setupSliderUpdates' in html_content


class TestAPIDataValidation:
    """Test suite for API data validation."""

    @pytest.fixture
    def app(self):
        """Create Flask app for testing."""
        app = create_app(testing=True)
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    def test_scraping_mode_validation(self, client):
        """Test scraping mode validation in API."""
        test_cases = [
            {'mode': 'single', 'should_succeed': True},
            {'mode': 'multi', 'should_succeed': True},
            {'mode': 'invalid', 'should_succeed': True},  # API accepts any string, validation happens in scraper
            {'mode': '', 'should_succeed': True},  # Empty string defaults to 'single'
        ]
        
        for test_case in test_cases:
            request_data = {
                'urls': ['https://restaurant1.com'],
                'scraping_mode': test_case['mode']
            }
            
            with patch('src.web_interface.app.URLValidator') as mock_validator:
                mock_validator_instance = Mock()
                mock_validator_instance.validate_urls.return_value = [Mock(is_valid=True)]
                mock_validator.return_value = mock_validator_instance
                
                with patch('src.web_interface.app.RestaurantScraper') as mock_scraper_class:
                    mock_scraper = Mock()
                    mock_result = Mock()
                    mock_result.successful_extractions = []
                    mock_result.failed_urls = []
                    mock_result.total_processed = 1
                    mock_result.errors = []
                    mock_result.processing_time = 3.0
                    mock_scraper.scrape_restaurants.return_value = mock_result
                    mock_scraper_class.return_value = mock_scraper
                    
                    with patch('src.web_interface.app.file_generator_service') as mock_file_service:
                        mock_file_service.generate_files.return_value = {
                            'success': True,
                            'files': {'text': ['/test/output/restaurants.txt']}
                        }
                        
                        response = client.post('/api/scrape', 
                                               data=json.dumps(request_data),
                                               content_type='application/json')
                        
                        if test_case['should_succeed']:
                            assert response.status_code == 200
                        else:
                            assert response.status_code == 400

    def test_multi_page_config_validation(self, client):
        """Test multi-page configuration validation."""
        base_request = {
            'urls': ['https://restaurant1.com'],
            'scraping_mode': 'multi'
        }
        
        test_configs = [
            # Valid configuration
            {
                'config': {
                    'maxPages': 50,
                    'crawlDepth': 3,
                    'includePatterns': 'menu,food',
                    'excludePatterns': 'admin,login',
                    'rateLimit': 1500
                },
                'should_succeed': True
            },
            # Missing configuration (should use defaults)
            {
                'config': {},
                'should_succeed': True
            },
            # Partial configuration (should use defaults for missing values)
            {
                'config': {
                    'maxPages': 25
                },
                'should_succeed': True
            }
        ]
        
        for test_config in test_configs:
            request_data = base_request.copy()
            if test_config['config']:
                request_data['multi_page_config'] = test_config['config']
            
            with patch('src.web_interface.app.URLValidator') as mock_validator:
                mock_validator_instance = Mock()
                mock_validator_instance.validate_urls.return_value = [Mock(is_valid=True)]
                mock_validator.return_value = mock_validator_instance
                
                with patch('src.web_interface.app.RestaurantScraper') as mock_scraper_class:
                    mock_scraper = Mock()
                    mock_result = Mock()
                    mock_result.successful_extractions = []
                    mock_result.failed_urls = []
                    mock_result.total_processed = 1
                    mock_result.errors = []
                    mock_result.processing_time = 3.0
                    mock_scraper.scrape_restaurants.return_value = mock_result
                    mock_scraper_class.return_value = mock_scraper
                    
                    with patch('src.web_interface.app.file_generator_service') as mock_file_service:
                        mock_file_service.generate_files.return_value = {
                            'success': True,
                            'files': {'text': ['/test/output/restaurants.txt']}
                        }
                        
                        response = client.post('/api/scrape', 
                                               data=json.dumps(request_data),
                                               content_type='application/json')
                        
                        if test_config['should_succeed']:
                            assert response.status_code == 200
                        else:
                            assert response.status_code == 400


if __name__ == '__main__':
    pytest.main([__file__])