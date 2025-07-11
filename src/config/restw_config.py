"""RestW configuration management for obfuscated WTEG schema usage."""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class RestWFieldConfig:
    """Configuration for individual RestW fields."""
    
    field_name: str
    enabled: bool = True
    required: bool = False
    display_name: str = ""
    description: str = ""
    
    def __post_init__(self):
        """Set default display name if not provided."""
        if not self.display_name:
            self.display_name = self._generate_display_name()
    
    def _generate_display_name(self) -> str:
        """Generate display name from field name."""
        display_names = {
            'location': 'Location Data',
            'menu_items': 'Menu Items',
            'services_offered': 'Services Offered',
            'contact_info': 'Contact Information',
            'web_links': 'Web Links'
        }
        return display_names.get(self.field_name, self.field_name.replace('_', ' ').title())
    
    def get_display_name(self) -> str:
        """Get display name for field."""
        return self.display_name
    
    def get_description(self) -> str:
        """Get description for field."""
        if self.description:
            return self.description
        
        descriptions = {
            'location': 'Street address, city, state, zip code, and neighborhood information',
            'menu_items': 'Menu items with names, prices, categories, and descriptions',
            'services_offered': 'Available services like delivery, takeout, catering, and reservations',
            'contact_info': 'Phone numbers, formatted display, and clickable links',
            'web_links': 'Official website, menu PDFs, and social media links'
        }
        return descriptions.get(self.field_name, f'Extract {self.field_name.replace("_", " ")} data')
    
    def get_wteg_mapping(self) -> Dict[str, str]:
        """Get WTEG mapping for field."""
        mappings = {
            'location': {'wteg_field': 'location', 'wteg_class': 'WTEGLocation'},
            'menu_items': {'wteg_field': 'menu_items', 'wteg_class': 'WTEGMenuItem'},
            'services_offered': {'wteg_field': 'services_offered', 'wteg_class': 'WTEGServices'},
            'contact_info': {'wteg_field': 'click_to_call', 'wteg_class': 'WTEGContactInfo'},
            'web_links': {'wteg_field': 'click_for_website', 'wteg_class': 'WTEGWebLinks'}
        }
        return mappings.get(self.field_name, {'wteg_field': self.field_name, 'wteg_class': 'WTEGGeneric'})
    
    @staticmethod
    def is_valid_field_name(field_name: str) -> bool:
        """Check if field name is valid."""
        valid_fields = ['location', 'menu_items', 'services_offered', 'contact_info', 'web_links']
        return field_name in valid_fields
    
    @staticmethod
    def get_available_fields() -> List[str]:
        """Get list of available fields."""
        return ['location', 'menu_items', 'services_offered', 'contact_info', 'web_links']
    
    def validate_field_configuration(self, config: Dict[str, Any]) -> bool:
        """Validate field configuration."""
        try:
            # Check required fields
            if not isinstance(config.get('enabled'), bool):
                return False
            
            # Check optional fields
            if 'required' in config and not isinstance(config['required'], bool):
                return False
            
            return True
        except Exception:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'field_name': self.field_name,
            'enabled': self.enabled,
            'required': self.required,
            'display_name': self.display_name,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RestWFieldConfig':
        """Create from dictionary."""
        return cls(
            field_name=data['field_name'],
            enabled=data.get('enabled', True),
            required=data.get('required', False),
            display_name=data.get('display_name', ''),
            description=data.get('description', '')
        )


