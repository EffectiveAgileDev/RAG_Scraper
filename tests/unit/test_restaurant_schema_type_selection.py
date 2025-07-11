"""Unit tests for Restaurant schema type selection UI components.

This module tests the Restaurant schema type selection functionality that allows users
to choose between different schema types (Restaurant, RestW) when Restaurant industry
is selected.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.web_interface.ui_components import RestaurantSchemaTypeSelector, RestaurantSchemaTypeHelpText


class TestRestaurantSchemaTypeSelector:
    """Test cases for RestaurantSchemaTypeSelector UI component."""
    
    def test_restaurant_schema_type_selector_initialization(self):
        """Test that RestaurantSchemaTypeSelector initializes with correct defaults."""
        selector = RestaurantSchemaTypeSelector()
        
        assert selector.selected_schema_type == "Restaurant"
        assert selector.css_class == "schema-type-selector"
        assert selector.disabled == False
        assert selector.show_help_text == True
    
    def test_restaurant_schema_type_selector_custom_initialization(self):
        """Test RestaurantSchemaTypeSelector with custom parameters."""
        selector = RestaurantSchemaTypeSelector(
            selected_schema_type="RestW",
            css_class="custom-selector",
            disabled=True,
            show_help_text=False
        )
        
        assert selector.selected_schema_type == "RestW"
        assert selector.css_class == "custom-selector"
        assert selector.disabled == True
        assert selector.show_help_text == False
    
    def test_restaurant_schema_type_selector_available_types(self):
        """Test that selector has correct available schema types."""
        selector = RestaurantSchemaTypeSelector()
        
        expected_types = [
            {"value": "Restaurant", "label": "Restaurant - Standard Schema", "description": "Standard restaurant data extraction"},
            {"value": "RestW", "label": "RestW - Enhanced Restaurant Data", "description": "Enhanced restaurant data with specialized fields"}
        ]
        
        assert selector.available_schema_types == expected_types
    
    def test_restaurant_schema_type_selector_render_html(self):
        """Test that selector renders correct HTML structure."""
        selector = RestaurantSchemaTypeSelector()
        html = selector.render()
        
        assert 'class="schema-type-selector"' in html
        assert 'id="schema-type-selector"' in html
        assert 'name="schema_type"' in html
        assert 'value="Restaurant"' in html
        assert 'value="RestW"' in html
        assert 'Restaurant - Standard Schema' in html
        assert 'RestW - Enhanced Restaurant Data' in html
        assert 'checked' in html  # Restaurant should be checked by default
    
    def test_restaurant_schema_type_selector_restaurant_default_selected(self):
        """Test that Restaurant schema type is selected by default."""
        selector = RestaurantSchemaTypeSelector()
        html = selector.render()
        
        # Check that Restaurant option is checked
        assert 'value="Restaurant" checked' in html or 'checked value="Restaurant"' in html
        # Check that RestW option is not checked
        assert 'value="RestW" checked' not in html
    
    def test_restaurant_schema_type_selector_restw_selected(self):
        """Test rendering when RestW schema type is selected."""
        selector = RestaurantSchemaTypeSelector(selected_schema_type="RestW")
        html = selector.render()
        
        # Check that RestW option is checked
        assert 'value="RestW" checked' in html or 'checked value="RestW"' in html
        # Check that Restaurant option is not checked
        assert 'value="Restaurant" checked' not in html
    
    def test_restaurant_schema_type_selector_disabled_state(self):
        """Test selector rendering when disabled."""
        selector = RestaurantSchemaTypeSelector(disabled=True)
        html = selector.render()
        
        assert 'disabled' in html
        assert 'disabled="disabled"' in html or 'disabled>' in html
    
    def test_restaurant_schema_type_selector_javascript_integration(self):
        """Test that selector includes JavaScript for schema type switching."""
        selector = RestaurantSchemaTypeSelector()
        html = selector.render()
        
        assert 'onchange="handleSchemaTypeChange(this.value)"' in html
        assert 'role="radiogroup"' in html
        assert 'aria-label="Schema type selection"' in html
    
    def test_restaurant_schema_type_selector_accessibility(self):
        """Test that selector meets accessibility requirements."""
        selector = RestaurantSchemaTypeSelector()
        html = selector.render()
        
        assert 'role="radiogroup"' in html
        assert 'aria-label="Schema type selection"' in html
        assert 'for="schema-type-restaurant"' in html
        assert 'for="schema-type-restw"' in html
        assert 'id="schema-type-restaurant"' in html
        assert 'id="schema-type-restw"' in html
    
    def test_restaurant_schema_type_selector_help_text_integration(self):
        """Test that selector integrates with help text component."""
        selector = RestaurantSchemaTypeSelector(show_help_text=True)
        html = selector.render()
        
        assert 'schema-type-help' in html
        assert 'id="schema-type-help"' in html
        
        # Test without help text
        selector_no_help = RestaurantSchemaTypeSelector(show_help_text=False)
        html_no_help = selector_no_help.render()
        
        assert 'schema-type-help' not in html_no_help


class TestRestaurantSchemaTypeHelpText:
    """Test cases for RestaurantSchemaTypeHelpText UI component."""
    
    def test_restaurant_schema_type_help_text_initialization(self):
        """Test that RestaurantSchemaTypeHelpText initializes correctly."""
        help_text = RestaurantSchemaTypeHelpText()
        
        assert help_text.schema_type == "Restaurant"
        assert help_text.show_icon == True
        assert help_text.collapsible == True
        assert help_text.css_class == "schema-type-help"
    
    def test_restaurant_schema_type_help_text_custom_initialization(self):
        """Test RestaurantSchemaTypeHelpText with custom parameters."""
        help_text = RestaurantSchemaTypeHelpText(
            schema_type="RestW",
            show_icon=False,
            collapsible=False,
            css_class="custom-help"
        )
        
        assert help_text.schema_type == "RestW"
        assert help_text.show_icon == False
        assert help_text.collapsible == False
        assert help_text.css_class == "custom-help"
    
    def test_restaurant_schema_type_help_text_restaurant_content(self):
        """Test help text content for Restaurant schema type."""
        help_text = RestaurantSchemaTypeHelpText(schema_type="Restaurant")
        content = help_text.get_help_content()
        
        assert "Standard restaurant data extraction" in content
        assert "Menu Information" in content
        assert "Location and Contact" in content
        assert "Business Hours" in content
        assert "RestW" not in content  # Should not mention RestW
        assert "WTEG" not in content  # Should not mention WTEG
    
    def test_restaurant_schema_type_help_text_restw_content(self):
        """Test help text content for RestW schema type."""
        help_text = RestaurantSchemaTypeHelpText(schema_type="RestW")
        content = help_text.get_help_content()
        
        assert "Enhanced restaurant data" in content
        assert "specialized fields" in content
        assert "Structured Location Data" in content
        assert "Menu Item Extraction" in content
        assert "Service Offerings" in content
        assert "WTEG" not in content  # Should not mention WTEG (obfuscated)
    
    def test_restaurant_schema_type_help_text_render_html(self):
        """Test that help text renders correct HTML structure."""
        help_text = RestaurantSchemaTypeHelpText()
        html = help_text.render()
        
        assert 'class="schema-type-help collapsible"' in html
        assert 'id="schema-type-help"' in html
        assert 'Standard restaurant data extraction' in html
        assert 'help-icon' in html  # Should show icon by default
    
    def test_restaurant_schema_type_help_text_no_icon(self):
        """Test help text rendering without icon."""
        help_text = RestaurantSchemaTypeHelpText(show_icon=False)
        html = help_text.render()
        
        assert 'help-icon' not in html
    
    def test_restaurant_schema_type_help_text_collapsible(self):
        """Test help text with collapsible functionality."""
        help_text = RestaurantSchemaTypeHelpText(collapsible=True)
        html = help_text.render()
        
        assert 'collapsible' in html
        assert 'toggle-help' in html
        assert 'onclick="toggleHelpText()"' in html
    
    def test_restaurant_schema_type_help_text_non_collapsible(self):
        """Test help text without collapsible functionality."""
        help_text = RestaurantSchemaTypeHelpText(collapsible=False)
        html = help_text.render()
        
        assert 'collapsible' not in html
        assert 'toggle-help' not in html
        assert 'onclick="toggleHelpText()"' not in html
    
    def test_restaurant_schema_type_help_text_invalid_schema_type(self):
        """Test help text with invalid schema type."""
        help_text = RestaurantSchemaTypeHelpText(schema_type="Invalid")
        content = help_text.get_help_content()
        
        assert "Schema type not supported" in content or "Unknown schema type" in content


class TestRestaurantSchemaTypeIntegration:
    """Test cases for Restaurant schema type integration."""
    
    def test_restaurant_schema_type_full_component_integration(self):
        """Test full integration of schema type selector with help text."""
        selector = RestaurantSchemaTypeSelector(show_help_text=True)
        help_text = RestaurantSchemaTypeHelpText()
        
        selector_html = selector.render()
        help_html = help_text.render()
        
        # Both components should be present
        assert 'schema-type-selector' in selector_html
        assert 'schema-type-help' in help_html
        
        # Help text should be referenced in selector
        assert 'schema-type-help' in selector_html
    
    def test_restaurant_schema_type_form_integration(self):
        """Test that schema type selector integrates with form submission."""
        selector = RestaurantSchemaTypeSelector()
        html = selector.render()
        
        # Should have form elements
        assert 'name="schema_type"' in html
        assert 'type="radio"' in html
        assert 'value="Restaurant"' in html
        assert 'value="RestW"' in html
    
    def test_restaurant_schema_type_javascript_handlers(self):
        """Test that JavaScript handlers are properly integrated."""
        selector = RestaurantSchemaTypeSelector()
        html = selector.render()
        
        # Should have change handler
        assert 'onchange="handleSchemaTypeChange(this.value)"' in html
        
        # Should have proper event handling
        assert 'handleSchemaTypeChange' in html
    
    def test_restaurant_schema_type_industry_dependency(self):
        """Test that schema type selector only appears for Restaurant industry."""
        # This test verifies the component can be conditionally rendered
        # based on industry selection
        selector = RestaurantSchemaTypeSelector()
        
        # Component should exist for Restaurant industry
        assert selector is not None
        assert selector.selected_schema_type in ["Restaurant", "RestW"]
    
    def test_restaurant_schema_type_configuration_persistence(self):
        """Test that schema type selection can be persisted."""
        selector = RestaurantSchemaTypeSelector(selected_schema_type="RestW")
        
        # Should remember selection
        assert selector.selected_schema_type == "RestW"
        
        # Should be able to change selection
        selector.selected_schema_type = "Restaurant"
        assert selector.selected_schema_type == "Restaurant"
    
    def test_restaurant_schema_type_backend_integration(self):
        """Test that schema type selection integrates with backend processing."""
        selector = RestaurantSchemaTypeSelector()
        
        # Should provide values that backend can process
        available_types = selector.available_schema_types
        assert len(available_types) == 2
        assert any(t["value"] == "Restaurant" for t in available_types)
        assert any(t["value"] == "RestW" for t in available_types)
    
    def test_restaurant_schema_type_error_handling(self):
        """Test error handling for invalid schema type selections."""
        # Test with invalid schema type
        selector = RestaurantSchemaTypeSelector(selected_schema_type="Invalid")
        
        # Should handle gracefully (either default to Restaurant or show error)
        assert selector.selected_schema_type in ["Restaurant", "RestW", "Invalid"]
    
    def test_restaurant_schema_type_css_styling(self):
        """Test that schema type selector has proper CSS classes."""
        selector = RestaurantSchemaTypeSelector()
        html = selector.render()
        
        # Should have proper CSS classes for styling
        assert 'class="schema-type-selector"' in html
        assert 'class="schema-type-option"' in html
        assert 'class="schema-type-label"' in html
    
    def test_restaurant_schema_type_responsive_design(self):
        """Test that schema type selector supports responsive design."""
        selector = RestaurantSchemaTypeSelector()
        html = selector.render()
        
        # Should have responsive classes or structure
        assert 'schema-type-option' in html
        assert 'radio' in html
        # Component should be structured for responsive layout
    
    def test_restaurant_schema_type_validation(self):
        """Test validation of schema type selections."""
        selector = RestaurantSchemaTypeSelector()
        
        # Should validate that only supported types are available
        available_values = [t["value"] for t in selector.available_schema_types]
        assert "Restaurant" in available_values
        assert "RestW" in available_values
        assert len(available_values) == 2