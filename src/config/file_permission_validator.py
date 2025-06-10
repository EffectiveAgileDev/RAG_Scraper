"""File permission validation and error handling for RAG_Scraper."""
import os
import tempfile
import shutil
import re
from pathlib import Path
from typing import Optional


class ValidationMessages:
    """Centralized error message handling for consistent messaging."""
    
    @staticmethod
    def directory_not_exist(path: str) -> str:
        """Standard message for non-existent directory."""
        return f"Directory does not exist: {path}"
    
    @staticmethod
    def path_not_directory(path: str) -> str:
        """Standard message for path that is not a directory."""
        return f"Path is not a directory: {path}"
    
    @staticmethod
    def directory_not_writable(path: str, reason: str = "") -> str:
        """Standard message for non-writable directory."""
        base_msg = f"Directory is not writable: {path}"
        return f"{base_msg} - {reason}" if reason else base_msg
    
    @staticmethod
    def invalid_path_input(issue: str) -> str:
        """Standard message for invalid path input."""
        return f"Invalid path input: {issue}"
    
    @staticmethod
    def filename_invalid(reason: str) -> str:
        """Standard message for invalid filename."""
        return f"Invalid filename: {reason}"
    
    @staticmethod
    def insufficient_space(required: int, available: int) -> str:
        """Standard message for insufficient disk space."""
        return (
            f"Insufficient disk space. "
            f"Required: {required:,} bytes ({required / (1024*1024):.1f} MB), "
            f"Available: {available:,} bytes ({available / (1024*1024):.1f} MB)"
        )
    
    @staticmethod
    def permission_error(operation: str, details: str = "") -> str:
        """Standard message for permission errors."""
        base_msg = f"Permission denied: {operation}"
        return f"{base_msg} - {details}" if details else base_msg


class DirectoryValidationResult:
    """Result of directory validation."""
    
    def __init__(self, directory_path: str, is_writable: bool, error_message: Optional[str] = None):
        self.directory_path = directory_path
        self.is_writable = is_writable
        self.error_message = error_message


class FileCreationResult:
    """Result of file creation validation."""
    
    def __init__(self, full_path: str, can_create: bool, error_message: Optional[str] = None):
        self.full_path = full_path
        self.can_create = can_create
        self.error_message = error_message


class DiskSpaceResult:
    """Result of disk space validation."""
    
    def __init__(self, available_bytes: int, required_bytes: int, 
                 has_space: bool, error_message: Optional[str] = None):
        self.available_bytes = available_bytes
        self.required_bytes = required_bytes
        self.has_space = has_space
        self.error_message = error_message
    
    @property
    def available_mb(self) -> int:
        """Available space in MB."""
        return int(self.available_bytes / 1024)
    
    @property
    def required_mb(self) -> int:
        """Required space in MB."""
        return int(self.required_bytes / 1024)


class DirectoryCreationResult:
    """Result of directory creation."""
    
    def __init__(self, directory_path: str, created: bool, 
                 message: str, error_message: Optional[str] = None):
        self.directory_path = directory_path
        self.created = created
        self.message = message
        self.error_message = error_message


