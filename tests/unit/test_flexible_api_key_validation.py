"""Unit tests for flexible API key length validation."""

import pytest
from unittest.mock import Mock, patch

from src.web_interface.ai_config_manager import AIConfigManager, validate_api_key


class TestFlexibleAPIKeyValidation:
    """Test flexible API key length validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.ai_config_manager = AIConfigManager()

    def test_validate_api_key_accepts_short_keys(self):
        """Test that short API keys are accepted."""
        # Short but valid API keys
        short_keys = [
            "sk-123",
            "sk-abc",
            "sk-test",
            "sk-1234567890",
            "claude-key-123"
        ]
        
        for key in short_keys:
            # Should accept short keys for OpenAI
            assert validate_api_key(key, 'openai') is True
            # Should accept short keys for Claude  
            assert validate_api_key(key, 'claude') is True

    def test_validate_api_key_accepts_long_keys(self):
        """Test that very long API keys are accepted."""
        # Very long API keys
        long_key = "sk-" + "x" * 200  # 203 characters total
        very_long_key = "sk-" + "a" * 500  # 503 characters total
        
        assert validate_api_key(long_key, 'openai') is True
        assert validate_api_key(very_long_key, 'openai') is True
        assert validate_api_key(long_key, 'claude') is True
        assert validate_api_key(very_long_key, 'claude') is True

    def test_validate_api_key_accepts_non_standard_formats(self):
        """Test that non-standard API key formats are accepted."""
        non_standard_keys = [
            "api-key-123456789",
            "bearer-token-abcdefgh",
            "custom-key-format-12345",
            "gpt-key-xyz789",
            "local-llm-key-123",
            "123456789",  # Pure numeric
            "abcdefghijklmnop",  # Pure alphabetic
            "my-custom-api-key-format-2024"
        ]
        
        for key in non_standard_keys:
            assert validate_api_key(key, 'openai') is True
            assert validate_api_key(key, 'claude') is True

    def test_validate_api_key_rejects_empty_keys(self):
        """Test that empty API keys are rejected."""
        empty_keys = [
            "",
            "   ",
            "\t",
            "\n",
            None
        ]
        
        for key in empty_keys:
            assert validate_api_key(key, 'openai') is False
            assert validate_api_key(key, 'claude') is False

    def test_validate_api_key_handles_special_characters(self):
        """Test that API keys with special characters are accepted."""
        special_keys = [
            "sk-123_abc-def",
            "api.key.with.dots",
            "key-with-dashes-123",
            "key_with_underscores_456",
            "key@with@symbols#789",
            "key+with+plus=signs",
            "key$with%special&chars*789"
        ]
        
        for key in special_keys:
            assert validate_api_key(key, 'openai') is True
            assert validate_api_key(key, 'claude') is True

    def test_ai_config_manager_validation_flexible(self):
        """Test that AIConfigManager uses flexible validation."""
        config_data = {
            'ai_enhancement_enabled': True,
            'llm_provider': 'openai',
            'api_key': 'sk-123',  # Short key
            'confidence_threshold': 0.7,
            'features': {'nutritional_analysis': True}
        }
        
        is_valid, errors = self.ai_config_manager.validate_config(config_data)
        
        assert is_valid is True
        assert len(errors) == 0

    def test_ai_config_manager_validation_very_long_key(self):
        """Test that AIConfigManager accepts very long keys."""
        config_data = {
            'ai_enhancement_enabled': True,
            'llm_provider': 'openai',
            'api_key': 'sk-' + 'x' * 200,  # Very long key
            'confidence_threshold': 0.7,
            'features': {'nutritional_analysis': True}
        }
        
        is_valid, errors = self.ai_config_manager.validate_config(config_data)
        
        assert is_valid is True
        assert len(errors) == 0

    def test_ai_config_manager_validation_non_standard_key(self):
        """Test that AIConfigManager accepts non-standard key formats."""
        config_data = {
            'ai_enhancement_enabled': True,
            'llm_provider': 'openai',
            'api_key': 'my-custom-api-key-format-2024',
            'confidence_threshold': 0.7,
            'features': {'nutritional_analysis': True}
        }
        
        is_valid, errors = self.ai_config_manager.validate_config(config_data)
        
        assert is_valid is True
        assert len(errors) == 0

    def test_ai_config_manager_validation_empty_key_rejected(self):
        """Test that AIConfigManager rejects empty keys."""
        config_data = {
            'ai_enhancement_enabled': True,
            'llm_provider': 'openai',
            'api_key': '',
            'confidence_threshold': 0.7,
            'features': {'nutritional_analysis': True}
        }
        
        is_valid, errors = self.ai_config_manager.validate_config(config_data)
        
        assert is_valid is False
        assert any('API key' in error for error in errors)

    def test_validate_api_key_with_different_providers(self):
        """Test that flexible validation works with different providers."""
        test_key = "custom-format-key-123"
        
        providers = ['openai', 'claude', 'ollama', 'llama_cpp', 'custom']
        
        for provider in providers:
            assert validate_api_key(test_key, provider) is True

    def test_validate_api_key_local_providers_no_key_required(self):
        """Test that local providers don't require API keys."""
        # Local providers should work without API keys
        assert validate_api_key("", 'ollama') is True
        assert validate_api_key("", 'llama_cpp') is True
        assert validate_api_key(None, 'ollama') is True
        assert validate_api_key(None, 'llama_cpp') is True

    def test_validate_api_key_custom_provider_flexible(self):
        """Test that custom providers have flexible validation."""
        custom_keys = [
            "custom-123",
            "local-llm-key",
            "my-personal-key-format",
            "abc123",
            "x" * 300  # Very long custom key
        ]
        
        for key in custom_keys:
            assert validate_api_key(key, 'custom') is True

    def test_api_key_validation_performance(self):
        """Test that API key validation is performant with long keys."""
        import time
        
        # Test with very long key
        long_key = "sk-" + "x" * 10000
        
        start_time = time.time()
        result = validate_api_key(long_key, 'openai')
        end_time = time.time()
        
        assert result is True
        assert end_time - start_time < 0.1  # Should be fast

    def test_validate_api_key_unicode_characters(self):
        """Test that API keys with unicode characters are handled."""
        unicode_keys = [
            "sk-café123",
            "key-with-émojis-🤖",
            "αβγ-key-123",
            "中文-key-789"
        ]
        
        for key in unicode_keys:
            # Should handle unicode gracefully
            result = validate_api_key(key, 'openai')
            assert isinstance(result, bool)  # Should not crash

    def test_validate_api_key_whitespace_handling(self):
        """Test that API keys with whitespace are handled correctly."""
        whitespace_keys = [
            " sk-123 ",  # Leading/trailing spaces
            "sk-123\t",  # Tab character
            "sk-123\n",  # Newline
            "sk - 123",  # Spaces in middle
        ]
        
        for key in whitespace_keys:
            # Should handle whitespace gracefully
            result = validate_api_key(key, 'openai')
            assert isinstance(result, bool)

    def test_validate_api_key_backwards_compatibility(self):
        """Test that validation maintains backwards compatibility."""
        # Traditional OpenAI format should still work
        traditional_key = "sk-" + "x" * 48
        assert validate_api_key(traditional_key, 'openai') is True
        
        # Traditional Claude format should still work
        claude_key = "sk-ant-" + "x" * 40
        assert validate_api_key(claude_key, 'claude') is True