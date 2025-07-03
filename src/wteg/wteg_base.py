"""Base classes for WTEG data structures.

Provides common functionality for WTEG data classes following DRY principle.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, fields, asdict
from typing import Dict, Any, TypeVar, Generic

T = TypeVar('T')


@dataclass
class WTEGSerializable(ABC):
    """Base class for serializable WTEG data structures."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert dataclass to dictionary with nested object handling."""
        result = {}
        
        for field in fields(self):
            value = getattr(self, field.name)
            
            if value is None:
                result[field.name] = None
            elif hasattr(value, 'to_dict'):
                # Handle nested WTEG objects
                result[field.name] = value.to_dict()
            elif isinstance(value, list):
                # Handle lists of WTEG objects or primitives
                result[field.name] = self._serialize_list(value)
            else:
                # Handle primitive types
                result[field.name] = value
                
        return result
    
    def _serialize_list(self, items: list) -> list:
        """Serialize a list of items."""
        serialized = []
        for item in items:
            if hasattr(item, 'to_dict'):
                serialized.append(item.to_dict())
            else:
                serialized.append(item)
        return serialized
    
    def is_complete(self) -> bool:
        """Check if all required fields are populated."""
        for field in fields(self):
            if field.default is None and getattr(self, field.name) is None:
                return False
        return True
    
    def get_completeness_score(self) -> float:
        """Calculate completeness score (0.0 to 1.0)."""
        total_fields = len(fields(self))
        populated_fields = sum(
            1 for field in fields(self) 
            if self._is_field_populated(getattr(self, field.name))
        )
        return populated_fields / total_fields if total_fields > 0 else 0.0
    
    def _is_field_populated(self, value: Any) -> bool:
        """Check if a field value is considered populated."""
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, list):
            return len(value) > 0
        if hasattr(value, 'is_complete'):
            return value.is_complete()
        return True


class WTEGValidator:
    """Validator for WTEG data structures."""
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        if not phone:
            return False
        # Remove common formatting characters
        digits = ''.join(c for c in phone if c.isdigit())
        return 10 <= len(digits) <= 11
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format."""
        if not url:
            return False
        return url.startswith(('http://', 'https://'))
    
    @staticmethod
    def validate_address(address: str) -> bool:
        """Validate address has minimal required components."""
        if not address:
            return False
        # Should have at least street and city/state info
        parts = address.split(',')
        return len(parts) >= 2 and all(part.strip() for part in parts)


class WTEGConstants:
    """Constants used across WTEG module."""
    
    # Confidence thresholds
    HIGH_CONFIDENCE = 0.8
    MEDIUM_CONFIDENCE = 0.5
    LOW_CONFIDENCE = 0.3
    
    # Field weights for scoring
    FIELD_WEIGHTS = {
        'name': 0.2,
        'description': 0.15,
        'location': 0.15,
        'cuisine': 0.1,
        'phone': 0.15,
        'menu': 0.15,
        'website': 0.1
    }
    
    # Extraction methods
    EXTRACTION_WTEG = 'wteg_specific'
    EXTRACTION_GENERIC = 'generic'
    EXTRACTION_AI = 'ai_enhanced'