"""Unit tests for industry selection UI components."""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestIndustryDropdownComponent:
    """Test cases for industry dropdown UI component."""

    def test_render_dropdown_html_with_all_industries(self):
        """Test that dropdown renders with all industries."""
        from src.web_interface.ui_components import IndustryDropdown
        
        with patch('src.config.industry_config.IndustryConfig') as mock_config:
            mock_instance = Mock()
            mock_instance.get_industry_list.return_value = [
                "Restaurant", "Real Estate", "Medical"
            ]
            mock_config.return_value = mock_instance
            
            dropdown = IndustryDropdown()
            html = dropdown.render()
            
            assert '<select' in html
            assert 'name="industry"' in html
            assert 'id="industry"' in html
            assert '<option value="Restaurant">Restaurant</option>' in html
            assert '<option value="Real Estate">Real Estate</option>' in html
            assert '<option value="Medical">Medical</option>' in html

    def test_render_dropdown_with_selected_industry(self):
        """Test that dropdown shows selected industry."""
        from src.web_interface.ui_components import IndustryDropdown
        
        with patch('src.config.industry_config.IndustryConfig') as mock_config:
            mock_instance = Mock()
            mock_instance.get_industry_list.return_value = ["Restaurant", "Medical"]
            mock_config.return_value = mock_instance
            
            dropdown = IndustryDropdown(selected="Medical")
            html = dropdown.render()
            
            assert '<option value="Medical" selected>Medical</option>' in html
            assert '<option value="Restaurant">Restaurant</option>' in html

    def test_render_dropdown_with_placeholder(self):
        """Test that dropdown includes placeholder option."""
        from src.web_interface.ui_components import IndustryDropdown
        
        with patch('src.config.industry_config.IndustryConfig') as mock_config:
            mock_instance = Mock()
            mock_instance.get_industry_list.return_value = ["Restaurant"]
            mock_config.return_value = mock_instance
            
            dropdown = IndustryDropdown()
            html = dropdown.render()
            
            assert '<option value="">Select an industry...</option>' in html

    def test_render_dropdown_with_required_attribute(self):
        """Test that dropdown has required attribute."""
        from src.web_interface.ui_components import IndustryDropdown
        
        with patch('src.config.industry_config.IndustryConfig') as mock_config:
            mock_instance = Mock()
            mock_instance.get_industry_list.return_value = []
            mock_config.return_value = mock_instance
            
            dropdown = IndustryDropdown(required=True)
            html = dropdown.render()
            
            assert 'required' in html

    def test_render_dropdown_with_custom_css_class(self):
        """Test that dropdown can have custom CSS classes."""
        from src.web_interface.ui_components import IndustryDropdown
        
        with patch('src.config.industry_config.IndustryConfig') as mock_config:
            mock_instance = Mock()
            mock_instance.get_industry_list.return_value = []
            mock_config.return_value = mock_instance
            
            dropdown = IndustryDropdown(css_class="form-control industry-select")
            html = dropdown.render()
            
            assert 'class="industry-dropdown form-control industry-select"' in html

    def test_render_dropdown_with_error_state(self):
        """Test that dropdown can show error state."""
        from src.web_interface.ui_components import IndustryDropdown
        
        with patch('src.config.industry_config.IndustryConfig') as mock_config:
            mock_instance = Mock()
            mock_instance.get_industry_list.return_value = []
            mock_config.return_value = mock_instance
            
            dropdown = IndustryDropdown(error=True)
            html = dropdown.render()
            
            assert 'error' in html or 'is-invalid' in html


class TestIndustryHelpText:
    """Test cases for industry help text display."""

    def test_render_help_text_for_industry(self):
        """Test rendering help text for a specific industry."""
        from src.web_interface.ui_components import IndustryHelpText
        
        with patch('src.web_interface.ui_components.IndustryConfig') as mock_config:
            mock_instance = Mock()
            mock_instance.get_help_text.return_value = "Test help text for Restaurant"
            mock_config.return_value = mock_instance
            
            help_component = IndustryHelpText(industry="Restaurant")
            html = help_component.render()
            
            assert "Test help text for Restaurant" in html
            assert 'class="help-text industry-help"' in html

    def test_render_empty_when_no_industry(self):
        """Test that help text is empty when no industry is selected."""
        from src.web_interface.ui_components import IndustryHelpText
        
        help_component = IndustryHelpText(industry=None)
        html = help_component.render()
        
        assert html == "" or "display: none" in html

    def test_render_help_text_with_icon(self):
        """Test that help text includes an info icon."""
        from src.web_interface.ui_components import IndustryHelpText
        
        with patch('src.web_interface.ui_components.IndustryConfig') as mock_config:
            mock_instance = Mock()
            mock_instance.get_help_text.return_value = "Help text"
            mock_config.return_value = mock_instance
            
            help_component = IndustryHelpText(industry="Medical", show_icon=True)
            html = help_component.render()
            
            assert "ℹ️" in html


class TestIndustryClearButton:
    """Test cases for industry clear button component."""

    def test_render_clear_button(self):
        """Test rendering the clear selection button."""
        from src.web_interface.ui_components import IndustryClearButton
        
        button = IndustryClearButton()
        html = button.render()
        
        assert '<button' in html
        assert 'Clear Selection' in html or 'Clear' in html
        assert 'onclick' in html or 'data-action="clear"' in html

    def test_render_clear_button_with_custom_text(self):
        """Test rendering clear button with custom text."""
        from src.web_interface.ui_components import IndustryClearButton
        
        button = IndustryClearButton(text="Reset Industry")
        html = button.render()
        
        assert 'Reset Industry' in html

    def test_render_clear_button_disabled_when_no_selection(self):
        """Test that clear button is disabled when no industry is selected."""
        from src.web_interface.ui_components import IndustryClearButton
        
        button = IndustryClearButton(has_selection=False)
        html = button.render()
        
        assert 'disabled' in html

    def test_clear_button_javascript_function(self):
        """Test that clear button includes JavaScript to clear selection."""
        from src.web_interface.ui_components import IndustryClearButton
        
        button = IndustryClearButton()
        html = button.render()
        js = button.get_javascript()
        
        assert 'clearIndustrySelection' in js or 'clear' in js
        assert 'industry' in js
        assert 'value = ""' in js or "value = ''" in js


class TestIndustryValidationMessage:
    """Test cases for industry validation message display."""

    def test_render_validation_error_message(self):
        """Test rendering validation error message."""
        from src.web_interface.ui_components import IndustryValidationMessage
        
        message = IndustryValidationMessage(
            error="Industry selection is required",
            field="industry"
        )
        html = message.render()
        
        assert "Industry selection is required" in html
        assert 'class="error invalid-feedback"' in html

    def test_render_empty_when_no_error(self):
        """Test that no message is rendered when there's no error."""
        from src.web_interface.ui_components import IndustryValidationMessage
        
        message = IndustryValidationMessage(error=None)
        html = message.render()
        
        assert html == "" or len(html.strip()) == 0

    def test_render_with_field_highlighting(self):
        """Test that validation message includes field reference."""
        from src.web_interface.ui_components import IndustryValidationMessage
        
        message = IndustryValidationMessage(
            error="Please select an industry",
            field="industry",
            highlight=True
        )
        html = message.render()
        attrs = message.get_field_attributes()
        
        assert "Please select an industry" in html
        assert 'aria-invalid="true"' in attrs or 'error' in attrs