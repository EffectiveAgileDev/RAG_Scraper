"""Unit tests for AI Settings Persistence."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from cryptography.fernet import Fernet

from src.web_interface.ai_settings_persistence import (
    AISettingsPersistence,
    EncryptionService,
    LocalStorageBackend,
    SessionStorageBackend
)


class TestEncryptionService:
    """Test encryption service for API keys."""
    
    def test_generate_encryption_key(self):
        """Test encryption key generation."""
        service = EncryptionService()
        key = service.generate_key()
        
        assert key is not None
        assert isinstance(key, bytes)
        assert len(key) == 44  # Fernet key length
    
    def test_encrypt_decrypt_api_key(self):
        """Test API key encryption and decryption."""
        service = EncryptionService()
        api_key = "sk-test123456789"
        
        encrypted = service.encrypt(api_key)
        assert encrypted != api_key
        assert isinstance(encrypted, str)
        
        decrypted = service.decrypt(encrypted)
        assert decrypted == api_key
    
    def test_encrypt_empty_string(self):
        """Test encrypting empty string."""
        service = EncryptionService()
        
        encrypted = service.encrypt("")
        assert encrypted == ""
    
    def test_decrypt_invalid_data(self):
        """Test decrypting invalid data."""
        service = EncryptionService()
        
        # Should return original if decryption fails
        result = service.decrypt("invalid_encrypted_data")
        assert result == "invalid_encrypted_data"
    
    def test_different_keys_produce_different_results(self):
        """Test that different keys produce different encrypted values."""
        service1 = EncryptionService()
        service2 = EncryptionService()
        
        api_key = "sk-test123456789"
        
        encrypted1 = service1.encrypt(api_key)
        encrypted2 = service2.encrypt(api_key)
        
        # Different keys should produce different encrypted values
        assert encrypted1 != encrypted2


class TestLocalStorageBackend:
    """Test local storage backend."""
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', create=True)
    def test_save_settings(self, mock_open, mock_mkdir, mock_exists):
        """Test saving settings to local storage."""
        mock_exists.return_value = True
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        backend = LocalStorageBackend()
        settings = {
            'ai_enhancement_enabled': True,
            'llm_provider': 'openai',
            'api_key': 'encrypted_key'
        }
        
        result = backend.save(settings)
        
        assert result is True
        assert mock_file.write.call_count > 0
        # Check that json data was written by examining all write calls
        all_written = ''.join(call[0][0] for call in mock_file.write.call_args_list)
        assert 'ai_enhancement_enabled' in all_written
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open', create=True)
    def test_load_settings(self, mock_open, mock_exists):
        """Test loading settings from local storage."""
        mock_exists.return_value = True
        settings_data = {
            'ai_enhancement_enabled': True,
            'llm_provider': 'claude'
        }
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(settings_data)
        
        backend = LocalStorageBackend()
        loaded = backend.load()
        
        assert loaded == settings_data
    
    @patch('pathlib.Path.exists')
    def test_load_nonexistent_file(self, mock_exists):
        """Test loading when file doesn't exist."""
        mock_exists.return_value = False
        
        backend = LocalStorageBackend()
        loaded = backend.load()
        
        assert loaded is None
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.unlink')
    def test_clear_settings(self, mock_unlink, mock_exists):
        """Test clearing settings."""
        mock_exists.return_value = True
        
        backend = LocalStorageBackend()
        result = backend.clear()
        
        assert result is True
        mock_unlink.assert_called_once()


class TestSessionStorageBackend:
    """Test session storage backend."""
    
    def test_save_to_session(self):
        """Test saving to session storage."""
        mock_session = {}
        backend = SessionStorageBackend(mock_session)
        
        settings = {
            'ai_enhancement_enabled': True,
            'llm_provider': 'ollama'
        }
        
        result = backend.save(settings)
        
        assert result is True
        assert 'ai_settings' in mock_session
        assert mock_session['ai_settings'] == settings
    
    def test_load_from_session(self):
        """Test loading from session storage."""
        settings = {
            'ai_enhancement_enabled': True,
            'confidence_threshold': 0.8
        }
        mock_session = {'ai_settings': settings}
        backend = SessionStorageBackend(mock_session)
        
        loaded = backend.load()
        
        assert loaded == settings
    
    def test_clear_session(self):
        """Test clearing session storage."""
        mock_session = {'ai_settings': {'some': 'data'}}
        backend = SessionStorageBackend(mock_session)
        
        result = backend.clear()
        
        assert result is True
        assert 'ai_settings' not in mock_session


