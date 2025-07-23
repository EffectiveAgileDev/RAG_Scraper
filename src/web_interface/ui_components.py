"""UI components for industry selection interface."""
from typing import List, Optional
from src.config.industry_config import IndustryConfig


class IndustryDropdown:
    """Industry selection dropdown component."""

    def __init__(
        self,
        selected: Optional[str] = None,
        required: bool = False,
        css_class: str = "",
        error: bool = False,
    ):
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
        """Render the dropdown HTML with status-aware grouping."""
        industries_by_status = self.config.get_industries_by_status()

        # Build CSS classes
        classes = ["industry-dropdown", "terminal-input"]
        if self.css_class:
            classes.append(self.css_class)
        if self.error:
            classes.append("error is-invalid")

        css_class_attr = f' class="{" ".join(classes)}"' if classes else ""
        required_attr = " required" if self.required else ""

        html = (
            f'<select name="industry" id="industry"{css_class_attr}{required_attr}>\n'
        )

        # Add placeholder option
        html += '    <option value="">Select an industry...</option>\n'

        # Add available industries section
        if industries_by_status.get("available"):
            html += '    <optgroup label="✅ Available Now">\n'
            for industry in industries_by_status["available"]:
                industry_name = industry["name"]
                selected_attr = " selected" if industry_name == self.selected else ""
                html += f'        <option value="{industry_name}"{selected_attr}>{industry_name}</option>\n'
            html += "    </optgroup>\n"

        # Add beta industries section
        if industries_by_status.get("beta"):
            html += '    <optgroup label="🔬 Beta">\n'
            for industry in industries_by_status["beta"]:
                industry_name = industry["name"]
                selected_attr = " selected" if industry_name == self.selected else ""
                html += f'        <option value="{industry_name}"{selected_attr}>{industry_name} (Beta)</option>\n'
            html += "    </optgroup>\n"

        # Add coming soon industries section (disabled)
        if industries_by_status.get("coming_soon"):
            html += '    <optgroup label="🚧 Coming Soon">\n'
            for industry in industries_by_status["coming_soon"]:
                industry_name = industry["name"]
                eta = industry.get("eta", "TBD")
                html += f'        <option value="" disabled>{industry_name} ({eta})</option>\n'
            html += "    </optgroup>\n"

        html += "</select>"

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
        disabled_attr = " disabled" if not self.has_selection else ""
        onclick_attr = ' onclick="clearIndustrySelection()"'

        return f'<button type="button" data-action="clear"{onclick_attr}{disabled_attr}>{self.text}</button>'


class RestWSchemaSelector:
    """RestW schema selection component for Restaurant industry."""

    def __init__(
        self,
        selected: bool = False,
        industry: str = None,
        css_class: str = "",
        disabled: bool = False,
    ):
        """Initialize RestW schema selector.

        Args:
            selected: Whether RestW schema is selected
            industry: Current industry selection
            css_class: Custom CSS classes
            disabled: Whether the component is disabled
        """
        self.selected = selected
        self.industry = industry
        self.css_class = css_class
        self.disabled = disabled

    def is_available_for_industry(self, industry: str) -> bool:
        """Check if RestW schema is available for the given industry."""
        return industry == "Restaurant"

    def get_display_label(self) -> str:
        """Get display label for RestW option."""
        return "RestW - Enhanced Restaurant Data"

    def get_description(self) -> str:
        """Get description text for RestW option."""
        return "Structured restaurant data extraction with enhanced location, menu, and service information"

    def get_help_text(self) -> str:
        """Get help text for RestW option."""
        return """RestW schema provides comprehensive restaurant data extraction including:
        • Structured location data with address components
        • Categorized menu items with prices and descriptions
        • Service offerings (delivery, takeout, catering, etc.)
        • Contact information with clickable phone links
        • Web presence and social media links"""

    def render_checkbox(self) -> str:
        """Render the RestW checkbox component."""
        if not self.is_available_for_industry(self.industry):
            return ""

        # Build CSS classes
        classes = ["restw-checkbox"]
        if self.css_class:
            classes.append(self.css_class)

        css_class_attr = f' class="{" ".join(classes)}"' if classes else ""
        checked_attr = " checked" if self.selected else ""
        disabled_attr = " disabled" if self.disabled else ""

        return f'<input type="checkbox" name="restw_schema" id="restw_schema" value="RestW"{css_class_attr}{checked_attr}{disabled_attr}>'

    def render_label(self) -> str:
        """Render the label for RestW checkbox."""
        return f'<label for="restw_schema" class="restw-label">{self.get_display_label()}</label>'

    def render_description(self) -> str:
        """Render the description for RestW option."""
        return f'<div class="restw-description">{self.get_description()}</div>'

    def render(self) -> str:
        """Render the complete RestW schema selector component."""
        if not self.is_available_for_industry(self.industry):
            return ""

        checkbox = self.render_checkbox()
        label = self.render_label()
        description = self.render_description()

        return f"""
        <div class="restw-schema-selector">
            <div class="restw-option">
                {checkbox}
                {label}
            </div>
            {description}
        </div>
        """

    def are_options_visible(self, schema_selected: bool) -> bool:
        """Check if RestW options should be visible."""
        return schema_selected

    def get_javascript_handlers(self) -> dict:
        """Get JavaScript handlers for RestW selector."""
        return {
            "onChange": "handleRestWSchemaChange(this)",
            "onShow": "showRestWOptions()",
            "onHide": "hideRestWOptions()",
        }


