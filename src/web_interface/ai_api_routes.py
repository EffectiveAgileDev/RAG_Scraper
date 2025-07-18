"""AI API routes for web interface integration."""

import logging
import sys
import os
from flask import Blueprint, request, jsonify, session
from typing import Dict, Any

from src.web_interface.ai_config_manager import AIConfigManager
from src.web_interface.ai_settings_persistence import AISettingsPersistence, LocalStorageBackend
from src.ai.content_analyzer import AIContentAnalyzer

# Configure logging to output to stderr with environment variable control
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, log_level), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', stream=sys.stderr)
logger = logging.getLogger(__name__)

# Create blueprint for AI API routes
ai_api = Blueprint('ai_api', __name__, url_prefix='/api/ai')

# Initialize AI configuration manager
ai_config_manager = AIConfigManager()


@ai_api.route('/providers', methods=['GET'])
def get_ai_providers():
    """Get available AI providers and their status."""
    try:
        providers = {
            'openai': {
                'name': 'OpenAI GPT',
                'type': 'external',
                'requires_api_key': True,
                'available': ai_config_manager.check_provider_availability('openai'),
                'description': 'OpenAI GPT models (GPT-3.5, GPT-4)'
            },
            'claude': {
                'name': 'Anthropic Claude',
                'type': 'external', 
                'requires_api_key': True,
                'available': ai_config_manager.check_provider_availability('claude'),
                'description': 'Anthropic Claude AI assistant'
            },
            'ollama': {
                'name': 'Ollama (Local)',
                'type': 'local',
                'requires_api_key': False,
                'available': ai_config_manager.check_provider_availability('ollama'),
                'description': 'Local LLM via Ollama service'
            },
            'llama_cpp': {
                'name': 'llama.cpp (Local)',
                'type': 'local',
                'requires_api_key': False,
                'available': ai_config_manager.check_provider_availability('llama_cpp'),
                'description': 'Local LLM via llama.cpp'
            },
            'custom': {
                'name': 'Custom OpenAI-Compatible',
                'type': 'external',
                'requires_api_key': True,
                'available': ai_config_manager.check_provider_availability('custom'),
                'description': 'Custom OpenAI-compatible API endpoint'
            }
        }
        
        return jsonify({
            'success': True,
            'providers': providers,
            'default_provider': 'openai'
        })
        
    except Exception as e:
        logger.error(f"Error getting AI providers: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_api.route('/configure', methods=['POST'])
def configure_ai():
    """Configure AI settings for the session."""
    try:
        config_data = request.get_json()
        
        if not config_data:
            return jsonify({
                'success': False,
                'error': 'No configuration data provided'
            }), 400
        
        # Validate configuration
        is_valid, errors = ai_config_manager.validate_config(config_data)
        
        if not is_valid:
            return jsonify({
                'success': False,
                'error': 'Invalid configuration',
                'validation_errors': errors
            }), 400
        
        # Save configuration to session
        session_id = session.get('session_id', 'default')
        ai_config_manager.set_session_config(session_id, config_data)
        
        logger.info(f"AI configuration saved for session {session_id}")
        
        return jsonify({
            'success': True,
            'message': 'AI configuration saved successfully',
            'config': ai_config_manager.mask_sensitive_data(config_data.copy())
        })
        
    except Exception as e:
        logger.error(f"Error configuring AI: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_api.route('/analyze-content', methods=['POST'])
def analyze_content():
    """Analyze content using AI enhancement."""
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                'success': False,
                'error': 'No content data provided'
            }), 400
        
        content = request_data.get('content', '')
        menu_items = request_data.get('menu_items', [])
        analysis_type = request_data.get('analysis_type', 'nutritional')
        
        if not content and not menu_items:
            return jsonify({
                'success': False,
                'error': 'Content or menu_items required'
            }), 400
        
        # Get AI configuration from session
        session_id = session.get('session_id', 'default')
        ai_config = ai_config_manager.get_session_config(session_id)
        
        # Check if AI enhancement is enabled
        if not ai_config.get('ai_enhancement_enabled', False):
            return jsonify({
                'success': True,
                'ai_analysis': None,
                'fallback_used': True,
                'message': 'AI enhancement disabled, using traditional extraction'
            })
        
        # Initialize AI Content Analyzer with configuration
        api_key = ai_config.get('api_key')
        analyzer = AIContentAnalyzer(api_key=api_key)
        
        # Configure provider settings
        provider = ai_config.get('llm_provider', 'openai')
        provider_config = {
            'enabled': True,
            'api_key': api_key
        }
        
        # Add custom provider specific settings
        if provider == 'custom':
            provider_config.update({
                'base_url': ai_config.get('custom_base_url', ''),
                'model_name': ai_config.get('custom_model_name', 'gpt-3.5-turbo'),
                'provider_name': ai_config.get('custom_provider_name', 'Custom Provider')
            })
        
        # Update analyzer configuration
        analyzer.update_configuration({
            'providers': {
                provider: provider_config
            },
            'default_provider': provider,
            'multimodal_enabled': ai_config.get('features', {}).get('multimodal_analysis', False),
            'pattern_learning_enabled': ai_config.get('features', {}).get('pattern_learning', False),
            'dynamic_prompts_enabled': ai_config.get('features', {}).get('dynamic_prompts', False)
        })
        
        # Perform AI analysis
        result = analyzer.analyze_content(
            content=content,
            menu_items=menu_items,
            analysis_type=analysis_type,
            monitor_performance=True
        )
        
        # Add confidence score based on configuration
        confidence_threshold = ai_config.get('confidence_threshold', 0.7)
        integrated_confidence = analyzer.calculate_integrated_confidence(result)
        
        return jsonify({
            'success': True,
            'ai_analysis': result,
            'confidence_score': integrated_confidence,
            'confidence_threshold': confidence_threshold,
            'meets_threshold': integrated_confidence >= confidence_threshold,
            'provider_used': ai_config.get('llm_provider', 'openai'),
            'fallback_used': False
        })
        
    except Exception as e:
        logger.error(f"Error in AI content analysis: {e}")
        
        # Return graceful fallback
        return jsonify({
            'success': True,
            'ai_analysis': None,
            'fallback_used': True,
            'error_message': str(e),
            'message': 'AI analysis failed, using traditional extraction'
        })


