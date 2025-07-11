"""Unit tests for Save Settings functionality."""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.web_interface.ui_components import SaveSettingsToggle


class TestSaveSettingsToggle:
    """Test SaveSettingsToggle UI component."""
    
    def test_init_default_state(self):
        """Test default initialization state."""
        toggle = SaveSettingsToggle()
        assert toggle.checked is False
        assert toggle.css_class == "save-settings-toggle"
        assert toggle.label_text == "Save Settings"
    
    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        toggle = SaveSettingsToggle(
            checked=True,
            css_class="custom-toggle",
            label_text="Remember Settings"
        )
        assert toggle.checked is True
        assert toggle.css_class == "custom-toggle"
        assert toggle.label_text == "Remember Settings"
    
    def test_render_unchecked(self):
        """Test rendering unchecked toggle."""
        toggle = SaveSettingsToggle()
        html = toggle.render()
        
        assert 'id="save-settings-toggle"' in html
        assert 'class="save-settings-toggle"' in html
        assert 'type="checkbox"' in html
        assert 'id="save-settings-checkbox"' in html
        assert 'checked' not in html
        assert 'Save Settings' in html
        assert 'onchange="handleSaveSettingsToggle(this)"' in html
    
    def test_render_checked(self):
        """Test rendering checked toggle."""
        toggle = SaveSettingsToggle(checked=True)
        html = toggle.render()
        
        assert 'checked' in html
    
    def test_render_with_help_text(self):
        """Test rendering with help text."""
        toggle = SaveSettingsToggle()
        html = toggle.render()
        
        assert 'save-settings-help' in html
        assert 'ON:' in html
        assert 'OFF:' in html
        assert 'Settings persist' in html
        assert 'Settings reset to defaults' in html


class TestSettingsStorage:
    """Test settings storage functionality."""
    
    def test_gather_settings(self):
        """Test gathering current settings from form."""
        from src.web_interface.settings_storage import SettingsStorage
        
        storage = SettingsStorage()
        
        # Mock DOM elements
        mock_elements = {
            'scrapingMode': 'multi',
            'fileMode': 'multiple',
            'fileFormat': 'pdf',
            'maxPages': '100',
            'crawlDepth': '3',
            'includePatterns': 'menu,food',
            'excludePatterns': 'admin,login',
            'rateLimit': '2000',
            'enableJavaScript': True,
            'respectRobotsTxt': False
        }
        
        settings = storage.gather_settings(mock_elements)
        
        assert settings['scrapingMode'] == 'multi'
        assert settings['aggregationMode'] == 'multiple'
        assert settings['outputFormat'] == 'pdf'
        assert settings['maxPages'] == 100
        assert settings['crawlDepth'] == 3
        assert settings['includePatterns'] == 'menu,food'
        assert settings['excludePatterns'] == 'admin,login'
        assert settings['rateLimit'] == 2000
        assert settings['enableJavaScript'] is True
        assert settings['respectRobotsTxt'] is False
    
    def test_apply_settings(self):
        """Test applying saved settings to form."""
        from src.web_interface.settings_storage import SettingsStorage
        
        storage = SettingsStorage()
        
        saved_settings = {
            'scrapingMode': 'multi',
            'aggregationMode': 'multiple',
            'outputFormat': 'pdf',
            'maxPages': 100,
            'crawlDepth': 3,
            'includePatterns': 'menu,food',
            'excludePatterns': 'admin,login',
            'rateLimit': 2000,
            'enableJavaScript': True,
            'respectRobotsTxt': False
        }
        
        mock_form = Mock()
        storage.apply_settings(saved_settings, mock_form)
        
        # Verify the form was updated
        mock_form.set_scraping_mode.assert_called_with('multi')
        mock_form.set_aggregation_mode.assert_called_with('multiple')
        mock_form.set_output_format.assert_called_with('pdf')
        mock_form.set_max_pages.assert_called_with(100)
        mock_form.set_crawl_depth.assert_called_with(3)
    
    def test_get_default_settings(self):
        """Test getting default settings."""
        from src.web_interface.settings_storage import SettingsStorage
        
        storage = SettingsStorage()
        defaults = storage.get_default_settings()
        
        assert defaults['scrapingMode'] == 'single'
        assert defaults['aggregationMode'] == 'single'
        assert defaults['outputFormat'] == 'text'
        assert defaults['maxPages'] == 50
        assert defaults['crawlDepth'] == 2
        assert defaults['includePatterns'] == 'menu,food,restaurant'
        assert defaults['excludePatterns'] == 'admin,login,cart'
        assert defaults['rateLimit'] == 1000
        assert defaults['enableJavaScript'] is False
        assert defaults['respectRobotsTxt'] is True
    
    def test_validate_settings(self):
        """Test settings validation."""
        from src.web_interface.settings_storage import SettingsStorage
        
        storage = SettingsStorage()
        
        # Valid settings
        valid_settings = storage.get_default_settings()
        assert storage.validate_settings(valid_settings) is True
        
        # Invalid scraping mode
        invalid_settings = valid_settings.copy()
        invalid_settings['scrapingMode'] = 'invalid'
        assert storage.validate_settings(invalid_settings) is False
        
        # Invalid max pages
        invalid_settings = valid_settings.copy()
        invalid_settings['maxPages'] = 1000  # Too high
        assert storage.validate_settings(invalid_settings) is False
        
        # Invalid crawl depth
        invalid_settings = valid_settings.copy()
        invalid_settings['crawlDepth'] = 10  # Too deep
        assert storage.validate_settings(invalid_settings) is False


