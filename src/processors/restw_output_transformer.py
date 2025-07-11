"""RestW output transformer for obfuscating WTEG terminology."""

import re
from typing import Dict, Any, Optional, List, Union


class RestWOutputTransformer:
    """Transforms WTEG output to RestW format with obfuscated terminology."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize RestW output transformer.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.obfuscate_terminology_enabled = self.config.get('obfuscate_terminology', True)
        
        # Initialize field mappings
        self.field_mappings = self._initialize_field_mappings()
        
        # Initialize terminology mappings
        self.terminology_mappings = self._initialize_terminology_mappings()
        
        # Statistics tracking
        self.transformation_stats = {
            'fields_transformed': 0,
            'terminology_obfuscated': 0,
            'data_structures_processed': 0
        }
    
    @property
    def obfuscate_terminology(self) -> bool:
        """Get obfuscate terminology setting for backward compatibility."""
        return self.obfuscate_terminology_enabled
    
    def _initialize_field_mappings(self) -> Dict[str, str]:
        """Initialize field mappings from WTEG to RestW."""
        return {
            'WTEGLocation': 'RestWLocation',
            'WTEGMenuItem': 'RestWMenuItem',
            'WTEGServices': 'RestWServices',
            'WTEGContactInfo': 'RestWContactInfo',
            'WTEGWebLinks': 'RestWWebLinks',
            'WTEGRestaurantData': 'RestWRestaurantData',
            'WTEGOnlineOrdering': 'RestWOnlineOrdering'
        }
    
    def _initialize_terminology_mappings(self) -> Dict[str, str]:
        """Initialize terminology mappings."""
        return {
            'WTEG': 'RestW',
            'wteg': 'restw',
            'Wteg': 'RestW',
            'Where To Eat Guide': 'RestW',
            'where to eat guide': 'restw'
        }
    
    def transform(self, wteg_data: Any) -> Dict[str, Any]:
        """Transform WTEG data to RestW format.
        
        Args:
            wteg_data: WTEG data to transform
            
        Returns:
            RestW-formatted data
        """
        if not wteg_data:
            return {}
        
        # Reset statistics
        self.transformation_stats = {
            'fields_transformed': 0,
            'terminology_obfuscated': 0,
            'data_structures_processed': 0
        }
        
        # Transform the data
        transformed_data = self._transform_data_structure(wteg_data)
        
        # Apply terminology obfuscation if enabled
        if self.obfuscate_terminology_enabled:
            transformed_data = self._obfuscate_terminology_in_data(transformed_data)
        
        return transformed_data
    
    def _transform_data_structure(self, data: Any) -> Any:
        """Transform data structure recursively.
        
        Args:
            data: Data to transform
            
        Returns:
            Transformed data
        """
        self.transformation_stats['data_structures_processed'] += 1
        
        if isinstance(data, dict):
            return self._transform_dict(data)
        elif isinstance(data, list):
            return self._transform_list(data)
        else:
            return data
    
    def _transform_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform dictionary data.
        
        Args:
            data: Dictionary to transform
            
        Returns:
            Transformed dictionary
        """
        transformed = {}
        
        for key, value in data.items():
            # Transform key if needed
            transformed_key = self._transform_key(key)
            
            # Transform value recursively
            transformed_value = self._transform_data_structure(value)
            
            transformed[transformed_key] = transformed_value
            
            if transformed_key != key:
                self.transformation_stats['fields_transformed'] += 1
        
        return transformed
    
    def _transform_list(self, data: List[Any]) -> List[Any]:
        """Transform list data.
        
        Args:
            data: List to transform
            
        Returns:
            Transformed list
        """
        return [self._transform_data_structure(item) for item in data]
    
    def _transform_key(self, key: str) -> str:
        """Transform a key using field mappings.
        
        Args:
            key: Key to transform
            
        Returns:
            Transformed key
        """
        if not isinstance(key, str):
            return key
        
        # Apply field mappings
        for wteg_field, restw_field in self.field_mappings.items():
            if key == wteg_field:
                return restw_field
            # Handle camelCase and snake_case variations
            if key.replace('_', '').lower() == wteg_field.replace('_', '').lower():
                return restw_field
        
        return key
    
    def _obfuscate_terminology_in_data(self, data: Any) -> Any:
        """Obfuscate terminology in data recursively.
        
        Args:
            data: Data to obfuscate
            
        Returns:
            Data with obfuscated terminology
        """
        if isinstance(data, dict):
            return {
                self.obfuscate_terminology_text(key): self._obfuscate_terminology_in_data(value)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._obfuscate_terminology_in_data(item) for item in data]
        elif isinstance(data, str):
            return self.obfuscate_terminology_text(data)
        else:
            return data
    
    def obfuscate_terminology_text(self, text: str) -> str:
        """Obfuscate terminology in text.
        
        Args:
            text: Text to obfuscate
            
        Returns:
            Text with obfuscated terminology
        """
        if not isinstance(text, str):
            return text
        
        original_text = text
        
        # Apply terminology mappings
        for wteg_term, restw_term in self.terminology_mappings.items():
            text = text.replace(wteg_term, restw_term)
        
        # Track obfuscation
        if text != original_text:
            self.transformation_stats['terminology_obfuscated'] += 1
        
        return text
    
    def obfuscate_field_names(self, field_name: str) -> str:
        """Obfuscate field names.
        
        Args:
            field_name: Field name to obfuscate
            
        Returns:
            Obfuscated field name
        """
        # Apply field mappings
        transformed_name = self._transform_key(field_name)
        
        # Apply terminology obfuscation
        if self.obfuscate_terminology_enabled:
            transformed_name = self.obfuscate_terminology_text(transformed_name)
        
        return transformed_name
    
    def transform_menu_items(self, menu_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform menu items specifically.
        
        Args:
            menu_items: List of menu items
            
        Returns:
            Transformed menu items
        """
        if not menu_items:
            return []
        
        transformed_items = []
        
        for item in menu_items:
            if isinstance(item, dict):
                transformed_item = self._transform_dict(item)
                transformed_items.append(transformed_item)
            else:
                transformed_items.append(item)
        
        return transformed_items
    
    def transform_location_data(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform location data specifically.
        
        Args:
            location_data: Location data dictionary
            
        Returns:
            Transformed location data
        """
        if not location_data:
            return {}
        
        return self._transform_dict(location_data)
    
    def transform_services_data(self, services_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform services data specifically.
        
        Args:
            services_data: Services data dictionary
            
        Returns:
            Transformed services data
        """
        if not services_data:
            return {}
        
        return self._transform_dict(services_data)
    
    def transform_contact_info(self, contact_info: Dict[str, Any]) -> Dict[str, Any]:
        """Transform contact information specifically.
        
        Args:
            contact_info: Contact information dictionary
            
        Returns:
            Transformed contact information
        """
        if not contact_info:
            return {}
        
        return self._transform_dict(contact_info)
    
    def transform_web_links(self, web_links: Dict[str, Any]) -> Dict[str, Any]:
        """Transform web links specifically.
        
        Args:
            web_links: Web links dictionary
            
        Returns:
            Transformed web links
        """
        if not web_links:
            return {}
        
        return self._transform_dict(web_links)
    
    def validate_transformed_output(self, output: Dict[str, Any]) -> bool:
        """Validate transformed output.
        
        Args:
            output: Output to validate
            
        Returns:
            True if output is valid
        """
        if not isinstance(output, dict):
            return False
        
        # Check that no WTEG terminology remains if obfuscation is enabled
        if self.obfuscate_terminology_enabled:
            output_str = str(output)
            if 'WTEG' in output_str or 'wteg' in output_str:
                return False
        
        # Check for expected RestW fields
        expected_fields = ['location', 'menu_items', 'services_offered', 'contact_info', 'web_links']
        has_expected_field = any(field in output for field in expected_fields)
        
        return has_expected_field
    
    def get_transformation_statistics(self) -> Dict[str, Any]:
        """Get transformation statistics.
        
        Returns:
            Dictionary with transformation statistics
        """
        return self.transformation_stats.copy()
    
    def create_transformation_report(self, original_data: Any, transformed_data: Any) -> Dict[str, Any]:
        """Create transformation report.
        
        Args:
            original_data: Original data before transformation
            transformed_data: Data after transformation
            
        Returns:
            Transformation report
        """
        return {
            'transformation_statistics': self.get_transformation_statistics(),
            'original_data_type': type(original_data).__name__,
            'transformed_data_type': type(transformed_data).__name__,
            'obfuscation_applied': self.obfuscate_terminology_enabled,
            'field_mappings_used': len(self.field_mappings),
            'terminology_mappings_used': len(self.terminology_mappings),
            'transformation_successful': self.validate_transformed_output(transformed_data)
        }
    
    def get_reverse_mappings(self) -> Dict[str, str]:
        """Get reverse mappings from RestW to WTEG.
        
        Returns:
            Dictionary with reverse mappings
        """
        return {v: k for k, v in self.field_mappings.items()}
    
    def reverse_transform(self, restw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Reverse transform RestW data back to WTEG format.
        
        Args:
            restw_data: RestW data to reverse transform
            
        Returns:
            WTEG-formatted data
        """
        if not restw_data:
            return {}
        
        reverse_mappings = self.get_reverse_mappings()
        
        # Apply reverse field mappings
        wteg_data = {}
        for key, value in restw_data.items():
            wteg_key = reverse_mappings.get(key, key)
            wteg_data[wteg_key] = value
        
        # Apply reverse terminology mappings
        reverse_terminology = {v: k for k, v in self.terminology_mappings.items()}
        wteg_data = self._apply_reverse_terminology(wteg_data, reverse_terminology)
        
        return wteg_data
    
    def _apply_reverse_terminology(self, data: Any, reverse_mappings: Dict[str, str]) -> Any:
        """Apply reverse terminology mappings.
        
        Args:
            data: Data to apply reverse mappings to
            reverse_mappings: Reverse terminology mappings
            
        Returns:
            Data with reverse terminology applied
        """
        if isinstance(data, dict):
            return {
                self._reverse_terminology_in_text(key, reverse_mappings): 
                self._apply_reverse_terminology(value, reverse_mappings)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._apply_reverse_terminology(item, reverse_mappings) for item in data]
        elif isinstance(data, str):
            return self._reverse_terminology_in_text(data, reverse_mappings)
        else:
            return data
    
    def _reverse_terminology_in_text(self, text: str, reverse_mappings: Dict[str, str]) -> str:
        """Apply reverse terminology mappings to text.
        
        Args:
            text: Text to transform
            reverse_mappings: Reverse terminology mappings
            
        Returns:
            Text with reverse terminology applied
        """
        if not isinstance(text, str):
            return text
        
        for restw_term, wteg_term in reverse_mappings.items():
            text = text.replace(restw_term, wteg_term)
        
        return text