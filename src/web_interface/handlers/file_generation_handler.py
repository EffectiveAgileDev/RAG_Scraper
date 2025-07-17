"""File generation handler for scraping results."""

import threading
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from src.file_generator.file_generator_service import (
    FileGeneratorService,
    FileGenerationRequest,
)


@dataclass
class FileGenerationResult:
    """Result of file generation operations."""
    success: bool
    generated_files: List[str]
    errors: List[str]
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class FileGenerationHandler:
    """Handles file generation from scraping results."""
    
    def __init__(self, file_generator_service: FileGeneratorService):
        self.file_generator_service = file_generator_service
    
    def generate_files(self, 
                      result,
                      file_format: str,
                      output_dir: str,
                      generate_async: bool = True) -> FileGenerationResult:
        """Generate files from scraping results.
        
        Args:
            result: Scraping result object
            file_format: Format to generate (text, pdf, both)
            output_dir: Output directory path
            generate_async: Whether to generate additional files asynchronously
            
        Returns:
            FileGenerationResult with file paths and any errors
        """
        generated_files = []
        generation_errors = []
        
        if not result.successful_extractions:
            return FileGenerationResult(
                success=False,
                generated_files=[],
                errors=["No successful extractions to generate files from"]
            )
        
        try:
            # Generate primary file synchronously for immediate response
            primary_file = self._generate_primary_file(
                result.successful_extractions,
                file_format,
                output_dir
            )
            
            # Handle both dict and object response formats
            if isinstance(primary_file, dict):
                if primary_file.get('success'):
                    # Log for debugging
                    print(f"DEBUG: Primary file generated - success: {primary_file.get('success')}, file_path: {primary_file.get('file_path', 'None')}")
                    if primary_file.get('file_path'):
                        generated_files.append(primary_file['file_path'])
                else:
                    generation_errors.append(
                        f"{file_format.upper()} generation failed: {primary_file.get('error', 'Unknown error')}"
                    )
            else:
                # Handle object response
                if hasattr(primary_file, 'success') and primary_file.success:
                    if hasattr(primary_file, 'file_path'):
                        generated_files.append(primary_file.file_path)
                else:
                    error_msg = getattr(primary_file, 'error', 'Unknown error')
                    generation_errors.append(
                        f"{file_format.upper()} generation failed: {error_msg}"
                    )
            
            # Generate additional files asynchronously if requested
            if generate_async:
                self._start_async_generation(
                    result.successful_extractions,
                    file_format,
                    output_dir
                )
            
            return FileGenerationResult(
                success=len(generated_files) > 0,
                generated_files=generated_files,
                errors=generation_errors
            )
            
        except Exception as e:
            return FileGenerationResult(
                success=False,
                generated_files=[],
                errors=[f"File generation error: {str(e)}"]
            )
    
    def _generate_primary_file(self, 
                             restaurant_data: List,
                             file_format: str,
                             output_dir: str) -> Dict[str, Any]:
        """Generate primary file synchronously."""
        print(f"DEBUG: _generate_primary_file called with {len(restaurant_data)} restaurants")
        for i, restaurant in enumerate(restaurant_data):
            print(f"DEBUG: Restaurant {i} type: {type(restaurant)}")
            if hasattr(restaurant, 'ai_analysis'):
                print(f"DEBUG: Restaurant {i} has ai_analysis: {restaurant.ai_analysis}")
            else:
                print(f"DEBUG: Restaurant {i} has no ai_analysis attribute")
        
        file_request = FileGenerationRequest(
            restaurant_data=restaurant_data,
            file_format=file_format,
            output_directory=output_dir,
            allow_overwrite=True,
            save_preferences=False,
        )
        
        return self.file_generator_service.generate_file(file_request)
    
    def _start_async_generation(self,
                               restaurant_data: List,
                               file_format: str,
                               output_dir: str) -> None:
        """Start asynchronous file generation in background thread."""
        def generate_files_async():
            """Generate files in background thread."""
            formats_to_generate = [file_format]
            
            for fmt in formats_to_generate:
                try:
                    file_request = FileGenerationRequest(
                        restaurant_data=restaurant_data,
                        file_format=fmt,
                        output_directory=output_dir,
                        allow_overwrite=True,
                        save_preferences=False,
                    )
                    
                    self.file_generator_service.generate_file(file_request)
                    
                except Exception:
                    # Log error but don't block response
                    pass
        
        # Start file generation in background
        file_thread = threading.Thread(target=generate_files_async, daemon=True)
        file_thread.start()