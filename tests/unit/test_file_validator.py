"""Unit tests for file validator component."""

import pytest
from unittest.mock import Mock, patch
from werkzeug.datastructures import FileStorage
from io import BytesIO

# This will fail until we implement the actual class
try:
    from src.file_processing.file_validator import FileValidator, ValidationResult
except ImportError:
    # Expected to fail in RED phase - component doesn't exist yet
    FileValidator = None
    ValidationResult = None


class TestFileValidator:
    """Test cases for FileValidator class."""

    @pytest.fixture
    def file_validator(self):
        """Create FileValidator instance for testing."""
        if FileValidator is None:
            pytest.skip("FileValidator not implemented yet (expected in RED phase)")
        
        return FileValidator(
            max_file_size=50 * 1024 * 1024,  # 50MB
            allowed_types=['application/pdf', 'application/msword', 
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        )

    @pytest.fixture
    def valid_pdf_content(self):
        """Valid PDF content for testing."""
        return b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n173\n%%EOF"

    @pytest.fixture
    def valid_pdf_file(self, valid_pdf_content):
        """Valid PDF FileStorage for testing."""
        return FileStorage(
            stream=BytesIO(valid_pdf_content),
            filename="valid_menu.pdf",
            content_type="application/pdf"
        )

    @pytest.fixture
    def invalid_text_file(self):
        """Invalid text file for testing."""
        return FileStorage(
            stream=BytesIO(b"This is just plain text, not a PDF"),
            filename="document.txt",
            content_type="text/plain"
        )

    @pytest.fixture
    def oversized_pdf_file(self):
        """Oversized PDF file for testing."""
        # Create content larger than 50MB
        large_content = b"%PDF-1.4\n" + b"X" * (60 * 1024 * 1024)
        return FileStorage(
            stream=BytesIO(large_content),
            filename="large_menu.pdf",
            content_type="application/pdf"
        )

    def test_file_validator_initialization(self):
        """Test FileValidator initializes correctly."""
        if FileValidator is None:
            pytest.skip("FileValidator not implemented yet (expected in RED phase)")
        
        validator = FileValidator(
            max_file_size=100 * 1024 * 1024,  # 100MB
            allowed_types=['application/pdf']
        )
        
        assert validator.max_file_size == 100 * 1024 * 1024
        assert 'application/pdf' in validator.allowed_types

    def test_validate_file_type_pdf_success(self, file_validator, valid_pdf_file):
        """Test successful PDF file type validation."""
        if FileValidator is None:
            pytest.skip("FileValidator not implemented yet (expected in RED phase)")
        
        result = file_validator.validate_file_type(valid_pdf_file)
        
        assert result is True

    def test_validate_file_type_doc_success(self, file_validator):
        """Test successful DOC file type validation."""
        if FileValidator is None:
            pytest.skip("FileValidator not implemented yet (expected in RED phase)")
        
        doc_file = FileStorage(
            stream=BytesIO(b"Mock DOC content"),
            filename="document.doc",
            content_type="application/msword"
        )
        
        result = file_validator.validate_file_type(doc_file)
        
        assert result is True

    def test_validate_file_type_docx_success(self, file_validator):
        """Test successful DOCX file type validation."""
        if FileValidator is None:
            pytest.skip("FileValidator not implemented yet (expected in RED phase)")
        
        docx_file = FileStorage(
            stream=BytesIO(b"Mock DOCX content"),
            filename="document.docx",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        result = file_validator.validate_file_type(docx_file)
        
        assert result is True

    def test_validate_file_type_invalid_failure(self, file_validator, invalid_text_file):
        """Test file type validation failure for invalid types."""
        if FileValidator is None:
            pytest.skip("FileValidator not implemented yet (expected in RED phase)")
        
        result = file_validator.validate_file_type(invalid_text_file)
        
        assert result is False

    def test_validate_file_size_success(self, file_validator, valid_pdf_file):
        """Test successful file size validation."""
        if FileValidator is None:
            pytest.skip("FileValidator not implemented yet (expected in RED phase)")
        
        result = file_validator.validate_file_size(valid_pdf_file)
        
        assert result is True

    def test_validate_file_size_failure(self, file_validator, oversized_pdf_file):
        """Test file size validation failure for oversized files."""
        if FileValidator is None:
            pytest.skip("FileValidator not implemented yet (expected in RED phase)")
        
        result = file_validator.validate_file_size(oversized_pdf_file)
        
        assert result is False

    def test_validate_filename_security(self, file_validator):
        """Test filename security validation."""
        if FileValidator is None:
            pytest.skip("FileValidator not implemented yet (expected in RED phase)")
        
        # Test dangerous filenames
        dangerous_names = [
            "../../../etc/passwd.pdf",
            "..\\..\\..\\windows\\system32\\config.pdf",
            "file<script>alert('xss')</script>.pdf",
            "file with spaces and (special) chars.pdf",
            "normal_file.pdf"
        ]
        
        for filename in dangerous_names:
            file_obj = FileStorage(
                stream=BytesIO(b"content"),
                filename=filename,
                content_type="application/pdf"
            )
            
            result = file_validator.validate_filename_security(file_obj)
            
            if filename == "normal_file.pdf" or filename == "file with spaces and (special) chars.pdf":
                assert result is True
            else:
                assert result is False

    def test_validate_pdf_content_structure(self, file_validator, valid_pdf_content):
        """Test PDF content structure validation."""
        if FileValidator is None:
            pytest.skip("FileValidator not implemented yet (expected in RED phase)")
        
        pdf_file = FileStorage(
            stream=BytesIO(valid_pdf_content),
            filename="test.pdf",
            content_type="application/pdf"
        )
        
        result = file_validator.validate_pdf_content(pdf_file)
        
        assert result is True

    def test_validate_pdf_content_structure_invalid(self, file_validator):
        """Test PDF content structure validation with invalid content."""
        if FileValidator is None:
            pytest.skip("FileValidator not implemented yet (expected in RED phase)")
        
        # File claims to be PDF but has invalid content
        fake_pdf = FileStorage(
            stream=BytesIO(b"This is not a real PDF file"),
            filename="fake.pdf",
            content_type="application/pdf"
        )
        
        result = file_validator.validate_pdf_content(fake_pdf)
        
        assert result is False

    def test_validate_file_comprehensive_success(self, file_validator, valid_pdf_file):
        """Test comprehensive file validation with all checks passing."""
        if FileValidator is None or ValidationResult is None:
            pytest.skip("FileValidator/ValidationResult not implemented yet (expected in RED phase)")
        
        result = file_validator.validate_file(valid_pdf_file)
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert result.errors == []
        assert result.file_type == "application/pdf"
        assert result.file_size > 0

    def test_validate_file_comprehensive_failure_type(self, file_validator, invalid_text_file):
        """Test comprehensive file validation with type check failure."""
        if FileValidator is None or ValidationResult is None:
            pytest.skip("FileValidator/ValidationResult not implemented yet (expected in RED phase)")
        
        result = file_validator.validate_file(invalid_text_file)
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert any("type" in error.lower() for error in result.errors)

    def test_validate_file_comprehensive_failure_size(self, file_validator, oversized_pdf_file):
        """Test comprehensive file validation with size check failure."""
        if FileValidator is None or ValidationResult is None:
            pytest.skip("FileValidator/ValidationResult not implemented yet (expected in RED phase)")
        
        result = file_validator.validate_file(oversized_pdf_file)
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert any("size" in error.lower() for error in result.errors)

    def test_validate_multiple_files(self, file_validator, valid_pdf_content):
        """Test validation of multiple files."""
        if FileValidator is None:
            pytest.skip("FileValidator not implemented yet (expected in RED phase)")
        
        files = [
            FileStorage(stream=BytesIO(valid_pdf_content), filename="menu1.pdf", content_type="application/pdf"),
            FileStorage(stream=BytesIO(valid_pdf_content), filename="menu2.pdf", content_type="application/pdf"),
            FileStorage(stream=BytesIO(b"invalid"), filename="bad.txt", content_type="text/plain")
        ]
        
        results = file_validator.validate_multiple_files(files)
        
        assert len(results) == 3
        assert results[0].is_valid is True  # menu1.pdf
        assert results[1].is_valid is True  # menu2.pdf
        assert results[2].is_valid is False  # bad.txt

    def test_get_supported_file_types(self, file_validator):
        """Test retrieval of supported file types."""
        if FileValidator is None:
            pytest.skip("FileValidator not implemented yet (expected in RED phase)")
        
        supported_types = file_validator.get_supported_file_types()
        
        assert 'application/pdf' in supported_types
        assert 'application/msword' in supported_types
        assert 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in supported_types

    def test_get_max_file_size(self, file_validator):
        """Test retrieval of maximum file size."""
        if FileValidator is None:
            pytest.skip("FileValidator not implemented yet (expected in RED phase)")
        
        max_size = file_validator.get_max_file_size()
        
        assert max_size == 50 * 1024 * 1024  # 50MB

    def test_format_file_size(self, file_validator):
        """Test file size formatting for display."""
        if FileValidator is None:
            pytest.skip("FileValidator not implemented yet (expected in RED phase)")
        
        # Test various file sizes
        assert file_validator.format_file_size(1024) == "1.0 KB"
        assert file_validator.format_file_size(1024 * 1024) == "1.0 MB"
        assert file_validator.format_file_size(1024 * 1024 * 1024) == "1.0 GB"
        assert file_validator.format_file_size(512) == "512 bytes"

    def test_validate_file_extension_matching(self, file_validator):
        """Test validation that file extension matches content type."""
        if FileValidator is None:
            pytest.skip("FileValidator not implemented yet (expected in RED phase)")
        
        # PDF file with PDF extension - should pass
        pdf_file = FileStorage(
            stream=BytesIO(b"%PDF-1.4"),
            filename="document.pdf",
            content_type="application/pdf"
        )
        assert file_validator.validate_extension_content_match(pdf_file) is True
        
        # PDF content with TXT extension - should fail
        mismatched_file = FileStorage(
            stream=BytesIO(b"%PDF-1.4"),
            filename="document.txt",
            content_type="application/pdf"
        )
        assert file_validator.validate_extension_content_match(mismatched_file) is False

    def test_detect_file_type_from_content(self, file_validator, valid_pdf_content):
        """Test file type detection from content."""
        if FileValidator is None:
            pytest.skip("FileValidator not implemented yet (expected in RED phase)")
        
        # Create file with wrong content type but correct content
        file_obj = FileStorage(
            stream=BytesIO(valid_pdf_content),
            filename="document.pdf",
            content_type="text/plain"  # Wrong content type
        )
        
        detected_type = file_validator.detect_file_type_from_content(file_obj)
        
        assert detected_type == "application/pdf"

    def test_validation_error_messages(self, file_validator):
        """Test that validation errors include helpful messages."""
        if FileValidator is None or ValidationResult is None:
            pytest.skip("FileValidator/ValidationResult not implemented yet (expected in RED phase)")
        
        # Test with invalid file
        invalid_file = FileStorage(
            stream=BytesIO(b"not a pdf"),
            filename="fake.pdf",
            content_type="text/plain"
        )
        
        result = file_validator.validate_file(invalid_file)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        
        # Check that error messages are helpful
        error_text = " ".join(result.errors).lower()
        assert any(keyword in error_text for keyword in ["type", "format", "supported"])

    def test_custom_validator_configuration(self):
        """Test FileValidator with custom configuration."""
        if FileValidator is None:
            pytest.skip("FileValidator not implemented yet (expected in RED phase)")
        
        # Create validator with custom settings
        custom_validator = FileValidator(
            max_file_size=10 * 1024 * 1024,  # 10MB
            allowed_types=['application/pdf'],
            strict_mode=True
        )
        
        assert custom_validator.max_file_size == 10 * 1024 * 1024
        assert len(custom_validator.allowed_types) == 1
        assert custom_validator.strict_mode is True


class TestValidationResult:
    """Test cases for ValidationResult class."""

    def test_validation_result_success(self):
        """Test ValidationResult for successful validation."""
        if ValidationResult is None:
            pytest.skip("ValidationResult not implemented yet (expected in RED phase)")
        
        result = ValidationResult(
            is_valid=True,
            file_type="application/pdf",
            file_size=1024 * 100,  # 100KB
            errors=[]
        )
        
        assert result.is_valid is True
        assert result.file_type == "application/pdf"
        assert result.file_size == 1024 * 100
        assert result.errors == []

    def test_validation_result_failure(self):
        """Test ValidationResult for failed validation."""
        if ValidationResult is None:
            pytest.skip("ValidationResult not implemented yet (expected in RED phase)")
        
        result = ValidationResult(
            is_valid=False,
            file_type="text/plain",
            file_size=1024 * 60 * 1024,  # 60MB
            errors=["File type not supported", "File size exceeds limit"]
        )
        
        assert result.is_valid is False
        assert result.file_type == "text/plain"
        assert len(result.errors) == 2
        assert "File type not supported" in result.errors
        assert "File size exceeds limit" in result.errors

    def test_validation_result_string_representation(self):
        """Test string representation of ValidationResult."""
        if ValidationResult is None:
            pytest.skip("ValidationResult not implemented yet (expected in RED phase)")
        
        result = ValidationResult(
            is_valid=False,
            file_type="text/plain",
            file_size=1024,
            errors=["Invalid file type"]
        )
        
        str_repr = str(result)
        assert "Invalid file type" in str_repr
        assert "text/plain" in str_repr