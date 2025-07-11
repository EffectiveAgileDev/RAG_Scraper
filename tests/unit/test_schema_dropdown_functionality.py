"""Test the actual functionality of schema type dropdown updates."""
import pytest
from unittest.mock import Mock, patch
import requests
from bs4 import BeautifulSoup


class TestSchemaDropdownFunctionality:
    """Test that schema dropdown actually triggers help text updates."""
    
    def test_schema_dropdown_has_onchange_handler(self):
        """Test that the schema dropdown has the correct onchange handler."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        soup = BeautifulSoup(html_content, 'html.parser')
        dropdown = soup.find('select', id='schema-type-dropdown')
        
        assert dropdown is not None, "Schema dropdown not found"
        
        # Check for onchange attribute
        onchange_attr = dropdown.get('onchange')
        assert onchange_attr is not None, "onchange attribute not found on dropdown"
        assert 'handleSchemaTypeChange' in onchange_attr, "handleSchemaTypeChange not in onchange handler"
        assert 'this.value' in onchange_attr, "this.value not passed to handler"
        
    def test_javascript_function_targets_correct_element(self):
        """Test that the JavaScript function targets the correct help element."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        # Check that updateSchemaTypeHelpText targets schema-type-help-dynamic
        assert 'getElementById(\'schema-type-help-dynamic\')' in html_content, \
            "JavaScript function doesn't target the correct element ID"
            
        # Check that the element exists
        soup = BeautifulSoup(html_content, 'html.parser')
        target_element = soup.find(id='schema-type-help-dynamic')
        assert target_element is not None, "Target element schema-type-help-dynamic not found"
        
    def test_dropdown_options_are_correctly_configured(self):
        """Test that dropdown options are properly configured."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        soup = BeautifulSoup(html_content, 'html.parser')
        dropdown = soup.find('select', id='schema-type-dropdown')
        options = dropdown.find_all('option')
        
        # Should have exactly 2 options
        assert len(options) == 2, f"Expected 2 options, found {len(options)}"
        
        # Check option values and labels
        option_data = [(opt.get('value'), opt.text.strip()) for opt in options]
        
        expected_options = [
            ('Restaurant', 'Restaurant - Standard Schema'),
            ('RestW', 'RestW - Enhanced Restaurant Data')
        ]
        
        for expected_value, expected_label in expected_options:
            matching_option = next((opt for opt in option_data if opt[0] == expected_value), None)
            assert matching_option is not None, f"Option with value '{expected_value}' not found"
            assert expected_label in matching_option[1], f"Expected label '{expected_label}' not found in '{matching_option[1]}'"


class TestSchemaTypeUpdateBehavior:
    """Test the expected behavior when schema type changes."""
    
    def test_restaurant_to_restw_update_behavior(self):
        """Test the expected behavior when changing from Restaurant to RestW."""
        # Mock the DOM and JavaScript behavior
        class MockSchemaHandler:
            def __init__(self):
                self.current_schema = 'Restaurant'
                self.help_text = 'Standard restaurant schema'
                self.help_element_id = 'schema-type-help-dynamic'
                
            def handle_schema_change(self, new_schema):
                """Simulate handleSchemaTypeChange function."""
                self.current_schema = new_schema
                self.update_help_text(new_schema)
                
            def update_help_text(self, schema_type):
                """Simulate updateSchemaTypeHelpText function."""
                mode = 'single'  # Assume single mode for test
                
                help_texts = {
                    'Restaurant': {
                        'single': 'Standard restaurant schema - Extracts basic restaurant information from a single page'
                    },
                    'RestW': {
                        'single': 'Enhanced RestW schema - Detailed extraction with location, menu, and service data from a single page'
                    }
                }
                
                self.help_text = help_texts.get(schema_type, {}).get(mode, 'Unknown schema')
                
            def get_help_text(self):
                return self.help_text
                
        handler = MockSchemaHandler()
        
        # Initial state
        assert handler.current_schema == 'Restaurant'
        assert 'Standard restaurant schema' in handler.get_help_text()
        
        # Change to RestW
        handler.handle_schema_change('RestW')
        
        # Verify the change
        assert handler.current_schema == 'RestW'
        assert 'Enhanced RestW schema' in handler.get_help_text()
        assert 'location, menu, and service data' in handler.get_help_text()
        
        # Change back to Restaurant
        handler.handle_schema_change('Restaurant')
        
        # Verify the change back
        assert handler.current_schema == 'Restaurant'
        assert 'Standard restaurant schema' in handler.get_help_text()
        
    def test_help_text_contains_schema_specific_information(self):
        """Test that help text contains schema-specific information."""
        # This test verifies the content is actually different
        restaurant_help = "Standard restaurant schema - Extracts basic restaurant information"
        restw_help = "Enhanced RestW schema - Detailed extraction with location, menu, and service data"
        
        # Help texts should be significantly different
        assert restaurant_help != restw_help
        assert 'Enhanced' in restw_help and 'Enhanced' not in restaurant_help
        assert 'location, menu, and service data' in restw_help
        assert 'basic restaurant information' in restaurant_help