"""Main interface routes for the RAG Scraper web application."""

from flask import Blueprint, render_template
from src.config.industry_config import IndustryConfig
from src.web_interface.session_manager import IndustrySessionManager
from src.web_interface.ui_components import IndustryDropdown, IndustryHelpText


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
    
    # Render components
    industry_dropdown_html = industry_dropdown.render()
    help_text_html = help_text.render()
    
    # Render template with component data
    return render_template(
        'index.html',
        industry_dropdown=industry_dropdown_html,
        help_text=help_text_html
    )