class TestSaveSettingsIntegration:
    """Test Save Settings integration with frontend."""
    
    @patch('src.web_interface.routes.main_routes.render_template')
    def test_save_settings_toggle_in_template_context(self, mock_render):
        """Test Save Settings toggle is included in template context."""
        from src.web_interface.routes.main_routes import index
        
        # Mock request
        with patch('flask.request') as mock_request:
            mock_request.method = 'GET'
            
            # Call index route
            response = index()
            
            # Check render_template was called
            mock_render.assert_called_once()
            
            # Get the context passed to render_template
            context = mock_render.call_args[1]
            
            # Verify save_settings_toggle is in context
            assert 'save_settings_toggle' in context
            assert isinstance(context['save_settings_toggle'], str)
            assert 'save-settings-toggle' in context['save_settings_toggle']
    
    @patch('src.web_interface.routes.api_routes.jsonify')
    def test_save_settings_api_endpoint(self, mock_jsonify):
        """Test API endpoint for saving settings."""
        from src.web_interface.routes.api_routes import save_settings
        
        # Mock request with settings data
        with patch('flask.request') as mock_request:
            mock_request.method = 'POST'
            mock_request.json = {
                'settings': {
                    'scrapingMode': 'multi',
                    'aggregationMode': 'multiple',
                    'outputFormat': 'pdf'
                },
                'saveEnabled': True
            }
            
            # Call save_settings endpoint
            response = save_settings()
            
            # Verify response
            mock_jsonify.assert_called_with({
                'success': True,
                'message': 'Settings saved successfully'
            })
    
    @patch('src.web_interface.routes.api_routes.jsonify')
    def test_get_saved_settings_api_endpoint(self, mock_jsonify):
        """Test API endpoint for retrieving saved settings."""
        from src.web_interface.routes.api_routes import get_saved_settings
        
        # Mock stored settings
        mock_settings = {
            'scrapingMode': 'multi',
            'aggregationMode': 'multiple',
            'outputFormat': 'pdf',
            'saveEnabled': True
        }
        
        with patch('src.web_interface.settings_storage.SettingsStorage.load_settings') as mock_load:
            mock_load.return_value = mock_settings
            
            # Call get_saved_settings endpoint
            response = get_saved_settings()
            
            # Verify response
            mock_jsonify.assert_called_with({
                'success': True,
                'settings': mock_settings
            })
    
    def test_javascript_functions_generated(self):
        """Test JavaScript functions for Save Settings are generated."""
        from src.web_interface.ui_components import SaveSettingsToggle
        
        toggle = SaveSettingsToggle()
        js_code = toggle.get_javascript()
        
        # Verify required JavaScript functions
        assert 'handleSaveSettingsToggle' in js_code
        assert 'saveCurrentSettings' in js_code
        assert 'loadSavedSettings' in js_code
        assert 'resetToDefaults' in js_code
        assert 'localStorage' in js_code
        assert 'ragScraperSettings' in js_code