class RestWFieldSelector:
    """RestW field selection component."""

    def __init__(self, selected_fields: list = None, disabled: bool = False):
        """Initialize RestW field selector.

        Args:
            selected_fields: List of selected field names
            disabled: Whether the component is disabled
        """
        self.selected_fields = selected_fields or []
        self.disabled = disabled

    def get_available_fields(self) -> list:
        """Get available RestW fields."""
        return [
            "location",
            "menu_items",
            "services_offered",
            "contact_info",
            "web_links",
        ]

    def get_field_display_name(self, field_name: str) -> str:
        """Get display name for a field."""
        display_names = {
            "location": "Location Data",
            "menu_items": "Menu Items",
            "services_offered": "Services Offered",
            "contact_info": "Contact Information",
            "web_links": "Web Links",
        }
        return display_names.get(field_name, field_name.replace("_", " ").title())

    def get_field_description(self, field_name: str) -> str:
        """Get description for a field."""
        descriptions = {
            "location": "Street address, city, state, zip code, and neighborhood information",
            "menu_items": "Menu items with names, prices, categories, and descriptions",
            "services_offered": "Available services like delivery, takeout, catering, and reservations",
            "contact_info": "Phone numbers, formatted display, and clickable links",
            "web_links": "Official website, menu PDFs, and social media links",
        }
        return descriptions.get(
            field_name, f'Extract {field_name.replace("_", " ")} data'
        )

    def render_field_checkbox(self, field_name: str) -> str:
        """Render checkbox for individual field."""
        checked_attr = " checked" if field_name in self.selected_fields else ""
        disabled_attr = " disabled" if self.disabled else ""

        return f'<input type="checkbox" name="restw_fields" id="restw_field_{field_name}" value="{field_name}"{checked_attr}{disabled_attr}>'

    def render(self) -> str:
        """Render the complete field selector."""
        fields_html = []

        for field_name in self.get_available_fields():
            checkbox = self.render_field_checkbox(field_name)
            display_name = self.get_field_display_name(field_name)
            description = self.get_field_description(field_name)

            fields_html.append(
                f"""
            <div class="restw-field-option">
                <div class="field-checkbox">
                    {checkbox}
                    <label for="restw_field_{field_name}" class="field-label">{display_name}</label>
                </div>
                <div class="field-description">{description}</div>
            </div>
            """
            )

        return f"""
        <div class="restw-field-selector">
            <h4>Select RestW Fields to Extract:</h4>
            {"".join(fields_html)}
        </div>
        """

    def get_selected_field_config(self) -> dict:
        """Get configuration for selected fields."""
        config = {}
        for field_name in self.selected_fields:
            config[field_name] = {
                "enabled": True,
                "display_name": self.get_field_display_name(field_name),
                "description": self.get_field_description(field_name),
            }
        return config

    def validate_field_selection(self, fields: list) -> bool:
        """Validate field selection."""
        if not fields:
            return True  # Empty selection is valid

        available_fields = self.get_available_fields()
        return all(field in available_fields for field in fields)


