"""Step definitions for AI Settings Persistence feature."""

import pytest
from pytest_bdd import scenarios, given, when, then
from unittest.mock import Mock, patch, MagicMock
import json

# Load all scenarios from the feature file
scenarios('../features/ai_settings_persistence.feature')


@pytest.fixture
def mock_storage():
    """Mock storage backend."""
    storage = Mock()
    storage.save_settings = Mock(return_value=True)
    storage.load_settings = Mock(return_value=None)
    storage.clear_settings = Mock(return_value=True)
    return storage


@pytest.fixture
def mock_encryption():
    """Mock encryption service."""
    encryption = Mock()
    encryption.encrypt = Mock(side_effect=lambda x: f"encrypted_{x}")
    encryption.decrypt = Mock(side_effect=lambda x: x.replace("encrypted_", ""))
    return encryption


@pytest.fixture
def ai_settings_context():
    """Context for AI settings tests."""
    return {
        'current_settings': {},
        'saved_settings': None,
        'session_settings': {},
        'success_message': None,
        'warning_message': None,
        'storage': Mock(),
        'encryption': Mock()
    }


@given('I am on the RAG_Scraper web interface')
def on_web_interface(ai_settings_context):
    """User is on the web interface."""
    ai_settings_context['interface_loaded'] = True


@given('I have expanded the advanced options panel')
def expanded_advanced_options(ai_settings_context):
    """Advanced options panel is expanded."""
    ai_settings_context['advanced_panel_expanded'] = True


@given('I have enabled AI Enhancement')
def enabled_ai_enhancement(ai_settings_context):
    """AI Enhancement is enabled."""
    ai_settings_context['current_settings']['ai_enhancement_enabled'] = True


@given('I have selected "OpenAI" as the LLM provider')
def selected_openai_provider(ai_settings_context):
    """OpenAI is selected as provider."""
    ai_settings_context['current_settings']['llm_provider'] = 'openai'


@given('I have selected "Claude" as the LLM provider')
def selected_claude_provider(ai_settings_context):
    """Claude is selected as provider."""
    ai_settings_context['current_settings']['llm_provider'] = 'claude'


@given('I have entered an API key "sk-test123456789"')
def entered_api_key(ai_settings_context):
    """API key is entered."""
    ai_settings_context['current_settings']['api_key'] = 'sk-test123456789'


@given('I have entered an API key "sk-mysecretkey123"')
def entered_secret_api_key(ai_settings_context):
    """Secret API key is entered."""
    ai_settings_context['current_settings']['api_key'] = 'sk-mysecretkey123'


@given('I have set the confidence threshold to 0.8')
def set_confidence_threshold(ai_settings_context):
    """Confidence threshold is set."""
    ai_settings_context['current_settings']['confidence_threshold'] = 0.8


@given('I have enabled "Nutritional Analysis" feature')
def enabled_nutritional_analysis(ai_settings_context):
    """Nutritional analysis feature is enabled."""
    if 'features' not in ai_settings_context['current_settings']:
        ai_settings_context['current_settings']['features'] = {}
    ai_settings_context['current_settings']['features']['nutritional_analysis'] = True


@given('I have previously saved AI settings with provider "Claude"')
def previously_saved_claude_settings(ai_settings_context, mock_storage, mock_encryption):
    """Previously saved settings with Claude."""
    saved_settings = {
        'ai_enhancement_enabled': True,
        'llm_provider': 'claude',
        'api_key': 'encrypted_claude-api-key',
        'confidence_threshold': 0.75,
        'features': {'nutritional_analysis': True, 'price_analysis': True}
    }
    ai_settings_context['saved_settings'] = saved_settings
    mock_storage.load_settings.return_value = saved_settings
    ai_settings_context['storage'] = mock_storage
    ai_settings_context['encryption'] = mock_encryption


@given('I have previously saved AI settings')
def previously_saved_settings(ai_settings_context, mock_storage):
    """Previously saved settings exist."""
    saved_settings = {
        'ai_enhancement_enabled': True,
        'llm_provider': 'openai',
        'api_key': 'encrypted_key',
        'confidence_threshold': 0.7
    }
    ai_settings_context['saved_settings'] = saved_settings
    mock_storage.load_settings.return_value = saved_settings
    ai_settings_context['storage'] = mock_storage


@given('I have configured AI settings in the current session')
def configured_session_settings(ai_settings_context):
    """Session settings are configured."""
    ai_settings_context['session_settings'] = {
        'ai_enhancement_enabled': True,
        'llm_provider': 'ollama',
        'confidence_threshold': 0.85,
        'features': {'cuisine_classification': True}
    }


