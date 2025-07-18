"""AI Settings Persistence module for secure storage of AI configuration."""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from cryptography.fernet import Fernet
from pathlib import Path

logger = logging.getLogger(__name__)


class EncryptionService:
    """Service for encrypting sensitive data like API keys."""
    
    def __init__(self, key: Optional[bytes] = None):
        """Initialize encryption service with optional key."""
        if key:
            self._cipher = Fernet(key)
        else:
            # Use a persistent key derived from a consistent source
            self._cipher = Fernet(self._get_or_create_persistent_key())
    
    def generate_key(self) -> bytes:
        """Generate a new encryption key."""
        return Fernet.generate_key()
    
    def encrypt(self, data: str) -> str:
        """Encrypt a string value."""
        if not data:
            return ""
        
        try:
            encrypted_bytes = self._cipher.encrypt(data.encode('utf-8'))
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return data  # Return original if encryption fails
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt an encrypted string."""
        if not encrypted_data:
            return ""
        
        try:
            decrypted_bytes = self._cipher.decrypt(encrypted_data.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return encrypted_data  # Return original if decryption fails
    
    def _get_or_create_persistent_key(self) -> bytes:
        """Get or create a persistent encryption key."""
        key_file = Path.home() / '.rag_scraper' / 'encryption.key'
        
        # Ensure directory exists
        key_file.parent.mkdir(parents=True, exist_ok=True)
        
        if key_file.exists():
            # Load existing key
            try:
                with open(key_file, 'rb') as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Failed to load encryption key: {e}, generating new one")
        
        # Generate new key and save it
        key = Fernet.generate_key()
        try:
            with open(key_file, 'wb') as f:
                f.write(key)
            # Set restrictive permissions (owner read/write only)
            key_file.chmod(0o600)
        except Exception as e:
            logger.warning(f"Failed to save encryption key: {e}")
        
        return key


class StorageBackend:
    """Base class for storage backends."""
    
    def save(self, data: Dict[str, Any]) -> bool:
        """Save data to storage."""
        raise NotImplementedError
    
    def load(self) -> Optional[Dict[str, Any]]:
        """Load data from storage."""
        raise NotImplementedError
    
    def clear(self) -> bool:
        """Clear data from storage."""
        raise NotImplementedError


class LocalStorageBackend(StorageBackend):
    """Local file system storage backend."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize with storage path."""
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            # Default to user's home directory
            self.storage_path = Path.home() / '.rag_scraper' / 'ai_settings.json'
        
        # Ensure directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
    
    def save(self, data: Dict[str, Any]) -> bool:
        """Save data to local file."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False
    
    def load(self) -> Optional[Dict[str, Any]]:
        """Load data from local file."""
        if not self.storage_path.exists():
            return None
        
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            return None
    
    def clear(self) -> bool:
        """Clear local storage file."""
        try:
            if self.storage_path.exists():
                self.storage_path.unlink()
            return True
        except Exception as e:
            logger.error(f"Failed to clear settings: {e}")
            return False


class SessionStorageBackend(StorageBackend):
    """Session-based storage backend."""
    
    def __init__(self, session: Dict[str, Any]):
        """Initialize with session object."""
        self.session = session
    
    def save(self, data: Dict[str, Any]) -> bool:
        """Save data to session."""
        try:
            self.session['ai_settings'] = data
            return True
        except Exception as e:
            logger.error(f"Failed to save to session: {e}")
            return False
    
    def load(self) -> Optional[Dict[str, Any]]:
        """Load data from session."""
        return self.session.get('ai_settings')
    
    def clear(self) -> bool:
        """Clear data from session."""
        try:
            if 'ai_settings' in self.session:
                del self.session['ai_settings']
            return True
        except Exception as e:
            logger.error(f"Failed to clear session: {e}")
            return False


class AISettingsPersistence:
    """Main class for managing AI settings persistence."""
    
    SENSITIVE_FIELDS = ['api_key', 'api_secret', 'token']
    
    def __init__(self, 
                 storage: Optional[StorageBackend] = None,
                 encryption: Optional[EncryptionService] = None):
        """Initialize with storage and encryption services."""
        self.storage = storage or LocalStorageBackend()
        self.encryption = encryption or EncryptionService()
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save AI settings with encryption for sensitive data."""
        try:
            # Create a copy to avoid modifying original
            settings_to_save = settings.copy()
            
            # Encrypt sensitive fields
            for field in self.SENSITIVE_FIELDS:
                if field in settings_to_save and settings_to_save[field]:
                    settings_to_save[field] = self.encryption.encrypt(settings_to_save[field])
            
            # Add metadata
            settings_to_save['last_saved'] = datetime.now().isoformat()
            settings_to_save['version'] = '1.0'
            
            # Save to storage
            return self.storage.save(settings_to_save)
            
        except Exception as e:
            logger.error(f"Failed to save AI settings: {e}")
            return False
    
    def load_settings(self, validate_api_key: bool = False) -> Optional[Dict[str, Any]]:
        """Load AI settings with decryption for sensitive data."""
        try:
            # Load from storage
            settings = self.storage.load()
            if not settings:
                return None
            
            # Decrypt sensitive fields
            for field in self.SENSITIVE_FIELDS:
                if field in settings and settings[field]:
                    settings[field] = self.encryption.decrypt(settings[field])
            
            # Validate API key if requested
            if validate_api_key and 'api_key' in settings:
                # Check if API key might be expired (simplified check)
                last_validated = settings.get('api_key_last_validated')
                if last_validated:
                    # In real implementation, would check actual validity
                    settings['api_key_status'] = 'valid'  # or 'expired'
            
            return settings
            
        except Exception as e:
            logger.error(f"Failed to load AI settings: {e}")
            return None
    
    def clear_settings(self) -> bool:
        """Clear all AI settings."""
        return self.storage.clear()
    
    def migrate_session_to_permanent(self, session_settings: Dict[str, Any]) -> bool:
        """Migrate settings from session storage to permanent storage."""
        if not session_settings:
            return False
        
        # Save session settings using the regular save method
        return self.save_settings(session_settings)
    
    def encrypt_api_key(self, api_key: str) -> str:
        """Encrypt an API key."""
        return self.encryption.encrypt(api_key)
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt an API key."""
        return self.encryption.decrypt(encrypted_key)
    
    @staticmethod
    def get_masked_api_key(api_key: str) -> str:
        """Get masked version of API key for display."""
        if not api_key:
            return ""
        
        if len(api_key) <= 6:
            return "•" * len(api_key)
        
        # Show first 2 and last 2 characters, with proper masking
        masked_length = len(api_key) - 4
        return f"{api_key[:2]}{'•' * masked_length}{api_key[-2:]}"