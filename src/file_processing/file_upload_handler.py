"""File upload handler for managing uploaded files."""

import os
import uuid
import time
import threading
from typing import List, Dict, Any, Optional, Callable
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from .file_validator import FileValidator, ValidationResult
from .file_security_scanner import FileSecurityScanner, ScanResult


class FileUploadHandler:
    """Handler for file uploads with validation and security scanning."""
    
    def __init__(self, upload_dir: str, file_validator: Optional[FileValidator] = None,
                 security_scanner: Optional[FileSecurityScanner] = None,
                 max_file_size: int = 50 * 1024 * 1024):
        """Initialize file upload handler.
        
        Args:
            upload_dir: Directory to store uploaded files
            file_validator: File validator instance
            security_scanner: Security scanner instance
            max_file_size: Maximum file size in bytes
        """
        self.upload_dir = upload_dir
        self.max_file_size = max_file_size
        self.file_validator = file_validator or FileValidator(max_file_size=max_file_size)
        self.security_scanner = security_scanner or FileSecurityScanner()
        
        # Create upload directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)
        
        # File metadata storage
        self.file_metadata = {}
        self.upload_lock = threading.Lock()
    
    def handle_upload(self, file_storage: FileStorage, 
                     progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Handle single file upload.
        
        Args:
            file_storage: FileStorage object to upload
            progress_callback: Optional progress callback function
            
        Returns:
            Dictionary with upload result
        """
        if progress_callback:
            progress_callback(0, "Starting upload validation")
        
        try:
            # Validate file
            validation_result = self.file_validator.validate_file(file_storage)
            if not validation_result.is_valid:
                return {
                    'success': False,
                    'error': f"File validation failed: {', '.join(validation_result.errors)}",
                    'file_id': None,
                    'filename': file_storage.filename
                }
            
            if progress_callback:
                progress_callback(25, "File validation passed")
            
            # Security scan
            scan_result = self.security_scanner.scan_file(file_storage)
            if not scan_result.is_safe:
                return {
                    'success': False,
                    'error': f"Security scan failed: {', '.join(scan_result.threats_found)}",
                    'file_id': None,
                    'filename': file_storage.filename
                }
            
            if progress_callback:
                progress_callback(50, "Security scan passed")
            
            # Generate unique file ID and secure filename
            file_id = self.generate_file_id(file_storage.filename)
            secure_name = self.get_secure_filename(file_storage.filename)
            
            # Save file
            file_path = os.path.join(self.upload_dir, f"{file_id}_{secure_name}")
            
            if progress_callback:
                progress_callback(75, "Saving file")
            
            # Save the file content
            file_storage.stream.seek(0)
            with open(file_path, 'wb') as f:
                f.write(file_storage.stream.read())
            
            # Store metadata
            with self.upload_lock:
                self.file_metadata[file_id] = {
                    'filename': file_storage.filename,
                    'secure_filename': secure_name,
                    'file_path': file_path,
                    'content_type': file_storage.content_type,
                    'file_size': validation_result.file_size,
                    'upload_timestamp': time.time(),
                    'file_hash': scan_result.file_hash
                }
            
            if progress_callback:
                progress_callback(100, "Upload complete")
            
            return {
                'success': True,
                'file_id': file_id,
                'filename': file_storage.filename,
                'file_path': file_path,
                'file_size': validation_result.file_size
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Upload failed: {str(e)}",
                'file_id': None,
                'filename': file_storage.filename if file_storage else 'unknown'
            }
    
    def handle_multiple_uploads(self, files: List[FileStorage]) -> List[Dict[str, Any]]:
        """Handle multiple file uploads.
        
        Args:
            files: List of FileStorage objects to upload
            
        Returns:
            List of upload results
        """
        results = []
        for file_storage in files:
            result = self.handle_upload(file_storage)
            results.append(result)
        return results
    
    def generate_file_id(self, filename: str) -> str:
        """Generate unique file ID.
        
        Args:
            filename: Original filename
            
        Returns:
            Unique file ID
        """
        # Combine timestamp and UUID for uniqueness
        timestamp = str(int(time.time() * 1000))
        unique_id = str(uuid.uuid4().hex[:8])
        return f"{timestamp}_{unique_id}"
    
    def get_secure_filename(self, filename: str) -> str:
        """Get secure filename.
        
        Args:
            filename: Original filename
            
        Returns:
            Secure filename
        """
        # Use werkzeug's secure_filename and add additional security
        secure_name = secure_filename(filename)
        
        # Remove any remaining problematic characters
        secure_name = secure_name.replace('..', '_')
        
        # Ensure filename isn't empty
        if not secure_name:
            secure_name = 'uploaded_file'
        
        return secure_name
    
    def cleanup_file(self, file_id: str) -> bool:
        """Cleanup/delete uploaded file.
        
        Args:
            file_id: File ID to cleanup
            
        Returns:
            True if cleanup successful, False otherwise
        """
        with self.upload_lock:
            metadata = self.file_metadata.get(file_id)
            if not metadata:
                return False
            
            file_path = metadata['file_path']
            
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                
                # Remove from metadata
                del self.file_metadata[file_id]
                return True
                
            except Exception:
                return False
    
    def get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file metadata.
        
        Args:
            file_id: File ID
            
        Returns:
            File metadata or None if not found
        """
        with self.upload_lock:
            return self.file_metadata.get(file_id, {}).copy()
    
    def list_uploaded_files(self) -> List[Dict[str, Any]]:
        """List all uploaded files.
        
        Returns:
            List of file metadata
        """
        with self.upload_lock:
            return [
                {
                    'file_id': file_id,
                    **metadata
                }
                for file_id, metadata in self.file_metadata.items()
            ]
    
    def get_file_path(self, file_id: str) -> Optional[str]:
        """Get file path for a file ID.
        
        Args:
            file_id: File ID
            
        Returns:
            File path or None if not found
        """
        metadata = self.get_file_metadata(file_id)
        return metadata.get('file_path') if metadata else None
    
    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """Cleanup files older than specified age.
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            Number of files cleaned up
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        cleaned_count = 0
        
        with self.upload_lock:
            file_ids_to_remove = []
            
            for file_id, metadata in self.file_metadata.items():
                upload_time = metadata.get('upload_timestamp', 0)
                if current_time - upload_time > max_age_seconds:
                    file_ids_to_remove.append(file_id)
        
        # Remove old files
        for file_id in file_ids_to_remove:
            if self.cleanup_file(file_id):
                cleaned_count += 1
        
        return cleaned_count
    
    def get_upload_statistics(self) -> Dict[str, Any]:
        """Get upload statistics.
        
        Returns:
            Dictionary with upload statistics
        """
        with self.upload_lock:
            total_files = len(self.file_metadata)
            total_size = sum(metadata.get('file_size', 0) for metadata in self.file_metadata.values())
            
            # Calculate average file size
            avg_size = total_size / total_files if total_files > 0 else 0
            
            return {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'average_file_size_bytes': avg_size,
                'upload_directory': self.upload_dir
            }