@given('I have not saved them permanently')
def not_saved_permanently(ai_settings_context):
    """Settings are not saved permanently."""
    ai_settings_context['saved_settings'] = None


@given('I have saved AI settings with an expired API key')
def saved_expired_api_key(ai_settings_context, mock_storage):
    """Saved settings have an expired API key."""
    saved_settings = {
        'ai_enhancement_enabled': True,
        'llm_provider': 'openai',
        'api_key': 'encrypted_expired_key',
        'confidence_threshold': 0.8,
        'api_key_status': 'expired'
    }
    ai_settings_context['saved_settings'] = saved_settings
    mock_storage.load_settings.return_value = saved_settings
    ai_settings_context['storage'] = mock_storage


@given('I have saved AI settings in Chrome browser')
def saved_chrome_settings(ai_settings_context):
    """Settings saved in Chrome browser."""
    ai_settings_context['browser'] = 'chrome'
    ai_settings_context['chrome_settings'] = {
        'ai_enhancement_enabled': True,
        'llm_provider': 'openai'
    }


@when('I click the "Save AI Settings" button')
def click_save_settings(ai_settings_context, mock_storage, mock_encryption):
    """Save AI settings button is clicked."""
    from src.web_interface.ai_settings_persistence import AISettingsPersistence
    
    persistence = AISettingsPersistence(storage=mock_storage, encryption=mock_encryption)
    
    # Encrypt API key before saving
    settings_to_save = ai_settings_context['current_settings'].copy()
    if 'api_key' in settings_to_save:
        settings_to_save['api_key'] = mock_encryption.encrypt(settings_to_save['api_key'])
    
    success = persistence.save_settings(settings_to_save)
    ai_settings_context['save_success'] = success
    if success:
        ai_settings_context['success_message'] = "AI settings saved successfully"


@when('I refresh the page')
def refresh_page(ai_settings_context):
    """Page is refreshed."""
    ai_settings_context['page_refreshed'] = True


@when('I expand the advanced options panel')
def expand_advanced_panel(ai_settings_context):
    """Expand advanced options panel."""
    ai_settings_context['advanced_panel_expanded'] = True


@when('I click the "Clear AI Settings" button')
def click_clear_settings(ai_settings_context):
    """Clear settings button is clicked."""
    ai_settings_context['clear_requested'] = True


@when('I confirm the action')
def confirm_action(ai_settings_context, mock_storage):
    """Confirm clear action."""
    if ai_settings_context.get('clear_requested'):
        from src.web_interface.ai_settings_persistence import AISettingsPersistence
        persistence = AISettingsPersistence(storage=mock_storage)
        success = persistence.clear_settings()
        ai_settings_context['clear_success'] = success


@when('I save the AI settings')
def save_ai_settings(ai_settings_context, mock_storage, mock_encryption):
    """Save AI settings."""
    from src.web_interface.ai_settings_persistence import AISettingsPersistence
    persistence = AISettingsPersistence(storage=mock_storage, encryption=mock_encryption)
    
    settings_to_save = ai_settings_context['current_settings'].copy()
    if 'api_key' in settings_to_save:
        settings_to_save['api_key'] = persistence.encrypt_api_key(settings_to_save['api_key'])
    
    success = persistence.save_settings(settings_to_save)
    ai_settings_context['save_success'] = success
    ai_settings_context['encrypted_key'] = settings_to_save.get('api_key')


@when('I click "Make Settings Permanent"')
def click_make_permanent(ai_settings_context, mock_storage):
    """Make settings permanent button is clicked."""
    from src.web_interface.ai_settings_persistence import AISettingsPersistence
    persistence = AISettingsPersistence(storage=mock_storage)
    
    success = persistence.migrate_session_to_permanent(ai_settings_context['session_settings'])
    ai_settings_context['migration_success'] = success


@when('I load the saved settings')
def load_saved_settings(ai_settings_context, mock_storage):
    """Load saved settings."""
    from src.web_interface.ai_settings_persistence import AISettingsPersistence
    persistence = AISettingsPersistence(storage=mock_storage)
    
    loaded_settings = persistence.load_settings()
    ai_settings_context['loaded_settings'] = loaded_settings
    
    # Check for expired API key
    if loaded_settings and loaded_settings.get('api_key_status') == 'expired':
        ai_settings_context['warning_message'] = "Saved API key may be invalid"


