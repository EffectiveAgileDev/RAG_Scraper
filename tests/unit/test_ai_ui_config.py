"""Unit tests for AI UI configuration management."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from src.web_interface.ai_config_manager import AIConfigManager


class TestAIConfigManager:
    """Test AI configuration management for web interface."""

    @pytest.fixture
    def ai_config_manager(self):
        """Create AIConfigManager instance for testing."""
        return AIConfigManager()

    def test_default_ai_configuration(self, ai_config_manager):
        """Test default AI configuration settings."""
        config = ai_config_manager.get_default_config()
        
        assert config['ai_enhancement_enabled'] is False
        assert config['llm_provider'] == 'openai'
        assert config['features']['nutritional_analysis'] is True
        assert config['features']['price_analysis'] is True
        assert config['features']['cuisine_classification'] is True
        assert config['features']['multimodal_analysis'] is False
        assert config['confidence_threshold'] == 0.7

    def test_validate_ai_configuration_valid(self, ai_config_manager):
        """Test validation of valid AI configuration."""
        valid_config = {
            'ai_enhancement_enabled': True,
            'llm_provider': 'openai',
            'api_key': 'sk-test123',
            'features': {
                'nutritional_analysis': True,
                'price_analysis': False
            },
            'confidence_threshold': 0.8
        }
        
        is_valid, errors = ai_config_manager.validate_config(valid_config)
        print(f"Validation result: {is_valid}, Errors: {errors}")  # Debug output
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_ai_configuration_invalid_provider(self, ai_config_manager):
        """Test validation of invalid LLM provider."""
        invalid_config = {
            'ai_enhancement_enabled': True,
            'llm_provider': 'invalid_provider',
            'confidence_threshold': 0.8
        }
        
        is_valid, errors = ai_config_manager.validate_config(invalid_config)
        assert is_valid is False
        assert 'Invalid LLM provider' in str(errors)

    def test_validate_ai_configuration_invalid_confidence(self, ai_config_manager):
        """Test validation of invalid confidence threshold."""
        invalid_config = {
            'ai_enhancement_enabled': True,
            'llm_provider': 'openai',
            'confidence_threshold': 1.5  # Invalid: > 1.0
        }
        
        is_valid, errors = ai_config_manager.validate_config(invalid_config)
        assert is_valid is False
        assert 'Confidence threshold must be between 0.1 and 1.0' in str(errors)

    def test_save_ai_configuration(self, ai_config_manager):
        """Test saving AI configuration."""
        config = {
            'ai_enhancement_enabled': True,
            'llm_provider': 'claude',
            'api_key': 'claude_key_123',
            'features': {
                'nutritional_analysis': True,
                'multimodal_analysis': True
            }
        }
        
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            result = ai_config_manager.save_config(config)
            assert result is True
            # json.dump calls write multiple times, so just check that write was called
            assert mock_file.write.call_count > 0

    def test_load_ai_configuration(self, ai_config_manager):
        """Test loading AI configuration."""
        expected_config = {
            'ai_enhancement_enabled': True,
            'llm_provider': 'openai'
        }
        
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            mock_file.read.return_value = json.dumps(expected_config)
            
            config = ai_config_manager.load_config()
            assert config['ai_enhancement_enabled'] is True
            assert config['llm_provider'] == 'openai'

    def test_secure_api_key_handling(self, ai_config_manager):
        """Test secure handling of API keys."""
        config = {
            'api_key': 'sk-very-secret-key-123'
        }
        
        # API key should be masked in logs/displays
        masked_config = ai_config_manager.mask_sensitive_data(config)
        assert masked_config['api_key'] == 'sk-***'

    def test_provider_availability_check(self, ai_config_manager):
        """Test checking availability of AI providers."""
        with patch('requests.get') as mock_request:
            # Test OpenAI availability (external service)
            mock_request.return_value.status_code = 200
            is_available = ai_config_manager.check_provider_availability('openai')
            assert is_available is True

    def test_local_provider_availability_check(self, ai_config_manager):
        """Test checking availability of local AI providers."""
        with patch('requests.get') as mock_request:
            # Test Ollama availability (local service)
            mock_request.side_effect = Exception("Connection refused")
            is_available = ai_config_manager.check_provider_availability('ollama')
            assert is_available is False

    def test_merge_configurations(self, ai_config_manager):
        """Test merging user config with defaults."""
        default_config = ai_config_manager.get_default_config()
        user_config = {
            'ai_enhancement_enabled': True,
            'llm_provider': 'claude',
            'features': {
                'nutritional_analysis': False  # Override default
            }
        }
        
        merged_config = ai_config_manager.merge_with_defaults(user_config, default_config)
        
        assert merged_config['ai_enhancement_enabled'] is True  # From user
        assert merged_config['llm_provider'] == 'claude'  # From user
        assert merged_config['features']['nutritional_analysis'] is False  # User override
        assert merged_config['features']['price_analysis'] is True  # From default
        assert merged_config['confidence_threshold'] == 0.7  # From default

    def test_config_for_session(self, ai_config_manager):
        """Test configuration management for user sessions."""
        session_id = "test_session_123"
        config = {
            'ai_enhancement_enabled': True,
            'llm_provider': 'openai'
        }
        
        ai_config_manager.set_session_config(session_id, config)
        retrieved_config = ai_config_manager.get_session_config(session_id)
        
        assert retrieved_config['ai_enhancement_enabled'] is True
        assert retrieved_config['llm_provider'] == 'openai'

    def test_config_cleanup_for_session(self, ai_config_manager):
        """Test cleanup of session-specific configuration."""
        session_id = "test_session_456"
        config = {'ai_enhancement_enabled': True}
        
        ai_config_manager.set_session_config(session_id, config)
        ai_config_manager.clear_session_config(session_id)
        
        retrieved_config = ai_config_manager.get_session_config(session_id)
        # Should return default config after cleanup
        assert retrieved_config['ai_enhancement_enabled'] is False


class TestAIConfigValidation:
    """Test AI configuration validation logic."""

    def test_api_key_format_validation(self):
        """Test API key format validation."""
        from src.web_interface.ai_config_manager import validate_api_key
        
        # Valid OpenAI API key format
        assert validate_api_key('sk-abc123def456', 'openai') is True
        
        # Valid Claude API key format  
        assert validate_api_key('claude-key-123', 'claude') is True
        
        # Invalid format
        assert validate_api_key('invalid-key', 'openai') is False
        
        # Empty key (should be valid for optional usage)
        assert validate_api_key('', 'openai') is True

    def test_feature_toggles_validation(self):
        """Test validation of AI feature toggle configuration."""
        from src.web_interface.ai_config_manager import validate_feature_toggles
        
        valid_features = {
            'nutritional_analysis': True,
            'price_analysis': False,
            'cuisine_classification': True
        }
        assert validate_feature_toggles(valid_features) is True
        
        invalid_features = {
            'nutritional_analysis': 'yes',  # Should be boolean
            'invalid_feature': True
        }
        assert validate_feature_toggles(invalid_features) is False

    def test_confidence_threshold_validation(self):
        """Test confidence threshold validation."""
        from src.web_interface.ai_config_manager import validate_confidence_threshold
        
        assert validate_confidence_threshold(0.7) is True
        assert validate_confidence_threshold(0.1) is True  # Min value
        assert validate_confidence_threshold(1.0) is True  # Max value
        
        assert validate_confidence_threshold(0.05) is False  # Too low
        assert validate_confidence_threshold(1.5) is False   # Too high
        assert validate_confidence_threshold('0.7') is False # Wrong type