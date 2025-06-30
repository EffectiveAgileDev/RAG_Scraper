"""UI components for industry selection interface."""
from typing import List, Optional
from src.config.industry_config import IndustryConfig


class IndustryDropdown:
    """Industry selection dropdown component."""
    
    def __init__(self, selected: Optional[str] = None, required: bool = False, 
                 css_class: str = "", error: bool = False):
        """Initialize industry dropdown.
        
        Args:
            selected: Currently selected industry
            required: Whether the field is required
            css_class: Custom CSS classes
            error: Whether to show error state
        """
        self.selected = selected
        self.required = required
        self.css_class = css_class
        self.error = error
        self.config = IndustryConfig()
    
    def render(self) -> str:
        """Render the dropdown HTML."""
        industries = self.config.get_industry_list()
        
        # Build CSS classes
        classes = ['industry-dropdown']
        if self.css_class:
            classes.append(self.css_class)
        if self.error:
            classes.append('error is-invalid')
        
        css_class_attr = f' class="{" ".join(classes)}"' if classes else ''
        required_attr = ' required' if self.required else ''
        
        html = f'<select name="industry" id="industry"{css_class_attr}{required_attr}>\n'
        
        # Add placeholder option
        html += '    <option value="">Select an industry...</option>\n'
        
        # Add industry options
        for industry in industries:
            selected_attr = ' selected' if industry == self.selected else ''
            html += f'    <option value="{industry}"{selected_attr}>{industry}</option>\n'
        
        html += '</select>'
        
        return html


class IndustryHelpText:
    """Industry-specific help text component."""
    
    def __init__(self, industry: Optional[str] = None, show_icon: bool = False):
        """Initialize help text component.
        
        Args:
            industry: Industry to show help for
            show_icon: Whether to show an info icon
        """
        self.industry = industry
        self.show_icon = show_icon
        self.config = IndustryConfig()
    
    def render(self) -> str:
        """Render the help text HTML."""
        if not self.industry:
            return ""
        
        help_text = self.config.get_help_text(self.industry)
        if not help_text:
            return ""
        
        icon = "ℹ️ " if self.show_icon else ""
        
        return f'<div class="help-text industry-help">{icon}{help_text}</div>'


class IndustryClearButton:
    """Clear industry selection button component."""
    
    def __init__(self, text: str = "Clear Selection", has_selection: bool = True):
        """Initialize clear button.
        
        Args:
            text: Button text
            has_selection: Whether an industry is currently selected
        """
        self.text = text
        self.has_selection = has_selection
    
    def render(self) -> str:
        """Render the clear button HTML."""
        disabled_attr = ' disabled' if not self.has_selection else ''
        onclick_attr = ' onclick="clearIndustrySelection()"'
        
        return f'<button type="button" data-action="clear"{onclick_attr}{disabled_attr}>{self.text}</button>'
    
    def get_javascript(self) -> str:
        """Get JavaScript function for clearing selection."""
        return """
function clearIndustrySelection() {
    const industrySelect = document.getElementById('industry');
    if (industrySelect) {
        industrySelect.value = '';
        // Trigger change event
        industrySelect.dispatchEvent(new Event('change'));
    }
}
"""


class IndustryValidationMessage:
    """Industry validation error message component."""
    
    def __init__(self, error: Optional[str] = None, field: str = "industry", 
                 highlight: bool = False):
        """Initialize validation message.
        
        Args:
            error: Error message to display
            field: Field name for ARIA attributes
            highlight: Whether to highlight the field
        """
        self.error = error
        self.field = field
        self.highlight = highlight
    
    def render(self) -> str:
        """Render the validation message HTML."""
        if not self.error:
            return ""
        
        return f'<div class="error invalid-feedback">{self.error}</div>'
    
    def get_field_attributes(self) -> str:
        """Get attributes to add to the field for accessibility."""
        if not self.error:
            return ""
        
        attrs = []
        if self.highlight:
            attrs.append('aria-invalid="true"')
            attrs.append('class="error"')
        
        return " ".join(attrs)