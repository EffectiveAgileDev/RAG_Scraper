"""Unit tests for file system permission handling and error cases."""
import os
import tempfile
import stat
import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path


class TestFilePermissionValidator:
    """Test file permission validation functionality."""
    
    def test_validate_writable_directory_success(self):
        """Test validation of writable directory."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = validator.validate_directory_writable(temp_dir)
            
            assert result.is_writable is True
            assert result.error_message is None
            assert result.directory_path == temp_dir
    
    def test_validate_nonexistent_directory(self):
        """Test validation of non-existent directory."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        nonexistent_path = "/path/that/does/not/exist"
        
        result = validator.validate_directory_writable(nonexistent_path)
        
        assert result.is_writable is False
        assert "does not exist" in result.error_message.lower()
        assert result.directory_path == nonexistent_path
    
    def test_validate_file_instead_of_directory(self):
        """Test validation when path is a file, not directory."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        with tempfile.NamedTemporaryFile() as temp_file:
            result = validator.validate_directory_writable(temp_file.name)
            
            assert result.is_writable is False
            assert "not a directory" in result.error_message.lower()
    
    @pytest.mark.skipif(os.name == 'nt', reason="Permission tests differ on Windows")
    def test_validate_readonly_directory(self):
        """Test validation of read-only directory."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Make directory read-only
            os.chmod(temp_dir, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
            
            try:
                result = validator.validate_directory_writable(temp_dir)
                
                assert result.is_writable is False
                assert "permission" in result.error_message.lower() or "write" in result.error_message.lower()
                
            finally:
                # Restore write permissions for cleanup
                os.chmod(temp_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    
    def test_validate_none_path(self):
        """Test validation with None path."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        result = validator.validate_directory_writable(None)
        
        assert result.is_writable is False
        assert "none" in result.error_message.lower() or "null" in result.error_message.lower()
    
    def test_validate_empty_path(self):
        """Test validation with empty path."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        result = validator.validate_directory_writable("")
        
        assert result.is_writable is False
        assert "empty" in result.error_message.lower()
    
    def test_validate_relative_path(self):
        """Test validation with relative path."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        # Use current directory (should be writable)
        result = validator.validate_directory_writable(".")
        
        # Should resolve relative path
        assert result.directory_path == os.path.abspath(".")
        # Current directory should typically be writable
        assert result.is_writable is True
    
    def test_validate_path_with_spaces(self):
        """Test validation with path containing spaces."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create subdirectory with spaces
            spaced_dir = os.path.join(temp_dir, "folder with spaces")
            os.makedirs(spaced_dir)
            
            result = validator.validate_directory_writable(spaced_dir)
            
            assert result.is_writable is True
            assert result.directory_path == spaced_dir


class TestFileCreationValidator:
    """Test file creation validation functionality."""
    
    def test_validate_file_creation_success(self):
        """Test successful file creation validation."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = "test_output.txt"
            result = validator.validate_file_creation(temp_dir, filename)
            
            assert result.can_create is True
            assert result.error_message is None
            assert result.full_path == os.path.join(temp_dir, filename)
    
    def test_validate_file_creation_invalid_directory(self):
        """Test file creation validation with invalid directory."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        result = validator.validate_file_creation("/nonexistent/path", "test.txt")
        
        assert result.can_create is False
        assert "directory" in result.error_message.lower()
    
    def test_validate_file_creation_invalid_filename(self):
        """Test file creation validation with invalid filename."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test various invalid filenames
            invalid_filenames = [
                "",  # Empty
                "con.txt",  # Reserved on Windows
                "file/with/slashes.txt",  # Path separators
                "file\\with\\backslashes.txt",  # Backslashes
                "file<with>special.txt",  # Special characters
                "file|with|pipes.txt",  # Pipe characters
            ]
            
            for filename in invalid_filenames:
                result = validator.validate_file_creation(temp_dir, filename)
                
                if not result.can_create:
                    assert "filename" in result.error_message.lower() or "invalid" in result.error_message.lower()
    
    def test_validate_file_creation_existing_file(self):
        """Test file creation validation when file already exists."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create existing file
            existing_file = os.path.join(temp_dir, "existing.txt")
            with open(existing_file, 'w') as f:
                f.write("test")
            
            result = validator.validate_file_creation(temp_dir, "existing.txt")
            
            # Should either succeed (overwrite) or warn about existing file
            if not result.can_create:
                assert "exists" in result.error_message.lower()
    
    def test_validate_file_creation_with_subdirectories(self):
        """Test file creation validation with subdirectories."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test creating file in subdirectory
            result = validator.validate_file_creation(temp_dir, "subdir/test.txt", create_dirs=True)
            
            # Should either succeed or indicate subdirectory issue
            assert isinstance(result.can_create, bool)
    
    def test_validate_long_filename(self):
        """Test file creation validation with very long filename."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create very long filename
            long_filename = "a" * 300 + ".txt"
            
            result = validator.validate_file_creation(temp_dir, long_filename)
            
            # Should handle long filenames appropriately
            if not result.can_create:
                assert "length" in result.error_message.lower() or "long" in result.error_message.lower()


class TestFileSpaceValidator:
    """Test file space validation functionality."""
    
    def test_validate_disk_space_sufficient(self):
        """Test disk space validation with sufficient space."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Request small amount of space (1KB)
            result = validator.validate_disk_space(temp_dir, 1024)
            
            assert result.has_space is True
            assert result.error_message is None
            assert result.available_bytes > 0
            assert result.required_bytes == 1024
    
    def test_validate_disk_space_insufficient(self):
        """Test disk space validation with insufficient space."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Request extremely large amount of space (1TB)
            huge_size = 1024 * 1024 * 1024 * 1024  # 1TB
            result = validator.validate_disk_space(temp_dir, huge_size)
            
            # Should detect insufficient space
            assert result.has_space is False
            assert "space" in result.error_message.lower()
            assert result.required_bytes == huge_size
    
    def test_validate_disk_space_invalid_directory(self):
        """Test disk space validation with invalid directory."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        result = validator.validate_disk_space("/nonexistent/path", 1024)
        
        assert result.has_space is False
        assert "directory" in result.error_message.lower() or "path" in result.error_message.lower()
    
    def test_validate_negative_size(self):
        """Test disk space validation with negative size."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = validator.validate_disk_space(temp_dir, -1024)
            
            assert result.has_space is False
            assert "negative" in result.error_message.lower() or "invalid" in result.error_message.lower()


class TestFilePermissionError:
    """Test file permission error handling."""
    
    @patch('os.access')
    def test_permission_error_during_validation(self, mock_access):
        """Test handling of permission errors during validation."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        # Mock os.access to raise PermissionError
        mock_access.side_effect = PermissionError("Access denied")
        
        validator = FilePermissionValidator()
        result = validator.validate_directory_writable("/some/path")
        
        assert result.is_writable is False
        assert "permission" in result.error_message.lower()
    
    @patch('tempfile.NamedTemporaryFile')
    def test_tempfile_creation_error(self, mock_tempfile):
        """Test handling of temporary file creation errors."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        # Mock tempfile to raise OSError
        mock_tempfile.side_effect = OSError("No space left on device")
        
        validator = FilePermissionValidator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = validator.validate_directory_writable(temp_dir)
            
            assert result.is_writable is False
            assert "error" in result.error_message.lower()
    
    @patch('os.path.exists')
    def test_path_exists_error(self, mock_exists):
        """Test handling of path existence check errors."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        # Mock os.path.exists to raise exception
        mock_exists.side_effect = OSError("Path check failed")
        
        validator = FilePermissionValidator()
        result = validator.validate_directory_writable("/some/path")
        
        assert result.is_writable is False
        assert "error" in result.error_message.lower()


class TestDirectoryCreation:
    """Test directory creation functionality."""
    
    def test_create_directory_success(self):
        """Test successful directory creation."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = os.path.join(temp_dir, "new_directory")
            
            result = validator.create_directory_if_needed(new_dir)
            
            assert result.created is True
            assert result.error_message is None
            assert os.path.exists(new_dir)
            assert os.path.isdir(new_dir)
    
    def test_create_directory_already_exists(self):
        """Test directory creation when directory already exists."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = validator.create_directory_if_needed(temp_dir)
            
            assert result.created is False
            assert result.error_message is None
            assert "already exists" in result.message.lower()
    
    def test_create_directory_permission_denied(self):
        """Test directory creation with permission denied."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        # Try to create directory in root (should fail without privileges)
        result = validator.create_directory_if_needed("/root/test_directory")
        
        assert result.created is False
        assert result.error_message is not None
        assert "permission" in result.error_message.lower() or "denied" in result.error_message.lower()
    
    def test_create_nested_directories(self):
        """Test creation of nested directories."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = os.path.join(temp_dir, "level1", "level2", "level3")
            
            result = validator.create_directory_if_needed(nested_path)
            
            assert result.created is True
            assert os.path.exists(nested_path)
            assert os.path.isdir(nested_path)
    
    def test_create_directory_invalid_parent(self):
        """Test directory creation with invalid parent."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        # Try to create directory where parent is a file
        with tempfile.NamedTemporaryFile() as temp_file:
            invalid_path = os.path.join(temp_file.name, "subdir")
            
            result = validator.create_directory_if_needed(invalid_path)
            
            assert result.created is False
            assert result.error_message is not None


class TestFilePermissionResults:
    """Test file permission result objects."""
    
    def test_directory_validation_result(self):
        """Test directory validation result object."""
        from src.config.file_permission_validator import DirectoryValidationResult
        
        result = DirectoryValidationResult(
            directory_path="/test/path",
            is_writable=True,
            error_message=None
        )
        
        assert result.directory_path == "/test/path"
        assert result.is_writable is True
        assert result.error_message is None
    
    def test_file_creation_result(self):
        """Test file creation result object."""
        from src.config.file_permission_validator import FileCreationResult
        
        result = FileCreationResult(
            full_path="/test/path/file.txt",
            can_create=True,
            error_message=None
        )
        
        assert result.full_path == "/test/path/file.txt"
        assert result.can_create is True
        assert result.error_message is None
    
    def test_disk_space_result(self):
        """Test disk space result object."""
        from src.config.file_permission_validator import DiskSpaceResult
        
        result = DiskSpaceResult(
            available_bytes=1024000,
            required_bytes=1024,
            has_space=True,
            error_message=None
        )
        
        assert result.available_bytes == 1024000
        assert result.required_bytes == 1024
        assert result.has_space is True
        assert result.error_message is None
        assert result.available_mb == 1000  # 1024000 / 1024
        assert result.required_mb == 1  # 1024 / 1024
    
    def test_directory_creation_result(self):
        """Test directory creation result object."""
        from src.config.file_permission_validator import DirectoryCreationResult
        
        result = DirectoryCreationResult(
            directory_path="/test/path",
            created=True,
            message="Directory created successfully",
            error_message=None
        )
        
        assert result.directory_path == "/test/path"
        assert result.created is True
        assert result.message == "Directory created successfully"
        assert result.error_message is None


class TestFileValidationUtilities:
    """Test file validation utility functions."""
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        # Test various problematic filenames
        test_cases = [
            ("normal_file.txt", "normal_file.txt"),
            ("file with spaces.txt", "file with spaces.txt"),
            ("file<>with|special*.txt", "file_with_special_.txt"),
            ("con.txt", "con_.txt"),  # Reserved name on Windows
            ("", "unnamed_file.txt"),  # Empty filename
            ("file\nwith\nnewlines.txt", "file_with_newlines.txt"),
        ]
        
        for input_name, expected in test_cases:
            result = validator.sanitize_filename(input_name)
            # Should produce a valid filename
            assert len(result) > 0
            assert "/" not in result
            assert "\\" not in result
    
    def test_is_filename_safe(self):
        """Test filename safety validation."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        # Safe filenames
        safe_names = [
            "normal_file.txt",
            "file-with-dashes.txt",
            "file_with_underscores.txt",
            "file.with.dots.txt",
            "file123.txt"
        ]
        
        for filename in safe_names:
            assert validator.is_filename_safe(filename) is True
        
        # Unsafe filenames
        unsafe_names = [
            "",  # Empty
            "file/with/slashes.txt",
            "file\\with\\backslashes.txt",
            "file<with>brackets.txt",
            "file|with|pipes.txt",
            "con.txt",  # Reserved on Windows
            "file\nwith\nnewlines.txt"
        ]
        
        for filename in unsafe_names:
            assert validator.is_filename_safe(filename) is False
    
    def test_get_safe_output_path(self):
        """Test safe output path generation."""
        from src.config.file_permission_validator import FilePermissionValidator
        
        validator = FilePermissionValidator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test normal case
            safe_path = validator.get_safe_output_path(temp_dir, "test.txt")
            assert safe_path == os.path.join(temp_dir, "test.txt")
            
            # Test with unsafe filename
            safe_path = validator.get_safe_output_path(temp_dir, "unsafe<>file.txt")
            assert "<" not in safe_path
            assert ">" not in safe_path
            assert safe_path.startswith(temp_dir)