class FilePermissionValidator:
    """Validates file permissions and handles file system errors."""
    
    # Reserved filenames on Windows
    WINDOWS_RESERVED_NAMES = {
        'con', 'prn', 'aux', 'nul',
        'com1', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8', 'com9',
        'lpt1', 'lpt2', 'lpt3', 'lpt4', 'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9'
    }
    
    # Invalid characters for filenames
    INVALID_FILENAME_CHARS = '<>:"|?*\\/\r\n\t'
    
    def validate_directory_writable(self, directory_path: str) -> DirectoryValidationResult:
        """Validate that a directory exists and is writable."""
        # Input validation
        validation_error = self._validate_directory_input(directory_path)
        if validation_error:
            return DirectoryValidationResult(directory_path, False, validation_error)
        
        # Resolve relative paths
        directory_path = os.path.abspath(directory_path.strip())
        
        try:
            # Check existence and type
            if not os.path.exists(directory_path):
                return DirectoryValidationResult(
                    directory_path, False, 
                    ValidationMessages.directory_not_exist(directory_path)
                )
            
            if not os.path.isdir(directory_path):
                return DirectoryValidationResult(
                    directory_path, False, 
                    ValidationMessages.path_not_directory(directory_path)
                )
            
            # Test write permissions
            return self._test_directory_writability(directory_path)
                
        except (OSError, PermissionError) as e:
            return DirectoryValidationResult(
                directory_path, False, 
                ValidationMessages.permission_error("accessing directory", str(e))
            )
        except Exception as e:
            return DirectoryValidationResult(
                directory_path, False, 
                f"Unexpected error validating directory: {str(e)}"
            )
    
    def _validate_directory_input(self, directory_path: str) -> Optional[str]:
        """Validate directory path input."""
        if directory_path is None:
            return ValidationMessages.invalid_path_input("path cannot be None")
        
        if not directory_path or not directory_path.strip():
            return ValidationMessages.invalid_path_input("path cannot be empty")
        
        return None
    
    def _test_directory_writability(self, directory_path: str) -> DirectoryValidationResult:
        """Test if directory is writable by creating temporary file."""
        try:
            with tempfile.NamedTemporaryFile(dir=directory_path, delete=True):
                pass
            return DirectoryValidationResult(directory_path, True)
            
        except (OSError, PermissionError) as e:
            return DirectoryValidationResult(
                directory_path, False, 
                ValidationMessages.directory_not_writable(directory_path, str(e))
            )
    
    def validate_file_creation(self, directory: str, filename: str, 
                             create_dirs: bool = False) -> FileCreationResult:
        """Validate that a file can be created in the given directory."""
        # Validate directory first
        dir_result = self.validate_directory_writable(directory)
        if not dir_result.is_writable:
            return FileCreationResult(
                os.path.join(directory, filename), False,
                f"Directory validation failed: {dir_result.error_message}"
            )
        
        # Validate filename
        if not self.is_filename_safe(filename):
            error_msg = "Filename contains invalid characters or is unsafe"
            if len(filename) > 255:
                error_msg = "Filename is too long (maximum 255 characters)"
            return FileCreationResult(
                os.path.join(directory, filename), False,
                error_msg
            )
        
        full_path = os.path.join(directory, filename)
        
        # Check if subdirectories need to be created
        file_dir = os.path.dirname(full_path)
        if file_dir != directory:
            if not create_dirs:
                return FileCreationResult(
                    full_path, False,
                    "File path contains subdirectories but create_dirs=False"
                )
            
            # Validate that subdirectories can be created
            if not os.path.exists(file_dir):
                try:
                    os.makedirs(file_dir, exist_ok=True)
                except (OSError, PermissionError) as e:
                    return FileCreationResult(
                        full_path, False,
                        f"Cannot create subdirectories: {str(e)}"
                    )
        
        # Check if file already exists (warn but allow)
        if os.path.exists(full_path):
            if os.path.isdir(full_path):
                return FileCreationResult(
                    full_path, False,
                    "Path exists and is a directory, not a file"
                )
            # File exists but is a file - this is okay for overwriting
        
        return FileCreationResult(full_path, True)
    
    def validate_disk_space(self, directory: str, required_bytes: int) -> DiskSpaceResult:
        """Validate that sufficient disk space is available."""
        if required_bytes < 0:
            return DiskSpaceResult(
                0, required_bytes, False, 
                ValidationMessages.invalid_path_input("required bytes cannot be negative")
            )
        
        try:
            # Check if directory exists
            if not os.path.exists(directory):
                return DiskSpaceResult(
                    0, required_bytes, False, 
                    ValidationMessages.directory_not_exist(directory)
                )
            
            # Get available space
            available_bytes = self._get_available_disk_space(directory)
            has_space = available_bytes >= required_bytes
            
            if not has_space:
                error_msg = ValidationMessages.insufficient_space(required_bytes, available_bytes)
                return DiskSpaceResult(available_bytes, required_bytes, False, error_msg)
            
            return DiskSpaceResult(available_bytes, required_bytes, True)
            
        except (OSError, AttributeError) as e:
            return DiskSpaceResult(
                0, required_bytes, False, 
                ValidationMessages.permission_error("checking disk space", str(e))
            )
    
    def _get_available_disk_space(self, directory: str) -> int:
        """Get available disk space for directory."""
        if hasattr(shutil, 'disk_usage'):
            # Python 3.3+
            total, used, free = shutil.disk_usage(directory)
            return free
        else:
            # Fallback for older Python versions
            statvfs = os.statvfs(directory)
            return statvfs.f_frsize * statvfs.f_bavail
    
    def create_directory_if_needed(self, directory_path: str) -> DirectoryCreationResult:
        """Create directory if it doesn't exist."""
        directory_path = os.path.abspath(directory_path.strip())
        
        try:
            if os.path.exists(directory_path):
                if os.path.isdir(directory_path):
                    return DirectoryCreationResult(
                        directory_path, False, 
                        "Directory already exists", None
                    )
                else:
                    return DirectoryCreationResult(
                        directory_path, False, 
                        "Path exists but is not a directory",
                        "Cannot create directory: path exists as file"
                    )
            
            # Create directory and all parent directories
            os.makedirs(directory_path, exist_ok=True)
            
            return DirectoryCreationResult(
                directory_path, True, 
                "Directory created successfully", None
            )
            
        except (OSError, PermissionError) as e:
            return DirectoryCreationResult(
                directory_path, False, 
                "Failed to create directory",
                f"Permission denied or other OS error: {str(e)}"
            )
    
    def is_filename_safe(self, filename: str) -> bool:
        """Check if filename is safe for cross-platform use."""
        if not filename or not filename.strip():
            return False
        
        filename = filename.strip()
        
        # Check for invalid characters
        if any(char in filename for char in self.INVALID_FILENAME_CHARS):
            return False
        
        # Check for reserved names (Windows)
        base_name = os.path.splitext(filename)[0].lower()
        if base_name in self.WINDOWS_RESERVED_NAMES:
            return False
        
        # Check for names that start/end with dots or spaces
        if filename.startswith('.') and len(filename) == 1:
            return False
        
        if filename.endswith(' ') or filename.endswith('.'):
            return False
        
        # Check for excessively long filenames
        if len(filename) > 255:
            return False
        
        return True
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to make it safe for file system."""
        if not filename or not filename.strip():
            return "unnamed_file.txt"
        
        filename = filename.strip()
        
        # Replace invalid characters with underscores
        for char in self.INVALID_FILENAME_CHARS:
            filename = filename.replace(char, '_')
        
        # Handle reserved names
        base_name, ext = os.path.splitext(filename)
        if base_name.lower() in self.WINDOWS_RESERVED_NAMES:
            base_name = base_name + "_"
            filename = base_name + ext
        
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        
        # Ensure filename is not empty after sanitization
        if not filename:
            filename = "unnamed_file.txt"
        
        # Truncate if too long
        if len(filename) > 255:
            name_part, ext_part = os.path.splitext(filename)
            max_name_length = 255 - len(ext_part)
            filename = name_part[:max_name_length] + ext_part
        
        return filename
    
    def get_safe_output_path(self, directory: str, filename: str) -> str:
        """Get a safe output path with sanitized filename."""
        safe_filename = self.sanitize_filename(filename)
        return os.path.join(directory, safe_filename)
    
    def check_file_overwrite_safety(self, file_path: str) -> bool:
        """Check if it's safe to overwrite a file."""
        if not os.path.exists(file_path):
            return True  # Safe to create new file
        
        try:
            # Check if file is currently open/locked
            with open(file_path, 'a'):
                pass
            return True  # File can be opened for writing
            
        except (OSError, PermissionError):
            return False  # File is locked or permission denied
    
    def get_available_filename(self, directory: str, preferred_name: str) -> str:
        """Get an available filename by adding numbers if needed."""
        safe_name = self.sanitize_filename(preferred_name)
        full_path = os.path.join(directory, safe_name)
        
        if not os.path.exists(full_path):
            return safe_name
        
        # Add incrementing number to filename
        name_part, ext = os.path.splitext(safe_name)
        counter = 1
        
        while counter < 1000:  # Prevent infinite loop
            numbered_name = f"{name_part}_{counter}{ext}"
            full_path = os.path.join(directory, numbered_name)
            
            if not os.path.exists(full_path):
                return numbered_name
            
            counter += 1
        
        # If we still can't find a name, use timestamp
        import time
        timestamp = int(time.time())
        return f"{name_part}_{timestamp}{ext}"