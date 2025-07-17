"""Unit tests for AI API routes."""

import pytest
import json
from unittest.mock import Mock, patch
from flask import Flask

from src.web_interface.ai_api_routes import ai_api


class TestAIAPIRoutes:
    """Test AI API route endpoints."""

    @pytest.fixture
    def app(self):
        """Create test Flask app with AI API blueprint."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.register_blueprint(ai_api)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    def test_get_ai_providers_success(self, client):
        """Test getting AI providers endpoint."""
        with patch('src.web_interface.ai_api_routes.ai_config_manager') as mock_manager:
            # Mock provider availability checks
            mock_manager.check_provider_availability.side_effect = lambda p: p in ['openai', 'claude']
            
            response = client.get('/api/ai/providers')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert 'providers' in data
            assert 'openai' in data['providers']
            assert 'claude' in data['providers']
            assert 'ollama' in data['providers']
            assert data['providers']['openai']['available'] is True
            assert data['providers']['ollama']['available'] is False

    def test_configure_ai_success(self, client):
        """Test configuring AI settings endpoint."""
        with patch('src.web_interface.ai_api_routes.ai_config_manager') as mock_manager:
            # Mock validation success
            mock_manager.validate_config.return_value = (True, [])
            mock_manager.mask_sensitive_data.return_value = {'ai_enhancement_enabled': True}
            
            config_data = {
                'ai_enhancement_enabled': True,
                'llm_provider': 'openai',
                'api_key': 'sk-test123',
                'confidence_threshold': 0.8
            }
            
            with client.session_transaction() as sess:
                sess['session_id'] = 'test_session'
            
            response = client.post('/api/ai/configure',
                                 data=json.dumps(config_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert 'message' in data
            mock_manager.set_session_config.assert_called_once()

    def test_configure_ai_validation_error(self, client):
        """Test AI configuration with validation errors."""
        with patch('src.web_interface.ai_api_routes.ai_config_manager') as mock_manager:
            # Mock validation failure
            mock_manager.validate_config.return_value = (False, ['Invalid provider'])
            
            config_data = {
                'ai_enhancement_enabled': True,
                'llm_provider': 'invalid_provider'
            }
            
            response = client.post('/api/ai/configure',
                                 data=json.dumps(config_data),
                                 content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            
            assert data['success'] is False
            assert 'validation_errors' in data

    def test_analyze_content_ai_disabled(self, client):
        """Test content analysis with AI disabled."""
        with patch('src.web_interface.ai_api_routes.ai_config_manager') as mock_manager:
            # Mock AI disabled configuration
            mock_manager.get_session_config.return_value = {
                'ai_enhancement_enabled': False
            }
            
            content_data = {
                'content': 'Restaurant content',
                'menu_items': [{'name': 'Test Item', 'price': '$10'}],
                'analysis_type': 'nutritional'
            }
            
            with client.session_transaction() as sess:
                sess['session_id'] = 'test_session'
            
            response = client.post('/api/ai/analyze-content',
                                 data=json.dumps(content_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert data['fallback_used'] is True
            assert data['ai_analysis'] is None

    @patch('src.web_interface.ai_api_routes.AIContentAnalyzer')
    def test_analyze_content_ai_enabled(self, mock_analyzer_class, client):
        """Test content analysis with AI enabled."""
        with patch('src.web_interface.ai_api_routes.ai_config_manager') as mock_manager:
            # Mock AI enabled configuration
            mock_manager.get_session_config.return_value = {
                'ai_enhancement_enabled': True,
                'llm_provider': 'openai',
                'api_key': 'sk-test123',
                'features': {
                    'nutritional_analysis': True,
                    'multimodal_analysis': False
                },
                'confidence_threshold': 0.7
            }
            
            # Mock analyzer instance and methods
            mock_analyzer = Mock()
            mock_analyzer_class.return_value = mock_analyzer
            mock_analyzer.analyze_content.return_value = {
                'nutritional_context': [{'name': 'Test Item', 'tags': ['healthy']}]
            }
            mock_analyzer.calculate_integrated_confidence.return_value = 0.85
            
            content_data = {
                'content': 'Restaurant content',
                'menu_items': [{'name': 'Test Item', 'price': '$10'}],
                'analysis_type': 'nutritional'
            }
            
            with client.session_transaction() as sess:
                sess['session_id'] = 'test_session'
            
            response = client.post('/api/ai/analyze-content',
                                 data=json.dumps(content_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert data['fallback_used'] is False
            assert data['ai_analysis'] is not None
            assert data['confidence_score'] == 0.85
            assert data['meets_threshold'] is True
            assert data['provider_used'] == 'openai'

    def test_analyze_content_missing_data(self, client):
        """Test content analysis with missing data."""
        response = client.post('/api/ai/analyze-content',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert 'error' in data

    def test_get_ai_config(self, client):
        """Test getting AI configuration."""
        with patch('src.web_interface.ai_api_routes.ai_config_manager') as mock_manager:
            mock_config = {
                'ai_enhancement_enabled': True,
                'llm_provider': 'openai'
            }
            mock_manager.get_session_config.return_value = mock_config
            mock_manager.mask_sensitive_data.return_value = mock_config
            
            with client.session_transaction() as sess:
                sess['session_id'] = 'test_session'
            
            response = client.get('/api/ai/config')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert 'config' in data
            assert data['config']['ai_enhancement_enabled'] is True

    def test_validate_api_key(self, client):
        """Test API key validation endpoint."""
        with patch('src.web_interface.ai_api_routes.validate_api_key') as mock_validate:
            mock_validate.return_value = True
            
            request_data = {
                'api_key': 'sk-test123',
                'provider': 'openai'
            }
            
            response = client.post('/api/ai/validate-api-key',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert data['valid'] is True
            assert data['provider'] == 'openai'

    @patch('src.web_interface.ai_api_routes.AIContentAnalyzer')
    def test_test_ai_connection_external_provider(self, mock_analyzer_class, client):
        """Test AI connection for external provider."""
        mock_analyzer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_analyzer.analyze_content.return_value = {'success': True}
        
        request_data = {
            'provider': 'openai',
            'api_key': 'sk-test123'
        }
        
        response = client.post('/api/ai/test-connection',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert data['connection_successful'] is True
        assert data['provider'] == 'openai'

    def test_test_ai_connection_local_provider(self, client):
        """Test AI connection for local provider."""
        with patch('src.web_interface.ai_api_routes.ai_config_manager') as mock_manager:
            mock_manager.check_provider_availability.return_value = True
            
            request_data = {
                'provider': 'ollama'
            }
            
            response = client.post('/api/ai/test-connection',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert data['connection_successful'] is True
            assert data['provider'] == 'ollama'

    def test_clear_ai_config(self, client):
        """Test clearing AI configuration."""
        with patch('src.web_interface.ai_api_routes.ai_config_manager') as mock_manager:
            with client.session_transaction() as sess:
                sess['session_id'] = 'test_session'
            
            response = client.post('/api/ai/clear-config')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            mock_manager.clear_session_config.assert_called_once_with('test_session')

    def test_ai_api_404_error(self, client):
        """Test 404 error handling for AI API."""
        response = client.get('/api/ai/nonexistent-endpoint')
        
        assert response.status_code == 404
        # Flask returns HTML for 404 by default, just check status code
        assert b'Not Found' in response.data