class TestAISettingsPersistence:
    """Test AI settings persistence manager."""
    
    def test_save_settings_with_encryption(self):
        """Test saving settings with API key encryption."""
        mock_storage = Mock()
        mock_storage.save.return_value = True
        mock_encryption = Mock()
        mock_encryption.encrypt.side_effect = lambda x: f"encrypted_{x}"
        
        persistence = AISettingsPersistence(
            storage=mock_storage,
            encryption=mock_encryption
        )
        
        settings = {
            'ai_enhancement_enabled': True,
            'llm_provider': 'openai',
            'api_key': 'sk-test123',
            'confidence_threshold': 0.75
        }
        
        result = persistence.save_settings(settings)
        
        assert result is True
        
        # Verify API key was encrypted
        saved_settings = mock_storage.save.call_args[0][0]
        assert saved_settings['api_key'] == 'encrypted_sk-test123'
        assert saved_settings['llm_provider'] == 'openai'
    
    def test_load_settings_with_decryption(self):
        """Test loading settings with API key decryption."""
        stored_settings = {
            'ai_enhancement_enabled': True,
            'llm_provider': 'claude',
            'api_key': 'encrypted_claude-key',
            'confidence_threshold': 0.8
        }
        
        mock_storage = Mock()
        mock_storage.load.return_value = stored_settings
        mock_encryption = Mock()
        mock_encryption.decrypt.side_effect = lambda x: x.replace('encrypted_', '')
        
        persistence = AISettingsPersistence(
            storage=mock_storage,
            encryption=mock_encryption
        )
        
        loaded = persistence.load_settings()
        
        assert loaded is not None
        assert loaded['api_key'] == 'claude-key'
        assert loaded['llm_provider'] == 'claude'
    
    def test_clear_settings(self):
        """Test clearing all settings."""
        mock_storage = Mock()
        mock_storage.clear.return_value = True
        
        persistence = AISettingsPersistence(storage=mock_storage)
        result = persistence.clear_settings()
        
        assert result is True
        mock_storage.clear.assert_called_once()
    
    def test_migrate_session_to_permanent(self):
        """Test migrating session settings to permanent storage."""
        session_settings = {
            'ai_enhancement_enabled': True,
            'llm_provider': 'ollama',
            'api_key': 'ollama-local',
            'features': {'price_analysis': True}
        }
        
        mock_session_storage = Mock()
        mock_session_storage.load.return_value = session_settings
        
        mock_permanent_storage = Mock()
        mock_permanent_storage.save.return_value = True
        
        mock_encryption = Mock()
        mock_encryption.encrypt.side_effect = lambda x: f"encrypted_{x}"
        
        persistence = AISettingsPersistence(
            storage=mock_permanent_storage,
            encryption=mock_encryption
        )
        
        result = persistence.migrate_session_to_permanent(session_settings)
        
        assert result is True
        
        # Verify settings were saved with encryption
        saved_settings = mock_permanent_storage.save.call_args[0][0]
        assert saved_settings['api_key'] == 'encrypted_ollama-local'
    
    def test_validate_api_key_on_load(self):
        """Test API key validation when loading settings."""
        stored_settings = {
            'ai_enhancement_enabled': True,
            'llm_provider': 'openai',
            'api_key': 'encrypted_expired_key',
            'api_key_last_validated': '2020-01-01'
        }
        
        mock_storage = Mock()
        mock_storage.load.return_value = stored_settings
        mock_encryption = Mock()
        mock_encryption.decrypt.return_value = 'expired_key'
        
        persistence = AISettingsPersistence(
            storage=mock_storage,
            encryption=mock_encryption
        )
        
        loaded = persistence.load_settings(validate_api_key=True)
        
        assert loaded is not None
        assert 'api_key_status' in loaded
        # In real implementation, would check if key is expired
    
    def test_get_masked_api_key(self):
        """Test getting masked API key for display."""
        persistence = AISettingsPersistence()
        
        # Test various API key formats
        assert persistence.get_masked_api_key("sk-test123456") == "sk•••••••••56"  # 13 chars: sk + 9 bullets + 56
        assert persistence.get_masked_api_key("claude-key-abc") == "cl••••••••••bc"  # 14 chars: cl + 10 bullets + bc
        assert persistence.get_masked_api_key("short") == "•••••"  # 5 chars: all bullets
        assert persistence.get_masked_api_key("") == ""
    
    def test_encrypt_features(self):
        """Test that only sensitive data is encrypted."""
        mock_storage = Mock()
        mock_storage.save.return_value = True
        mock_encryption = Mock()
        mock_encryption.encrypt.side_effect = lambda x: f"encrypted_{x}"
        
        persistence = AISettingsPersistence(
            storage=mock_storage,
            encryption=mock_encryption
        )
        
        settings = {
            'ai_enhancement_enabled': True,
            'llm_provider': 'openai',
            'api_key': 'sk-secret',
            'confidence_threshold': 0.8,
            'features': {
                'nutritional_analysis': True,
                'price_analysis': False
            }
        }
        
        persistence.save_settings(settings)
        
        saved = mock_storage.save.call_args[0][0]
        
        # Only API key should be encrypted
        assert saved['api_key'] == 'encrypted_sk-secret'
        assert saved['llm_provider'] == 'openai'  # Not encrypted
        assert saved['features'] == settings['features']  # Not encrypted