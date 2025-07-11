"""Unit tests for RestW UI components."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.web_interface.ui_components import RestWSchemaSelector, RestWFieldSelector, RestWHelpText
from src.config.restw_config import RestWConfig


class TestRestWSchemaSelector:
    """Test RestW schema selector component."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        selector = RestWSchemaSelector()
        assert selector.selected is False
        assert selector.industry is None
        assert selector.css_class == ""
        assert selector.disabled is False

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        selector = RestWSchemaSelector(
            selected=True,
            industry="Restaurant",
            css_class="custom-class",
            disabled=True
        )
        assert selector.selected is True
        assert selector.industry == "Restaurant"
        assert selector.css_class == "custom-class"
        assert selector.disabled is True

    def test_is_available_for_industry_restaurant(self):
        """Test RestW is available for Restaurant industry."""
        selector = RestWSchemaSelector()
        assert selector.is_available_for_industry("Restaurant") is True

    def test_is_available_for_industry_other(self):
        """Test RestW is not available for other industries."""
        selector = RestWSchemaSelector()
        assert selector.is_available_for_industry("Medical") is False
        assert selector.is_available_for_industry("Real Estate") is False
        assert selector.is_available_for_industry("Dental") is False

    def test_is_available_for_industry_none(self):
        """Test RestW is not available for None industry."""
        selector = RestWSchemaSelector()
        assert selector.is_available_for_industry(None) is False

    def test_get_display_label(self):
        """Test display label for RestW option."""
        selector = RestWSchemaSelector()
        label = selector.get_display_label()
        assert label == "RestW - Enhanced Restaurant Data"
        assert "WTEG" not in label

    def test_get_description(self):
        """Test description text for RestW option."""
        selector = RestWSchemaSelector()
        description = selector.get_description()
        assert len(description) > 0
        assert "structured" in description.lower()
        assert "restaurant" in description.lower()
        assert "WTEG" not in description

    def test_get_help_text(self):
        """Test help text for RestW option."""
        selector = RestWSchemaSelector()
        help_text = selector.get_help_text()
        assert len(help_text) > 0
        assert "location" in help_text.lower()
        assert "menu" in help_text.lower()
        assert "service" in help_text.lower()
        assert "WTEG" not in help_text

    def test_render_checkbox_not_selected(self):
        """Test rendering checkbox when not selected."""
        selector = RestWSchemaSelector(industry="Restaurant")
        html = selector.render_checkbox()
        
        assert 'type="checkbox"' in html
        assert 'name="restw_schema"' in html
        assert 'id="restw_schema"' in html
        assert 'checked' not in html

    def test_render_checkbox_selected(self):
        """Test rendering checkbox when selected."""
        selector = RestWSchemaSelector(selected=True, industry="Restaurant")
        html = selector.render_checkbox()
        
        assert 'type="checkbox"' in html
        assert 'name="restw_schema"' in html
        assert 'id="restw_schema"' in html
        assert 'checked' in html

    def test_render_checkbox_disabled(self):
        """Test rendering checkbox when disabled."""
        selector = RestWSchemaSelector(disabled=True, industry="Restaurant")
        html = selector.render_checkbox()
        
        assert 'type="checkbox"' in html
        assert 'disabled' in html

    def test_render_checkbox_with_css_class(self):
        """Test rendering checkbox with custom CSS class."""
        selector = RestWSchemaSelector(css_class="custom-class", industry="Restaurant")
        html = selector.render_checkbox()
        
        assert 'class="' in html
        assert 'custom-class' in html

    def test_render_checkbox_wrong_industry(self):
        """Test rendering checkbox for wrong industry returns empty."""
        selector = RestWSchemaSelector(industry="Medical")
        html = selector.render_checkbox()
        
        assert html == ""

    def test_render_label(self):
        """Test rendering label for RestW checkbox."""
        selector = RestWSchemaSelector()
        html = selector.render_label()
        
        assert 'for="restw_schema"' in html
        assert 'RestW - Enhanced Restaurant Data' in html
        assert 'WTEG' not in html

    def test_render_description(self):
        """Test rendering description for RestW option."""
        selector = RestWSchemaSelector()
        html = selector.render_description()
        
        assert 'class="restw-description"' in html
        assert len(html) > 0
        assert 'WTEG' not in html

    def test_render_complete_component(self):
        """Test rendering complete RestW component."""
        selector = RestWSchemaSelector(industry="Restaurant")
        html = selector.render()
        
        assert 'restw-schema-selector' in html
        assert 'type="checkbox"' in html
        assert 'RestW - Enhanced Restaurant Data' in html
        assert 'WTEG' not in html

    def test_are_options_visible_true(self):
        """Test options are visible when schema is selected."""
        selector = RestWSchemaSelector()
        assert selector.are_options_visible(schema_selected=True) is True

    def test_are_options_visible_false(self):
        """Test options are hidden when schema is not selected."""
        selector = RestWSchemaSelector()
        assert selector.are_options_visible(schema_selected=False) is False

    def test_get_javascript_handlers(self):
        """Test JavaScript handlers for RestW selector."""
        selector = RestWSchemaSelector()
        js_handlers = selector.get_javascript_handlers()
        
        assert 'onChange' in js_handlers
        assert 'onShow' in js_handlers
        assert 'onHide' in js_handlers
        assert len(js_handlers['onChange']) > 0


