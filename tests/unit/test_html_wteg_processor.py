"""Unit tests for HTML WTEG processor."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import the modules we'll be testing
try:
    from src.processors.html_wteg_processor import HTMLWTEGProcessor
except ImportError:
    HTMLWTEGProcessor = None

try:
    from src.wteg.wteg_schema import WTEGRestaurantData, WTEGLocation, WTEGMenuItem, WTEGServices, WTEGContactInfo
except ImportError:
    WTEGRestaurantData = None
    WTEGLocation = None
    WTEGMenuItem = None
    WTEGServices = None
    WTEGContactInfo = None


class TestHTMLWTEGProcessor:
    """Test cases for HTMLWTEGProcessor."""

    @pytest.fixture
    def sample_html_content(self):
        """Sample HTML content for testing."""
        return """
        <html>
        <head>
            <title>Mario's Italian Restaurant</title>
        </head>
        <body>
            <h1>MARIO'S ITALIAN RESTAURANT</h1>
            <p>123 Main Street, Portland, OR 97201</p>
            <p>Phone: (503) 555-0123</p>
            <p>Email: info@marios.com</p>
            
            <h2>APPETIZERS</h2>
            <ul>
                <li>Bruschetta - $8.99</li>
                <li>Garlic Bread - $5.99</li>
            </ul>
            
            <h2>MAIN COURSES</h2>
            <ul>
                <li>Spaghetti Carbonara - $16.99</li>
                <li>Chicken Parmigiana - $18.99</li>
            </ul>
            
            <h2>SERVICES</h2>
            <p>Delivery Available</p>
            <p>Takeout Available</p>
        </body>
        </html>
        """

    @pytest.fixture
    def sample_url(self):
        """Sample URL for testing."""
        return "https://example.com/restaurant"

    @pytest.fixture
    def html_wteg_processor(self):
        """Create HTMLWTEGProcessor instance."""
        if HTMLWTEGProcessor is None:
            pytest.skip("HTMLWTEGProcessor not implemented yet")
        return HTMLWTEGProcessor()

    @pytest.fixture
    def mock_content_extractor(self):
        """Mock content extractor."""
        mock = Mock()
        mock.extract_content.return_value = "Extracted text content"
        mock.validate_source.return_value = True
        return mock

    @pytest.fixture
    def mock_pattern_recognizer(self):
        """Mock pattern recognizer."""
        mock = Mock()
        mock.recognize_patterns.return_value = {
            'restaurant_name': 'MARIO\'S ITALIAN RESTAURANT',
            'address': '123 Main Street, Portland, OR 97201',
            'phone': '(503) 555-0123',
            'email': 'info@marios.com',
            'website': 'www.marios.com',
            'cuisine_type': 'Italian',
            'prices': ['$8.99', '$16.99'],
            'menu_items': ['Bruschetta', 'Spaghetti Carbonara'],
            'hours': 'Monday-Thursday: 11:00 AM - 9:00 PM',
            'services': ['Delivery Available', 'Takeout Available'],
            'social_media': ['@marios'],
            'confidence_scores': {'restaurant_name': 0.9, 'address': 0.85, 'phone': 0.9}
        }
        mock.get_supported_patterns.return_value = ['restaurant_name', 'address', 'phone', 'email']
        return mock

    @pytest.fixture
    def mock_menu_section_identifier(self):
        """Mock menu section identifier."""
        mock = Mock()
        mock.identify_menu_sections.return_value = [
            {
                'name': 'APPETIZERS',
                'items': [
                    {'name': 'Bruschetta', 'price': '$8.99'},
                    {'name': 'Garlic Bread', 'price': '$5.99'}
                ],
                'confidence': 0.9
            },
            {
                'name': 'MAIN COURSES',
                'items': [
                    {'name': 'Spaghetti Carbonara', 'price': '$16.99'},
                    {'name': 'Chicken Parmigiana', 'price': '$18.99'}
                ],
                'confidence': 0.9
            }
        ]
        return mock

    @pytest.fixture
    def mock_service_extractor(self):
        """Mock service extractor."""
        if WTEGServices is None:
            pytest.skip("WTEGServices not available")
        
        mock = Mock()
        mock_services = WTEGServices()
        mock_services.delivery_available = True
        mock_services.takeout_available = True
        mock_services.catering_available = False
        mock_services.reservations_accepted = False
        mock.extract_services_from_text.return_value = mock_services
        return mock

    def test_html_wteg_processor_initialization(self):
        """Test HTMLWTEGProcessor initializes correctly."""
        if HTMLWTEGProcessor is None:
            pytest.skip("HTMLWTEGProcessor not implemented yet")
        
        processor = HTMLWTEGProcessor()
        assert processor is not None
        assert hasattr(processor, 'process_to_wteg_schema')
        assert hasattr(processor, 'process_url_to_wteg_schema')
        assert hasattr(processor, 'process_html_to_wteg_schema')
        assert processor.content_extractor is not None
        assert processor.pattern_recognizer is not None
        assert processor.menu_section_identifier is not None
        assert processor.service_extractor is not None

    def test_create_component_instances(self, html_wteg_processor):
        """Test creation of component instances."""
        # Test that all components are created
        assert html_wteg_processor.content_extractor is not None
        assert html_wteg_processor.pattern_recognizer is not None
        assert html_wteg_processor.menu_section_identifier is not None
        assert html_wteg_processor.hours_parser is not None
        assert html_wteg_processor.service_extractor is not None
        
        # Test that components have expected methods
        assert hasattr(html_wteg_processor.content_extractor, 'extract_content')
        assert hasattr(html_wteg_processor.pattern_recognizer, 'recognize_patterns')
        assert hasattr(html_wteg_processor.menu_section_identifier, 'identify_menu_sections')
        assert hasattr(html_wteg_processor.service_extractor, 'extract_services_from_text')

    @patch('src.processors.html_wteg_processor.HTMLContentExtractor')
    @patch('src.processors.html_wteg_processor.HTMLPatternRecognizer')
    @patch('src.processors.html_wteg_processor.MenuSectionIdentifier')
    @patch('src.processors.html_wteg_processor.ServiceExtractor')
    def test_process_html_to_wteg_schema(self, mock_service_extractor, mock_menu_identifier, 
                                        mock_pattern_recognizer, mock_content_extractor, 
                                        sample_html_content):
        """Test processing HTML content to WTEG schema."""
        if HTMLWTEGProcessor is None or WTEGRestaurantData is None:
            pytest.skip("Required classes not available")
        
        # Setup mocks
        mock_content_extractor.return_value.extract_content.return_value = "Extracted content"
        mock_pattern_recognizer.return_value.recognize_patterns.return_value = {
            'restaurant_name': 'MARIO\'S ITALIAN RESTAURANT',
            'address': '123 Main Street, Portland, OR 97201',
            'phone': '(503) 555-0123',
            'cuisine_type': 'Italian',
            'website': 'www.marios.com'
        }
        mock_menu_identifier.return_value.identify_menu_sections.return_value = [
            {
                'name': 'APPETIZERS',
                'items': [{'name': 'Bruschetta', 'price': '$8.99'}]
            }
        ]
        mock_services = WTEGServices()
        mock_services.delivery_available = True
        mock_service_extractor.return_value.extract_services_from_text.return_value = mock_services
        
        processor = HTMLWTEGProcessor()
        result = processor.process_html_to_wteg_schema(sample_html_content, "test.html")
        
        assert isinstance(result, WTEGRestaurantData)
        assert result.extraction_method == "HTML_WTEG_PROCESSING"
        assert result.source_url == "test.html"
        assert result.brief_description == 'MARIO\'S ITALIAN RESTAURANT'
        assert result.cuisine == 'Italian'

    @patch('requests.Session.get')
    def test_process_url_to_wteg_schema(self, mock_get, html_wteg_processor, sample_html_content):
        """Test processing URL to WTEG schema."""
        if WTEGRestaurantData is None:
            pytest.skip("WTEGRestaurantData not available")
        
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.text = sample_html_content
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        url = "https://example.com/restaurant"
        result = html_wteg_processor.process_url_to_wteg_schema(url)
        
        assert isinstance(result, WTEGRestaurantData)
        assert result.extraction_method == "HTML_WTEG_PROCESSING"
        assert result.source_url == url

    def test_process_to_wteg_schema_with_html_content(self, html_wteg_processor, sample_html_content):
        """Test generic processing to WTEG schema with HTML content."""
        if WTEGRestaurantData is None:
            pytest.skip("WTEGRestaurantData not available")
        
        result = html_wteg_processor.process_to_wteg_schema(sample_html_content, "test.html")
        
        assert isinstance(result, WTEGRestaurantData)
        assert result.extraction_method == "HTML_WTEG_PROCESSING"
        assert result.source_url == "test.html"

    @patch('requests.Session.get')
    def test_process_to_wteg_schema_with_url(self, mock_get, html_wteg_processor, sample_html_content):
        """Test generic processing to WTEG schema with URL."""
        if WTEGRestaurantData is None:
            pytest.skip("WTEGRestaurantData not available")
        
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.text = sample_html_content
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        url = "https://example.com/restaurant"
        result = html_wteg_processor.process_to_wteg_schema(url, url)
        
        assert isinstance(result, WTEGRestaurantData)
        assert result.extraction_method == "HTML_WTEG_PROCESSING"
        assert result.source_url == url

    def test_extract_structured_data(self, html_wteg_processor, sample_html_content):
        """Test extraction of structured data."""
        result = html_wteg_processor.extract_structured_data(sample_html_content, "test.html")
        
        assert isinstance(result, dict)
        assert 'text_content' in result
        # May contain additional structured data fields

    def test_process_multiple_restaurants(self, html_wteg_processor, sample_html_content):
        """Test processing multiple restaurants."""
        if WTEGRestaurantData is None:
            pytest.skip("WTEGRestaurantData not available")
        
        results = html_wteg_processor.process_multiple_restaurants(sample_html_content, "test.html")
        
        assert isinstance(results, list)
        assert len(results) == 1  # Currently treats as single restaurant
        assert isinstance(results[0], WTEGRestaurantData)

    def test_validate_html_source(self, html_wteg_processor, sample_html_content):
        """Test HTML source validation."""
        # Valid HTML content
        assert html_wteg_processor.validate_html_source(sample_html_content)
        
        # Valid URL
        assert html_wteg_processor.validate_html_source("https://example.com")
        
        # Invalid source
        assert not html_wteg_processor.validate_html_source("not html or url")

    def test_get_extraction_capabilities(self, html_wteg_processor):
        """Test getting extraction capabilities."""
        capabilities = html_wteg_processor.get_extraction_capabilities()
        
        assert isinstance(capabilities, dict)
        assert 'supported_sources' in capabilities
        assert 'supported_patterns' in capabilities
        assert 'extraction_method' in capabilities
        
        assert 'URL' in capabilities['supported_sources']
        assert 'HTML content' in capabilities['supported_sources']
        assert capabilities['extraction_method'] == 'HTML_WTEG_PROCESSING'
        assert capabilities['can_extract_structured_data'] is True

    def test_location_creation_from_patterns(self, html_wteg_processor):
        """Test creation of location object from patterns."""
        if WTEGLocation is None:
            pytest.skip("WTEGLocation not available")
        
        patterns = {
            'address': '123 Main Street, Portland, OR 97201'
        }
        
        location = html_wteg_processor._create_location_from_patterns(patterns)
        
        assert isinstance(location, WTEGLocation)
        assert location.street_address == '123 Main Street'
        assert location.city == 'Portland'
        assert location.state == 'OR'
        assert location.zip_code == '97201'

    def test_contact_creation_from_patterns(self, html_wteg_processor):
        """Test creation of contact object from patterns."""
        if WTEGContactInfo is None:
            pytest.skip("WTEGContactInfo not available")
        
        patterns = {
            'phone': '(503) 555-0123'
        }
        
        contact = html_wteg_processor._create_contact_from_patterns(patterns)
        
        assert isinstance(contact, WTEGContactInfo)
        assert contact.primary_phone == '(503) 555-0123'
        assert contact.formatted_display == '(503) 555-0123'

    def test_menu_items_creation_from_sections(self, html_wteg_processor):
        """Test creation of menu items from sections."""
        if WTEGMenuItem is None:
            pytest.skip("WTEGMenuItem not available")
        
        menu_sections = [
            {
                'name': 'APPETIZERS',
                'items': [
                    {'name': 'Bruschetta', 'price': '$8.99'},
                    {'name': 'Garlic Bread', 'price': '$5.99'}
                ]
            }
        ]
        
        menu_items = html_wteg_processor._create_menu_items_from_sections(menu_sections)
        
        assert isinstance(menu_items, list)
        assert len(menu_items) == 2
        assert all(isinstance(item, WTEGMenuItem) for item in menu_items)
        assert menu_items[0].item_name == 'Bruschetta'
        assert menu_items[0].price == '$8.99'
        assert menu_items[0].category == 'APPETIZERS'

    def test_confidence_score_calculation(self, html_wteg_processor):
        """Test confidence score calculation."""
        if WTEGServices is None:
            pytest.skip("WTEGServices not available")
        
        patterns = {
            'restaurant_name': 'Test Restaurant',
            'address': '123 Test St',
            'phone': '555-0123',
            'cuisine_type': 'Italian',
            'website': 'test.com'
        }
        
        menu_sections = [
            {'name': 'APPETIZERS', 'items': [{'name': 'Test Item', 'price': '$9.99'}]}
        ]
        
        services = WTEGServices()
        services.delivery_available = True
        
        score = html_wteg_processor._calculate_confidence_score(patterns, menu_sections, services)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be relatively high with good data

    def test_parse_address_components(self, html_wteg_processor):
        """Test parsing address components."""
        # Standard format
        address = "123 Main Street, Portland, OR 97201"
        components = html_wteg_processor._parse_address_components(address)
        
        assert components['street'] == '123 Main Street'
        assert components['city'] == 'Portland'
        assert components['state'] == 'OR'
        assert components['zip_code'] == '97201'
        
        # Fallback format
        address = "123 Main Street"
        components = html_wteg_processor._parse_address_components(address)
        
        assert components['street'] == '123 Main Street'
        assert components['city'] == ''
        assert components['state'] == ''
        assert components['zip_code'] == ''

    def test_error_handling_invalid_source(self, html_wteg_processor):
        """Test error handling with invalid source."""
        with pytest.raises(ValueError):
            html_wteg_processor.process_to_wteg_schema("invalid source", "test")

    @patch('requests.Session.get')
    def test_error_handling_network_failure(self, mock_get, html_wteg_processor):
        """Test error handling with network failure."""
        import requests
        mock_get.side_effect = requests.RequestException("Network error")
        
        with pytest.raises(requests.RequestException):
            html_wteg_processor.process_url_to_wteg_schema("https://example.com")

    def test_wteg_restaurant_data_fields(self, html_wteg_processor, sample_html_content):
        """Test that WTEG restaurant data has all required fields."""
        if WTEGRestaurantData is None:
            pytest.skip("WTEGRestaurantData not available")
        
        result = html_wteg_processor.process_html_to_wteg_schema(sample_html_content, "test.html")
        
        # Test required fields
        assert hasattr(result, 'brief_description')
        assert hasattr(result, 'cuisine')
        assert hasattr(result, 'source_url')
        assert hasattr(result, 'extraction_timestamp')
        assert hasattr(result, 'extraction_method')
        assert hasattr(result, 'location')
        assert hasattr(result, 'click_to_call')
        assert hasattr(result, 'menu_items')
        assert hasattr(result, 'services_offered')
        assert hasattr(result, 'confidence_score')
        
        # Test that extraction_timestamp is set
        assert result.extraction_timestamp is not None
        assert result.extraction_timestamp != ""