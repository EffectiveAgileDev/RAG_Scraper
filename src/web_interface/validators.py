"""Validation functions for web interface forms."""
from typing import Dict, Any, Tuple, Optional
from src.config.industry_config import IndustryConfig


def validate_industry_selection(form_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate that an industry has been selected.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    industry = form_data.get('industry', '')
    
    if not industry:
        return False, "Please select an industry before scraping"
    
    # Check if industry is valid
    config = IndustryConfig()
    if not config.validate_industry(industry):
        return False, "Invalid industry selected"
    
    return True, None