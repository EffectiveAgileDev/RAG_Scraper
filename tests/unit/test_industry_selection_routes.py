"""Unit tests for industry selection routes and validation."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import session
import json


class TestIndustrySelectionRoutes:
    """Test cases for industry selection routes."""

    @pytest.fixture
    def app(self):
        """Create test Flask app."""
        from src.web_interface.app import create_app
        app = create_app(testing=True)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    def test_get_industries_endpoint_returns_industry_list(self, client):
        """Test that /api/industries endpoint returns list of industries."""
        with patch('src.web_interface.api_routes.IndustryConfig') as mock_config:
            mock_instance = Mock()
            mock_instance.get_industry_list.return_value = [
                "Restaurant", "Real Estate", "Medical"
            ]
            mock_config.return_value = mock_instance
            
            response = client.get('/api/industries')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
            assert len(data) == 3
            assert "Restaurant" in data

    def test_get_industry_help_returns_help_text(self, client):
        """Test that /api/industry-help endpoint returns help text for selected industry."""
        with patch('src.web_interface.api_routes.IndustryConfig') as mock_config:
            mock_instance = Mock()
            mock_instance.get_help_text.return_value = "Test help text"
            mock_config.return_value = mock_instance
            
            with patch('src.web_interface.api_routes.IndustrySessionManager') as mock_session:
                mock_session_instance = Mock()
                mock_session_instance.get_industry.return_value = "Restaurant"
                mock_session.return_value = mock_session_instance
                
                response = client.get('/api/industry-help')
                
                assert response.status_code == 200
                assert b"Test help text" in response.data

    def test_get_industry_help_returns_empty_when_no_industry_selected(self, client):
        """Test that /api/industry-help returns empty when no industry is selected."""
        with patch('src.web_interface.api_routes.IndustrySessionManager') as mock_session:
            mock_session_instance = Mock()
            mock_session_instance.get_industry.return_value = None
            mock_session.return_value = mock_session_instance
            
            response = client.get('/api/industry-help')
            
            assert response.status_code == 200
            assert response.data == b""

    def test_clear_industry_endpoint_clears_session(self, client):
        """Test that /api/clear-industry endpoint clears the industry from session."""
        with patch('src.web_interface.api_routes.IndustrySessionManager') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value = mock_session_instance
            
            response = client.post('/api/clear-industry')
            
            assert response.status_code == 200
            mock_session_instance.clear_industry.assert_called_once()

    def test_scrape_validates_industry_selection(self, client):
        """Test that /scrape endpoint validates industry selection."""
        response = client.post('/scrape', data={
            'url': 'https://example.com'
        })
        
        assert response.status_code == 400
        assert b"Please select an industry before scraping" in response.data

    def test_scrape_accepts_request_with_valid_industry(self, client):
        """Test that /scrape endpoint accepts request with valid industry."""
        with patch('src.config.industry_config.IndustryConfig') as mock_config:
            mock_instance = Mock()
            mock_instance.validate_industry.return_value = True
            mock_config.return_value = mock_instance
            
            response = client.post('/scrape', data={
                'url': 'https://example.com',
                'industry': 'Restaurant'
            })
            
            # Should not get validation error (might get other errors)
            assert b"Please select an industry before scraping" not in response.data

    def test_scrape_stores_industry_in_session(self, client):
        """Test that /scrape endpoint stores selected industry in session."""
        with patch('src.config.industry_config.IndustryConfig') as mock_config:
            mock_instance = Mock()
            mock_instance.validate_industry.return_value = True
            mock_config.return_value = mock_instance
            
            with patch('src.web_interface.api_routes.RestaurantScraper'):
                client.post('/scrape', data={
                    'url': 'https://example.com',
                    'industry': 'Restaurant'
                })
            
            with client.session_transaction() as sess:
                assert sess.get('industry') == 'Restaurant'

    def test_scrape_batch_validates_industry_selection(self, client):
        """Test that /scrape/batch endpoint validates industry selection."""
        response = client.post('/scrape/batch', data={
            'urls': 'https://example1.com\nhttps://example2.com'
        })
        
        assert response.status_code == 400
        assert b"Please select an industry before scraping" in response.data

    def test_scrape_batch_uses_session_industry(self, client):
        """Test that /scrape/batch uses industry from session if not provided."""
        with patch('src.config.industry_config.IndustryConfig') as mock_config:
            mock_instance = Mock()
            mock_instance.validate_industry.return_value = True
            mock_config.return_value = mock_instance
            
            with client.session_transaction() as sess:
                sess['industry'] = 'Restaurant'
            
            response = client.post('/scrape/batch', data={
                'urls': 'https://example1.com\nhttps://example2.com'
            })
            
            # Should not get validation error
            assert b"Please select an industry before scraping" not in response.data

    def test_homepage_displays_industry_dropdown(self, client):
        """Test that homepage includes industry dropdown."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'<select' in response.data
        assert b'industry' in response.data
        assert b'Select an industry...' in response.data

    def test_homepage_shows_selected_industry_from_session(self, client):
        """Test that homepage shows previously selected industry from session."""
        with client.session_transaction() as sess:
            sess['industry'] = 'Restaurant'
        
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'value="Restaurant" selected' in response.data

    def test_industry_dropdown_is_required_field(self, client):
        """Test that industry dropdown has required attribute."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'required' in response.data
        assert b'<select' in response.data
        assert b'name="industry"' in response.data


class TestIndustryValidator:
    """Test cases for industry validation logic."""

    def test_validate_industry_form_data_missing_industry(self):
        """Test validation when industry is missing from form data."""
        from src.web_interface.validators import validate_industry_selection
        
        form_data = {'url': 'https://example.com'}
        is_valid, error_message = validate_industry_selection(form_data)
        
        assert is_valid is False
        assert error_message == "Please select an industry before scraping"

    def test_validate_industry_form_data_empty_industry(self):
        """Test validation when industry is empty string."""
        from src.web_interface.validators import validate_industry_selection
        
        form_data = {'url': 'https://example.com', 'industry': ''}
        is_valid, error_message = validate_industry_selection(form_data)
        
        assert is_valid is False
        assert error_message == "Please select an industry before scraping"

    def test_validate_industry_form_data_invalid_industry(self):
        """Test validation when industry is not in the allowed list."""
        from src.web_interface.validators import validate_industry_selection
        
        with patch('src.config.industry_config.IndustryConfig') as mock_config:
            mock_instance = Mock()
            mock_instance.validate_industry.return_value = False
            mock_config.return_value = mock_instance
            
            form_data = {'url': 'https://example.com', 'industry': 'InvalidIndustry'}
            is_valid, error_message = validate_industry_selection(form_data)
            
            assert is_valid is False
            assert error_message == "Invalid industry selected"

    def test_validate_industry_form_data_valid_industry(self):
        """Test validation when industry is valid."""
        from src.web_interface.validators import validate_industry_selection
        
        with patch('src.config.industry_config.IndustryConfig') as mock_config:
            mock_instance = Mock()
            mock_instance.validate_industry.return_value = True
            mock_config.return_value = mock_instance
            
            form_data = {'url': 'https://example.com', 'industry': 'Restaurant'}
            is_valid, error_message = validate_industry_selection(form_data)
            
            assert is_valid is True
            assert error_message is None


class TestIndustryExtractorFactory:
    """Test cases for industry-specific extractor factory."""

    def test_get_extractor_for_restaurant_industry(self):
        """Test that factory returns RestaurantScraper for Restaurant industry."""
        from src.scraper.industry_extractor_factory import get_industry_extractor
        
        extractor = get_industry_extractor("Restaurant")
        
        assert extractor is not None
        assert extractor.__class__.__name__ == "RestaurantScraper"

    def test_get_extractor_for_real_estate_industry(self):
        """Test that factory returns RealEstateScraper for Real Estate industry."""
        from src.scraper.industry_extractor_factory import get_industry_extractor
        
        extractor = get_industry_extractor("Real Estate")
        
        assert extractor is not None
        assert extractor.__class__.__name__ == "RealEstateScraper"

    def test_get_extractor_for_medical_industry(self):
        """Test that factory returns MedicalScraper for Medical industry."""
        from src.scraper.industry_extractor_factory import get_industry_extractor
        
        extractor = get_industry_extractor("Medical")
        
        assert extractor is not None
        assert extractor.__class__.__name__ == "MedicalScraper"

    def test_get_extractor_returns_none_for_invalid_industry(self):
        """Test that factory returns None for invalid industry."""
        from src.scraper.industry_extractor_factory import get_industry_extractor
        
        extractor = get_industry_extractor("InvalidIndustry")
        
        assert extractor is None

    def test_get_extractor_uses_config_for_class_name(self):
        """Test that factory uses IndustryConfig to get extractor class name."""
        from src.scraper.industry_extractor_factory import get_industry_extractor
        
        with patch('src.scraper.industry_extractor_factory.IndustryConfig') as mock_config:
            mock_instance = Mock()
            mock_instance.get_extractor_class.return_value = "CustomScraper"
            mock_config.return_value = mock_instance
            
            with patch('src.scraper.industry_extractor_factory.import_module') as mock_import:
                mock_module = Mock()
                mock_class = Mock()
                setattr(mock_module, "CustomScraper", mock_class)
                mock_import.return_value = mock_module
                
                extractor = get_industry_extractor("CustomIndustry")
                
                mock_instance.get_extractor_class.assert_called_with("CustomIndustry")
                assert extractor == mock_class()