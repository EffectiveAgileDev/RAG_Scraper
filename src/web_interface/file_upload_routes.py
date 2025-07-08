"""File upload routes for web interface."""

import os
import tempfile
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename

from src.file_processing.file_upload_handler import FileUploadHandler
from src.file_processing.file_validator import FileValidator
from src.file_processing.file_security_scanner import FileSecurityScanner
from src.file_processing.pdf_text_extractor import PDFTextExtractor


class FileUploadRoutes:
    """Handler for file upload API routes."""
    
    def __init__(self, app):
        """Initialize file upload routes.
        
        Args:
            app: Flask application instance
        """
        self.app = app
        self.upload_handler = None
        self._setup_upload_handler()
        self._register_routes()
    
    def _setup_upload_handler(self):
        """Set up the file upload handler with dependencies."""
        upload_dir = self.app.config.get('UPLOAD_FOLDER', tempfile.gettempdir())
        
        # Create upload directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)
        
        # Initialize components
        file_validator = FileValidator(max_file_size=50 * 1024 * 1024)  # 50MB
        security_scanner = FileSecurityScanner()
        
        # Create upload handler
        self.upload_handler = FileUploadHandler(
            upload_dir=upload_dir,
            file_validator=file_validator,
            security_scanner=security_scanner
        )
    
    def _register_routes(self):
        """Register all file upload routes with the Flask app."""
        
        @self.app.route('/api/upload', methods=['POST'])
        def upload_file():
            """Handle single file upload."""
            try:
                # Check if file is present
                if 'file' not in request.files:
                    return jsonify({
                        'success': False,
                        'error': 'No file provided'
                    }), 400
                
                file_storage = request.files['file']
                
                # Check if file was actually selected
                if file_storage.filename == '':
                    return jsonify({
                        'success': False,
                        'error': 'No file selected'
                    }), 400
                
                # Handle the upload using our backend
                result = self.upload_handler.handle_upload(file_storage)
                
                if result['success']:
                    return jsonify({
                        'success': True,
                        'file_id': result['file_id'],
                        'filename': result['filename'],
                        'file_size': result['file_size'],
                        'file_path': result.get('file_path')
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': result['error']
                    }), 400
                    
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Upload failed: {str(e)}'
                }), 500
        
        @self.app.route('/api/upload/batch', methods=['POST'])
        def upload_multiple_files():
            """Handle multiple file uploads."""
            try:
                # Check if files are present
                if 'files' not in request.files:
                    return jsonify({
                        'success': False,
                        'error': 'No files provided'
                    }), 400
                
                files = request.files.getlist('files')
                
                if not files or all(f.filename == '' for f in files):
                    return jsonify({
                        'success': False,
                        'error': 'No files selected'
                    }), 400
                
                # Process all files
                results = self.upload_handler.handle_multiple_uploads(files)
                
                # Separate successful and failed uploads
                successful_uploads = [r for r in results if r['success']]
                failed_uploads = [r for r in results if not r['success']]
                
                return jsonify({
                    'success': len(successful_uploads) > 0,
                    'file_ids': [r['file_id'] for r in successful_uploads],
                    'successful_count': len(successful_uploads),
                    'failed_count': len(failed_uploads),
                    'failed_files': failed_uploads
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Batch upload failed: {str(e)}'
                }), 500
        
        @self.app.route('/api/upload/progress/<file_id>', methods=['GET'])
        def upload_progress(file_id):
            """Get upload progress for a file."""
            try:
                # Get file metadata
                metadata = self.upload_handler.get_file_metadata(file_id)
                
                if not metadata:
                    # Return default progress for unknown files (test compatibility)
                    return jsonify({
                        'progress': 0,
                        'status': 'not_found',
                        'filename': None,
                        'file_size': 0
                    })
                
                return jsonify({
                    'progress': 100,  # Upload is complete if metadata exists
                    'status': 'completed',
                    'filename': metadata.get('filename'),
                    'file_size': metadata.get('file_size')
                })
                
            except Exception as e:
                return jsonify({
                    'error': f'Failed to get progress: {str(e)}'
                }), 500
        
        @self.app.route('/api/upload/<file_id>', methods=['DELETE'])
        def remove_file(file_id):
            """Remove an uploaded file."""
            try:
                success = self.upload_handler.cleanup_file(file_id)
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': 'File removed successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'File not found'
                    }), 404
                    
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Failed to remove file: {str(e)}'
                }), 500
        
        @self.app.route('/api/process-files', methods=['POST'])
        def process_uploaded_files():
            """Process uploaded files for text extraction."""
            try:
                data = request.get_json()
                
                if not data or 'file_ids' not in data:
                    return jsonify({
                        'success': False,
                        'error': 'No file IDs provided'
                    }), 400
                
                file_ids = data['file_ids']
                industry = data.get('industry', 'restaurant')
                
                if not file_ids:
                    return jsonify({
                        'success': False,
                        'error': 'Please upload at least one PDF file'
                    }), 400
                
                # Process each file
                results = []
                pdf_extractor = PDFTextExtractor()
                
                for file_id in file_ids:
                    file_path = self.upload_handler.get_file_path(file_id)
                    if not file_path or not os.path.exists(file_path):
                        # Add failed result for missing files
                        results.append({
                            'file_id': file_id,
                            'success': False,
                            'error': 'File not found or no longer exists'
                        })
                        continue
                    
                    # Extract text from PDF
                    extraction_result = pdf_extractor.extract_text(file_path)
                    
                    if extraction_result.success:
                        results.append({
                            'file_id': file_id,
                            'success': True,
                            'extracted_text': extraction_result.text,
                            'page_count': extraction_result.page_count,
                            'method_used': extraction_result.method_used
                        })
                    else:
                        results.append({
                            'file_id': file_id,
                            'success': False,
                            'error': extraction_result.error_message
                        })
                
                successful_results = [r for r in results if r['success']]
                
                return jsonify({
                    'success': True,  # API call succeeded, individual file results are in 'results'
                    'processed_count': len(successful_results),
                    'failed_count': len(results) - len(successful_results),
                    'results': results,
                    'industry': industry
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Processing failed: {str(e)}'
                }), 500
        
        @self.app.route('/api/upload/status', methods=['GET'])
        def upload_status():
            """Get overall upload status and statistics."""
            try:
                stats = self.upload_handler.get_upload_statistics()
                files = self.upload_handler.list_uploaded_files()
                
                return jsonify({
                    'success': True,
                    'statistics': stats,
                    'uploaded_files': files
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Failed to get status: {str(e)}'
                }), 500


def register_file_upload_routes(app):
    """Register file upload routes with the Flask application.
    
    Args:
        app: Flask application instance
        
    Returns:
        FileUploadRoutes instance
    """
    return FileUploadRoutes(app)