class RestWHelpText:
    """RestW help text component."""

    def __init__(self, show_icon: bool = True, collapsible: bool = True):
        """Initialize RestW help text.

        Args:
            show_icon: Whether to show help icon
            collapsible: Whether help text is collapsible
        """
        self.show_icon = show_icon
        self.collapsible = collapsible

    def get_general_help_text(self) -> str:
        """Get general help text about RestW."""
        return """RestW schema provides enhanced restaurant data extraction with structured output optimized for restaurant information systems. It extracts comprehensive restaurant data including location information, menu items, service offerings, and contact information."""

    def get_feature_help_text(self, feature: str) -> str:
        """Get help text for specific feature."""
        feature_help = {
            "location": "Extracts structured address information including street address, city, state, zip code, and neighborhood details",
            "menu_items": "Extracts menu items with names, prices, categories, descriptions, and dietary information",
            "services_offered": "Identifies available services such as delivery, takeout, catering, reservations, and online ordering",
            "contact_info": "Extracts phone numbers with formatted display and clickable tel: links",
            "web_links": "Identifies official website, menu PDFs, social media links, and online ordering platforms",
        }
        return feature_help.get(feature, f"Help for {feature} feature")

    def get_usage_examples(self) -> list:
        """Get usage examples for RestW."""
        return [
            "Select RestW when processing restaurant websites or PDF menus",
            "Use location extraction for restaurant finder applications",
            "Extract menu items for food ordering systems",
            "Identify services for restaurant comparison tools",
        ]

    def render_help_section(self) -> str:
        """Render help section."""
        icon_html = '<span class="help-icon">?</span>' if self.show_icon else ""
        general_help = self.get_general_help_text()

        return f"""
        <div class="restw-help-section">
            <div class="help-header">
                {icon_html}
                <span class="help-title">RestW Schema Help</span>
            </div>
            <div class="help-content">
                {general_help}
            </div>
        </div>
        """

    def render_collapsible_help(self) -> str:
        """Render collapsible help text."""
        return f"""
        <details class="restw-help-collapsible">
            <summary>RestW Schema Information</summary>
            <div class="help-content">
                {self.get_general_help_text()}
                <ul>
                    {"".join(f"<li>{example}</li>" for example in self.get_usage_examples())}
                </ul>
            </div>
        </details>
        """

    def render_static_help(self) -> str:
        """Render static help text."""
        return f"""
        <div class="restw-help-static">
            <div class="help-content">
                {self.get_general_help_text()}
            </div>
        </div>
        """

    def render(self) -> str:
        """Render the complete help component."""
        if self.collapsible:
            return self.render_collapsible_help()
        else:
            return self.render_static_help()

    def get_troubleshooting_tips(self) -> list:
        """Get troubleshooting tips."""
        return [
            "Ensure the selected industry is 'Restaurant' to enable RestW schema",
            "Check that the website or PDF contains restaurant-related content",
            "Verify that at least one RestW field is selected for extraction",
            "Review the extracted data for completeness and accuracy",
        ]

    def get_best_practices(self) -> list:
        """Get best practices for RestW usage."""
        return [
            "Use RestW schema specifically for restaurant data extraction",
            "Select only the fields you need to improve processing performance",
            "Combine with industry-specific knowledge for better results",
            "Validate extracted data before using in production systems",
        ]

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

    def __init__(
        self,
        error: Optional[str] = None,
        field: str = "industry",
        highlight: bool = False,
    ):
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


class RestaurantSchemaTypeSelector:
    """UI component for selecting restaurant schema type (Restaurant or RestW)."""

    def __init__(
        self,
        selected_schema_type: str = "Restaurant",
        css_class: str = "schema-type-selector",
        disabled: bool = False,
        show_help_text: bool = True,
    ):
        """Initialize restaurant schema type selector.

        Args:
            selected_schema_type: Currently selected schema type
            css_class: CSS class for styling
            disabled: Whether the component is disabled
            show_help_text: Whether to show help text
        """
        self.selected_schema_type = selected_schema_type
        self.css_class = css_class
        self.disabled = disabled
        self.show_help_text = show_help_text

        # Define available schema types
        self.available_schema_types = [
            {
                "value": "Restaurant",
                "label": "Restaurant - Standard Schema",
                "description": "Standard restaurant data extraction",
            },
            {
                "value": "RestW",
                "label": "RestW - Enhanced Restaurant Data",
                "description": "Enhanced restaurant data with specialized fields",
            },
        ]

    def render(self) -> str:
        """Render the schema type selector HTML."""
        disabled_attr = ' disabled="disabled"' if self.disabled else ""

        html = f'<div id="schema-type-selector" class="{self.css_class}" role="radiogroup" aria-label="Schema type selection">\n'
        html += '    <div class="schema-type-header">\n'
        html += '        <label class="schema-type-title">Schema Type:</label>\n'
        html += "    </div>\n"

        for schema_type in self.available_schema_types:
            value = schema_type["value"]
            label = schema_type["label"]
            description = schema_type["description"]

            checked_attr = " checked" if value == self.selected_schema_type else ""
            input_id = f"schema-type-{value.lower()}"

            html += f'    <div class="schema-type-option">\n'
            html += f'        <label class="schema-type-label" for="{input_id}">\n'
            html += f'            <input type="radio" id="{input_id}" name="schema_type" value="{value}"{checked_attr}{disabled_attr} onchange="handleSchemaTypeChange(this.value)">\n'
            html += f'            <span class="schema-type-label-text">{label}</span>\n'
            html += f'            <span class="schema-type-description">{description}</span>\n'
            html += f"        </label>\n"
            html += f"    </div>\n"

        html += "</div>\n"

        if self.show_help_text:
            html += (
                '<div id="schema-type-help-selector" class="schema-type-help"></div>\n'
            )

        return html


