"""Validation modules for web interface."""

from .industry_validator import IndustryValidator, IndustryValidationResult

# Import the function directly to avoid circular imports
def validate_industry_selection(form_data):
    """Validate that an industry has been selected."""
    from typing import Dict, Any, Tuple, Optional
    from src.config.industry_config import IndustryConfig
    
    industry = form_data.get('industry', '')
    
    if not industry:
        return False, "Please select an industry before scraping"
    
    # Check if industry is valid
    config = IndustryConfig()
    if not config.validate_industry(industry):
        return False, "Invalid industry selected"
    
    return True, None

__all__ = [
    "IndustryValidator",
    "IndustryValidationResult",
    "validate_industry_selection"
]