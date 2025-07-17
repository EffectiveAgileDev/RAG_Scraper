"""Unit tests for OpenAI API key validation functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from flask import Flask

from src.web_interface.ai_api_routes import ai_api


class TestOpenAIAPIKeyValidation:
    """Test class for OpenAI API key validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        
        # Register AI API blueprint
        self.app.register_blueprint(ai_api)
        
        self.client = self.app.test_client()
        self.valid_api_key = "sk-proj-test123valid456key789"
        self.invalid_api_key = "sk-invalid-key-123"
    
    def test_validate_api_key_endpoint_exists(self):
        """Test that the validate API key endpoint exists."""
        with self.app.test_request_context():
            response = self.client.post('/api/ai/validate-api-key', 
                                        json={'api_key': self.valid_api_key})
            # Should not return 404 (endpoint exists)
            assert response.status_code != 404
    
    @patch('requests.get')
    def test_validate_valid_openai_api_key(self, mock_get):
        """Test validation of a valid OpenAI API key."""
        # Mock successful OpenAI API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"id": "gpt-3.5-turbo", "object": "model"},
                {"id": "gpt-4", "object": "model"}
            ]
        }
        mock_get.return_value = mock_response
        
        with self.app.test_request_context():
            response = self.client.post('/api/ai/validate-api-key', 
                                        json={'api_key': self.valid_api_key})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['valid'] is True
            assert data['message'] == 'API key is valid'
            assert 'models' in data
            assert len(data['models']) == 2
    
    @patch('requests.get')
    def test_validate_invalid_openai_api_key(self, mock_get):
        """Test validation of an invalid OpenAI API key."""
        # Mock 401 Unauthorized response from OpenAI
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "error": {
                "message": "Incorrect API key provided",
                "type": "invalid_request_error"
            }
        }
        mock_get.return_value = mock_response
        
        with self.app.test_request_context():
            response = self.client.post('/api/ai/validate-api-key', 
                                        json={'api_key': self.invalid_api_key})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['valid'] is False
            assert 'invalid' in data['message'].lower() or 'incorrect' in data['message'].lower()
    
    @patch('requests.get')
    def test_validate_api_key_network_error(self, mock_get):
        """Test validation when network error occurs."""
        # Mock network error
        mock_get.side_effect = Exception("Network timeout")
        
        with self.app.test_request_context():
            response = self.client.post('/api/ai/validate-api-key', 
                                        json={'api_key': self.valid_api_key})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['valid'] is False
            assert 'network' in data['message'].lower() or 'error' in data['message'].lower()
    
    def test_validate_api_key_missing_key(self):
        """Test validation with missing API key."""
        with self.app.test_request_context():
            response = self.client.post('/api/ai/validate-api-key', json={})
            
            assert response.status_code == 400
            data = response.get_json()
            assert 'error' in data
            assert 'api key' in data['error'].lower()
    
    def test_validate_api_key_empty_key(self):
        """Test validation with empty API key."""
        with self.app.test_request_context():
            response = self.client.post('/api/ai/validate-api-key', 
                                        json={'api_key': ''})
            
            assert response.status_code == 400
            data = response.get_json()
            assert 'error' in data
            assert 'empty' in data['error'].lower() or 'required' in data['error'].lower()
    
    @patch('requests.get')
    def test_validate_api_key_calls_correct_endpoint(self, mock_get):
        """Test that validation calls the correct OpenAI endpoint."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response
        
        with self.app.test_request_context():
            self.client.post('/api/ai/validate-api-key', 
                              json={'api_key': self.valid_api_key})
            
            # Verify correct OpenAI endpoint was called
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "https://api.openai.com/v1/models"
            assert call_args[1]['headers']['Authorization'] == f"Bearer {self.valid_api_key}"
    
    @patch('requests.get')
    def test_validate_api_key_timeout_handling(self, mock_get):
        """Test that API key validation handles timeouts properly."""
        import requests
        mock_get.side_effect = requests.Timeout("Request timeout")
        
        with self.app.test_request_context():
            response = self.client.post('/api/ai/validate-api-key', 
                                        json={'api_key': self.valid_api_key})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['valid'] is False
            assert 'timeout' in data['message'].lower()
    
    @patch('requests.get')
    def test_validate_api_key_rate_limit_handling(self, mock_get):
        """Test that API key validation handles rate limiting."""
        # Mock 429 Too Many Requests response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {
            "error": {
                "message": "Rate limit exceeded",
                "type": "requests"
            }
        }
        mock_get.return_value = mock_response
        
        with self.app.test_request_context():
            response = self.client.post('/api/ai/validate-api-key', 
                                        json={'api_key': self.valid_api_key})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['valid'] is False
            assert 'rate limit' in data['message'].lower()
    
    @patch('requests.get')
    def test_validate_api_key_with_specific_model(self, mock_get):
        """Test validation of API key with specific model verification."""
        # Mock successful OpenAI API response with specific models
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"id": "gpt-3.5-turbo", "object": "model"},
                {"id": "gpt-4", "object": "model"},
                {"id": "gpt-4-turbo", "object": "model"}
            ]
        }
        mock_get.return_value = mock_response
        
        with self.app.test_request_context():
            response = self.client.post('/api/ai/validate-api-key', 
                                        json={
                                            'api_key': self.valid_api_key,
                                            'model': 'gpt-3.5-turbo'
                                        })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['valid'] is True
            assert data['model_available'] is True
            assert 'models' in data
    
    @patch('requests.get')
    def test_validate_api_key_with_unavailable_model(self, mock_get):
        """Test validation when requested model is not available."""
        # Mock successful OpenAI API response without the requested model
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"id": "gpt-3.5-turbo", "object": "model"},
                {"id": "gpt-4", "object": "model"}
            ]
        }
        mock_get.return_value = mock_response
        
        with self.app.test_request_context():
            response = self.client.post('/api/ai/validate-api-key', 
                                        json={
                                            'api_key': self.valid_api_key,
                                            'model': 'gpt-4-turbo-preview'
                                        })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['valid'] is True  # API key is valid
            assert data['model_available'] is False  # But model is not available
            assert 'not available' in data['message'].lower()