class RestaurantSchemaTypeHelpText:
    """UI component for displaying help text for restaurant schema types."""

    def __init__(
        self,
        schema_type: str = "Restaurant",
        show_icon: bool = True,
        collapsible: bool = True,
        css_class: str = "schema-type-help",
    ):
        """Initialize restaurant schema type help text.

        Args:
            schema_type: Schema type to show help for
            show_icon: Whether to show help icon
            collapsible: Whether help text is collapsible
            css_class: CSS class for styling
        """
        self.schema_type = schema_type
        self.show_icon = show_icon
        self.collapsible = collapsible
        self.css_class = css_class

    def get_help_content(self) -> str:
        """Get help content for the specified schema type."""
        if self.schema_type == "Restaurant":
            return """
            <h4>Restaurant Schema - Standard Extraction</h4>
            <p>Standard restaurant data extraction provides comprehensive information about restaurants including:</p>
            <ul>
                <li><strong>Basic Information:</strong> Restaurant name, description, and cuisine type</li>
                <li><strong>Menu Information:</strong> Menu items, prices, and categories</li>
                <li><strong>Location and Contact:</strong> Address, phone number, and website</li>
                <li><strong>Business Hours:</strong> Operating hours and special schedules</li>
                <li><strong>Services:</strong> Available services like delivery, takeout, and reservations</li>
            </ul>
            <p>This schema provides reliable extraction for most restaurant websites and documents.</p>
            """
        elif self.schema_type == "RestW":
            return """
            <h4>RestW Schema - Enhanced Restaurant Data</h4>
            <p>Enhanced restaurant data extraction with specialized fields and advanced processing:</p>
            <ul>
                <li><strong>Structured Location Data:</strong> Detailed address formatting with neighborhood information</li>
                <li><strong>Advanced Menu Item Extraction:</strong> Menu items with detailed categorization and pricing</li>
                <li><strong>Service Offerings:</strong> Comprehensive service information including delivery zones</li>
                <li><strong>Enhanced Contact Info:</strong> Multiple contact methods with formatted display</li>
                <li><strong>Web Links:</strong> Social media links, online menus, and reservation systems</li>
            </ul>
            <p>This schema provides enhanced extraction capabilities for complex restaurant data.</p>
            """
        else:
            return (
                "<p>Schema type not supported. Please select a valid schema type.</p>"
            )

    def render(self) -> str:
        """Render the help text HTML."""
        icon_html = '<span class="help-icon">ℹ️</span>' if self.show_icon else ""
        content = self.get_help_content()

        if self.collapsible:
            html = f'<div id="schema-type-help-static" class="{self.css_class} collapsible">\n'
            html += f'    <div class="help-header" onclick="toggleHelpText()">\n'
            html += f"        {icon_html}\n"
            html += f'        <span class="help-title">Schema Type Information</span>\n'
            html += f'        <span class="toggle-help">▶</span>\n'
            html += f"    </div>\n"
            html += f'    <div class="help-content">\n'
            html += f"        {content}\n"
            html += f"    </div>\n"
            html += f"</div>\n"
        else:
            html = f'<div id="schema-type-help-static" class="{self.css_class}">\n'
            html += f'    <div class="help-header">\n'
            html += f"        {icon_html}\n"
            html += f'        <span class="help-title">Schema Type Information</span>\n'
            html += f"    </div>\n"
            html += f'    <div class="help-content">\n'
            html += f"        {content}\n"
            html += f"    </div>\n"
            html += f"</div>\n"

        return html


class SinglePageSaveSettingsToggle:
    """UI component for Single Page Save Settings toggle."""

    def __init__(
        self,
        checked: bool = False,
        css_class: str = "save-settings-toggle",
        label_text: str = "Save Single Page Settings",
    ):
        """Initialize SinglePageSaveSettingsToggle.

        Args:
            checked: Whether the toggle is checked by default
            css_class: CSS class for styling
            label_text: Text label for the toggle
        """
        self.checked = checked
        self.css_class = css_class
        self.label_text = label_text

    def render(self) -> str:
        """Render the single page save settings toggle HTML.

        Returns:
            HTML string for the toggle component
        """
        checked_attr = "checked" if self.checked else ""

        html = f"""
        <div id="single-page-save-settings-toggle" class="save-settings-row">
            <label class="save-settings-label">
                <input type="checkbox" 
                       id="single-page-save-settings-checkbox" 
                       class="{self.css_class}" 
                       {checked_attr}
                       onchange="handleSinglePageSaveSettingsToggle(this)">
                <span class="save-settings-text">{self.label_text}</span>
            </label>
            <div class="save-settings-help" id="single-page-save-settings-help">
                <span class="help-text">
                    <strong>ON:</strong> Single page settings persist across sessions<br>
                    <strong>OFF:</strong> Single page settings reset to defaults on page load
                </span>
            </div>
        </div>
        """
        return html

    def get_javascript(self) -> str:
        """Get JavaScript for single page save settings functionality.

        Returns:
            JavaScript code as string
        """
        js = """
        function handleSinglePageSaveSettingsToggle(checkbox) {
            const isEnabled = checkbox.checked;
            
            if (isEnabled) {
                // Save current single page settings
                saveSinglePageSettings();
                updateSystemStatus('SINGLE_PAGE_SAVE_SETTINGS // ENABLED');
            } else {
                // Clear saved single page settings
                localStorage.removeItem('ragScraperSinglePageSettings');
                updateSystemStatus('SINGLE_PAGE_SAVE_SETTINGS // DISABLED');
            }
        }
        
        function saveSinglePageSettings() {
            const settings = {
                requestTimeout: document.getElementById('singleRequestTimeout')?.value || 30,
                enableJavaScript: document.getElementById('singleEnableJavaScript')?.checked || false,
                followRedirects: document.getElementById('singleFollowRedirects')?.checked || true,
                concurrentRequests: document.getElementById('singleConcurrentRequests')?.value || 1,
                jsTimeout: document.getElementById('singleJsTimeout')?.value || 30
            };
            
            localStorage.setItem('ragScraperSinglePageSettings', JSON.stringify(settings));
        }
        
        function loadSinglePageSettings() {
            try {
                const saved = localStorage.getItem('ragScraperSinglePageSettings');
                if (saved) {
                    const settings = JSON.parse(saved);
                    
                    // Apply settings to single page form elements
                    if (document.getElementById('singleRequestTimeout')) {
                        document.getElementById('singleRequestTimeout').value = settings.requestTimeout || 30;
                    }
                    if (document.getElementById('singleEnableJavaScript')) {
                        document.getElementById('singleEnableJavaScript').checked = settings.enableJavaScript || false;
                    }
                    if (document.getElementById('singleFollowRedirects')) {
                        document.getElementById('singleFollowRedirects').checked = settings.followRedirects !== false;
                    }
                    if (document.getElementById('singleConcurrentRequests')) {
                        document.getElementById('singleConcurrentRequests').value = settings.concurrentRequests || 1;
                    }
                    if (document.getElementById('singleJsTimeout')) {
                        document.getElementById('singleJsTimeout').value = settings.jsTimeout || 30;
                    }
                    
                    // Enable the toggle
                    const checkbox = document.getElementById('single-page-save-settings-checkbox');
                    if (checkbox) checkbox.checked = true;
                }
            } catch (error) {
                console.error('Error loading single page settings:', error);
            }
        }
        """
        return js


