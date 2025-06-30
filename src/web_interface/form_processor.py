"""Form processing with industry selection support."""
from typing import Dict, Any, Optional
from src.web_interface.session_manager import IndustrySessionManager


class IndustryFormProcessor:
    """Processes forms with industry selection integration."""
    
    def __init__(self):
        self.session_manager = IndustrySessionManager()
    
    def process_form(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process form data, adding industry from session if needed."""
        processed_data = form_data.copy()
        
        # If form has industry, update session
        if 'industry' in form_data and form_data['industry']:
            self.session_manager.store_industry(form_data['industry'])
        # If form doesn't have industry, use session value
        elif 'industry' not in form_data or not form_data['industry']:
            session_industry = self.session_manager.get_industry()
            if session_industry:
                processed_data['industry'] = session_industry
        
        return processed_data
    
    def validate(self, form_data: Dict[str, Any]) -> Dict[str, str]:
        """Validate form data, checking for required industry."""
        errors = {}
        
        # Process form to include session industry if needed
        processed_data = self.process_form(form_data)
        
        # Check if industry is present after processing
        if 'industry' not in processed_data or not processed_data['industry']:
            errors['industry'] = "Industry selection is required"
        
        return errors