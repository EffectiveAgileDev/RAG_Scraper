"""Unit tests for industry session management."""
import pytest
from unittest.mock import Mock, patch
from flask import Flask, session


class TestIndustrySessionManager:
    """Test cases for IndustrySessionManager class."""

    @pytest.fixture
    def app(self):
        """Create test Flask app."""
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['TESTING'] = True
        return app

    def test_store_industry_in_session(self, app):
        """Test storing industry in session."""
        from src.web_interface.session_manager import IndustrySessionManager
        
        with app.test_request_context():
            manager = IndustrySessionManager()
            manager.store_industry("Restaurant")
            
            assert session.get('industry') == "Restaurant"
            assert session.get('industry_timestamp') is not None

    def test_get_industry_from_session(self, app):
        """Test retrieving industry from session."""
        from src.web_interface.session_manager import IndustrySessionManager
        
        with app.test_request_context():
            session['industry'] = "Medical"
            
            manager = IndustrySessionManager()
            industry = manager.get_industry()
            
            assert industry == "Medical"

    def test_get_industry_returns_none_when_not_set(self, app):
        """Test get_industry returns None when no industry in session."""
        from src.web_interface.session_manager import IndustrySessionManager
        
        with app.test_request_context():
            manager = IndustrySessionManager()
            industry = manager.get_industry()
            
            assert industry is None

    def test_clear_industry_from_session(self, app):
        """Test clearing industry from session."""
        from src.web_interface.session_manager import IndustrySessionManager
        
        with app.test_request_context():
            session['industry'] = "Restaurant"
            session['industry_timestamp'] = "2024-01-01"
            
            manager = IndustrySessionManager()
            manager.clear_industry()
            
            assert 'industry' not in session
            assert 'industry_timestamp' not in session

    def test_has_industry_returns_true_when_set(self, app):
        """Test has_industry returns True when industry is in session."""
        from src.web_interface.session_manager import IndustrySessionManager
        
        with app.test_request_context():
            session['industry'] = "Real Estate"
            
            manager = IndustrySessionManager()
            
            assert manager.has_industry() is True

    def test_has_industry_returns_false_when_not_set(self, app):
        """Test has_industry returns False when no industry in session."""
        from src.web_interface.session_manager import IndustrySessionManager
        
        with app.test_request_context():
            manager = IndustrySessionManager()
            
            assert manager.has_industry() is False

    def test_update_industry_changes_existing_value(self, app):
        """Test updating existing industry value in session."""
        from src.web_interface.session_manager import IndustrySessionManager
        
        with app.test_request_context():
            session['industry'] = "Restaurant"
            old_timestamp = "2024-01-01"
            session['industry_timestamp'] = old_timestamp
            
            manager = IndustrySessionManager()
            manager.store_industry("Medical")
            
            assert session.get('industry') == "Medical"
            assert session.get('industry_timestamp') != old_timestamp

    def test_get_industry_info_returns_dict(self, app):
        """Test get_industry_info returns dictionary with industry data."""
        from src.web_interface.session_manager import IndustrySessionManager
        import datetime
        
        with app.test_request_context():
            session['industry'] = "Dental"
            timestamp = datetime.datetime.now().isoformat()
            session['industry_timestamp'] = timestamp
            
            manager = IndustrySessionManager()
            info = manager.get_industry_info()
            
            assert isinstance(info, dict)
            assert info['industry'] == "Dental"
            assert info['timestamp'] == timestamp
            assert 'is_set' in info
            assert info['is_set'] is True

    def test_get_industry_info_when_not_set(self, app):
        """Test get_industry_info when no industry is set."""
        from src.web_interface.session_manager import IndustrySessionManager
        
        with app.test_request_context():
            manager = IndustrySessionManager()
            info = manager.get_industry_info()
            
            assert isinstance(info, dict)
            assert info['industry'] is None
            assert info['timestamp'] is None
            assert info['is_set'] is False

    def test_persist_across_requests(self, app):
        """Test that industry persists across multiple requests."""
        from src.web_interface.session_manager import IndustrySessionManager
        
        with app.test_client() as client:
            # First request - set industry
            with client.session_transaction() as sess:
                manager = IndustrySessionManager()
                sess['industry'] = "Hardware / Home Improvement"
            
            # Second request - should still have industry
            with client.session_transaction() as sess:
                assert sess.get('industry') == "Hardware / Home Improvement"


class TestIndustryFormProcessor:
    """Test cases for processing forms with industry selection."""

    def test_process_form_adds_industry_from_session_if_missing(self):
        """Test that form processor adds industry from session if not in form."""
        from src.web_interface.form_processor import IndustryFormProcessor
        
        with patch('src.web_interface.form_processor.IndustrySessionManager') as mock_manager:
            mock_instance = Mock()
            mock_instance.get_industry.return_value = "Restaurant"
            mock_manager.return_value = mock_instance
            
            processor = IndustryFormProcessor()
            form_data = {'url': 'https://example.com'}
            
            processed_data = processor.process_form(form_data)
            
            assert processed_data['industry'] == "Restaurant"
            assert processed_data['url'] == 'https://example.com'

    def test_process_form_keeps_form_industry_over_session(self):
        """Test that form industry takes precedence over session industry."""
        from src.web_interface.form_processor import IndustryFormProcessor
        
        with patch('src.web_interface.form_processor.IndustrySessionManager') as mock_manager:
            mock_instance = Mock()
            mock_instance.get_industry.return_value = "Restaurant"
            mock_manager.return_value = mock_instance
            
            processor = IndustryFormProcessor()
            form_data = {
                'url': 'https://example.com',
                'industry': 'Medical'
            }
            
            processed_data = processor.process_form(form_data)
            
            assert processed_data['industry'] == "Medical"

    def test_process_form_updates_session_with_form_industry(self):
        """Test that form processor updates session with form industry."""
        from src.web_interface.form_processor import IndustryFormProcessor
        
        with patch('src.web_interface.form_processor.IndustrySessionManager') as mock_manager:
            mock_instance = Mock()
            mock_manager.return_value = mock_instance
            
            processor = IndustryFormProcessor()
            form_data = {
                'url': 'https://example.com',
                'industry': 'Real Estate'
            }
            
            processor.process_form(form_data)
            
            mock_instance.store_industry.assert_called_with('Real Estate')

    def test_get_validation_errors_for_missing_industry(self):
        """Test validation errors when industry is missing."""
        from src.web_interface.form_processor import IndustryFormProcessor
        
        with patch('src.web_interface.form_processor.IndustrySessionManager') as mock_manager:
            mock_instance = Mock()
            mock_instance.get_industry.return_value = None
            mock_manager.return_value = mock_instance
            
            processor = IndustryFormProcessor()
            form_data = {'url': 'https://example.com'}
            
            errors = processor.validate(form_data)
            
            assert 'industry' in errors
            assert errors['industry'] == "Industry selection is required"