class MultiPageSaveSettingsToggle:
    """UI component for Multi Page Save Settings toggle."""

    def __init__(
        self,
        checked: bool = False,
        css_class: str = "save-settings-toggle",
        label_text: str = "Save Multi Page Settings",
    ):
        """Initialize MultiPageSaveSettingsToggle.

        Args:
            checked: Whether the toggle is checked by default
            css_class: CSS class for styling
            label_text: Text label for the toggle
        """
        self.checked = checked
        self.css_class = css_class
        self.label_text = label_text

    def render(self) -> str:
        """Render the multi page save settings toggle HTML.

        Returns:
            HTML string for the toggle component
        """
        checked_attr = "checked" if self.checked else ""

        html = f"""
        <div id="multi-page-save-settings-toggle" class="save-settings-row">
            <label class="save-settings-label">
                <input type="checkbox" 
                       id="multi-page-save-settings-checkbox" 
                       class="{self.css_class}" 
                       {checked_attr}
                       onchange="handleMultiPageSaveSettingsToggle(this)">
                <span class="save-settings-text">{self.label_text}</span>
            </label>
            <div class="save-settings-help" id="multi-page-save-settings-help">
                <span class="help-text">
                    <strong>ON:</strong> Multi page settings persist across sessions<br>
                    <strong>OFF:</strong> Multi page settings reset to defaults on page load
                </span>
            </div>
        </div>
        """
        return html

    def get_javascript(self) -> str:
        """Get JavaScript for multi page save settings functionality.

        Returns:
            JavaScript code as string
        """
        js = """
        function handleMultiPageSaveSettingsToggle(checkbox) {
            const isEnabled = checkbox.checked;
            
            if (isEnabled) {
                // Save current multi page settings
                saveMultiPageSettings();
                updateSystemStatus('MULTI_PAGE_SAVE_SETTINGS // ENABLED');
            } else {
                // Clear saved multi page settings
                localStorage.removeItem('ragScraperMultiPageSettings');
                updateSystemStatus('MULTI_PAGE_SAVE_SETTINGS // DISABLED');
            }
        }
        
        function saveMultiPageSettings() {
            const settings = {
                maxPages: document.getElementById('maxPages')?.value || 50,
                crawlDepth: document.getElementById('crawlDepth')?.value || 2,
                rateLimit: document.getElementById('rateLimit')?.value || 1000,
                enableJavaScript: document.getElementById('enableJavaScript')?.checked || false,
                enablePageDiscovery: document.getElementById('pageDiscoveryEnabled')?.checked || true,
                respectRobotsTxt: document.getElementById('respectRobotsTxt')?.checked || true,
                includePatterns: document.getElementById('includePatterns')?.value || 'menu,food,restaurant',
                excludePatterns: document.getElementById('excludePatterns')?.value || 'admin,login,cart',
                concurrentRequests: document.getElementById('concurrentRequests')?.value || 5,
                requestTimeout: document.getElementById('requestTimeout')?.value || 30
            };
            
            localStorage.setItem('ragScraperMultiPageSettings', JSON.stringify(settings));
        }
        
        function loadMultiPageSettings() {
            try {
                const saved = localStorage.getItem('ragScraperMultiPageSettings');
                if (saved) {
                    const settings = JSON.parse(saved);
                    
                    // Apply settings to multi page form elements
                    if (document.getElementById('maxPages')) {
                        document.getElementById('maxPages').value = settings.maxPages || 50;
                    }
                    if (document.getElementById('crawlDepth')) {
                        document.getElementById('crawlDepth').value = settings.crawlDepth || 2;
                        // Update display value
                        const depthValue = document.getElementById('depthValue');
                        if (depthValue) depthValue.textContent = settings.crawlDepth || 2;
                    }
                    if (document.getElementById('rateLimit')) {
                        document.getElementById('rateLimit').value = settings.rateLimit || 1000;
                        // Update display value
                        const rateLimitValue = document.getElementById('rateLimitValue');
                        if (rateLimitValue) rateLimitValue.textContent = (settings.rateLimit || 1000) + 'ms';
                    }
                    if (document.getElementById('enableJavaScript')) {
                        document.getElementById('enableJavaScript').checked = settings.enableJavaScript || false;
                    }
                    if (document.getElementById('pageDiscoveryEnabled')) {
                        document.getElementById('pageDiscoveryEnabled').checked = settings.enablePageDiscovery !== false;
                    }
                    if (document.getElementById('respectRobotsTxt')) {
                        document.getElementById('respectRobotsTxt').checked = settings.respectRobotsTxt !== false;
                    }
                    if (document.getElementById('includePatterns')) {
                        document.getElementById('includePatterns').value = settings.includePatterns || 'menu,food,restaurant';
                    }
                    if (document.getElementById('excludePatterns')) {
                        document.getElementById('excludePatterns').value = settings.excludePatterns || 'admin,login,cart';
                    }
                    if (document.getElementById('concurrentRequests')) {
                        document.getElementById('concurrentRequests').value = settings.concurrentRequests || 5;
                        // Update display value
                        const concurrentValue = document.getElementById('concurrentRequestsValue');
                        if (concurrentValue) concurrentValue.textContent = settings.concurrentRequests || 5;
                    }
                    if (document.getElementById('requestTimeout')) {
                        document.getElementById('requestTimeout').value = settings.requestTimeout || 30;
                    }
                    
                    // Enable the toggle
                    const checkbox = document.getElementById('multi-page-save-settings-checkbox');
                    if (checkbox) checkbox.checked = true;
                }
            } catch (error) {
                console.error('Error loading multi page settings:', error);
            }
        }
        """
        return js


