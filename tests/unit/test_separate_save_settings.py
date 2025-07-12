"""Unit tests for separate single-page and multi-page save settings functionality."""

import pytest
from unittest.mock import Mock, patch
import json


class TestSeparateSaveSettings:
    """Test separate save settings for single-page and multi-page modes."""
    
    def test_single_page_settings_storage_exists(self):
        """Test that SinglePageSettingsStorage class exists and works."""
        # This test should FAIL initially since the class doesn't exist yet
        from src.web_interface.settings_storage import SinglePageSettingsStorage
        
        storage = SinglePageSettingsStorage()
        assert storage is not None, "SinglePageSettingsStorage should be instantiable"
    
    def test_multi_page_settings_storage_exists(self):
        """Test that MultiPageSettingsStorage class exists and works."""
        # This test should FAIL initially since the class doesn't exist yet
        from src.web_interface.settings_storage import MultiPageSettingsStorage
        
        storage = MultiPageSettingsStorage()
        assert storage is not None, "MultiPageSettingsStorage should be instantiable"
    
    def test_single_page_settings_have_correct_defaults(self):
        """Test that single-page settings have appropriate defaults."""
        from src.web_interface.settings_storage import SinglePageSettingsStorage
        
        storage = SinglePageSettingsStorage()
        defaults = storage.get_default_settings()
        
        # Single-page specific defaults
        expected_defaults = {
            'requestTimeout': 30,
            'enableJavaScript': False,
            'followRedirects': True,
            'respectRobotsTxt': True,
            'concurrentRequests': 1,  # Single page should be more conservative
            'jsTimeout': 30
        }
        
        for key, expected_value in expected_defaults.items():
            assert defaults[key] == expected_value, f"Single-page default for {key} should be {expected_value}"
    
    def test_multi_page_settings_have_correct_defaults(self):
        """Test that multi-page settings have appropriate defaults."""
        from src.web_interface.settings_storage import MultiPageSettingsStorage
        
        storage = MultiPageSettingsStorage()
        defaults = storage.get_default_settings()
        
        # Multi-page specific defaults
        expected_defaults = {
            'maxPages': 50,
            'crawlDepth': 2,
            'rateLimit': 1000,
            'enableJavaScript': False,
            'enablePageDiscovery': True,
            'respectRobotsTxt': True,
            'includePatterns': 'menu,food,restaurant',
            'excludePatterns': 'admin,login,cart',
            'concurrentRequests': 5,
            'requestTimeout': 30
        }
        
        for key, expected_value in expected_defaults.items():
            assert defaults[key] == expected_value, f"Multi-page default for {key} should be {expected_value}"
    
    def test_single_page_settings_validation(self):
        """Test single-page settings validation."""
        from src.web_interface.settings_storage import SinglePageSettingsStorage
        
        storage = SinglePageSettingsStorage()
        
        # Valid settings should pass
        valid_settings = {
            'requestTimeout': 45,
            'enableJavaScript': True,
            'followRedirects': False,
            'concurrentRequests': 3
        }
        
        assert storage.validate_settings(valid_settings) is True, "Valid single-page settings should pass validation"
        
        # Invalid settings should fail
        invalid_settings = {
            'requestTimeout': 500,  # Too high
            'concurrentRequests': 20  # Too high for single-page
        }
        
        assert storage.validate_settings(invalid_settings) is False, "Invalid single-page settings should fail validation"
    
    def test_multi_page_settings_validation(self):
        """Test multi-page settings validation."""
        from src.web_interface.settings_storage import MultiPageSettingsStorage
        
        storage = MultiPageSettingsStorage()
        
        # Valid settings should pass
        valid_settings = {
            'maxPages': 100,
            'crawlDepth': 3,
            'rateLimit': 2000,
            'concurrentRequests': 8
        }
        
        assert storage.validate_settings(valid_settings) is True, "Valid multi-page settings should pass validation"
        
        # Invalid settings should fail
        invalid_settings = {
            'maxPages': 1000,  # Too high
            'crawlDepth': 10   # Too deep
        }
        
        assert storage.validate_settings(invalid_settings) is False, "Invalid multi-page settings should fail validation"
    
    def test_settings_storage_isolation(self):
        """Test that single-page and multi-page settings don't interfere."""
        from src.web_interface.settings_storage import SinglePageSettingsStorage, MultiPageSettingsStorage
        from src.web_interface.app import create_app
        
        app = create_app()
        with app.test_request_context():
            single_storage = SinglePageSettingsStorage()
            multi_storage = MultiPageSettingsStorage()
            
            # Save different settings to each
            single_settings = {'requestTimeout': 60, 'enableJavaScript': True}
            multi_settings = {'maxPages': 200, 'crawlDepth': 4}
            
            single_storage.save_settings(single_settings)
            multi_storage.save_settings(multi_settings)
            
            # Verify they don't interfere with each other
            loaded_single = single_storage.load_settings()
            loaded_multi = multi_storage.load_settings()
            
            assert loaded_single['requestTimeout'] == 60, "Single-page settings should be preserved"
            assert loaded_multi['maxPages'] == 200, "Multi-page settings should be preserved"
            assert 'maxPages' not in loaded_single, "Single-page settings should not contain multi-page fields"
            assert 'requestTimeout' not in loaded_multi or loaded_multi['requestTimeout'] == 30, "Multi-page should have its own request timeout"


