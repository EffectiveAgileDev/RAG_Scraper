"""Base RestW processor class."""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class RestWProcessor(ABC):
    """Base class for RestW processors."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize RestW processor.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.schema_type = self.config.get('schema_type', 'RestW')
        self.obfuscate_terminology = self.config.get('obfuscate_terminology', True)
        
        # Initialize output transformer
        from .restw_output_transformer import RestWOutputTransformer
        self.output_transformer = RestWOutputTransformer(self.config)
    
    def uses_wteg_schema(self) -> bool:
        """Check if processor uses WTEG schema internally."""
        return self.schema_type == 'RestW'
    
    def get_schema_type(self) -> str:
        """Get schema type."""
        return self.schema_type
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Get processing configuration."""
        return {
            'schema_type': self.schema_type,
            'obfuscate_terminology': self.obfuscate_terminology,
            'uses_wteg_schema': self.uses_wteg_schema()
        }
    
    def transform_wteg_to_restw(self, wteg_data: Any) -> Dict[str, Any]:
        """Transform WTEG data to RestW format."""
        return self.output_transformer.transform(wteg_data)
    
    def validate_restw_output(self, output: Dict[str, Any]) -> bool:
        """Validate RestW output."""
        if not isinstance(output, dict):
            return False
        
        # Check for at least one expected RestW field
        expected_fields = ['location', 'menu_items', 'services_offered', 'contact_info', 'web_links']
        return any(field in output for field in expected_fields)
    
    def get_error_handling_config(self) -> Dict[str, Any]:
        """Get error handling configuration."""
        return {
            'fallback_to_standard': True,
            'log_errors': True,
            'retry_count': 3,
            'retry_delay': 1.0
        }