class SaveSettingsToggle:
    """UI component for Save Settings toggle."""

    def __init__(
        self,
        checked: bool = False,
        css_class: str = "save-settings-toggle",
        label_text: str = "Save Settings",
    ):
        """Initialize Save Settings toggle.

        Args:
            checked: Whether toggle is checked
            css_class: CSS class for styling
            label_text: Label text for the toggle
        """
        self.checked = checked
        self.css_class = css_class
        self.label_text = label_text

    def render(self) -> str:
        """Render the Save Settings toggle HTML."""
        checked_attr = " checked" if self.checked else ""

        html = f"""
        <div id="save-settings-toggle" class="{self.css_class}">
            <label class="toggle-label">
                <input type="checkbox" id="save-settings-checkbox" 
                       name="saveSettings"{checked_attr} 
                       onchange="handleSaveSettingsToggle(this)">
                <span class="toggle-text">{self.label_text}</span>
            </label>
            <div class="save-settings-help">
                <span class="help-text">
                    <strong>ON:</strong> Settings persist across sessions<br>
                    <strong>OFF:</strong> Settings reset to defaults on page load
                </span>
            </div>
        </div>
        """
        return html

    def get_javascript(self) -> str:
        """Get JavaScript code for Save Settings functionality."""
        return """
        function handleSaveSettingsToggle(checkbox) {
            if (checkbox.checked) {
                saveCurrentSettings();
            } else {
                localStorage.removeItem('ragScraperSettings');
            }
        }
        
        function saveCurrentSettings() {
            const settings = {
                scrapingMode: document.querySelector('input[name="scrapingMode"]:checked')?.value || 'single',
                aggregationMode: document.getElementById('fileMode')?.value || 'single',
                outputFormat: document.querySelector('input[name="fileFormat"]:checked')?.value || 'text',
                maxPages: parseInt(document.getElementById('maxPages')?.value) || 50,
                crawlDepth: parseInt(document.getElementById('crawlDepth')?.value) || 2,
                includePatterns: document.getElementById('includePatterns')?.value || 'menu,food,restaurant',
                excludePatterns: document.getElementById('excludePatterns')?.value || 'admin,login,cart',
                rateLimit: parseInt(document.getElementById('rateLimit')?.value) || 1000,
                enableJavaScript: document.getElementById('enableJavaScript')?.checked || false,
                respectRobotsTxt: document.getElementById('respectRobotsTxt')?.checked ?? true,
                saveEnabled: true
            };
            
            localStorage.setItem('ragScraperSettings', JSON.stringify(settings));
        }
        
        function loadSavedSettings() {
            const savedSettings = localStorage.getItem('ragScraperSettings');
            if (!savedSettings) return;
            
            try {
                const settings = JSON.parse(savedSettings);
                if (settings.saveEnabled) {
                    applySavedSettings(settings);
                }
            } catch (e) {
                console.error('Failed to load saved settings:', e);
            }
        }
        
        function applySavedSettings(settings) {
            // Apply scraping mode
            const scrapingModeInput = document.querySelector(`input[name="scrapingMode"][value="${settings.scrapingMode}"]`);
            if (scrapingModeInput) scrapingModeInput.click();
            
            // Apply aggregation mode
            const fileModeSelect = document.getElementById('fileMode');
            if (fileModeSelect) fileModeSelect.value = settings.aggregationMode;
            
            // Apply output format
            const formatInput = document.querySelector(`input[name="fileFormat"][value="${settings.outputFormat}"]`);
            if (formatInput) formatInput.click();
            
            // Apply other settings
            if (settings.maxPages) document.getElementById('maxPages').value = settings.maxPages;
            if (settings.crawlDepth) document.getElementById('crawlDepth').value = settings.crawlDepth;
            if (settings.includePatterns) document.getElementById('includePatterns').value = settings.includePatterns;
            if (settings.excludePatterns) document.getElementById('excludePatterns').value = settings.excludePatterns;
            if (settings.rateLimit) document.getElementById('rateLimit').value = settings.rateLimit;
            if (settings.enableJavaScript !== undefined) {
                document.getElementById('enableJavaScript').checked = settings.enableJavaScript;
            }
            if (settings.respectRobotsTxt !== undefined) {
                document.getElementById('respectRobotsTxt').checked = settings.respectRobotsTxt;
            }
            
            // Set the toggle to ON
            document.getElementById('save-settings-checkbox').checked = true;
        }
        
        function resetToDefaults() {
            // Reset all settings to defaults
            document.querySelector('input[name="scrapingMode"][value="single"]')?.click();
            document.getElementById('fileMode').value = 'single';
            document.querySelector('input[name="fileFormat"][value="text"]')?.click();
            document.getElementById('maxPages').value = 50;
            document.getElementById('crawlDepth').value = 2;
            document.getElementById('includePatterns').value = 'menu,food,restaurant';
            document.getElementById('excludePatterns').value = 'admin,login,cart';
            document.getElementById('rateLimit').value = 1000;
            document.getElementById('enableJavaScript').checked = false;
            document.getElementById('respectRobotsTxt').checked = true;
        }
        
        // Load settings on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadSavedSettings();
        });
        """


