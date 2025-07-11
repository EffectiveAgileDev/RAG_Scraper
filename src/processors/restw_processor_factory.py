"""RestW processor factory for creating obfuscated WTEG processors."""

from typing import Dict, Any, Optional

from .restw_base_processor import RestWProcessor
from .restw_url_processor import RestWUrlProcessor
from .restw_pdf_processor import RestWPdfProcessor
from .restw_html_processor import RestWHtmlProcessor


class RestWProcessorFactory:
    """Factory for creating RestW processors."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize RestW processor factory.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.obfuscate_terminology = self.config.get('obfuscate_terminology', True)
        self.use_wteg_processors = self.config.get('use_wteg_processors', True)
        
        # Processor registry
        self.processors = {
            'url': RestWUrlProcessor,
            'pdf': RestWPdfProcessor,
            'html': RestWHtmlProcessor
        }
    
    def create_processor(self, processor_type: str, schema_type: str) -> RestWProcessor:
        """Create a RestW processor.
        
        Args:
            processor_type: Type of processor ('url', 'pdf', 'html')
            schema_type: Schema type ('RestW', 'standard')
            
        Returns:
            RestW processor instance
            
        Raises:
            ValueError: If processor type is invalid
        """
        if processor_type not in self.processors:
            raise ValueError(f"Invalid processor type: {processor_type}")
        
        processor_class = self.processors[processor_type]
        
        # Create processor configuration
        processor_config = {
            'schema_type': schema_type,
            'obfuscate_terminology': self.obfuscate_terminology,
            'use_wteg_processors': self.use_wteg_processors
        }
        
        return processor_class(processor_config)
    
    def get_available_processors(self) -> list:
        """Get list of available processor types."""
        return list(self.processors.keys())
    
    def get_processor_config(self, processor_type: str) -> Dict[str, Any]:
        """Get configuration for a processor type."""
        if processor_type not in self.processors:
            return {}
        
        return {
            'processor_type': processor_type,
            'uses_wteg_processors': self.use_wteg_processors,
            'obfuscate_output': self.obfuscate_terminology,
            'available': True
        }
    
    def validate_processor_type(self, processor_type: str) -> bool:
        """Validate processor type."""
        return processor_type in self.processors
    
    def validate_schema_type(self, schema_type: str) -> bool:
        """Validate schema type."""
        valid_schemas = ['RestW', 'standard']
        return schema_type in valid_schemas
    
    def register_processor(self, processor_type: str, processor_class: type):
        """Register a new processor type.
        
        Args:
            processor_type: Type identifier
            processor_class: Processor class
        """
        self.processors[processor_type] = processor_class
    
    def create_batch_processor(self, processor_type: str, urls: list) -> 'RestWBatchProcessor':
        """Create batch processor for multiple URLs.
        
        Args:
            processor_type: Type of processor
            urls: List of URLs to process
            
        Returns:
            RestW batch processor instance
        """
        from .restw_batch_processor import RestWBatchProcessor
        
        batch_config = {
            'processor_type': processor_type,
            'urls': urls,
            'obfuscate_terminology': self.obfuscate_terminology,
            'use_wteg_processors': self.use_wteg_processors
        }
        
        return RestWBatchProcessor(batch_config)
    
    def get_factory_configuration(self) -> Dict[str, Any]:
        """Get factory configuration."""
        return {
            'obfuscate_terminology': self.obfuscate_terminology,
            'use_wteg_processors': self.use_wteg_processors,
            'available_processors': self.get_available_processors(),
            'processor_registry': list(self.processors.keys())
        }
    
    def validate_factory_configuration(self, config: Dict[str, Any]) -> bool:
        """Validate factory configuration."""
        try:
            # Check boolean fields
            boolean_fields = ['obfuscate_terminology', 'use_wteg_processors']
            for field in boolean_fields:
                if field in config and not isinstance(config[field], bool):
                    return False
            
            return True
        except Exception:
            return False
    
    def create_processor_from_config(self, config: Dict[str, Any]) -> RestWProcessor:
        """Create processor from configuration dictionary.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            RestW processor instance
        """
        processor_type = config.get('processor_type', 'url')
        schema_type = config.get('schema_type', 'RestW')
        
        return self.create_processor(processor_type, schema_type)
    
    def get_processor_statistics(self) -> Dict[str, Any]:
        """Get processor factory statistics."""
        return {
            'total_processors': len(self.processors),
            'available_processors': self.get_available_processors(),
            'wteg_processors_enabled': self.use_wteg_processors,
            'terminology_obfuscation': self.obfuscate_terminology
        }