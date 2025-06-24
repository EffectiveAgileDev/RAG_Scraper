"""Validation script generators for RAG framework integration."""

from typing import Dict, Any, List, Optional, Tuple
from abc import ABC, abstractmethod
from pathlib import Path

from .integration_config import FRAMEWORK_CONFIGS, VERSION_INFO


class BaseSampleGenerator(ABC):
    """Base class for sample code generators."""
    
    def __init__(self, framework: str, version: str = "1.0.0"):
        self.framework = framework
        self.version = version
        self.config = FRAMEWORK_CONFIGS.get(framework, {})
    
    @abstractmethod
    def generate(self, **kwargs) -> str:
        """Generate sample code."""
        pass
    
    def _format_header(self, title: str, description: str) -> str:
        """Generate header comment."""
        return f'''"""
{title}
{description}

Generated for RAG_Scraper version {self.version}
Framework: {self.framework}
"""

'''
    
    def _format_imports(self, imports: List[str]) -> str:
        """Format import statements."""
        return '\n'.join(imports) + '\n\n'
    
    def _format_class_header(self, class_name: str, description: str) -> str:
        """Format class definition with docstring."""
        return f'''class {class_name}:
    """{description}"""
    
'''


class ValidationScriptGenerator(BaseSampleGenerator):
    """Generator for validation scripts."""
    
    def __init__(self, version: str = "1.0.0"):
        super().__init__("validation", version)
    
    def generate(self, **kwargs) -> str:
        """Generate validation script."""
        code = self._format_header(
            "Schema validation script for RAG_Scraper data",
            "Validates restaurant data against JSON Schema with comprehensive error reporting"
        )
        
        code += self._generate_validation_script()
        return code
    
    def _generate_validation_script(self) -> str:
        """Generate complete validation script."""
        return '''#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import argparse

try:
    from jsonschema import validate, ValidationError, Draft7Validator
    from jsonschema.exceptions import SchemaError
except ImportError:
    print("Error: jsonschema package not found. Install with: pip install jsonschema")
    sys.exit(1)


class RestaurantDataValidator:
    """Comprehensive validator for restaurant data."""
    
    def __init__(self, schema_dir: Path):
        self.schema_dir = Path(schema_dir)
        self.schemas = self._load_schemas()
        self.errors = []
        self.warnings = []
    
    def _load_schemas(self) -> Dict[str, Dict]:
        """Load all validation schemas."""
        schemas = {}
        
        # Load restaurant data schema
        restaurant_schema_path = self.schema_dir / "restaurant_data.schema.json"
        if restaurant_schema_path.exists():
            with open(restaurant_schema_path, 'r') as f:
                schemas['restaurant'] = json.load(f)
        else:
            raise FileNotFoundError(f"Restaurant schema not found: {restaurant_schema_path}")
        
        # Load configuration schema
        config_schema_path = self.schema_dir / "config.schema.json"
        if config_schema_path.exists():
            with open(config_schema_path, 'r') as f:
                schemas['config'] = json.load(f)
        
        return schemas
    
    def validate_file(self, data_path: Path) -> Tuple[bool, List[str], List[str]]:
        """Validate a single data file."""
        self.errors.clear()
        self.warnings.clear()
        
        try:
            with open(data_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
            return False, self.errors, self.warnings
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return False, self.errors, self.warnings
        
        # Determine data type and validate
        if self._is_batch_result(data):
            return self._validate_batch_result(data)
        elif self._is_restaurant_list(data):
            return self._validate_restaurant_list(data)
        elif self._is_single_restaurant(data):
            return self._validate_single_restaurant(data)
        elif self._is_config_data(data):
            return self._validate_config(data)
        else:
            self.errors.append("Unable to determine data type")
            return False, self.errors, self.warnings
    
    def _is_batch_result(self, data: Any) -> bool:
        """Check if data is a batch result."""
        return (isinstance(data, dict) and 
                'restaurants' in data and 
                'metadata' in data)
    
    def _is_restaurant_list(self, data: Any) -> bool:
        """Check if data is a list of restaurants."""
        return (isinstance(data, list) and 
                len(data) > 0 and 
                isinstance(data[0], dict) and 
                'restaurant_id' in data[0])
    
    def _is_single_restaurant(self, data: Any) -> bool:
        """Check if data is a single restaurant."""
        return (isinstance(data, dict) and 
                'restaurant_id' in data and 
                'restaurant_name' in data)
    
    def _is_config_data(self, data: Any) -> bool:
        """Check if data is configuration."""
        return (isinstance(data, dict) and 
                'chunk_settings' in data)
    
    def _validate_batch_result(self, data: Dict) -> Tuple[bool, List[str], List[str]]:
        """Validate batch result data."""
        # Validate individual restaurants
        restaurants = data.get('restaurants', [])
        valid_count = 0
        
        for i, restaurant in enumerate(restaurants):
            try:
                validate(instance=restaurant, schema=self.schemas['restaurant'])
                valid_count += 1
                print(f"✓ Restaurant {i+1}: {restaurant.get('restaurant_name', 'Unknown')}")
            except ValidationError as e:
                self.errors.append(f"Restaurant {i+1} ({restaurant.get('restaurant_name', 'Unknown')}): {e.message}")
                print(f"✗ Restaurant {i+1}: {e.message}")
        
        # Check metadata
        metadata = data.get('metadata', {})
        if not isinstance(metadata, dict):
            self.errors.append("Metadata must be an object")
        else:
            # Validate metadata fields
            required_meta_fields = ['extraction_id', 'total_pages', 'successful_pages', 'failed_pages']
            for field in required_meta_fields:
                if field not in metadata:
                    self.warnings.append(f"Missing metadata field: {field}")
        
        # Summary
        total_restaurants = len(restaurants)
        print(f"\\nValidation Summary: {valid_count}/{total_restaurants} restaurants valid")
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _validate_restaurant_list(self, data: List) -> Tuple[bool, List[str], List[str]]:
        """Validate list of restaurants."""
        valid_count = 0
        
        for i, restaurant in enumerate(data):
            try:
                validate(instance=restaurant, schema=self.schemas['restaurant'])
                valid_count += 1
                print(f"✓ Restaurant {i+1}: {restaurant.get('restaurant_name', 'Unknown')}")
            except ValidationError as e:
                self.errors.append(f"Restaurant {i+1}: {e.message}")
                print(f"✗ Restaurant {i+1}: {e.message}")
        
        print(f"\\nValidation Summary: {valid_count}/{len(data)} restaurants valid")
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _validate_single_restaurant(self, data: Dict) -> Tuple[bool, List[str], List[str]]:
        """Validate single restaurant."""
        try:
            validate(instance=data, schema=self.schemas['restaurant'])
            print(f"✓ Restaurant valid: {data.get('restaurant_name', 'Unknown')}")
            return True, [], []
        except ValidationError as e:
            self.errors.append(e.message)
            print(f"✗ Restaurant invalid: {e.message}")
            return False, self.errors, self.warnings
    
    def _validate_config(self, data: Dict) -> Tuple[bool, List[str], List[str]]:
        """Validate configuration data."""
        if 'config' not in self.schemas:
            self.warnings.append("No configuration schema available")
            return True, [], self.warnings
        
        try:
            validate(instance=data, schema=self.schemas['config'])
            print("✓ Configuration valid")
            return True, [], []
        except ValidationError as e:
            self.errors.append(f"Configuration invalid: {e.message}")
            print(f"✗ Configuration invalid: {e.message}")
            return False, self.errors, self.warnings
    
    def validate_directory(self, directory: Path) -> Dict[str, Any]:
        """Validate all JSON files in directory."""
        results = {
            'total_files': 0,
            'valid_files': 0,
            'invalid_files': 0,
            'file_results': {}
        }
        
        for json_file in directory.rglob("*.json"):
            results['total_files'] += 1
            print(f"\\nValidating: {json_file}")
            
            is_valid, errors, warnings = self.validate_file(json_file)
            
            results['file_results'][str(json_file)] = {
                'valid': is_valid,
                'errors': errors,
                'warnings': warnings
            }
            
            if is_valid:
                results['valid_files'] += 1
            else:
                results['invalid_files'] += 1
        
        return results


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(
        description="Validate RAG_Scraper data against JSON schemas"
    )
    parser.add_argument(
        'data_path',
        type=Path,
        help="Path to JSON file or directory to validate"
    )
    parser.add_argument(
        '--schema-dir',
        type=Path,
        default=Path(__file__).parent.parent / "schemas",
        help="Directory containing JSON schemas"
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.data_path.exists():
        print(f"Error: Data path not found: {args.data_path}")
        sys.exit(1)
    
    if not args.schema_dir.exists():
        print(f"Error: Schema directory not found: {args.schema_dir}")
        sys.exit(1)
    
    # Create validator
    try:
        validator = RestaurantDataValidator(args.schema_dir)
    except Exception as e:
        print(f"Error initializing validator: {e}")
        sys.exit(1)
    
    # Validate
    try:
        if args.data_path.is_file():
            # Validate single file
            print(f"Validating file: {args.data_path}")
            is_valid, errors, warnings = validator.validate_file(args.data_path)
            
            if warnings:
                print("\\nWarnings:")
                for warning in warnings:
                    print(f"  - {warning}")
            
            if errors:
                print("\\nErrors:")
                for error in errors:
                    print(f"  - {error}")
            
            if is_valid:
                print("\\n✓ Validation successful!")
                sys.exit(0)
            else:
                print("\\n✗ Validation failed!")
                sys.exit(1)
        
        elif args.data_path.is_dir():
            # Validate directory
            print(f"Validating directory: {args.data_path}")
            results = validator.validate_directory(args.data_path)
            
            print(f"\\n{'='*60}")
            print("VALIDATION SUMMARY")
            print('='*60)
            print(f"Total files: {results['total_files']}")
            print(f"Valid files: {results['valid_files']}")
            print(f"Invalid files: {results['invalid_files']}")
            
            if results['invalid_files'] > 0:
                print("\\nFiles with errors:")
                for file_path, result in results['file_results'].items():
                    if not result['valid']:
                        print(f"  - {file_path}")
                        for error in result['errors'][:3]:  # Show first 3 errors
                            print(f"    {error}")
            
            # Exit code based on results
            if results['invalid_files'] == 0:
                print("\\n✓ All files valid!")
                sys.exit(0)
            else:
                print(f"\\n✗ {results['invalid_files']} files failed validation!")
                sys.exit(1)
        
        else:
            print(f"Error: Path must be a file or directory: {args.data_path}")
            sys.exit(1)
    
    except Exception as e:
        print(f"Validation error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
'''