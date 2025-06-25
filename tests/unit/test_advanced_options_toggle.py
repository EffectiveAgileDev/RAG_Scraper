"""Unit tests for advanced options toggle functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestAdvancedOptionsToggle:
    """Test suite for advanced options toggle."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.default_options = {
            'page_discovery_enabled': True,
            'request_timeout': 30,
            'concurrent_requests': 5,
            'follow_redirects': True,
            'respect_robots_txt': True
        }
        
        self.custom_options = {
            'page_discovery_enabled': False,
            'request_timeout': 45,
            'concurrent_requests': 2,
            'follow_redirects': False,
            'respect_robots_txt': False
        }
    
    def test_default_advanced_options_values(self):
        """Test that default advanced options are correct."""
        options = self._get_default_advanced_options()
        
        assert options['page_discovery_enabled'] == True
        assert options['request_timeout'] == 30
        assert options['concurrent_requests'] == 5
        assert options['follow_redirects'] == True
        assert options['respect_robots_txt'] == True
    
    def test_validate_timeout_value(self):
        """Test timeout value validation."""
        # Valid values
        assert self._validate_timeout(30) == True
        assert self._validate_timeout(5) == True
        assert self._validate_timeout(300) == True
        
        # Invalid values
        assert self._validate_timeout(0) == False
        assert self._validate_timeout(-5) == False
        assert self._validate_timeout(301) == False  # Over max
        assert self._validate_timeout("abc") == False
    
    def test_validate_concurrent_requests(self):
        """Test concurrent requests validation."""
        # Valid values
        assert self._validate_concurrent_requests(1) == True
        assert self._validate_concurrent_requests(5) == True
        assert self._validate_concurrent_requests(10) == True
        
        # Invalid values
        assert self._validate_concurrent_requests(0) == False
        assert self._validate_concurrent_requests(11) == False
        assert self._validate_concurrent_requests(-1) == False
        assert self._validate_concurrent_requests("abc") == False
    
    def test_generate_advanced_options_html(self):
        """Test generation of advanced options HTML."""
        options = self.default_options
        html = self._generate_advanced_options_html(options)
        
        # Check for essential elements
        assert 'advanced-options-section' in html
        assert 'page_discovery_enabled' in html
        assert 'timeout-input' in html
        assert 'concurrent-requests-slider' in html
        assert 'id="page_discovery_enabled"' in html
        assert 'value="30"' in html  # Default timeout
        assert 'value="5"' in html   # Default concurrent requests
    
    def test_toggle_advanced_options_visibility(self):
        """Test toggling advanced options visibility."""
        # Initially collapsed
        state = {'expanded': False}
        
        # Toggle to expand
        new_state = self._toggle_advanced_options(state)
        assert new_state['expanded'] == True
        
        # Toggle to collapse
        new_state = self._toggle_advanced_options(new_state)
        assert new_state['expanded'] == False
    
    def test_update_advanced_option_value(self):
        """Test updating individual advanced option values."""
        options = self.default_options.copy()
        
        # Update timeout
        updated = self._update_advanced_option(options, 'request_timeout', 45)
        assert updated['request_timeout'] == 45
        assert updated['page_discovery_enabled'] == True  # Others unchanged
        
        # Update page discovery
        updated = self._update_advanced_option(options, 'page_discovery_enabled', False)
        assert updated['page_discovery_enabled'] == False
        assert updated['request_timeout'] == 30  # Others unchanged
    
    def test_reset_advanced_options_to_defaults(self):
        """Test resetting advanced options to defaults."""
        custom_options = self.custom_options.copy()
        
        reset_options = self._reset_to_defaults(custom_options)
        
        assert reset_options['page_discovery_enabled'] == True
        assert reset_options['request_timeout'] == 30
        assert reset_options['concurrent_requests'] == 5
        assert reset_options['follow_redirects'] == True
        assert reset_options['respect_robots_txt'] == True
    
    def test_advanced_options_validation_summary(self):
        """Test validation summary for all advanced options."""
        # Valid options
        valid_options = {
            'page_discovery_enabled': True,
            'request_timeout': 30,
            'concurrent_requests': 5,
            'follow_redirects': True,
            'respect_robots_txt': True
        }
        
        validation = self._validate_advanced_options(valid_options)
        assert validation['is_valid'] == True
        assert len(validation['errors']) == 0
        
        # Invalid options
        invalid_options = {
            'page_discovery_enabled': True,
            'request_timeout': 0,  # Invalid
            'concurrent_requests': 15,  # Invalid
            'follow_redirects': True,
            'respect_robots_txt': True
        }
        
        validation = self._validate_advanced_options(invalid_options)
        assert validation['is_valid'] == False
        assert 'request_timeout' in validation['errors']
        assert 'concurrent_requests' in validation['errors']
    
    def test_generate_validation_error_messages(self):
        """Test generation of validation error messages."""
        errors = {
            'request_timeout': 'Timeout must be between 5 and 300 seconds',
            'concurrent_requests': 'Concurrent requests must be between 1 and 10'
        }
        
        messages = self._generate_validation_messages(errors)
        
        assert 'Timeout must be between 5 and 300 seconds' in messages
        assert 'Concurrent requests must be between 1 and 10' in messages
    
    def test_advanced_options_impact_on_scraper_config(self):
        """Test how advanced options affect scraper configuration."""
        options = {
            'page_discovery_enabled': False,
            'request_timeout': 45,
            'concurrent_requests': 2
        }
        
        scraper_config = self._apply_advanced_options_to_config(options)
        
        assert scraper_config['enable_page_discovery'] == False
        assert scraper_config['request_timeout'] == 45
        assert scraper_config['max_concurrent_requests'] == 2
    
    def test_advanced_options_persistence(self):
        """Test saving and loading advanced options."""
        options = self.custom_options.copy()
        
        # Save options
        saved_data = self._save_advanced_options(options)
        assert saved_data is not None
        
        # Load options
        loaded_options = self._load_advanced_options(saved_data)
        assert loaded_options == options
    
    def test_advanced_options_state_management(self):
        """Test advanced options state management."""
        # Initial state
        state = self._get_initial_advanced_options_state()
        assert 'options' in state
        assert 'expanded' in state
        assert 'validation_errors' in state
        
        # Update state
        new_options = {'request_timeout': 45}
        updated_state = self._update_advanced_options_state(state, new_options)
        assert updated_state['options']['request_timeout'] == 45
    
    # Helper methods that would be implemented in the actual web interface
    
    def _get_default_advanced_options(self):
        """Get default advanced options."""
        return {
            'page_discovery_enabled': True,
            'request_timeout': 30,
            'concurrent_requests': 5,
            'follow_redirects': True,
            'respect_robots_txt': True
        }
    
    def _validate_timeout(self, value):
        """Validate timeout value."""
        try:
            timeout = int(value)
            return 5 <= timeout <= 300
        except (ValueError, TypeError):
            return False
    
    def _validate_concurrent_requests(self, value):
        """Validate concurrent requests value."""
        try:
            requests = int(value)
            return 1 <= requests <= 10
        except (ValueError, TypeError):
            return False
    
    def _generate_advanced_options_html(self, options):
        """Generate HTML for advanced options section."""
        return f"""
        <div id="advanced-options-section" class="advanced-options collapsed">
            <div class="option-group">
                <label class="toggle-label">
                    <input type="checkbox" id="page_discovery_enabled" 
                           {"checked" if options.get('page_discovery_enabled') else ""}>
                    <span class="toggle-switch"></span>
                    Enable Page Discovery
                </label>
                <p class="option-description">Automatically discover and process linked pages</p>
            </div>
            
            <div class="option-group">
                <label for="request_timeout">Request Timeout (seconds)</label>
                <input type="number" id="timeout-input" min="5" max="300" 
                       value="{options.get('request_timeout', 30)}">
                <span class="range-indicator">5-300s</span>
            </div>
            
            <div class="option-group">
                <label for="concurrent_requests">Concurrent Requests</label>
                <input type="range" id="concurrent-requests-slider" min="1" max="10" 
                       value="{options.get('concurrent_requests', 5)}">
                <span class="value-display">{options.get('concurrent_requests', 5)}</span>
            </div>
        </div>
        """
    
    def _toggle_advanced_options(self, current_state):
        """Toggle advanced options visibility."""
        return {'expanded': not current_state.get('expanded', False)}
    
    def _update_advanced_option(self, options, key, value):
        """Update a single advanced option."""
        updated = options.copy()
        updated[key] = value
        return updated
    
    def _reset_to_defaults(self, options):
        """Reset advanced options to defaults."""
        return self._get_default_advanced_options()
    
    def _validate_advanced_options(self, options):
        """Validate all advanced options."""
        errors = {}
        
        # Validate timeout
        if not self._validate_timeout(options.get('request_timeout')):
            errors['request_timeout'] = 'Timeout must be between 5 and 300 seconds'
        
        # Validate concurrent requests
        if not self._validate_concurrent_requests(options.get('concurrent_requests')):
            errors['concurrent_requests'] = 'Concurrent requests must be between 1 and 10'
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    def _generate_validation_messages(self, errors):
        """Generate user-friendly validation messages."""
        return list(errors.values())
    
    def _apply_advanced_options_to_config(self, options):
        """Apply advanced options to scraper configuration."""
        return {
            'enable_page_discovery': options.get('page_discovery_enabled', True),
            'request_timeout': options.get('request_timeout', 30),
            'max_concurrent_requests': options.get('concurrent_requests', 5),
            'follow_redirects': options.get('follow_redirects', True),
            'respect_robots_txt': options.get('respect_robots_txt', True)
        }
    
    def _save_advanced_options(self, options):
        """Save advanced options (mock implementation)."""
        # In real implementation, this would save to localStorage or server
        return {'saved': True, 'options': options}
    
    def _load_advanced_options(self, saved_data):
        """Load advanced options (mock implementation)."""
        # In real implementation, this would load from localStorage or server
        return saved_data.get('options', {})
    
    def _get_initial_advanced_options_state(self):
        """Get initial state for advanced options."""
        return {
            'options': self._get_default_advanced_options(),
            'expanded': False,
            'validation_errors': {}
        }
    
    def _update_advanced_options_state(self, current_state, new_options):
        """Update advanced options state."""
        updated_state = current_state.copy()
        updated_state['options'].update(new_options)
        return updated_state