"""Session management for industry selection."""
from flask import session
from typing import Optional, Dict, Any
import datetime


class IndustrySessionManager:
    """Manages industry selection in Flask session."""
    
    INDUSTRY_KEY = 'industry'
    TIMESTAMP_KEY = 'industry_timestamp'
    
    def store_industry(self, industry: str) -> None:
        """Store selected industry in session with timestamp."""
        session[self.INDUSTRY_KEY] = industry
        session[self.TIMESTAMP_KEY] = datetime.datetime.now().isoformat()
        session.permanent = True  # Make session persistent
    
    def get_industry(self) -> Optional[str]:
        """Get current industry from session."""
        return session.get(self.INDUSTRY_KEY)
    
    def clear_industry(self) -> None:
        """Remove industry selection from session."""
        session.pop(self.INDUSTRY_KEY, None)
        session.pop(self.TIMESTAMP_KEY, None)
    
    def has_industry(self) -> bool:
        """Check if an industry is currently selected."""
        return self.INDUSTRY_KEY in session
    
    def get_industry_info(self) -> Dict[str, Any]:
        """Get detailed industry information from session."""
        return {
            'industry': self.get_industry(),
            'timestamp': session.get(self.TIMESTAMP_KEY),
            'is_set': self.has_industry()
        }