@dataclass
class RestWProcessingConfig:
    """Configuration for RestW processing."""
    
    use_wteg_processors: bool = True
    obfuscate_terminology: bool = True
    parallel_processing: bool = True
    batch_size: int = 10
    max_workers: int = 4
    timeout: int = 30
    
    def get_processor_factory_config(self) -> Dict[str, Any]:
        """Get processor factory configuration."""
        return {
            'use_wteg_processors': self.use_wteg_processors,
            'obfuscate_output': self.obfuscate_terminology,
            'parallel_processing': self.parallel_processing
        }
    
    def get_extraction_config(self) -> Dict[str, Any]:
        """Get extraction configuration."""
        return {
            'field_mappings': self._get_field_mappings(),
            'output_format': 'RestW',
            'obfuscate_terminology': self.obfuscate_terminology
        }
    
    def _get_field_mappings(self) -> Dict[str, str]:
        """Get field mappings from WTEG to RestW."""
        return {
            'WTEGLocation': 'RestWLocation',
            'WTEGMenuItem': 'RestWMenuItem',
            'WTEGServices': 'RestWServices',
            'WTEGContactInfo': 'RestWContactInfo',
            'WTEGWebLinks': 'RestWWebLinks'
        }
    
    def get_output_transformation_config(self) -> Dict[str, Any]:
        """Get output transformation configuration."""
        return {
            'terminology_mapping': {
                'WTEG': 'RestW',
                'wteg': 'restw'
            },
            'field_name_mapping': self._get_field_mappings(),
            'obfuscate_class_names': self.obfuscate_terminology
        }
    
    def validate_processing_configuration(self, config: Dict[str, Any]) -> bool:
        """Validate processing configuration."""
        try:
            # Check boolean fields
            boolean_fields = ['use_wteg_processors', 'obfuscate_terminology', 'parallel_processing']
            for field in boolean_fields:
                if field in config and not isinstance(config[field], bool):
                    return False
            
            # Check integer fields
            integer_fields = ['batch_size', 'max_workers', 'timeout']
            for field in integer_fields:
                if field in config and not isinstance(config[field], int):
                    return False
            
            return True
        except Exception:
            return False
    
    def get_batch_processing_config(self) -> Dict[str, Any]:
        """Get batch processing configuration."""
        return {
            'batch_size': self.batch_size,
            'max_workers': self.max_workers,
            'timeout': self.timeout,
            'parallel_processing': self.parallel_processing
        }
    
    def get_error_handling_config(self) -> Dict[str, Any]:
        """Get error handling configuration."""
        return {
            'fallback_to_standard': True,
            'log_wteg_errors': True,
            'retry_count': 3,
            'retry_delay': 1.0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'use_wteg_processors': self.use_wteg_processors,
            'obfuscate_terminology': self.obfuscate_terminology,
            'parallel_processing': self.parallel_processing,
            'batch_size': self.batch_size,
            'max_workers': self.max_workers,
            'timeout': self.timeout
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RestWProcessingConfig':
        """Create from dictionary."""
        return cls(
            use_wteg_processors=data.get('use_wteg_processors', True),
            obfuscate_terminology=data.get('obfuscate_terminology', True),
            parallel_processing=data.get('parallel_processing', True),
            batch_size=data.get('batch_size', 10),
            max_workers=data.get('max_workers', 4),
            timeout=data.get('timeout', 30)
        )


class RestWConfig:
    """Main RestW configuration manager."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize RestW configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        self.obfuscate_wteg = self.config.get('obfuscate_wteg', True)
        self.default_fields = self.config.get('default_fields', [
            'location', 'menu_items', 'services_offered', 'contact_info', 'web_links'
        ])
        
        # Initialize sub-configurations
        self.processing_config = RestWProcessingConfig.from_dict(
            self.config.get('processing_config', {})
        )
        
        # Configuration file path
        self.config_file_path = self.config.get('config_file_path', 'restw_config.json')
    
    def is_restw_schema_selected(self, form_data: Dict[str, Any]) -> bool:
        """Check if RestW schema is selected in form data."""
        return form_data.get('schema') == 'RestW'
    
    def get_extraction_fields(self, custom_fields: Optional[List[str]] = None) -> List[str]:
        """Get extraction fields list."""
        if custom_fields:
            return custom_fields
        return self.default_fields
    
    def get_field_configuration(self, field_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific field."""
        if not RestWFieldConfig.is_valid_field_name(field_name):
            return None
        
        field_config = RestWFieldConfig(field_name)
        return {
            'display_name': field_config.get_display_name(),
            'description': field_config.get_description(),
            'wteg_mapping': field_config.get_wteg_mapping()
        }
    
    def get_processing_configuration(self) -> Dict[str, Any]:
        """Get processing configuration."""
        return {
            'use_wteg_processors': True,
            'obfuscate_terminology': self.obfuscate_wteg,
            'parallel_processing': self.processing_config.parallel_processing,
            'batch_size': self.processing_config.batch_size
        }
    
    def get_output_configuration(self) -> Dict[str, Any]:
        """Get output configuration."""
        return {
            'schema_name': 'RestW',
            'field_mappings': self.get_wteg_to_restw_mapping(),
            'obfuscate_terminology': self.obfuscate_wteg
        }
    
    def obfuscate_wteg_terminology(self, text: str) -> str:
        """Obfuscate WTEG terminology in text."""
        if not self.obfuscate_wteg:
            return text
        
        # Replace WTEG with RestW
        text = text.replace('WTEG', 'RestW')
        text = text.replace('wteg', 'restw')
        text = text.replace('Wteg', 'RestW')
        
        return text
    
    def get_wteg_to_restw_mapping(self) -> Dict[str, str]:
        """Get WTEG to RestW field mapping."""
        return {
            'WTEGLocation': 'RestWLocation',
            'WTEGMenuItem': 'RestWMenuItem',
            'WTEGServices': 'RestWServices',
            'WTEGContactInfo': 'RestWContactInfo',
            'WTEGWebLinks': 'RestWWebLinks',
            'WTEGRestaurantData': 'RestWRestaurantData'
        }
    
    def translate_wteg_data_to_restw(self, wteg_data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate WTEG data to RestW format."""
        if not wteg_data:
            return {}
        
        # Create a copy to avoid modifying original
        restw_data = wteg_data.copy()
        
        # Apply terminology obfuscation if enabled
        if self.obfuscate_wteg:
            restw_data = self._obfuscate_data_terminology(restw_data)
        
        return restw_data
    
    def _obfuscate_data_terminology(self, data: Any) -> Any:
        """Recursively obfuscate terminology in data."""
        if isinstance(data, dict):
            return {
                self.obfuscate_wteg_terminology(key): self._obfuscate_data_terminology(value)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._obfuscate_data_terminology(item) for item in data]
        elif isinstance(data, str):
            return self.obfuscate_wteg_terminology(data)
        else:
            return data
    
    def validate_restw_configuration(self, config: Dict[str, Any]) -> bool:
        """Validate RestW configuration."""
        try:
            # Check enabled field
            if 'enabled' in config and not isinstance(config['enabled'], bool):
                return False
            
            # Check fields
            if 'fields' in config:
                fields = config['fields']
                if not isinstance(fields, list):
                    return False
                
                # Validate each field
                for field in fields:
                    if not RestWFieldConfig.is_valid_field_name(field):
                        return False
            
            return True
        except Exception:
            return False
    
    def has_saved_configuration(self) -> bool:
        """Check if saved configuration exists."""
        saved_config = self._load_saved_configuration()
        return saved_config is not None
    
    def _load_saved_configuration(self) -> Optional[Dict[str, Any]]:
        """Load saved configuration."""
        try:
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return None
    
    def save_configuration(self, config_data: Dict[str, Any]) -> bool:
        """Save configuration to file."""
        try:
            self._save_configuration_to_file(config_data)
            return True
        except Exception:
            return False
    
    def _save_configuration_to_file(self, config_data: Dict[str, Any]):
        """Save configuration to file."""
        with open(self.config_file_path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def load_configuration(self) -> Optional[Dict[str, Any]]:
        """Load configuration from file."""
        return self._load_configuration_from_file()
    
    def _load_configuration_from_file(self) -> Optional[Dict[str, Any]]:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return None
    
    def get_batch_configuration(self) -> Dict[str, Any]:
        """Get batch processing configuration."""
        return {
            'batch_size': self.processing_config.batch_size,
            'parallel_processing': self.processing_config.parallel_processing,
            'max_workers': self.processing_config.max_workers,
            'use_wteg_processors': True
        }
    
    def get_ui_configuration(self) -> Dict[str, Any]:
        """Get UI configuration."""
        return {
            'show_restw_option': self.enabled,
            'available_for_industries': ['Restaurant'],
            'default_fields': self.default_fields,
            'field_configurations': {
                field: self.get_field_configuration(field)
                for field in RestWFieldConfig.get_available_fields()
            }
        }
    
    def is_enabled_for_industry(self, industry: str) -> bool:
        """Check if RestW is enabled for industry."""
        return industry == 'Restaurant' and self.enabled
    
    def get_help_text_for_field(self, field_name: str) -> str:
        """Get help text for specific field."""
        field_config = RestWFieldConfig(field_name)
        help_text = field_config.get_description()
        
        # Obfuscate if enabled
        if self.obfuscate_wteg:
            help_text = self.obfuscate_wteg_terminology(help_text)
        
        return help_text
    
    def get_processor_mapping(self) -> Dict[str, str]:
        """Get processor mapping for different input types."""
        return {
            'url': 'RestWUrlProcessor (uses WTEG internally)',
            'pdf': 'RestWPdfProcessor (uses WTEG internally)',
            'html': 'RestWHtmlProcessor (uses WTEG internally)'
        }
    
    def get_javascript_config(self) -> Dict[str, Any]:
        """Get JavaScript configuration for UI."""
        return {
            'enabled': self.enabled,
            'available_for_industries': ['Restaurant'],
            'default_fields': self.default_fields,
            'obfuscate_wteg': self.obfuscate_wteg,
            'handlers': {
                'onChange': 'handleRestWSchemaChange',
                'onFieldChange': 'handleRestWFieldChange',
                'onShow': 'showRestWOptions',
                'onHide': 'hideRestWOptions'
            }
        }
    
    def create_default_configuration(self) -> Dict[str, Any]:
        """Create default configuration."""
        return {
            'enabled': True,
            'obfuscate_wteg': True,
            'default_fields': ['location', 'menu_items', 'services_offered', 'contact_info', 'web_links'],
            'processing_config': self.processing_config.to_dict(),
            'ui_config': self.get_ui_configuration()
        }