class TestRestWFieldSelector:
    """Test RestW field selector component."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        selector = RestWFieldSelector()
        assert selector.selected_fields == []
        assert selector.disabled is False

    def test_init_with_custom_fields(self):
        """Test initialization with custom fields."""
        fields = ['location', 'menu_items', 'services']
        selector = RestWFieldSelector(selected_fields=fields)
        assert selector.selected_fields == fields

    def test_get_available_fields(self):
        """Test getting available RestW fields."""
        selector = RestWFieldSelector()
        fields = selector.get_available_fields()
        
        expected_fields = ['location', 'menu_items', 'services_offered', 'contact_info', 'web_links']
        for field in expected_fields:
            assert field in fields

    def test_get_field_display_name(self):
        """Test getting display names for fields."""
        selector = RestWFieldSelector()
        
        assert selector.get_field_display_name('location') == 'Location Data'
        assert selector.get_field_display_name('menu_items') == 'Menu Items'
        assert selector.get_field_display_name('services_offered') == 'Services Offered'
        assert selector.get_field_display_name('contact_info') == 'Contact Information'
        assert selector.get_field_display_name('web_links') == 'Web Links'

    def test_get_field_description(self):
        """Test getting descriptions for fields."""
        selector = RestWFieldSelector()
        
        location_desc = selector.get_field_description('location')
        assert 'address' in location_desc.lower()
        assert 'WTEG' not in location_desc

        menu_desc = selector.get_field_description('menu_items')
        assert 'menu' in menu_desc.lower()
        assert 'WTEG' not in menu_desc

    def test_render_field_checkbox(self):
        """Test rendering individual field checkbox."""
        selector = RestWFieldSelector()
        html = selector.render_field_checkbox('location')
        
        assert 'type="checkbox"' in html
        assert 'name="restw_fields"' in html
        assert 'value="location"' in html

    def test_render_field_checkbox_selected(self):
        """Test rendering selected field checkbox."""
        selector = RestWFieldSelector(selected_fields=['location'])
        html = selector.render_field_checkbox('location')
        
        assert 'checked' in html

    def test_render_field_checkbox_not_selected(self):
        """Test rendering non-selected field checkbox."""
        selector = RestWFieldSelector(selected_fields=['menu_items'])
        html = selector.render_field_checkbox('location')
        
        assert 'checked' not in html

    def test_render_complete_selector(self):
        """Test rendering complete field selector."""
        selector = RestWFieldSelector()
        html = selector.render()
        
        assert 'restw-field-selector' in html
        assert 'Location Data' in html
        assert 'Menu Items' in html
        assert 'Services Offered' in html
        assert 'WTEG' not in html

    def test_get_selected_field_config(self):
        """Test getting configuration for selected fields."""
        selector = RestWFieldSelector(selected_fields=['location', 'menu_items'])
        config = selector.get_selected_field_config()
        
        assert 'location' in config
        assert 'menu_items' in config
        assert 'services_offered' not in config

    def test_validate_field_selection(self):
        """Test validating field selection."""
        selector = RestWFieldSelector()
        
        # Valid selection
        assert selector.validate_field_selection(['location', 'menu_items']) is True
        
        # Invalid selection
        assert selector.validate_field_selection(['invalid_field']) is False
        
        # Empty selection
        assert selector.validate_field_selection([]) is True


class TestRestWHelpText:
    """Test RestW help text component."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        help_text = RestWHelpText()
        assert help_text.show_icon is True
        assert help_text.collapsible is True

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        help_text = RestWHelpText(show_icon=False, collapsible=False)
        assert help_text.show_icon is False
        assert help_text.collapsible is False

    def test_get_general_help_text(self):
        """Test getting general help text."""
        help_text = RestWHelpText()
        text = help_text.get_general_help_text()
        
        assert len(text) > 0
        assert 'RestW' in text
        assert 'restaurant' in text.lower()
        assert 'WTEG' not in text

    def test_get_feature_help_text(self):
        """Test getting feature-specific help text."""
        help_text = RestWHelpText()
        
        location_text = help_text.get_feature_help_text('location')
        assert 'address' in location_text.lower()
        assert 'WTEG' not in location_text

        menu_text = help_text.get_feature_help_text('menu_items')
        assert 'menu' in menu_text.lower()
        assert 'WTEG' not in menu_text

    def test_get_usage_examples(self):
        """Test getting usage examples."""
        help_text = RestWHelpText()
        examples = help_text.get_usage_examples()
        
        assert len(examples) > 0
        assert isinstance(examples, list)
        
        for example in examples:
            assert 'WTEG' not in example

    def test_render_help_section(self):
        """Test rendering help section."""
        help_text = RestWHelpText()
        html = help_text.render_help_section()
        
        assert 'restw-help-section' in html
        assert 'RestW' in html
        assert 'WTEG' not in html

    def test_render_help_section_with_icon(self):
        """Test rendering help section with icon."""
        help_text = RestWHelpText(show_icon=True)
        html = help_text.render_help_section()
        
        assert 'help-icon' in html or '?' in html

    def test_render_help_section_without_icon(self):
        """Test rendering help section without icon."""
        help_text = RestWHelpText(show_icon=False)
        html = help_text.render_help_section()
        
        assert 'help-icon' not in html

    def test_render_collapsible_help(self):
        """Test rendering collapsible help text."""
        help_text = RestWHelpText(collapsible=True)
        html = help_text.render_collapsible_help()
        
        assert 'collapsible' in html
        assert 'details' in html or 'summary' in html

    def test_render_static_help(self):
        """Test rendering static help text."""
        help_text = RestWHelpText(collapsible=False)
        html = help_text.render_static_help()
        
        assert 'collapsible' not in html
        assert 'details' not in html
        assert len(html) > 0

    def test_render_complete_help(self):
        """Test rendering complete help component."""
        help_text = RestWHelpText()
        html = help_text.render()
        
        assert 'restw-help' in html
        assert 'RestW' in html
        assert 'WTEG' not in html

    def test_get_troubleshooting_tips(self):
        """Test getting troubleshooting tips."""
        help_text = RestWHelpText()
        tips = help_text.get_troubleshooting_tips()
        
        assert len(tips) > 0
        assert isinstance(tips, list)
        
        for tip in tips:
            assert 'WTEG' not in tip

    def test_get_best_practices(self):
        """Test getting best practices."""
        help_text = RestWHelpText()
        practices = help_text.get_best_practices()
        
        assert len(practices) > 0
        assert isinstance(practices, list)
        
        for practice in practices:
            assert 'WTEG' not in practice