class RestaurantSchemaTypeDropdown:
    """UI component for selecting restaurant schema type from a dropdown menu."""

    def __init__(
        self,
        selected_schema_type: str = "Restaurant",
        css_class: str = "schema-type-dropdown",
        disabled: bool = False,
        required: bool = True,
        show_help_text: bool = True,
    ):
        """Initialize restaurant schema type dropdown.

        Args:
            selected_schema_type: Currently selected schema type
            css_class: CSS class for styling
            disabled: Whether the dropdown is disabled
            required: Whether the dropdown is required
            show_help_text: Whether to show help text
        """
        self.selected_schema_type = selected_schema_type
        self.css_class = css_class
        self.disabled = disabled
        self.required = required
        self.show_help_text = show_help_text

        # Define available schema types
        self.available_schema_types = [
            {
                "value": "Restaurant",
                "label": "Restaurant - Standard Schema",
                "description": "Standard restaurant data extraction",
            },
            {
                "value": "RestW",
                "label": "RestW - Enhanced Restaurant Data",
                "description": "Enhanced restaurant data with specialized fields",
            },
        ]

    def get_schema_types(self) -> list:
        """Get available schema types."""
        return self.available_schema_types

    def render(self) -> str:
        """Render the schema type dropdown HTML."""
        disabled_attr = ' disabled="disabled"' if self.disabled else ""
        required_attr = " required" if self.required else ""

        html = f'<div class="input-group">\n'
        html += f'    <label class="input-label" for="schema-type-dropdown">SCHEMA_TYPE:</label>\n'
        html += f'    <select id="schema-type-dropdown" name="schema_type" class="{self.css_class} terminal-input" aria-label="Schema type selection"{disabled_attr}{required_attr} onchange="handleSchemaTypeChange(this.value)">\n'

        # Add placeholder option if not required
        if not self.required:
            html += (
                f'        <option value="" disabled>Select schema type...</option>\n'
            )

        # Add schema type options
        for schema_type in self.available_schema_types:
            value = schema_type["value"]
            label = schema_type["label"]
            description = schema_type["description"]

            selected_attr = " selected" if value == self.selected_schema_type else ""

            html += f'        <option value="{value}"{selected_attr} title="{description}">{label}</option>\n'

        html += f"    </select>\n"
        html += f"</div>\n"

        if self.show_help_text:
            html += (
                '<div id="schema-type-help-dynamic" class="schema-type-help"></div>\n'
            )

        return html


