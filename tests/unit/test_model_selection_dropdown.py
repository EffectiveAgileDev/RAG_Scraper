"""Unit tests for model selection dropdown functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from flask import Flask

from src.web_interface.ai_api_routes import ai_api


class TestModelSelectionDropdown:
    """Test class for model selection dropdown functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        
        # Register AI API blueprint
        self.app.register_blueprint(ai_api)
        
        self.client = self.app.test_client()
        self.valid_api_key = "sk-proj-test123valid456key789"
    
    def test_get_models_endpoint_exists(self):
        """Test that the get models endpoint exists."""
        with self.app.test_request_context():
            response = self.client.post('/api/ai/get-models', 
                                        json={'provider': 'openai', 'api_key': self.valid_api_key})
            # Should not return 404 (endpoint exists)
            assert response.status_code != 404
    
    @patch('requests.get')
    def test_get_models_for_openai_provider(self, mock_get):
        """Test getting models for OpenAI provider."""
        # Mock successful OpenAI API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"id": "gpt-3.5-turbo", "object": "model", "owned_by": "openai"},
                {"id": "gpt-4", "object": "model", "owned_by": "openai"},
                {"id": "gpt-4-turbo", "object": "model", "owned_by": "openai"},
                {"id": "gpt-4-vision-preview", "object": "model", "owned_by": "openai"},
                {"id": "dall-e-3", "object": "model", "owned_by": "openai"},
                {"id": "whisper-1", "object": "model", "owned_by": "openai"}
            ]
        }
        mock_get.return_value = mock_response
        
        with self.app.test_request_context():
            response = self.client.post('/api/ai/get-models', 
                                        json={
                                            'provider': 'openai',
                                            'api_key': self.valid_api_key
                                        })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'models' in data
            assert len(data['models']) > 0
            
            # Check that models are filtered for text generation (not DALL-E, Whisper, etc.)
            model_ids = [model['id'] for model in data['models']]
            assert 'gpt-3.5-turbo' in model_ids
            assert 'gpt-4' in model_ids
            # Should not include non-text models
            assert 'dall-e-3' not in model_ids
            assert 'whisper-1' not in model_ids
    
    def test_get_models_for_claude_provider(self):
        """Test getting models for Claude provider (not implemented)."""
        with self.app.test_request_context():
            response = self.client.post('/api/ai/get-models', 
                                        json={
                                            'provider': 'claude',
                                            'api_key': 'test-claude-key'
                                        })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['implemented'] is False
            assert 'not implemented' in data['message'].lower()
            assert data['models'] == []
    
    def test_get_models_for_ollama_provider(self):
        """Test getting models for Ollama provider (not implemented)."""
        with self.app.test_request_context():
            response = self.client.post('/api/ai/get-models', 
                                        json={
                                            'provider': 'ollama',
                                            'api_key': ''
                                        })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['implemented'] is False
            assert 'not implemented' in data['message'].lower()
    
    def test_get_models_missing_provider(self):
        """Test getting models with missing provider."""
        with self.app.test_request_context():
            response = self.client.post('/api/ai/get-models', 
                                        json={'api_key': self.valid_api_key})
            
            assert response.status_code == 400
            data = response.get_json()
            assert 'error' in data
            assert 'provider' in data['error'].lower()
    
    def test_get_models_missing_api_key_for_openai(self):
        """Test getting models with missing API key for OpenAI."""
        with self.app.test_request_context():
            response = self.client.post('/api/ai/get-models', 
                                        json={'provider': 'openai'})
            
            assert response.status_code == 400
            data = response.get_json()
            assert 'error' in data
            assert 'api key' in data['error'].lower()
    
    @patch('requests.get')
    def test_get_models_invalid_api_key(self, mock_get):
        """Test getting models with invalid API key."""
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
            response = self.client.post('/api/ai/get-models', 
                                        json={
                                            'provider': 'openai',
                                            'api_key': 'invalid-key'
                                        })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is False
            assert 'invalid' in data['message'].lower() or 'unauthorized' in data['message'].lower()
    
    @patch('requests.get')
    def test_get_models_network_error(self, mock_get):
        """Test getting models with network error."""
        # Mock network error
        mock_get.side_effect = Exception("Network timeout")
        
        with self.app.test_request_context():
            response = self.client.post('/api/ai/get-models', 
                                        json={
                                            'provider': 'openai',
                                            'api_key': self.valid_api_key
                                        })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is False
            assert 'network' in data['message'].lower() or 'error' in data['message'].lower()
    
    def test_get_models_filters_text_models_only(self):
        """Test that only text generation models are returned."""
        with patch('requests.get') as mock_get:
            # Mock response with various model types
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": [
                    {"id": "gpt-3.5-turbo", "object": "model", "owned_by": "openai"},
                    {"id": "gpt-4", "object": "model", "owned_by": "openai"},
                    {"id": "dall-e-3", "object": "model", "owned_by": "openai"},
                    {"id": "whisper-1", "object": "model", "owned_by": "openai"},
                    {"id": "tts-1", "object": "model", "owned_by": "openai"},
                    {"id": "text-embedding-ada-002", "object": "model", "owned_by": "openai"}
                ]
            }
            mock_get.return_value = mock_response
            
            with self.app.test_request_context():
                response = self.client.post('/api/ai/get-models', 
                                            json={
                                                'provider': 'openai',
                                                'api_key': self.valid_api_key
                                            })
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                
                # Should only include text generation models
                model_ids = [model['id'] for model in data['models']]
                assert 'gpt-3.5-turbo' in model_ids
                assert 'gpt-4' in model_ids
                assert 'dall-e-3' not in model_ids
                assert 'whisper-1' not in model_ids
                assert 'tts-1' not in model_ids
                assert 'text-embedding-ada-002' not in model_ids
    
    def test_get_models_sorts_models_by_relevance(self):
        """Test that models are sorted by relevance (GPT-4 first, then GPT-3.5)."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": [
                    {"id": "gpt-3.5-turbo", "object": "model", "owned_by": "openai"},
                    {"id": "gpt-4", "object": "model", "owned_by": "openai"},
                    {"id": "gpt-4-turbo", "object": "model", "owned_by": "openai"},
                    {"id": "gpt-3.5-turbo-16k", "object": "model", "owned_by": "openai"}
                ]
            }
            mock_get.return_value = mock_response
            
            with self.app.test_request_context():
                response = self.client.post('/api/ai/get-models', 
                                            json={
                                                'provider': 'openai',
                                                'api_key': self.valid_api_key
                                            })
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                
                # Check that GPT-4 models come first
                model_ids = [model['id'] for model in data['models']]
                gpt4_index = next(i for i, mid in enumerate(model_ids) if 'gpt-4' in mid)
                gpt35_index = next(i for i, mid in enumerate(model_ids) if 'gpt-3.5' in mid)
                assert gpt4_index < gpt35_index