@ai_api.route('/config', methods=['GET'])
def get_ai_config():
    """Get current AI configuration for the session."""
    try:
        session_id = session.get('session_id', 'default')
        config = ai_config_manager.get_session_config(session_id)
        
        # Mask sensitive data before returning
        safe_config = ai_config_manager.mask_sensitive_data(config.copy())
        
        return jsonify({
            'success': True,
            'config': safe_config
        })
        
    except Exception as e:
        logger.error(f"Error getting AI config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_api.route('/validate-api-key', methods=['POST'])
def validate_api_key():
    """Validate API key by making actual API call to provider."""
    try:
        request_data = request.get_json()
        
        if not request_data or 'api_key' not in request_data:
            return jsonify({
                'success': False,
                'error': 'API key is required'
            }), 400
        
        api_key = request_data.get('api_key', '').strip()
        provider = request_data.get('provider', 'openai')
        model_to_check = request_data.get('model', None)
        
        # Validate required fields
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key is required'
            }), 400
        
        # Validate OpenAI API key by calling their models endpoint
        if provider == 'openai':
            import requests
            try:
                response = requests.get(
                    "https://api.openai.com/v1/models",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    models_data = response.json()
                    available_models = [model['id'] for model in models_data.get('data', [])]
                    
                    # Check if specific model is available
                    model_available = True
                    message = 'API key is valid'
                    if model_to_check:
                        if model_to_check in available_models:
                            message = f'API key is valid and model "{model_to_check}" is available'
                        else:
                            model_available = False
                            message = f'API key is valid but model "{model_to_check}" is not available'
                    
                    response_data = {
                        'success': True,
                        'valid': True,
                        'message': message,
                        'provider': provider,
                        'models': available_models[:10]  # Limit to first 10 models
                    }
                    
                    # Add model availability info if specific model was checked
                    if model_to_check:
                        response_data['model_available'] = model_available
                        response_data['requested_model'] = model_to_check
                    
                    return jsonify(response_data)
                elif response.status_code == 401:
                    return jsonify({
                        'success': True,
                        'valid': False,
                        'message': 'Invalid API key - authentication failed',
                        'provider': provider
                    })
                elif response.status_code == 429:
                    return jsonify({
                        'success': True,
                        'valid': False,
                        'message': 'Rate limit exceeded - please try again later',
                        'provider': provider
                    })
                else:
                    return jsonify({
                        'success': True,
                        'valid': False,
                        'message': f'API returned status {response.status_code}',
                        'provider': provider
                    })
                    
            except requests.Timeout:
                return jsonify({
                    'success': True,
                    'valid': False,
                    'message': 'Request timeout - please check your network connection',
                    'provider': provider
                })
            except requests.RequestException as e:
                return jsonify({
                    'success': True,
                    'valid': False,
                    'message': f'Network error: {str(e)}',
                    'provider': provider
                })
            except Exception as e:
                # Handle generic network errors
                return jsonify({
                    'success': True,
                    'valid': False,
                    'message': f'Network error: {str(e)}',
                    'provider': provider
                })
        else:
            # For other providers, use basic format validation
            from src.web_interface.ai_config_manager import validate_api_key
            is_valid = validate_api_key(api_key, provider)
            
            return jsonify({
                'success': True,
                'valid': is_valid,
                'message': 'API key format is valid' if is_valid else 'Invalid API key format',
                'provider': provider
            })
        
    except Exception as e:
        logger.error(f"Error validating API key: {e}")
        return jsonify({
            'success': True,
            'valid': False,
            'message': f'Unexpected error: {str(e)}',
            'provider': 'unknown'
        })


@ai_api.route('/get-models', methods=['POST'])
def get_models():
    """Get available models for specified LLM provider."""
    try:
        request_data = request.get_json()
        
        if not request_data or 'provider' not in request_data:
            return jsonify({
                'success': False,
                'error': 'Provider is required'
            }), 400
        
        provider = request_data.get('provider', '').lower()
        api_key = request_data.get('api_key', '').strip()
        use_saved_key = request_data.get('use_saved_key', False)
        
        # If using saved key, try to load it from persistence
        if use_saved_key and not api_key:
            try:
                persistence = AISettingsPersistence()
                saved_settings = persistence.load_settings()
                if saved_settings and 'api_key' in saved_settings:
                    api_key = saved_settings['api_key']
            except Exception as e:
                current_app.logger.error(f"Failed to load saved API key: {str(e)}")
        
        if provider == 'openai':
            # OpenAI requires API key for model listing
            if not api_key:
                return jsonify({
                    'success': False,
                    'error': 'API key is required for OpenAI provider'
                }), 400
            
            import requests
            try:
                response = requests.get(
                    "https://api.openai.com/v1/models",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    models_data = response.json()
                    all_models = models_data.get('data', [])
                    
                    # Filter for text generation models only
                    text_models = []
                    for model in all_models:
                        model_id = model.get('id', '')
                        # Include GPT models for text generation, exclude DALL-E, Whisper, TTS, embedding models
                        if (model_id.startswith('gpt-') and 
                            'dall-e' not in model_id.lower() and 
                            'whisper' not in model_id.lower() and 
                            'tts' not in model_id.lower() and 
                            'embedding' not in model_id.lower()):
                            text_models.append({
                                'id': model_id,
                                'name': model_id,
                                'object': model.get('object', 'model'),
                                'owned_by': model.get('owned_by', 'openai')
                            })
                    
                    # Sort models by relevance (GPT-4 first, then GPT-3.5)
                    def model_sort_key(model):
                        model_id = model['id']
                        if 'gpt-4' in model_id:
                            return (0, model_id)  # GPT-4 models first
                        elif 'gpt-3.5' in model_id:
                            return (1, model_id)  # GPT-3.5 models second
                        else:
                            return (2, model_id)  # Other models last
                    
                    text_models.sort(key=model_sort_key)
                    
                    return jsonify({
                        'success': True,
                        'provider': provider,
                        'models': text_models,
                        'default_model': 'gpt-3.5-turbo',
                        'implemented': True
                    })
                    
                elif response.status_code == 401:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid API key - unauthorized access',
                        'provider': provider,
                        'models': []
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': f'API returned status {response.status_code}',
                        'provider': provider,
                        'models': []
                    })
                    
            except requests.Timeout:
                return jsonify({
                    'success': False,
                    'message': 'Request timeout - please check your network connection',
                    'provider': provider,
                    'models': []
                })
            except requests.RequestException as e:
                return jsonify({
                    'success': False,
                    'message': f'Network error: {str(e)}',
                    'provider': provider,
                    'models': []
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'Error fetching models: {str(e)}',
                    'provider': provider,
                    'models': []
                })
        
        elif provider in ['claude', 'ollama', 'local', 'custom']:
            # For other providers, return not implemented message
            return jsonify({
                'success': True,
                'provider': provider,
                'models': [],
                'message': f'Model listing not implemented for {provider.title()} provider',
                'implemented': False,
                'default_model': None
            })
        
        else:
            return jsonify({
                'success': False,
                'error': f'Unsupported provider: {provider}'
            }), 400
        
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_api.route('/test-connection', methods=['POST'])
def test_ai_connection():
    """Test connection to AI provider."""
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        provider = request_data.get('provider', 'openai')
        api_key = request_data.get('api_key', '')
        
        # Test connection based on provider
        if provider in ['openai', 'claude']:
            # For external providers, check if API key works
            analyzer = AIContentAnalyzer(api_key=api_key)
            
            # Try a simple test analysis
            test_result = analyzer.analyze_content(
                content="Test content for connection verification",
                menu_items=[{"name": "Test Item", "price": "$10"}],
                analysis_type="nutritional"
            )
            
            success = 'error' not in test_result
            
        else:
            # For local providers, check service availability
            success = ai_config_manager.check_provider_availability(provider)
        
        return jsonify({
            'success': True,
            'connection_successful': success,
            'provider': provider,
            'message': 'Connection successful' if success else 'Connection failed'
        })
        
    except Exception as e:
        logger.error(f"Error testing AI connection: {e}")
        return jsonify({
            'success': True,
            'connection_successful': False,
            'provider': request_data.get('provider', 'unknown'),
            'error_message': str(e)
        })