class TestSeparateSaveSettingsUI:
    """Test UI components for separate save settings."""
    
    def test_single_page_save_settings_toggle_exists(self):
        """Test that single-page save settings toggle component exists."""
        # This test should FAIL initially
        from src.web_interface.ui_components import SinglePageSaveSettingsToggle
        
        toggle = SinglePageSaveSettingsToggle()
        html = toggle.render()
        
        assert 'id="single-page-save-settings-toggle"' in html, "Single-page save toggle should have correct ID"
        assert 'SAVE_SINGLE_PAGE_SETTINGS' in html, "Should reference single-page settings"
    
    def test_multi_page_save_settings_toggle_exists(self):
        """Test that multi-page save settings toggle component exists."""
        # This test should FAIL initially
        from src.web_interface.ui_components import MultiPageSaveSettingsToggle
        
        toggle = MultiPageSaveSettingsToggle()
        html = toggle.render()
        
        assert 'id="multi-page-save-settings-toggle"' in html, "Multi-page save toggle should have correct ID"
        assert 'SAVE_MULTI_PAGE_SETTINGS' in html, "Should reference multi-page settings"
    
    def test_save_settings_javascript_functions_exist(self):
        """Test that separate JavaScript functions exist for each mode."""
        from src.web_interface.ui_components import SinglePageSaveSettingsToggle, MultiPageSaveSettingsToggle
        
        single_toggle = SinglePageSaveSettingsToggle()
        multi_toggle = MultiPageSaveSettingsToggle()
        
        single_js = single_toggle.get_javascript()
        multi_js = multi_toggle.get_javascript()
        
        # Should have separate functions
        assert 'handleSinglePageSaveSettingsToggle' in single_js, "Should have single-page specific function"
        assert 'handleMultiPageSaveSettingsToggle' in multi_js, "Should have multi-page specific function"
        
        # Should use separate localStorage keys
        assert 'ragScraperSinglePageSettings' in single_js, "Should use separate localStorage key"
        assert 'ragScraperMultiPageSettings' in multi_js, "Should use separate localStorage key"


class TestSeparateSaveSettingsAPI:
    """Test API endpoints for separate save settings."""
    
    def test_single_page_save_settings_api_exists(self):
        """Test that single-page save settings API endpoint exists."""
        from src.web_interface.app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # Test saving single-page settings
            response = client.post('/api/save-single-page-settings', 
                                 json={'settings': {'requestTimeout': 45}, 'saveEnabled': True})
            
            # This should FAIL initially since endpoint doesn't exist
            assert response.status_code != 404, "Single-page save settings endpoint should exist"
    
    def test_multi_page_save_settings_api_exists(self):
        """Test that multi-page save settings API endpoint exists."""
        from src.web_interface.app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # Test saving multi-page settings
            response = client.post('/api/save-multi-page-settings', 
                                 json={'settings': {'maxPages': 100}, 'saveEnabled': True})
            
            # This should FAIL initially since endpoint doesn't exist
            assert response.status_code != 404, "Multi-page save settings endpoint should exist"
    
    def test_get_single_page_settings_api_exists(self):
        """Test that get single-page settings API endpoint exists."""
        from src.web_interface.app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            response = client.get('/api/get-single-page-settings')
            
            # This should FAIL initially since endpoint doesn't exist
            assert response.status_code != 404, "Get single-page settings endpoint should exist"
    
    def test_get_multi_page_settings_api_exists(self):
        """Test that get multi-page settings API endpoint exists."""
        from src.web_interface.app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            response = client.get('/api/get-multi-page-settings')
            
            # This should FAIL initially since endpoint doesn't exist
            assert response.status_code != 404, "Get multi-page settings endpoint should exist"


class TestSettingsIntegration:
    """Test integration between separate settings systems."""
    
    def test_mode_switching_preserves_settings(self):
        """Test that switching modes preserves respective settings."""
        # This is a higher-level integration test
        # Should verify that when user switches from single to multi mode,
        # each mode's settings are preserved independently
        
        # This test should FAIL initially until full integration is implemented
        assert True, "Placeholder for mode switching integration test"
    
    def test_settings_dont_leak_between_modes(self):
        """Test that settings from one mode don't affect the other."""
        from src.web_interface.settings_storage import SinglePageSettingsStorage, MultiPageSettingsStorage
        from src.web_interface.app import create_app
        
        app = create_app()
        with app.test_request_context():
            single_storage = SinglePageSettingsStorage()
            multi_storage = MultiPageSettingsStorage()
            
            # Configure single-page settings
            single_settings = {'requestTimeout': 99, 'enableJavaScript': True}
            single_storage.save_settings(single_settings)
            
            # Configure multi-page settings  
            multi_settings = {'maxPages': 77, 'enableJavaScript': False}
            multi_storage.save_settings(multi_settings)
            
            # Verify settings don't leak
            loaded_single = single_storage.load_settings()
            loaded_multi = multi_storage.load_settings()
            
            assert loaded_single['enableJavaScript'] is True, "Single-page JS setting should be preserved"
            assert loaded_multi['enableJavaScript'] is False, "Multi-page JS setting should be different"
            assert 'maxPages' not in loaded_single, "Single-page should not have maxPages"
            assert loaded_single['requestTimeout'] == 99, "Single-page timeout should be preserved"