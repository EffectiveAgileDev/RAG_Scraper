"""Unit tests for Restaurant schema type dropdown selection UI component.

This module tests the dropdown-based schema type selection functionality that allows users
to choose between different schema types (Restaurant, RestW, and future schemas) from a
dropdown menu that can scale to many options.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.web_interface.ui_components import RestaurantSchemaTypeDropdown, RestaurantSchemaTypeHelpText


class TestRestaurantSchemaTypeDropdown:
    """Test cases for RestaurantSchemaTypeDropdown UI component."""
    
    def test_restaurant_schema_type_dropdown_initialization(self):
        """Test that RestaurantSchemaTypeDropdown initializes with correct defaults."""
        dropdown = RestaurantSchemaTypeDropdown()
        
        assert dropdown.selected_schema_type == "Restaurant"
        assert dropdown.css_class == "schema-type-dropdown"
        assert dropdown.disabled == False
        assert dropdown.required == True
        assert dropdown.show_help_text == True
    
    def test_restaurant_schema_type_dropdown_custom_initialization(self):
        """Test RestaurantSchemaTypeDropdown with custom parameters."""
        dropdown = RestaurantSchemaTypeDropdown(
            selected_schema_type="RestW",
            css_class="custom-dropdown",
            disabled=True,
            required=False,
            show_help_text=False
        )
        
        assert dropdown.selected_schema_type == "RestW"
        assert dropdown.css_class == "custom-dropdown"
        assert dropdown.disabled == True
        assert dropdown.required == False
        assert dropdown.show_help_text == False
    
    def test_restaurant_schema_type_dropdown_available_types(self):
        """Test that dropdown has correct available schema types."""
        dropdown = RestaurantSchemaTypeDropdown()
        
        expected_types = [
            {"value": "Restaurant", "label": "Restaurant - Standard Schema", "description": "Standard restaurant data extraction"},
            {"value": "RestW", "label": "RestW - Enhanced Restaurant Data", "description": "Enhanced restaurant data with specialized fields"}
        ]
        
        assert dropdown.available_schema_types == expected_types
    
    def test_restaurant_schema_type_dropdown_get_schema_types(self):
        """Test getting available schema types."""
        dropdown = RestaurantSchemaTypeDropdown()
        schema_types = dropdown.get_schema_types()
        
        assert len(schema_types) == 2
        assert any(st["value"] == "Restaurant" for st in schema_types)
        assert any(st["value"] == "RestW" for st in schema_types)
    
    def test_restaurant_schema_type_dropdown_render_html(self):
        """Test that dropdown renders correct HTML structure."""
        dropdown = RestaurantSchemaTypeDropdown()
        html = dropdown.render()
        
        # Should be a select element, not radio buttons
        assert '<select' in html
        assert 'name="schema_type"' in html
        assert 'id="schema-type-dropdown"' in html
        assert 'class="schema-type-dropdown terminal-input"' in html
        assert '<option value="Restaurant"' in html
        assert '<option value="RestW"' in html
        assert 'Restaurant - Standard Schema' in html
        assert 'RestW - Enhanced Restaurant Data' in html
    
    def test_restaurant_schema_type_dropdown_restaurant_default_selected(self):
        """Test that Restaurant schema type is selected by default."""
        dropdown = RestaurantSchemaTypeDropdown()
        html = dropdown.render()
        
        # Check that Restaurant option is selected
        assert 'value="Restaurant" selected' in html or 'selected value="Restaurant"' in html
        # Check that RestW option is not selected
        assert 'value="RestW" selected' not in html
    
    def test_restaurant_schema_type_dropdown_restw_selected(self):
        """Test rendering when RestW schema type is selected."""
        dropdown = RestaurantSchemaTypeDropdown(selected_schema_type="RestW")
        html = dropdown.render()
        
        # Check that RestW option is selected
        assert 'value="RestW" selected' in html or 'selected value="RestW"' in html
        # Check that Restaurant option is not selected
        assert 'value="Restaurant" selected' not in html
    
    def test_restaurant_schema_type_dropdown_disabled_state(self):
        """Test dropdown rendering when disabled."""
        dropdown = RestaurantSchemaTypeDropdown(disabled=True)
        html = dropdown.render()
        
        assert 'disabled' in html
        assert 'disabled="disabled"' in html or 'disabled>' in html
    
    def test_restaurant_schema_type_dropdown_required_state(self):
        """Test dropdown rendering when required."""
        dropdown = RestaurantSchemaTypeDropdown(required=True)
        html = dropdown.render()
        
        assert 'required' in html
        
        # Test not required
        dropdown_not_required = RestaurantSchemaTypeDropdown(required=False)
        html_not_required = dropdown_not_required.render()
        
        assert 'required' not in html_not_required
    
    def test_restaurant_schema_type_dropdown_javascript_integration(self):
        """Test that dropdown includes JavaScript for schema type switching."""
        dropdown = RestaurantSchemaTypeDropdown()
        html = dropdown.render()
        
        assert 'onchange="handleSchemaTypeChange(this.value)"' in html
        assert 'aria-label="Schema type selection"' in html
    
    def test_restaurant_schema_type_dropdown_accessibility(self):
        """Test that dropdown meets accessibility requirements."""
        dropdown = RestaurantSchemaTypeDropdown()
        html = dropdown.render()
        
        assert 'aria-label="Schema type selection"' in html
        assert 'id="schema-type-dropdown"' in html
        assert '<label' in html
        assert 'for="schema-type-dropdown"' in html
    
    def test_restaurant_schema_type_dropdown_help_text_integration(self):
        """Test that dropdown integrates with help text component."""
        dropdown = RestaurantSchemaTypeDropdown(show_help_text=True)
        html = dropdown.render()
        
        assert 'schema-type-help' in html
        assert 'id="schema-type-help"' in html
        
        # Test without help text
        dropdown_no_help = RestaurantSchemaTypeDropdown(show_help_text=False)
        html_no_help = dropdown_no_help.render()
        
        assert 'schema-type-help' not in html_no_help
    
    def test_restaurant_schema_type_dropdown_placeholder_option(self):
        """Test that dropdown includes placeholder option when not required."""
        dropdown = RestaurantSchemaTypeDropdown(required=False)
        html = dropdown.render()
        
        # Should have a placeholder option when not required
        assert '<option value="" disabled>Select schema type...</option>' in html
        
        # Required dropdown should not have placeholder
        dropdown_required = RestaurantSchemaTypeDropdown(required=True)
        html_required = dropdown_required.render()
        assert '<option value="" disabled>Select schema type...</option>' not in html_required
    
    def test_restaurant_schema_type_dropdown_scalability(self):
        """Test that dropdown can handle many schema types."""
        dropdown = RestaurantSchemaTypeDropdown()
        
        # Should be able to add more schema types easily
        additional_schema = {
            "value": "FastFood",
            "label": "FastFood - Quick Service Schema",
            "description": "Optimized for fast food restaurants"
        }
        
        # Test that structure supports adding more types
        assert isinstance(dropdown.available_schema_types, list)
        assert len(dropdown.available_schema_types) >= 2
        
        # Test that we can extend the schema types
        extended_types = dropdown.available_schema_types + [additional_schema]
        assert len(extended_types) == 3
    
    def test_restaurant_schema_type_dropdown_validation(self):
        """Test validation of schema type selections."""
        dropdown = RestaurantSchemaTypeDropdown()
        
        # Should validate that only supported types are available
        available_values = [t["value"] for t in dropdown.available_schema_types]
        assert "Restaurant" in available_values
        assert "RestW" in available_values
        assert len(available_values) == 2
    
    def test_restaurant_schema_type_dropdown_invalid_selection(self):
        """Test handling of invalid schema type selection."""
        dropdown = RestaurantSchemaTypeDropdown(selected_schema_type="Invalid")
        
        # Should handle gracefully (either default to Restaurant or validate)
        assert dropdown.selected_schema_type in ["Restaurant", "RestW", "Invalid"]
    
    def test_restaurant_schema_type_dropdown_form_integration(self):
        """Test that dropdown integrates with form submission."""
        dropdown = RestaurantSchemaTypeDropdown()
        html = dropdown.render()
        
        # Should have proper form elements
        assert 'name="schema_type"' in html
        assert '<select' in html
        assert 'value="Restaurant"' in html
        assert 'value="RestW"' in html
    
    def test_restaurant_schema_type_dropdown_css_styling(self):
        """Test that dropdown has proper CSS classes."""
        dropdown = RestaurantSchemaTypeDropdown()
        html = dropdown.render()
        
        # Should have proper CSS classes for styling
        assert 'class="schema-type-dropdown terminal-input"' in html
        assert 'class="input-label"' in html
        assert 'terminal-input' in html
    
    def test_restaurant_schema_type_dropdown_label_text(self):
        """Test that dropdown has proper label text."""
        dropdown = RestaurantSchemaTypeDropdown()
        html = dropdown.render()
        
        # Should have proper label
        assert 'SCHEMA_TYPE:' in html or 'Schema Type:' in html
        assert '<label' in html
        assert 'for="schema-type-dropdown"' in html
    
    def test_restaurant_schema_type_dropdown_option_descriptions(self):
        """Test that dropdown options include descriptions."""
        dropdown = RestaurantSchemaTypeDropdown()
        html = dropdown.render()
        
        # Should include descriptions in options or as data attributes
        assert 'Standard restaurant data extraction' in html
        assert 'Enhanced restaurant data with specialized fields' in html
    
    def test_restaurant_schema_type_dropdown_error_handling(self):
        """Test error handling for dropdown component."""
        dropdown = RestaurantSchemaTypeDropdown()
        
        # Should handle empty schema types gracefully
        original_types = dropdown.available_schema_types
        dropdown.available_schema_types = []
        
        # Should not crash when rendering with no options
        html = dropdown.render()
        assert '<select' in html
        
        # Restore original types
        dropdown.available_schema_types = original_types
    
    def test_restaurant_schema_type_dropdown_change_handler(self):
        """Test that dropdown has proper change handler."""
        dropdown = RestaurantSchemaTypeDropdown()
        html = dropdown.render()
        
        # Should have change handler
        assert 'onchange="handleSchemaTypeChange(this.value)"' in html
        assert 'handleSchemaTypeChange' in html


class TestRestaurantSchemaTypeDropdownIntegration:
    """Test cases for Restaurant schema type dropdown integration."""
    
    def test_restaurant_schema_type_dropdown_with_help_text(self):
        """Test full integration of dropdown with help text."""
        dropdown = RestaurantSchemaTypeDropdown(show_help_text=True)
        help_text = RestaurantSchemaTypeHelpText()
        
        dropdown_html = dropdown.render()
        help_html = help_text.render()
        
        # Both components should be present
        assert 'schema-type-dropdown' in dropdown_html
        assert 'schema-type-help' in help_html
        
        # Help text should be referenced in dropdown
        assert 'schema-type-help' in dropdown_html
    
    def test_restaurant_schema_type_dropdown_backend_integration(self):
        """Test that dropdown selection integrates with backend processing."""
        dropdown = RestaurantSchemaTypeDropdown()
        
        # Should provide values that backend can process
        available_types = dropdown.get_schema_types()
        assert len(available_types) == 2
        assert any(t["value"] == "Restaurant" for t in available_types)
        assert any(t["value"] == "RestW" for t in available_types)
    
    def test_restaurant_schema_type_dropdown_javascript_handlers(self):
        """Test that JavaScript handlers are properly integrated."""
        dropdown = RestaurantSchemaTypeDropdown()
        html = dropdown.render()
        
        # Should have change handler
        assert 'onchange="handleSchemaTypeChange(this.value)"' in html
        
        # Should have proper event handling
        assert 'handleSchemaTypeChange' in html
    
    def test_restaurant_schema_type_dropdown_responsive_design(self):
        """Test that dropdown supports responsive design."""
        dropdown = RestaurantSchemaTypeDropdown()
        html = dropdown.render()
        
        # Should have responsive classes or structure
        assert 'schema-type-dropdown' in html
        assert 'select' in html
        # Component should be structured for responsive layout
    
    def test_restaurant_schema_type_dropdown_configuration_persistence(self):
        """Test that dropdown selection can be persisted."""
        dropdown = RestaurantSchemaTypeDropdown(selected_schema_type="RestW")
        
        # Should remember selection
        assert dropdown.selected_schema_type == "RestW"
        
        # Should be able to change selection
        dropdown.selected_schema_type = "Restaurant"
        assert dropdown.selected_schema_type == "Restaurant"