@ai_api.route('/clear-config', methods=['POST'])
def clear_ai_config():
    """Clear AI configuration for the session."""
    try:
        session_id = session.get('session_id', 'default')
        ai_config_manager.clear_session_config(session_id)
        
        return jsonify({
            'success': True,
            'message': 'AI configuration cleared'
        })
        
    except Exception as e:
        logger.error(f"Error clearing AI config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_api.route('/save-settings', methods=['POST'])
def save_ai_settings():
    """Save AI settings to persistent storage."""
    try:
        request_data = request.get_json()
        logger.debug(f"save_ai_settings called with data: {request_data}")
        
        if not request_data:
            logger.debug("No request data provided")
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        settings = request_data.get('settings', {})
        logger.debug(f"Extracted settings: {settings}")
        if not settings:
            logger.debug("No settings provided")
            return jsonify({
                'success': False,
                'error': 'No settings provided'
            }), 400
        
        # Initialize persistence manager
        persistence = AISettingsPersistence()
        logger.debug("Initialized persistence manager")
        
        # Save settings with encryption
        logger.debug("About to save settings...")
        success = persistence.save_settings(settings)
        logger.debug(f"Save result: {success}")
        
        if success:
            return jsonify({
                'success': True,
                'message': 'AI settings saved successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save AI settings'
            }), 500
            
    except Exception as e:
        logger.error(f"Exception in save_ai_settings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_api.route('/load-settings', methods=['GET'])
def load_ai_settings():
    """Load AI settings from persistent storage."""
    try:
        # Initialize persistence manager
        persistence = AISettingsPersistence()
        
        # Load settings with decryption
        settings = persistence.load_settings(validate_api_key=True)
        
        if settings:
            # Mask sensitive data for display
            masked_settings = settings.copy()
            if 'api_key' in masked_settings:
                masked_settings['api_key_masked'] = persistence.get_masked_api_key(masked_settings['api_key'])
                # Don't send actual API key to frontend
                del masked_settings['api_key']
            
            return jsonify({
                'success': True,
                'settings': masked_settings,
                'has_saved_settings': True
            })
        else:
            return jsonify({
                'success': True,
                'settings': None,
                'has_saved_settings': False
            })
            
    except Exception as e:
        logger.error(f"Error loading AI settings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_api.route('/clear-saved-settings', methods=['POST'])
def clear_saved_ai_settings():
    """Clear saved AI settings from persistent storage."""
    try:
        # Initialize persistence manager
        persistence = AISettingsPersistence()
        
        # Clear all saved settings
        success = persistence.clear_settings()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Saved AI settings cleared successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to clear saved AI settings'
            }), 500
            
    except Exception as e:
        logger.error(f"Error clearing saved AI settings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_api.route('/migrate-session', methods=['POST'])
def migrate_session_to_permanent():
    """Migrate current session settings to permanent storage."""
    try:
        session_id = session.get('session_id', 'default')
        session_settings = ai_config_manager.get_session_config(session_id)
        
        if not session_settings:
            return jsonify({
                'success': False,
                'error': 'No session settings to migrate'
            }), 400
        
        # Initialize persistence manager
        persistence = AISettingsPersistence()
        
        # Migrate settings to permanent storage
        success = persistence.migrate_session_to_permanent(session_settings)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Session settings migrated to permanent storage'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to migrate session settings'
            }), 500
            
    except Exception as e:
        logger.error(f"Error migrating session settings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Error handlers for AI API blueprint
@ai_api.errorhandler(404)
def ai_api_not_found(error):
    """Handle 404 errors for AI API routes."""
    return jsonify({
        'success': False,
        'error': 'AI API endpoint not found'
    }), 404


@ai_api.errorhandler(500)
def ai_api_internal_error(error):
    """Handle 500 errors for AI API routes."""
    logger.error(f"AI API internal error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error in AI API'
    }), 500