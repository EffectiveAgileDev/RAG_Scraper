"""File generator service for web interface integration."""
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .text_file_generator import TextFileGenerator, TextFileConfig, TextFileConfigManager
from src.scraper.multi_strategy_scraper import RestaurantData
from src.config.file_permission_validator import FilePermissionValidator


@dataclass
class FileGenerationRequest:
    """Request for file generation with restaurant data."""
    restaurant_data: List[RestaurantData]
    file_format: str
    output_directory: Optional[str] = None
    allow_overwrite: bool = True
    save_preferences: bool = False
    
    def validate(self) -> List[str]:
        """Validate the request parameters.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Validate restaurant data
        if not self.restaurant_data:
            errors.append("No restaurant data provided")
        
        # Validate file format
        supported_formats = ['text']  # Will expand in future sprints
        if self.file_format not in supported_formats:
            errors.append(f"Unsupported file format: {self.file_format}. Supported: {supported_formats}")
        
        return errors


class FileGeneratorService:
    """Service for generating files from restaurant data with web interface integration."""
    
    def __init__(self, config_file: str = "file_generator_config.json"):
        """Initialize file generator service.
        
        Args:
            config_file: Path to configuration file for persistence
        """
        self.config_manager = TextFileConfigManager(config_file)
        self.permission_validator = FilePermissionValidator()
        
        # Load existing configuration or create default
        self.current_config = self.config_manager.get_or_create_config()
    
    def generate_file(self, request: FileGenerationRequest) -> Dict[str, Any]:
        """Generate file from restaurant data.
        
        Args:
            request: File generation request
            
        Returns:
            Dictionary with generation result
        """
        try:
            # Validate request
            validation_errors = request.validate()
            if validation_errors:
                return {
                    'success': False,
                    'error': '; '.join(validation_errors)
                }
            
            # Determine output directory
            output_directory = request.output_directory or self.current_config.output_directory
            
            # Create output directory if needed
            try:
                os.makedirs(output_directory, exist_ok=True)
            except (OSError, PermissionError) as e:
                return {
                    'success': False,
                    'error': f"Cannot create output directory: {str(e)}"
                }
            
            # Validate directory permissions
            permission_result = self.validate_directory_permissions(output_directory)
            if not permission_result['valid']:
                return {
                    'success': False,
                    'error': f"Directory permission error: {permission_result['error']}"
                }
            
            # Update configuration if saving preferences
            if request.save_preferences:
                self.current_config.output_directory = output_directory
                self.current_config.allow_overwrite = request.allow_overwrite
                self.config_manager.save_config(self.current_config)
            
            # Generate file based on format
            if request.file_format == 'text':
                return self._generate_text_file(request, output_directory)
            else:
                return {
                    'success': False,
                    'error': f"File format not implemented: {request.file_format}"
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error during file generation: {str(e)}"
            }
    
    def _generate_text_file(self, request: FileGenerationRequest, output_directory: str) -> Dict[str, Any]:
        """Generate text file from restaurant data.
        
        Args:
            request: File generation request
            output_directory: Directory to save file
            
        Returns:
            Dictionary with generation result
        """
        try:
            # Create text file configuration
            config = TextFileConfig(
                output_directory=output_directory,
                allow_overwrite=request.allow_overwrite,
                encoding='utf-8',
                filename_pattern='WebScrape_{timestamp}.txt'
            )
            
            # Generate file
            generator = TextFileGenerator(config)
            file_path = generator.generate_file(request.restaurant_data)
            
            return {
                'success': True,
                'file_path': file_path,
                'file_format': 'text',
                'restaurant_count': len(request.restaurant_data)
            }
        
        except ValueError as e:
            return {
                'success': False,
                'error': f"No data available for file generation: {str(e)}"
            }
        except PermissionError as e:
            return {
                'success': False,
                'error': f"Permission denied: {str(e)}"
            }
        except FileExistsError as e:
            return {
                'success': False,
                'error': f"File already exists: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Text file generation failed: {str(e)}"
            }
    
    def validate_directory_permissions(self, directory_path: str) -> Dict[str, Any]:
        """Validate directory permissions for file generation.
        
        Args:
            directory_path: Path to directory to validate
            
        Returns:
            Dictionary with validation result
        """
        try:
            result = self.permission_validator.validate_directory_writable(directory_path)
            
            if result.is_writable:
                return {'valid': True}
            else:
                return {
                    'valid': False,
                    'error': result.error_message or "Directory is not writable"
                }
        
        except Exception as e:
            return {
                'valid': False,
                'error': f"Error validating directory: {str(e)}"
            }
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats.
        
        Returns:
            List of supported format strings
        """
        return ['text']  # Will expand in future sprints (pdf, etc.)
    
    def get_current_config(self) -> Dict[str, Any]:
        """Get current configuration.
        
        Returns:
            Dictionary with current configuration
        """
        return {
            'output_directory': self.current_config.output_directory,
            'allow_overwrite': self.current_config.allow_overwrite,
            'encoding': self.current_config.encoding,
            'filename_pattern': self.current_config.filename_pattern
        }
    
    def update_config(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """Update configuration.
        
        Args:
            new_config: Dictionary with new configuration values
            
        Returns:
            Dictionary with update result
        """
        try:
            # Validate new configuration
            if 'output_directory' in new_config:
                permission_result = self.validate_directory_permissions(new_config['output_directory'])
                if not permission_result['valid']:
                    return {
                        'success': False,
                        'error': f"Invalid output directory: {permission_result['error']}"
                    }
                
                # Create directory if needed
                os.makedirs(new_config['output_directory'], exist_ok=True)
            
            # Update configuration
            if 'output_directory' in new_config:
                self.current_config.output_directory = new_config['output_directory']
            if 'allow_overwrite' in new_config:
                self.current_config.allow_overwrite = new_config['allow_overwrite']
            if 'encoding' in new_config:
                self.current_config.encoding = new_config['encoding']
            if 'filename_pattern' in new_config:
                self.current_config.filename_pattern = new_config['filename_pattern']
            
            # Save updated configuration
            self.config_manager.save_config(self.current_config)
            
            return {'success': True}
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to update configuration: {str(e)}"
            }
    
    def get_output_directory_options(self) -> Dict[str, Any]:
        """Get common output directory options for user interface.
        
        Returns:
            Dictionary with directory options and suggestions
        """
        options = {
            'current': self.current_config.output_directory,
            'suggestions': []
        }
        
        # Add common directory suggestions
        common_dirs = [
            os.path.expanduser('~/Documents'),
            os.path.expanduser('~/Desktop'),
            os.path.expanduser('~/Downloads'),
            '.'
        ]
        
        for directory in common_dirs:
            if os.path.exists(directory):
                permission_result = self.validate_directory_permissions(directory)
                if permission_result['valid']:
                    options['suggestions'].append({
                        'path': directory,
                        'display_name': self._get_directory_display_name(directory),
                        'writable': True
                    })
        
        return options
    
    def _get_directory_display_name(self, directory_path: str) -> str:
        """Get user-friendly display name for directory.
        
        Args:
            directory_path: Path to directory
            
        Returns:
            User-friendly display name
        """
        if directory_path == '.':
            return 'Current Directory'
        elif directory_path == os.path.expanduser('~/Documents'):
            return 'Documents'
        elif directory_path == os.path.expanduser('~/Desktop'):
            return 'Desktop'
        elif directory_path == os.path.expanduser('~/Downloads'):
            return 'Downloads'
        else:
            return os.path.basename(directory_path) or directory_path
    
    def create_custom_directory(self, parent_directory: str, directory_name: str) -> Dict[str, Any]:
        """Create a custom directory for file output.
        
        Args:
            parent_directory: Parent directory path
            directory_name: Name of new directory to create
            
        Returns:
            Dictionary with creation result
        """
        try:
            # Validate parent directory
            permission_result = self.validate_directory_permissions(parent_directory)
            if not permission_result['valid']:
                return {
                    'success': False,
                    'error': f"Cannot create directory in {parent_directory}: {permission_result['error']}"
                }
            
            # Sanitize directory name
            safe_name = self.permission_validator.sanitize_filename(directory_name)
            new_directory = os.path.join(parent_directory, safe_name)
            
            # Create directory
            creation_result = self.permission_validator.create_directory_if_needed(new_directory)
            
            if creation_result.created or creation_result.message == "Directory already exists":
                return {
                    'success': True,
                    'directory_path': new_directory,
                    'message': creation_result.message
                }
            else:
                return {
                    'success': False,
                    'error': creation_result.error_message or "Failed to create directory"
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Error creating directory: {str(e)}"
            }