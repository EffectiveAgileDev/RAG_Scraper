"""Centralized industry validation logic."""

from typing import Dict, Any, Tuple
from dataclasses import dataclass

from src.web_interface.session_manager import IndustrySessionManager


@dataclass
class IndustryValidationResult:
    """Result of industry validation."""
    is_valid: bool
    error_message: str = ""
    industry: str = ""


class IndustryValidator:
    """Centralized industry validation handler."""
    
    def __init__(self, session_manager: IndustrySessionManager = None):
        self.session_manager = session_manager or IndustrySessionManager()
    
    def validate_and_store_industry(self, form_data: Dict[str, Any]) -> IndustryValidationResult:
        """Validate industry selection and store in session.
        
        Args:
            form_data: Form data dictionary containing industry selection
            
        Returns:
            IndustryValidationResult with validation status and industry
        """
        # Create a copy to avoid modifying original data
        data = form_data.copy()
        
        # Add industry from session if not in form data
        if 'industry' not in data or not data['industry']:
            session_industry = self.session_manager.get_industry()
            if session_industry:
                data['industry'] = session_industry
        
        # Import here to avoid circular imports
        from ..validators import validate_industry_selection
        
        # Validate industry using existing validator
        is_valid, error_message = validate_industry_selection(data)
        if not is_valid:
            return IndustryValidationResult(
                is_valid=False,
                error_message=error_message
            )
        
        # Store industry in session
        industry = data.get('industry', '')
        if industry:
            self.session_manager.store_industry(industry)
        
        return IndustryValidationResult(
            is_valid=True,
            industry=industry
        )
    
    def get_current_industry(self) -> str:
        """Get current industry from session."""
        return self.session_manager.get_industry() or ""
    
    def clear_industry_selection(self) -> None:
        """Clear industry selection from session."""
        self.session_manager.clear_industry()
    
    def validate_industry_for_restw(self, industry: str) -> bool:
        """Check if industry supports RestW schema."""
        return industry == "Restaurant"