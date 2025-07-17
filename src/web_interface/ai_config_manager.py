"""AI Configuration Manager for Web Interface."""

import json
import logging
import os
import re
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class AIConfigManager:
    """Manages AI configuration for the web interface."""

    def __init__(self):
        """Initialize AI Configuration Manager."""
        self.session_configs = {}
        self.default_config_path = "ai_config.json"
        self.valid_providers = ['openai', 'claude', 'ollama', 'llama_cpp', 'custom']
        self.valid_features = [
            'nutritional_analysis',
            'price_analysis', 
            'cuisine_classification',
            'multimodal_analysis',
            'pattern_learning',
            'dynamic_prompts'
        ]

    def get_default_config(self) -> Dict[str, Any]:
        """Get default AI configuration."""
        return {
            'ai_enhancement_enabled': False,
            'llm_provider': 'openai',
            'api_key': '',
            'features': {
                'nutritional_analysis': True,
                'price_analysis': True,
                'cuisine_classification': True,
                'multimodal_analysis': False,
                'pattern_learning': False,
                'dynamic_prompts': False
            },
            'confidence_threshold': 0.7,
            'custom_questions': [],
            'ollama_endpoint': 'http://localhost:11434',
            'llama_cpp_model_path': '',
            'custom_provider_name': '',
            'custom_base_url': '',
            'custom_model_name': '',
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }

    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate AI configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Validate LLM provider
        if 'llm_provider' in config:
            if config['llm_provider'] not in self.valid_providers:
                errors.append(f"Invalid LLM provider: {config['llm_provider']}")
        
        # Validate confidence threshold
        if 'confidence_threshold' in config:
            threshold = config['confidence_threshold']
            if not isinstance(threshold, (int, float)) or threshold < 0.1 or threshold > 1.0:
                errors.append("Confidence threshold must be between 0.1 and 1.0")
        
        # Validate API key format
        if 'api_key' in config:
            provider = config.get('llm_provider', 'openai')
            api_key = config['api_key']
            
            # For external providers, API key is required
            if provider in ['openai', 'claude', 'custom']:
                if not api_key or not api_key.strip():
                    errors.append(f"API key is required for {provider}")
                elif not validate_api_key(api_key, provider):
                    errors.append(f"Invalid API key format for {provider}")
            # For local providers, API key is optional
            elif provider in ['ollama', 'llama_cpp']:
                if api_key and not validate_api_key(api_key, provider):
                    errors.append(f"Invalid API key format for {provider}")
        
        # Validate features
        if 'features' in config:
            if not validate_feature_toggles(config['features']):
                errors.append("Invalid feature configuration")
        
        # Validate custom provider configuration
        if config.get('llm_provider') == 'custom':
            if 'custom_base_url' in config and config['custom_base_url']:
                base_url = config['custom_base_url'].strip()
                if not base_url.startswith(('http://', 'https://')):
                    errors.append("Custom base URL must start with http:// or https://")
        
        return len(errors) == 0, errors

    def save_config(self, config: Dict[str, Any], config_path: str = None) -> bool:
        """Save AI configuration to file.
        
        Args:
            config: Configuration to save
            config_path: Optional path to save config file
            
        Returns:
            Success status
        """
        try:
            config_path = config_path or self.default_config_path
            config['last_updated'] = datetime.now().isoformat()
            
            # Mask sensitive data before saving
            safe_config = self.mask_sensitive_data(config.copy())
            
            with open(config_path, 'w') as f:
                json.dump(safe_config, f, indent=2)
            
            logger.info(f"AI configuration saved to {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save AI configuration: {e}")
            return False

    def load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load AI configuration from file.
        
        Args:
            config_path: Optional path to config file
            
        Returns:
            Configuration dictionary
        """
        try:
            config_path = config_path or self.default_config_path
            
            # For testing, if mocked file read is available, use it
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"AI configuration loaded from {config_path}")
            return config
                
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info("No existing AI config found or invalid format, using defaults")
            return self.get_default_config()
        except Exception as e:
            logger.error(f"Failed to load AI configuration: {e}")
            return self.get_default_config()

    def mask_sensitive_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data in configuration.
        
        Args:
            config: Configuration to mask
            
        Returns:
            Configuration with masked sensitive data
        """
        if 'api_key' in config and config['api_key']:
            # Show only first few characters
            api_key = config['api_key']
            if len(api_key) > 6:
                config['api_key'] = api_key[:3] + '***'
            else:
                config['api_key'] = '***'
        
        return config

    def check_provider_availability(self, provider: str) -> bool:
        """Check if AI provider is available.
        
        Args:
            provider: Provider name to check
            
        Returns:
            Availability status
        """
        try:
            if provider == 'openai':
                # Check if OpenAI API is accessible
                response = requests.get('https://api.openai.com/v1/models', timeout=5)
                return response.status_code in [200, 401]  # 200 or 401 means API is accessible
                
            elif provider == 'claude':
                # Check if Anthropic API is accessible
                response = requests.get('https://api.anthropic.com', timeout=5)
                return response.status_code in [200, 401, 404]  # Service is running
                
            elif provider == 'ollama':
                # Check if local Ollama service is running
                response = requests.get('http://localhost:11434/api/version', timeout=5)
                return response.status_code == 200
                
            elif provider == 'llama_cpp':
                # For llama.cpp, just check if it's a valid provider name
                return True
                
            elif provider == 'custom':
                # For custom providers, availability depends on configuration
                # This would need to be checked with the actual custom endpoint
                return True
                
            return False
            
        except Exception as e:
            logger.debug(f"Provider {provider} not available: {e}")
            return False

    def merge_with_defaults(self, user_config: Dict[str, Any], default_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user configuration with defaults.
        
        Args:
            user_config: User provided configuration
            default_config: Default configuration
            
        Returns:
            Merged configuration
        """
        merged = default_config.copy()
        
        for key, value in user_config.items():
            if key == 'features' and isinstance(value, dict):
                # Merge features dictionary
                merged['features'].update(value)
            else:
                merged[key] = value
        
        return merged

    def set_session_config(self, session_id: str, config: Dict[str, Any]) -> None:
        """Set configuration for a specific session.
        
        Args:
            session_id: Session identifier
            config: Configuration to set
        """
        self.session_configs[session_id] = config

    def get_session_config(self, session_id: str) -> Dict[str, Any]:
        """Get configuration for a specific session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session configuration or defaults
        """
        return self.session_configs.get(session_id, self.get_default_config())

    def clear_session_config(self, session_id: str) -> None:
        """Clear configuration for a specific session.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.session_configs:
            del self.session_configs[session_id]


def validate_api_key(api_key: str, provider: str) -> bool:
    """Validate API key format for specific provider.
    
    Args:
        api_key: API key to validate
        provider: AI provider name
        
    Returns:
        Validation status
    """
    # For local providers, no API key needed (None or empty is fine)
    if provider in ['ollama', 'llama_cpp']:
        return True
    
    # Handle None/empty values
    if api_key is None:
        return False  # None is not valid for external providers
    
    # Convert to string and strip whitespace
    api_key = str(api_key).strip()
    
    if not api_key:  # Empty key is not valid for external providers
        return False
    
    # For external providers, accept any non-empty string
    # This allows for:
    # - Traditional formats (sk-xxx, claude-xxx)
    # - Custom formats (bearer tokens, etc.)
    # - Any length (short test keys, long production keys)
    # - Special characters and unicode
    if provider in ['openai', 'claude', 'custom']:
        return len(api_key) > 0
    
    # For unknown providers, also accept any non-empty string
    return len(api_key) > 0


def validate_feature_toggles(features: Dict[str, Any]) -> bool:
    """Validate AI feature toggle configuration.
    
    Args:
        features: Feature toggles dictionary
        
    Returns:
        Validation status
    """
    valid_features = [
        'nutritional_analysis',
        'price_analysis',
        'cuisine_classification', 
        'multimodal_analysis',
        'pattern_learning',
        'dynamic_prompts'
    ]
    
    for feature_name, enabled in features.items():
        # Check if feature name is valid
        if feature_name not in valid_features:
            return False
        
        # Check if value is boolean
        if not isinstance(enabled, bool):
            return False
    
    return True


def validate_confidence_threshold(threshold: Any) -> bool:
    """Validate confidence threshold value.
    
    Args:
        threshold: Threshold value to validate
        
    Returns:
        Validation status
    """
    if not isinstance(threshold, (int, float)):
        return False
    
    return 0.1 <= threshold <= 1.0