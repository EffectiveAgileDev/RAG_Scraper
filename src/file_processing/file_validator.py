"""File validator for validating uploaded files."""

import os
from typing import List, Dict, Any
from werkzeug.datastructures import FileStorage


class ValidationResult:
    """Result of file validation."""
    
    def __init__(self, is_valid: bool, file_type: str = None, file_size: int = None, 
                 errors: List[str] = None):
        """Initialize validation result.
        
        Args:
            is_valid: Whether the file passed validation
            file_type: MIME type of the file
            file_size: Size of the file in bytes
            errors: List of validation errors
        """
        self.is_valid = is_valid
        self.file_type = file_type
        self.file_size = file_size
        self.errors = errors or []
    
    def __str__(self):
        """String representation of validation result."""
        if self.is_valid:
            return f"ValidationResult(valid=True, type={self.file_type}, size={self.file_size})"
        else:
            return f"ValidationResult(valid=False, type={self.file_type}, errors={self.errors})"


class FileValidator:
    """Validator for uploaded files."""
    
    def __init__(self, max_file_size: int = 50 * 1024 * 1024, 
                 allowed_types: List[str] = None, strict_mode: bool = False):
        """Initialize file validator.
        
        Args:
            max_file_size: Maximum allowed file size in bytes
            allowed_types: List of allowed MIME types
            strict_mode: Whether to use strict validation
        """
        self.max_file_size = max_file_size
        self.allowed_types = allowed_types or [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/html',
            'text/plain'
        ]
        self.strict_mode = strict_mode
    
    def validate_file_type(self, file_storage: FileStorage) -> bool:
        """Validate file type.
        
        Args:
            file_storage: FileStorage object to validate
            
        Returns:
            True if file type is valid, False otherwise
        """
        return file_storage.content_type in self.allowed_types
    
    def validate_file_size(self, file_storage: FileStorage) -> bool:
        """Validate file size.
        
        Args:
            file_storage: FileStorage object to validate
            
        Returns:
            True if file size is valid, False otherwise
        """
        # Get file size by seeking to end
        file_storage.stream.seek(0, 2)  # Seek to end
        size = file_storage.stream.tell()
        file_storage.stream.seek(0)  # Reset to beginning
        
        return size <= self.max_file_size
    
    def validate_filename_security(self, file_storage: FileStorage) -> bool:
        """Validate filename for security issues.
        
        Args:
            file_storage: FileStorage object to validate
            
        Returns:
            True if filename is safe, False otherwise
        """
        filename = file_storage.filename
        if not filename:
            return False
        
        # Check for path traversal attempts
        if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
            return False
        
        # Check for script injection attempts
        dangerous_chars = ['<', '>', '&', '"', "'"]
        if any(char in filename for char in dangerous_chars):
            return False
        
        return True
    
    def validate_pdf_content(self, file_storage: FileStorage) -> bool:
        """Validate PDF content structure.
        
        Args:
            file_storage: FileStorage object to validate
            
        Returns:
            True if PDF content is valid, False otherwise
        """
        if file_storage.content_type != 'application/pdf':
            return True  # Skip PDF validation for non-PDF files
        
        # Read first few bytes to check PDF header
        file_storage.stream.seek(0)
        header = file_storage.stream.read(8)
        file_storage.stream.seek(0)
        
        return header.startswith(b'%PDF-')
    
    def validate_extension_content_match(self, file_storage: FileStorage) -> bool:
        """Validate that file extension matches content type.
        
        Args:
            file_storage: FileStorage object to validate
            
        Returns:
            True if extension matches content, False otherwise
        """
        if not file_storage.filename:
            return False
        
        extension = os.path.splitext(file_storage.filename)[1].lower()
        content_type = file_storage.content_type
        
        extension_mapping = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        
        expected_type = extension_mapping.get(extension)
        return expected_type == content_type
    
    def detect_file_type_from_content(self, file_storage: FileStorage) -> str:
        """Detect file type from content.
        
        Args:
            file_storage: FileStorage object to analyze
            
        Returns:
            Detected MIME type
        """
        file_storage.stream.seek(0)
        header = file_storage.stream.read(1024)
        file_storage.stream.seek(0)
        
        if header.startswith(b'%PDF-'):
            return 'application/pdf'
        elif header.startswith(b'\xd0\xcf\x11\xe0'):  # MS Office format
            return 'application/msword'
        elif header.startswith(b'PK\x03\x04'):  # ZIP-based format (DOCX)
            return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        else:
            return 'application/octet-stream'
    
    def validate_file(self, file_storage: FileStorage) -> ValidationResult:
        """Perform comprehensive file validation.
        
        Args:
            file_storage: FileStorage object to validate
            
        Returns:
            ValidationResult with validation details
        """
        errors = []
        
        # Get file size
        file_storage.stream.seek(0, 2)
        file_size = file_storage.stream.tell()
        file_storage.stream.seek(0)
        
        # Validate file type
        if not self.validate_file_type(file_storage):
            errors.append(f"File type {file_storage.content_type} is not supported. Allowed types: {', '.join(self.allowed_types)}")
        
        # Validate file size
        if not self.validate_file_size(file_storage):
            errors.append(f"File size {self.format_file_size(file_size)} exceeds maximum allowed size {self.format_file_size(self.max_file_size)}")
        
        # Validate filename security
        if not self.validate_filename_security(file_storage):
            errors.append("Filename contains unsafe characters or path traversal attempts")
        
        # Validate PDF content if applicable
        if not self.validate_pdf_content(file_storage):
            errors.append("File claims to be PDF but has invalid PDF structure")
        
        # Validate extension matches content
        if not self.validate_extension_content_match(file_storage):
            errors.append("File extension does not match content type")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            file_type=file_storage.content_type,
            file_size=file_size,
            errors=errors
        )
    
    def validate_multiple_files(self, files: List[FileStorage]) -> List[ValidationResult]:
        """Validate multiple files.
        
        Args:
            files: List of FileStorage objects to validate
            
        Returns:
            List of ValidationResult objects
        """
        return [self.validate_file(file_storage) for file_storage in files]
    
    def get_supported_file_types(self) -> List[str]:
        """Get list of supported file types.
        
        Returns:
            List of supported MIME types
        """
        return self.allowed_types.copy()
    
    def get_max_file_size(self) -> int:
        """Get maximum allowed file size.
        
        Returns:
            Maximum file size in bytes
        """
        return self.max_file_size
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size for display.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"