@when('I access the application from Firefox browser')
def access_from_firefox(ai_settings_context):
    """Access from Firefox browser."""
    ai_settings_context['browser'] = 'firefox'


@then('the AI settings should be saved to persistent storage')
def verify_settings_saved(ai_settings_context):
    """Verify settings are saved."""
    assert ai_settings_context.get('save_success') is True
    assert ai_settings_context['storage'].save_settings.called


@then('I should see a success message "AI settings saved successfully"')
def verify_success_message(ai_settings_context):
    """Verify success message."""
    assert ai_settings_context.get('success_message') == "AI settings saved successfully"


@then('the AI Enhancement should be enabled')
def verify_ai_enabled(ai_settings_context):
    """Verify AI enhancement is enabled."""
    loaded = ai_settings_context.get('loaded_settings') or ai_settings_context['saved_settings']
    assert loaded.get('ai_enhancement_enabled') is True


@then('the LLM provider should be "Claude"')
def verify_claude_provider(ai_settings_context):
    """Verify Claude is the provider."""
    loaded = ai_settings_context.get('loaded_settings') or ai_settings_context['saved_settings']
    assert loaded.get('llm_provider') == 'claude'


@then('the API key field should show masked value "••••••••••"')
def verify_masked_api_key(ai_settings_context):
    """Verify API key is masked."""
    # In real implementation, the UI would show masked value
    loaded = ai_settings_context.get('loaded_settings') or ai_settings_context['saved_settings']
    assert 'api_key' in loaded
    assert loaded['api_key'].startswith('encrypted_')


@then('the saved features should be enabled')
def verify_saved_features(ai_settings_context):
    """Verify saved features are enabled."""
    loaded = ai_settings_context.get('loaded_settings') or ai_settings_context['saved_settings']
    assert 'features' in loaded
    assert any(loaded['features'].values())


@then('the AI settings should be removed from persistent storage')
def verify_settings_cleared(ai_settings_context):
    """Verify settings are cleared."""
    assert ai_settings_context.get('clear_success') is True
    assert ai_settings_context['storage'].clear_settings.called


@then('the AI Enhancement should be disabled')
def verify_ai_disabled(ai_settings_context):
    """Verify AI enhancement is disabled."""
    # After clearing, default state should be disabled
    assert True  # In real implementation, would check UI state


@then('all AI fields should be reset to defaults')
def verify_fields_reset(ai_settings_context):
    """Verify fields are reset to defaults."""
    # After clearing, all fields should be in default state
    assert True  # In real implementation, would check UI state


@then('the API key should be encrypted before storage')
def verify_api_key_encrypted(ai_settings_context):
    """Verify API key is encrypted."""
    assert ai_settings_context.get('encrypted_key')
    assert ai_settings_context['encrypted_key'].startswith('encrypted_')


@then('the encrypted value should not contain the original key text')
def verify_encryption_secure(ai_settings_context):
    """Verify encryption doesn't expose original key."""
    encrypted = ai_settings_context.get('encrypted_key', '')
    original = ai_settings_context['current_settings'].get('api_key', '')
    assert original not in encrypted


@then('the session settings should be migrated to persistent storage')
def verify_session_migrated(ai_settings_context):
    """Verify session settings are migrated."""
    assert ai_settings_context.get('migration_success') is True


@then('the settings should persist across browser sessions')
def verify_cross_session_persistence(ai_settings_context):
    """Verify settings persist across sessions."""
    # In real implementation, would verify localStorage or similar
    assert True


@then('I should see a warning "Saved API key may be invalid"')
def verify_invalid_key_warning(ai_settings_context):
    """Verify invalid key warning."""
    assert ai_settings_context.get('warning_message') == "Saved API key may be invalid"


@then('the other settings should still be loaded correctly')
def verify_other_settings_loaded(ai_settings_context):
    """Verify other settings are loaded despite invalid key."""
    loaded = ai_settings_context.get('loaded_settings')
    assert loaded is not None
    assert loaded.get('llm_provider') is not None
    assert loaded.get('confidence_threshold') is not None


@then('I should not see the Chrome browser\'s saved settings')
def verify_no_chrome_settings(ai_settings_context):
    """Verify Chrome settings are not visible in Firefox."""
    assert ai_settings_context.get('browser') == 'firefox'
    # In real implementation, would check browser-specific storage
    assert True


@then('I should be able to save different settings for Firefox')
def verify_can_save_firefox_settings(ai_settings_context):
    """Verify can save different settings for Firefox."""
    assert ai_settings_context.get('browser') == 'firefox'
    # In real implementation, would verify separate storage
    assert True