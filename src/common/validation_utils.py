"""Common validation utilities and result classes."""
import re
from typing import Optional, Union, List
from urllib.parse import urlparse
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Base result class for validation operations."""

    is_valid: bool
    error_message: Optional[str] = None
    value: Optional[str] = None


class ValidationUtils:
    """Common validation utilities used across the application."""

    @staticmethod
    def validate_not_empty(value: str, field_name: str) -> Optional[str]:
        """Validate that a string value is not empty.
        
        Args:
            value: The string to validate
            field_name: Name of the field for error messages
            
        Returns:
            None if valid, error message if invalid
        """
        if not value or not value.strip():
            return f"{field_name} cannot be empty"
        return None

    @staticmethod
    def validate_positive_number(
        value: Union[int, float], field_name: str
    ) -> Optional[str]:
        """Validate that a number is positive.
        
        Args:
            value: The number to validate
            field_name: Name of the field for error messages
            
        Returns:
            None if valid, error message if invalid
        """
        if value is None:
            return f"{field_name} cannot be None"
        if not isinstance(value, (int, float)):
            return f"{field_name} must be a number"
        if value <= 0:
            return f"{field_name} must be positive"
        return None

    @staticmethod
    def validate_url_format(url: str) -> Optional[str]:
        """Validate URL format.
        
        Args:
            url: The URL to validate
            
        Returns:
            None if valid, error message if invalid
        """
        if not url or not url.strip():
            return "URL cannot be empty"

        try:
            parsed = urlparse(url.strip())
            if not parsed.scheme:
                return "URL must include a scheme (http:// or https://)"
            if not parsed.netloc:
                return "URL must include a domain"
            if parsed.scheme not in ["http", "https"]:
                return "URL scheme must be http or https"
            return None
        except Exception as e:
            return f"Invalid URL format: {str(e)}"

    @staticmethod
    def validate_enum_choice(
        value: str, choices: List[str], field_name: str
    ) -> Optional[str]:
        """Validate that a value is one of the allowed choices.
        
        Args:
            value: The value to validate
            choices: List of allowed values
            field_name: Name of the field for error messages
            
        Returns:
            None if valid, error message if invalid
        """
        if not value:
            return f"{field_name} cannot be empty"
        if value not in choices:
            return f"{field_name} must be one of: {', '.join(choices)}"
        return None

    @staticmethod
    def validate_range(
        value: Union[int, float], 
        min_val: Union[int, float], 
        max_val: Union[int, float], 
        field_name: str
    ) -> Optional[str]:
        """Validate that a number is within a specified range.
        
        Args:
            value: The number to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            field_name: Name of the field for error messages
            
        Returns:
            None if valid, error message if invalid
        """
        if value is None:
            return f"{field_name} cannot be None"
        if not isinstance(value, (int, float)):
            return f"{field_name} must be a number"
        if value < min_val or value > max_val:
            return f"{field_name} must be between {min_val} and {max_val}"
        return None

    @staticmethod
    def validate_filename(filename: str) -> Optional[str]:
        """Validate filename for safety.
        
        Args:
            filename: The filename to validate
            
        Returns:
            None if valid, error message if invalid
        """
        if not filename or not filename.strip():
            return "Filename cannot be empty"

        # Check for dangerous patterns
        dangerous_patterns = [
            r"\.\.[\\/]",  # Directory traversal
            r"^[\\/]",     # Absolute paths
            r"[\x00-\x1f]",  # Control characters
            r"[<>:\"|?*]",   # Windows reserved characters
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, filename):
                return f"Filename contains unsafe characters: {filename}"

        # Check for reserved names (Windows)
        reserved_names = {
            "CON", "PRN", "AUX", "NUL",
            "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
            "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
        }
        
        name_without_ext = filename.split('.')[0].upper()
        if name_without_ext in reserved_names:
            return f"Filename uses reserved name: {filename}"

        return None

    @staticmethod
    def create_validation_result(
        is_valid: bool, 
        error_message: Optional[str] = None, 
        value: Optional[str] = None
    ) -> ValidationResult:
        """Create a standardized validation result.
        
        Args:
            is_valid: Whether the validation passed
            error_message: Error message if validation failed
            value: The validated value
            
        Returns:
            ValidationResult object
        """
        return ValidationResult(
            is_valid=is_valid,
            error_message=error_message,
            value=value
        )