class SinglePageSaveSettingsToggle:
    """UI component for Single Page Save Settings toggle."""

    def __init__(self, enabled: bool = False, css_class: str = "save-settings-toggle"):
        """Initialize single page save settings toggle.

        Args:
            enabled: Whether save settings is currently enabled
            css_class: CSS class for styling
        """
        self.enabled = enabled
        self.css_class = css_class
        self.label_text = "💾 SAVE_SINGLE_PAGE_SETTINGS"

    def render(self) -> str:
        """Render the single page save settings toggle HTML."""
        checked_attr = " checked" if self.enabled else ""

        html = f"""
        <div id="single-page-save-settings-toggle" class="save-settings-row">
            <label class="save-settings-label">
                <input type="checkbox" 
                       id="single-page-save-settings-checkbox" 
                       class="{self.css_class}" 
                       {checked_attr}
                       onchange="handleSinglePageSaveSettingsToggle(this)">
                <span class="save-settings-text">{self.label_text}</span>
            </label>
        </div>
        """
        return html

    def get_javascript(self) -> str:
        """Get JavaScript code for single page save settings functionality."""
        return """
        function handleSinglePageSaveSettingsToggle(checkbox) {
            const isEnabled = checkbox.checked;
            const settings = gatherSinglePageSettings();
            
            if (isEnabled) {
                // Save current settings to localStorage
                localStorage.setItem('ragScraperSinglePageSettings', JSON.stringify(settings));
                updateSystemStatus('SINGLE_PAGE_SETTINGS // SAVE_ENABLED');
            } else {
                // Remove saved settings from localStorage
                localStorage.removeItem('ragScraperSinglePageSettings');
                updateSystemStatus('SINGLE_PAGE_SETTINGS // SAVE_DISABLED');
            }
            
            // Send to server
            fetch('/api/save-single-page-settings', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({settings: settings, saveEnabled: isEnabled})
            });
        }
        
        function gatherSinglePageSettings() {
            return {
                requestTimeout: parseInt(document.getElementById('singleRequestTimeout')?.value || 30),
                enableJavaScript: document.getElementById('singleEnableJavaScript')?.checked || false,
                followRedirects: document.getElementById('singleFollowRedirects')?.checked || true,
                respectRobotsTxt: document.getElementById('singleRespectRobotsTxt')?.checked || true,
                concurrentRequests: parseInt(document.getElementById('singleConcurrentRequests')?.value || 1),
                jsTimeout: parseInt(document.getElementById('singleJsTimeout')?.value || 30)
            };
        }
        """


class MultiPageSaveSettingsToggle:
    """UI component for Multi Page Save Settings toggle."""

    def __init__(self, enabled: bool = False, css_class: str = "save-settings-toggle"):
        """Initialize multi page save settings toggle.

        Args:
            enabled: Whether save settings is currently enabled
            css_class: CSS class for styling
        """
        self.enabled = enabled
        self.css_class = css_class
        self.label_text = "💾 SAVE_MULTI_PAGE_SETTINGS"

    def render(self) -> str:
        """Render the multi page save settings toggle HTML."""
        checked_attr = " checked" if self.enabled else ""

        html = f"""
        <div id="multi-page-save-settings-toggle" class="save-settings-row">
            <label class="save-settings-label">
                <input type="checkbox" 
                       id="multi-page-save-settings-checkbox" 
                       class="{self.css_class}" 
                       {checked_attr}
                       onchange="handleMultiPageSaveSettingsToggle(this)">
                <span class="save-settings-text">{self.label_text}</span>
            </label>
        </div>
        """
        return html

    def get_javascript(self) -> str:
        """Get JavaScript code for multi page save settings functionality."""
        return """
        function handleMultiPageSaveSettingsToggle(checkbox) {
            const isEnabled = checkbox.checked;
            const settings = gatherMultiPageSettings();
            
            if (isEnabled) {
                // Save current settings to localStorage
                localStorage.setItem('ragScraperMultiPageSettings', JSON.stringify(settings));
                updateSystemStatus('MULTI_PAGE_SETTINGS // SAVE_ENABLED');
            } else {
                // Remove saved settings from localStorage
                localStorage.removeItem('ragScraperMultiPageSettings');
                updateSystemStatus('MULTI_PAGE_SETTINGS // SAVE_DISABLED');
            }
            
            // Send to server
            fetch('/api/save-multi-page-settings', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({settings: settings, saveEnabled: isEnabled})
            });
        }
        
        function gatherMultiPageSettings() {
            return {
                maxPages: parseInt(document.getElementById('maxPages')?.value || 50),
                crawlDepth: parseInt(document.getElementById('crawlDepth')?.value || 2),
                rateLimit: parseInt(document.getElementById('rateLimit')?.value || 1000),
                enableJavaScript: document.getElementById('enableJavaScript')?.checked || false,
                enablePageDiscovery: document.getElementById('enablePageDiscovery')?.checked || true,
                respectRobotsTxt: document.getElementById('respectRobotsTxt')?.checked || true,
                includePatterns: document.getElementById('includePatterns')?.value || 'menu,food,restaurant',
                excludePatterns: document.getElementById('excludePatterns')?.value || 'admin,login,cart',
                concurrentRequests: parseInt(document.getElementById('concurrentRequests')?.value || 5),
                requestTimeout: parseInt(document.getElementById('requestTimeout')?.value || 30)
            };
        }
        """
