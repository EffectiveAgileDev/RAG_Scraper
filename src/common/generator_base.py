"""Base classes for file generators."""
import os
from datetime import datetime
from typing import List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from src.config.file_permission_validator import FilePermissionValidator


@dataclass
class BaseGeneratorConfig:
    """Base configuration for file generators."""

    output_directory: str = "."
    allow_overwrite: bool = True
    filename_pattern: str = "WebScrape_{timestamp}"

    def __post_init__(self):
        """Ensure output directory exists."""
        Path(self.output_directory).mkdir(parents=True, exist_ok=True)


class BaseFileGenerator:
    """Base class for file generators with common functionality."""

    def __init__(self, config: BaseGeneratorConfig):
        """Initialize base file generator.
        
        Args:
            config: Configuration for file generation
        """
        self.config = config
        self.permission_validator = FilePermissionValidator()

    def _validate_input_data(self, data: List) -> bool:
        """Validate that input data is not empty.
        
        Args:
            data: Input data to validate
            
        Returns:
            True if data is valid
            
        Raises:
            ValueError: If data is empty or None
        """
        if not data:
            raise ValueError("No data available for file generation")
        return True

    def _generate_output_path(self, extension: str) -> str:
        """Generate output file path with timestamp.
        
        Args:
            extension: File extension (with or without dot)
            
        Returns:
            Complete file path
        """
        # Ensure extension starts with dot
        if not extension.startswith('.'):
            extension = f'.{extension}'
            
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        filename = f"{self.config.filename_pattern.format(timestamp=timestamp)}{extension}"
        return os.path.join(self.config.output_directory, filename)

    def _validate_write_permissions(self) -> None:
        """Validate write permissions for output directory.
        
        Raises:
            PermissionError: If directory is not writable
        """
        result = self.permission_validator.validate_directory_writable(
            self.config.output_directory
        )
        if not result.is_writable:
            raise PermissionError(
                f"No write permission for directory: {self.config.output_directory}"
            )

    def _handle_file_exists(self, file_path: str) -> None:
        """Handle existing file based on overwrite settings.
        
        Args:
            file_path: Path to check for existing file
            
        Raises:
            FileExistsError: If file exists and overwrite not allowed
        """
        if os.path.exists(file_path) and not self.config.allow_overwrite:
            raise FileExistsError(f"File already exists: {file_path}")

    def _write_with_error_handling(self, file_path: str, content: Any, mode: str = "w", **kwargs) -> str:
        """Write content to file with error handling.
        
        Args:
            file_path: Path to write file
            content: Content to write
            mode: File open mode
            **kwargs: Additional arguments for file opening
            
        Returns:
            Path to written file
            
        Raises:
            IOError: If file cannot be written
        """
        try:
            with open(file_path, mode, **kwargs) as f:
                if hasattr(content, 'read'):
                    # Handle file-like objects
                    f.write(content.read())
                else:
                    # Handle string/bytes content
                    f.write(content)
            return file_path
        except Exception as e:
            raise IOError(f"Failed to write file {file_path}: {str(e)}")

    def generate_file(self, data: List, **kwargs) -> str:
        """Generate file from data. Must be implemented by subclasses.
        
        Args:
            data: Input data to process
            **kwargs: Additional generation options
            
        Returns:
            Path to generated file
        """
        raise NotImplementedError("Subclasses must implement generate_file method")