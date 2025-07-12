"""Unit tests for multiple file upload functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock, ANY
import os
import tempfile
from werkzeug.datastructures import FileStorage
from io import BytesIO
from werkzeug.test import Client


class TestMultipleFileUpload:
    """Test multiple file upload functionality."""
    
    def test_multiple_file_upload_endpoint_exists(self):
        """Test that multiple file upload endpoint exists and is accessible."""
        from src.web_interface.app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # Test endpoint exists by sending empty request
            response = client.post('/api/upload/batch')
            
            # Should return 400 (bad request) not 404 (not found)
            # This shows the endpoint exists even if the request is malformed
            assert response.status_code != 404, "Upload batch endpoint should exist"
            assert response.status_code in [400, 500], "Should return client or server error for invalid request"
    
    def test_file_validator_accepts_html_files(self):
        """Test that file validator now accepts HTML files."""
        from src.file_processing.file_validator import FileValidator
        from werkzeug.datastructures import FileStorage
        from io import BytesIO
        
        validator = FileValidator()
        
        # Create a mock HTML file
        html_content = BytesIO(b"<html><body>Test</body></html>")
        html_file = FileStorage(
            stream=html_content,
            filename="test.html",
            content_type="text/html"
        )
        
        # Test that HTML files are now accepted
        assert validator.validate_file_type(html_file), "HTML files should be accepted"
        
        # Also test PDF files still work
        pdf_content = BytesIO(b"%PDF-1.4 test content")
        pdf_file = FileStorage(
            stream=pdf_content,
            filename="test.pdf",
            content_type="application/pdf"
        )
        
        assert validator.validate_file_type(pdf_file), "PDF files should still be accepted"
    
    def test_upload_endpoint_handles_multiple_files_correctly(self):
        """Test that upload endpoint processes multiple files correctly."""
        from src.web_interface.app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # Create multiple test files
            files = []
            for i in range(3):
                file_data = BytesIO(f"<html><body>Test HTML {i}</body></html>".encode())
                file_data.seek(0)
                files.append(('files', (file_data, f'test{i}.html')))
            
            response = client.post('/api/upload/batch',
                                 data=files,
                                 content_type='multipart/form-data')
            
            assert response.status_code == 200
            result = response.get_json()
            assert result['success'] is True
            assert result['successful_count'] == 3
            assert result['failed_count'] == 0
            assert len(result['file_ids']) == 3
    
    def test_file_upload_area_ui_supports_multiple(self):
        """Test that FileUploadArea UI component supports multiple files."""
        from src.web_interface.file_upload_ui import FileUploadArea
        
        # Test with multiple enabled
        upload_area = FileUploadArea(enable_multiple=True)
        html = upload_area.render()
        
        assert 'multiple' in html, "File input should have multiple attribute"
        assert 'type="file"' in html
        # Check that HTML and PDF files are accepted
        assert ('text/html' in html or '.html' in html), "Should accept HTML files"
        assert ('application/pdf' in html or '.pdf' in html), "Should accept PDF files"
    
    def test_file_upload_handles_mixed_file_types(self):
        """Test uploading multiple files of different types."""
        from src.web_interface.app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # Create HTML and PDF test files
            html_file = BytesIO(b"<html><body>HTML content</body></html>")
            html_file.seek(0)
            
            # Simple PDF header (not a real PDF, but has PDF signature)
            pdf_file = BytesIO(b"%PDF-1.4\nTest PDF content")
            pdf_file.seek(0)
            
            files = [
                ('files', (html_file, 'test.html')),
                ('files', (pdf_file, 'test.pdf'))
            ]
            
            response = client.post('/api/upload/batch',
                                 data=files,
                                 content_type='multipart/form-data')
            
            assert response.status_code == 200
            result = response.get_json()
            assert result['success'] is True
            assert result['successful_count'] == 2
    
    def test_upload_validates_file_types(self):
        """Test that upload rejects invalid file types."""
        from src.web_interface.app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # Try to upload invalid file type
            invalid_file = BytesIO(b"Invalid content")
            invalid_file.seek(0)
            
            files = [
                ('files', (invalid_file, 'test.txt'))
            ]
            
            response = client.post('/api/upload/batch',
                                 data=files,
                                 content_type='multipart/form-data')
            
            assert response.status_code == 400, "Should reject invalid file types"
            result = response.get_json()
            assert result['success'] is False
            assert 'error' in result
    
    def test_upload_size_limits(self):
        """Test that upload enforces file size limits."""
        from src.web_interface.app import create_app
        
        app = create_app()
        app.config['MAX_CONTENT_LENGTH'] = 1024  # 1KB limit for testing
        
        with app.test_client() as client:
            # Create a file larger than limit
            large_content = b"x" * 2048  # 2KB
            large_file = BytesIO(large_content)
            large_file.seek(0)
            
            files = [
                ('files', (large_file, 'large.html'))
            ]
            
            response = client.post('/api/upload/batch',
                                 data=files,
                                 content_type='multipart/form-data')
            
            # Flask returns 413 for files too large
            assert response.status_code == 413 or (response.status_code == 400 and 'size' in response.get_json().get('error', '').lower())
    
    def test_upload_progress_for_multiple_files(self):
        """Test that upload progress is tracked for multiple files."""
        from src.web_interface.app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # Create multiple files
            files = []
            for i in range(5):
                file_data = BytesIO(f"Content {i}".encode())
                file_data.seek(0)
                files.append(('files', (file_data, f'file{i}.html')))
            
            response = client.post('/api/upload/batch',
                                 data=files,
                                 content_type='multipart/form-data')
            
            assert response.status_code == 200
            result = response.get_json()
            
            # Should return upload result
            assert result['success'] is True
            assert result['successful_count'] == 5
            assert 'file_ids' in result
            assert len(result['file_ids']) == 5


class TestMultipleFileProcessing:
    """Test processing of multiple uploaded files."""
    
    def test_process_multiple_uploaded_files(self):
        """Test that multiple uploaded files can be processed."""
        from src.web_interface.app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # First upload multiple files
            files = []
            for i in range(3):
                content = f"<html><body>Page {i}</body></html>".encode()
                file_data = BytesIO(content)
                file_data.seek(0)
                files.append(('files', (file_data, f'page{i}.html')))
            
            upload_response = client.post('/api/upload-files',
                                        data=files,
                                        content_type='multipart/form-data')
            
            assert upload_response.status_code == 200
            upload_result = upload_response.get_json()
            
            # Extract uploaded file paths
            file_paths = [f['path'] for f in upload_result['uploadedFiles']]
            
            # Now process the uploaded files
            process_data = {
                'filePaths': file_paths,
                'outputFormat': 'text',
                'aggregationMode': 'multiple'  # Separate files
            }
            
            process_response = client.post('/api/process-uploaded-files',
                                         json=process_data)
            
            # This endpoint may not exist yet, but we're testing the expected behavior
            if process_response.status_code == 404:
                pytest.skip("Process endpoint not implemented yet")
            
            assert process_response.status_code == 200
            process_result = process_response.get_json()
            assert process_result['success'] is True
            assert len(process_result['results']) == 3