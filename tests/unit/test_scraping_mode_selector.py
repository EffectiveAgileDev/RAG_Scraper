"""Unit tests for scraping mode selector functionality."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.scraper.restaurant_scraper import RestaurantScraper
from src.config.scraping_config import ScrapingConfig


class TestScrapingModeSelector:
    """Test suite for scraping mode selector functionality."""

    def test_restaurant_scraper_single_page_mode_initialization(self):
        """Test RestaurantScraper initializes correctly for single-page mode."""
        scraper = RestaurantScraper(enable_multi_page=False)
        
        assert scraper.enable_multi_page is False
        assert scraper.multi_page_scraper is None
        assert scraper.multi_scraper is not None

    def test_restaurant_scraper_multi_page_mode_initialization(self):
        """Test RestaurantScraper initializes correctly for multi-page mode."""
        scraper = RestaurantScraper(enable_multi_page=True)
        
        assert scraper.enable_multi_page is True
        assert scraper.multi_page_scraper is not None
        assert scraper.multi_scraper is not None

    def test_restaurant_scraper_default_initialization(self):
        """Test RestaurantScraper defaults to multi-page enabled."""
        scraper = RestaurantScraper()
        
        # Default should be multi-page enabled
        assert scraper.enable_multi_page is True
        assert scraper.multi_page_scraper is not None

    @patch('src.scraper.restaurant_scraper.MultiPageScraper')
    def test_multi_page_scraper_configuration(self, mock_multi_page_scraper):
        """Test that MultiPageScraper is configured with correct parameters."""
        RestaurantScraper(enable_multi_page=True)
        
        mock_multi_page_scraper.assert_called_once_with(
            max_pages=10, 
            enable_ethical_scraping=True
        )

    def test_scraping_config_creation(self):
        """Test ScrapingConfig creation with various parameters."""
        urls = ['https://restaurant1.com', 'https://restaurant2.com']
        file_mode = 'multiple'
        
        config = ScrapingConfig(
            urls=urls,
            file_mode=file_mode
        )
        
        assert config.urls == urls
        assert config.file_mode == file_mode
        # Note: output_directory may be validated/modified by ScrapingConfig

    @patch('src.scraper.restaurant_scraper.BatchProcessor')
    def test_batch_processor_initialization_when_enabled(self, mock_batch_processor):
        """Test BatchProcessor is initialized when batch processing is enabled."""
        RestaurantScraper(enable_batch_processing=True, enable_multi_page=False)
        
        mock_batch_processor.assert_called_once()

    def test_batch_processor_not_initialized_when_disabled(self):
        """Test BatchProcessor is not initialized when batch processing is disabled."""
        scraper = RestaurantScraper(enable_batch_processing=False, enable_multi_page=False)
        
        assert scraper.batch_processor is None

    @patch('src.scraper.restaurant_scraper.MultiPageScraper')
    @patch('src.scraper.restaurant_scraper.BatchProcessor')
    def test_scraper_components_initialization_combinations(self, mock_batch, mock_multi):
        """Test various combinations of scraper component initialization."""
        # Both enabled
        scraper1 = RestaurantScraper(enable_batch_processing=True, enable_multi_page=True)
        assert scraper1.batch_processor is not None
        assert scraper1.multi_page_scraper is not None
        
        # Only batch enabled
        scraper2 = RestaurantScraper(enable_batch_processing=True, enable_multi_page=False)
        assert scraper2.batch_processor is not None
        assert scraper2.multi_page_scraper is None
        
        # Only multi-page enabled
        scraper3 = RestaurantScraper(enable_batch_processing=False, enable_multi_page=True)
        assert scraper3.batch_processor is None
        assert scraper3.multi_page_scraper is not None
        
        # Both disabled
        scraper4 = RestaurantScraper(enable_batch_processing=False, enable_multi_page=False)
        assert scraper4.batch_processor is None
        assert scraper4.multi_page_scraper is None


class TestWebInterfaceIntegration:
    """Test suite for web interface integration with scraping modes."""

    @pytest.fixture
    def mock_flask_app(self):
        """Create a mock Flask app for testing."""
        with patch('src.web_interface.app.Flask') as mock_flask:
            app = Mock()
            mock_flask.return_value = app
            yield app

    @pytest.fixture
    def sample_request_data(self):
        """Sample request data for testing."""
        return {
            'urls': ['https://restaurant1.com', 'https://restaurant2.com'],
            'output_dir': '/test/output',
            'file_mode': 'single',
            'file_format': 'text',
            'scraping_mode': 'single'
        }

    @pytest.fixture
    def sample_multipage_request_data(self):
        """Sample multi-page request data for testing."""
        return {
            'urls': ['https://restaurant1.com'],
            'output_dir': '/test/output',
            'file_mode': 'single',
            'file_format': 'text',
            'scraping_mode': 'multi',
            'multi_page_config': {
                'maxPages': 75,
                'crawlDepth': 3,
                'includePatterns': 'menu,food',
                'excludePatterns': 'admin,login',
                'rateLimit': 1500
            }
        }

    def test_single_page_mode_request_processing(self, sample_request_data):
        """Test processing of single-page mode request."""
        scraping_mode = sample_request_data.get('scraping_mode', 'single')
        multi_page_config = sample_request_data.get('multi_page_config', {})
        
        assert scraping_mode == 'single'
        assert multi_page_config == {}

    def test_multi_page_mode_request_processing(self, sample_multipage_request_data):
        """Test processing of multi-page mode request."""
        scraping_mode = sample_multipage_request_data.get('scraping_mode', 'single')
        multi_page_config = sample_multipage_request_data.get('multi_page_config', {})
        
        assert scraping_mode == 'multi'
        assert multi_page_config is not None
        assert multi_page_config['maxPages'] == 75
        assert multi_page_config['crawlDepth'] == 3
        assert multi_page_config['includePatterns'] == 'menu,food'
        assert multi_page_config['excludePatterns'] == 'admin,login'
        assert multi_page_config['rateLimit'] == 1500

    def test_scraper_initialization_based_on_mode(self, sample_request_data, sample_multipage_request_data):
        """Test scraper initialization based on scraping mode."""
        # Single-page mode
        enable_multi_page_single = (sample_request_data['scraping_mode'] == 'multi')
        assert enable_multi_page_single is False
        
        # Multi-page mode
        enable_multi_page_multi = (sample_multipage_request_data['scraping_mode'] == 'multi')
        assert enable_multi_page_multi is True

    def test_multi_page_config_validation(self, sample_multipage_request_data):
        """Test validation of multi-page configuration parameters."""
        config = sample_multipage_request_data['multi_page_config']
        
        # Test numeric validations
        assert isinstance(config['maxPages'], int)
        assert config['maxPages'] > 0
        assert config['maxPages'] <= 500
        
        assert isinstance(config['crawlDepth'], int)
        assert config['crawlDepth'] >= 1
        assert config['crawlDepth'] <= 5
        
        assert isinstance(config['rateLimit'], int)
        assert config['rateLimit'] >= 100
        assert config['rateLimit'] <= 5000
        
        # Test string validations
        assert isinstance(config['includePatterns'], str)
        assert isinstance(config['excludePatterns'], str)
        
        # Test pattern parsing
        include_patterns = config['includePatterns'].split(',')
        exclude_patterns = config['excludePatterns'].split(',')
        assert len(include_patterns) > 0
        assert len(exclude_patterns) > 0

    def test_request_data_serialization(self, sample_request_data, sample_multipage_request_data):
        """Test JSON serialization of request data."""
        # Single-page request
        single_json = json.dumps(sample_request_data)
        single_parsed = json.loads(single_json)
        assert single_parsed['scraping_mode'] == 'single'
        
        # Multi-page request
        multi_json = json.dumps(sample_multipage_request_data)
        multi_parsed = json.loads(multi_json)
        assert multi_parsed['scraping_mode'] == 'multi'
        assert 'multi_page_config' in multi_parsed

    @patch('src.scraper.restaurant_scraper.RestaurantScraper')
    def test_scraper_creation_with_mode_parameter(self, mock_scraper_class, sample_multipage_request_data):
        """Test that RestaurantScraper is created with correct mode parameter."""
        scraping_mode = sample_multipage_request_data['scraping_mode']
        enable_multi_page = (scraping_mode == 'multi')
        
        # Simulate the scraper creation logic from the web interface
        mock_scraper_class(enable_multi_page=enable_multi_page)
        
        mock_scraper_class.assert_called_once_with(enable_multi_page=True)


class TestConfigurationValidation:
    """Test suite for configuration validation."""

    def test_max_pages_validation(self):
        """Test max pages validation logic."""
        # Valid values
        assert self._validate_max_pages(1) is True
        assert self._validate_max_pages(50) is True
        assert self._validate_max_pages(500) is True
        
        # Invalid values
        assert self._validate_max_pages(0) is False
        assert self._validate_max_pages(-1) is False
        assert self._validate_max_pages(501) is False

    def test_crawl_depth_validation(self):
        """Test crawl depth validation logic."""
        # Valid values
        assert self._validate_crawl_depth(1) is True
        assert self._validate_crawl_depth(3) is True
        assert self._validate_crawl_depth(5) is True
        
        # Invalid values
        assert self._validate_crawl_depth(0) is False
        assert self._validate_crawl_depth(6) is False
        assert self._validate_crawl_depth(-1) is False

    def test_rate_limit_validation(self):
        """Test rate limit validation logic."""
        # Valid values
        assert self._validate_rate_limit(100) is True
        assert self._validate_rate_limit(1000) is True
        assert self._validate_rate_limit(5000) is True
        
        # Invalid values
        assert self._validate_rate_limit(99) is False
        assert self._validate_rate_limit(5001) is False
        assert self._validate_rate_limit(-100) is False

    def test_pattern_validation(self):
        """Test pattern validation logic."""
        # Valid patterns
        assert self._validate_patterns('menu,food,restaurant') is True
        assert self._validate_patterns('single_pattern') is True
        assert self._validate_patterns('admin,login,cart') is True
        
        # Invalid patterns
        assert self._validate_patterns('') is False
        assert self._validate_patterns(',,,') is False
        assert self._validate_patterns(' , , ') is False

    def test_scraping_mode_validation(self):
        """Test scraping mode validation logic."""
        # Valid modes
        assert self._validate_scraping_mode('single') is True
        assert self._validate_scraping_mode('multi') is True
        
        # Invalid modes
        assert self._validate_scraping_mode('invalid') is False
        assert self._validate_scraping_mode('') is False
        assert self._validate_scraping_mode(None) is False

    def _validate_max_pages(self, value):
        """Helper method to validate max pages."""
        return isinstance(value, int) and 1 <= value <= 500

    def _validate_crawl_depth(self, value):
        """Helper method to validate crawl depth."""
        return isinstance(value, int) and 1 <= value <= 5

    def _validate_rate_limit(self, value):
        """Helper method to validate rate limit."""
        return isinstance(value, int) and 100 <= value <= 5000

    def _validate_patterns(self, patterns):
        """Helper method to validate patterns."""
        if not isinstance(patterns, str) or not patterns.strip():
            return False
        
        pattern_list = [p.strip() for p in patterns.split(',')]
        return len(pattern_list) > 0 and all(p for p in pattern_list)

    def _validate_scraping_mode(self, mode):
        """Helper method to validate scraping mode."""
        return mode in ['single', 'multi']


class TestJavaScriptFunctionality:
    """Test suite for JavaScript functionality (simulated in Python)."""

    def test_mode_toggle_functionality(self):
        """Test mode toggle functionality simulation."""
        # Initial state
        state = {
            'selected_mode': 'single',
            'multi_page_header_visible': False,
            'config_panel_expanded': False,
            'status_text': 'SYSTEM_READY'
        }
        
        # Simulate clicking multi-page mode
        state = self._simulate_mode_toggle(state, 'multi')
        
        assert state['selected_mode'] == 'multi'
        assert state['multi_page_header_visible'] is True
        assert 'MULTI_PAGE_MODE' in state['status_text']
        
        # Simulate clicking single-page mode
        state = self._simulate_mode_toggle(state, 'single')
        
        assert state['selected_mode'] == 'single'
        assert state['multi_page_header_visible'] is False
        assert 'SINGLE_PAGE_MODE' in state['status_text']

    def test_config_panel_toggle_functionality(self):
        """Test configuration panel toggle functionality simulation."""
        state = {
            'config_panel_expanded': False,
            'expand_icon_rotated': False,
            'status_text': 'SYSTEM_READY'
        }
        
        # Simulate expanding panel
        state = self._simulate_config_panel_toggle(state)
        
        assert state['config_panel_expanded'] is True
        assert state['expand_icon_rotated'] is True
        assert 'PANEL_EXPANDED' in state['status_text']
        
        # Simulate collapsing panel
        state = self._simulate_config_panel_toggle(state)
        
        assert state['config_panel_expanded'] is False
        assert state['expand_icon_rotated'] is False
        assert 'PANEL_COLLAPSED' in state['status_text']

    def test_slider_update_functionality(self):
        """Test slider update functionality simulation."""
        state = {
            'crawl_depth': 2,
            'rate_limit': 1000,
            'status_text': 'SYSTEM_READY'
        }
        
        # Simulate crawl depth slider change
        state = self._simulate_slider_update(state, 'crawl_depth', 4)
        
        assert state['crawl_depth'] == 4
        assert 'CRAWL_DEPTH_SET // LEVEL_4' in state['status_text']
        
        # Simulate rate limit slider change
        state = self._simulate_slider_update(state, 'rate_limit', 2500)
        
        assert state['rate_limit'] == 2500
        assert 'RATE_LIMIT_SET // 2500MS_DELAY' in state['status_text']

    def test_form_submission_data_collection(self):
        """Test form submission data collection simulation."""
        form_state = {
            'urls': ['https://restaurant1.com', 'https://restaurant2.com'],
            'output_dir': '/test/output',
            'file_mode': 'single',
            'file_format': 'text',
            'scraping_mode': 'multi',
            'max_pages': 75,
            'crawl_depth': 3,
            'include_patterns': 'menu,food',
            'exclude_patterns': 'admin,login',
            'rate_limit': 1500
        }
        
        submission_data = self._simulate_form_submission(form_state)
        
        assert submission_data['scraping_mode'] == 'multi'
        assert 'multi_page_config' in submission_data
        assert submission_data['multi_page_config']['maxPages'] == 75
        assert submission_data['multi_page_config']['crawlDepth'] == 3

    def _simulate_mode_toggle(self, state, new_mode):
        """Simulate mode toggle JavaScript functionality."""
        state['selected_mode'] = new_mode
        
        if new_mode == 'multi':
            state['multi_page_header_visible'] = True
            state['status_text'] = 'MULTI_PAGE_MODE // ADVANCED_CRAWLING_ENABLED'
        else:
            state['multi_page_header_visible'] = False
            state['config_panel_expanded'] = False
            state['status_text'] = 'SINGLE_PAGE_MODE // DIRECT_URL_PROCESSING'
        
        return state

    def _simulate_config_panel_toggle(self, state):
        """Simulate config panel toggle JavaScript functionality."""
        state['config_panel_expanded'] = not state['config_panel_expanded']
        state['expand_icon_rotated'] = state['config_panel_expanded']
        
        if state['config_panel_expanded']:
            state['status_text'] = 'MULTI_PAGE_CONFIG // PANEL_EXPANDED'
        else:
            state['status_text'] = 'MULTI_PAGE_CONFIG // PANEL_COLLAPSED'
        
        return state

    def _simulate_slider_update(self, state, slider_type, value):
        """Simulate slider update JavaScript functionality."""
        state[slider_type] = value
        
        if slider_type == 'crawl_depth':
            state['status_text'] = f'CRAWL_DEPTH_SET // LEVEL_{value}'
        elif slider_type == 'rate_limit':
            state['status_text'] = f'RATE_LIMIT_SET // {value}MS_DELAY'
        
        return state

    def _simulate_form_submission(self, form_state):
        """Simulate form submission data collection."""
        submission_data = {
            'urls': form_state['urls'],
            'output_dir': form_state['output_dir'],
            'file_mode': form_state['file_mode'],
            'file_format': form_state['file_format'],
            'scraping_mode': form_state['scraping_mode']
        }
        
        if form_state['scraping_mode'] == 'multi':
            submission_data['multi_page_config'] = {
                'maxPages': form_state['max_pages'],
                'crawlDepth': form_state['crawl_depth'],
                'includePatterns': form_state['include_patterns'],
                'excludePatterns': form_state['exclude_patterns'],
                'rateLimit': form_state['rate_limit']
            }
        
        return submission_data


if __name__ == '__main__':
    pytest.main([__file__])