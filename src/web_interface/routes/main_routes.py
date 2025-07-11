"""Main interface routes for the RAG Scraper web application."""

from flask import Blueprint, render_template
from src.config.industry_config import IndustryConfig
from src.web_interface.session_manager import IndustrySessionManager
from src.web_interface.ui_components import IndustryDropdown, IndustryHelpText, RestaurantSchemaTypeDropdown, RestaurantSchemaTypeHelpText, SaveSettingsToggle
from src.web_interface.file_upload_ui import InputModeToggle, FileUploadArea, get_file_upload_scripts, get_file_upload_styles


# Create blueprint for main routes
main_routes = Blueprint('main', __name__)


@main_routes.route('/')
def index():
    """Serve main interface."""
    # Get current industry from session
    session_manager = IndustrySessionManager()
    current_industry = session_manager.get_industry()
    
    # Create UI components
    industry_dropdown = IndustryDropdown(
        selected=current_industry, 
        required=True, 
        css_class="terminal-input"
    )
    help_text = IndustryHelpText(industry=current_industry)
    
    # Create Restaurant schema type dropdown component
    restaurant_schema_type_dropdown = RestaurantSchemaTypeDropdown(
        selected_schema_type="Restaurant",  # Default to Restaurant
        css_class="schema-type-dropdown"
    )
    restaurant_schema_type_help_text = RestaurantSchemaTypeHelpText(
        schema_type="Restaurant",
        show_icon=True, 
        collapsible=True
    )
    
    # Create separate file upload UI components
    input_mode_toggle = InputModeToggle()
    file_upload_area = FileUploadArea(enable_multiple=True)
    
    # Create Save Settings toggle
    save_settings_toggle = SaveSettingsToggle()
    
    # Render components
    industry_dropdown_html = industry_dropdown.render()
    help_text_html = help_text.render()
    restaurant_schema_type_dropdown_html = restaurant_schema_type_dropdown.render()
    restaurant_schema_type_help_text_html = restaurant_schema_type_help_text.render()
    input_mode_toggle_html = input_mode_toggle.render()
    file_upload_area_html = file_upload_area.render()
    save_settings_toggle_html = save_settings_toggle.render()
    save_settings_javascript = save_settings_toggle.get_javascript()
    
    # Get scripts and styles
    file_upload_scripts = get_file_upload_scripts()
    file_upload_styles = get_file_upload_styles()
    
    # Render template with component data
    return render_template(
        'index.html',
        industry_dropdown=industry_dropdown_html,
        help_text=help_text_html,
        restaurant_schema_type_dropdown=restaurant_schema_type_dropdown_html,
        restaurant_schema_type_help_text=restaurant_schema_type_help_text_html,
        input_mode_toggle=input_mode_toggle_html,
        file_upload_area=file_upload_area_html,
        save_settings_toggle=save_settings_toggle_html,
        save_settings_javascript=save_settings_javascript,
        file_upload_scripts=file_upload_scripts,
        file_upload_styles=file_upload_styles
    )