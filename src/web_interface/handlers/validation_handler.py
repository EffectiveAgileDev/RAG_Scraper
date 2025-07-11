"""Centralized validation handler for scraping requests."""

from typing import Dict, Any, Tuple, List
from dataclasses import dataclass

from src.config.url_validator import URLValidator
from src.web_interface.session_manager import IndustrySessionManager
from src.web_interface.validators.industry_validator import IndustryValidator


@dataclass
class ValidationResult:
    """Result of validation operations."""
    is_valid: bool
    error_message: str = ""
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class ValidationHandler:
    """Handles all validation logic for scraping requests."""
    
    def __init__(self):
        self.url_validator = URLValidator()
        self.session_manager = IndustrySessionManager()
        self.industry_validator = IndustryValidator(self.session_manager)
    
    def validate_scraping_request(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate complete scraping request data.
        
        Args:
            data: Request data dictionary
            
        Returns:
            ValidationResult with validation status and any errors
        """
        # Validate basic request data
        if not data:
            return ValidationResult(False, "No data provided")
        
        # Extract and validate URLs
        urls = self._extract_urls(data)
        if not urls:
            return ValidationResult(False, "No URLs provided")
        
        # Validate URLs
        url_validation = self._validate_urls(urls)
        if not url_validation.is_valid:
            return url_validation
        
        # Validate industry selection
        industry_validation = self._validate_industry_selection(data)
        if not industry_validation.is_valid:
            return industry_validation
        
        return ValidationResult(True)
    
    def _extract_urls(self, data: Dict[str, Any]) -> List[str]:
        """Extract URLs from request data."""
        urls = []
        if "url" in data:
            urls = [data["url"]]
        elif "urls" in data:
            urls = data["urls"]
        return urls
    
    def _validate_urls(self, urls: List[str]) -> ValidationResult:
        """Validate list of URLs."""
        validation_results = self.url_validator.validate_urls(urls)
        
        invalid_urls = [
            result for result in validation_results if not result.is_valid
        ]
        
        if invalid_urls:
            error_count = len(invalid_urls)
            total_count = len(urls)
            return ValidationResult(
                False,
                f"Invalid URLs provided: {error_count} of {total_count} URLs are invalid"
            )
        
        return ValidationResult(True)
    
    def _validate_industry_selection(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate industry selection and update session."""
        industry_result = self.industry_validator.validate_and_store_industry(data)
        
        if not industry_result.is_valid:
            return ValidationResult(False, industry_result.error_message)
        
        return ValidationResult(True)