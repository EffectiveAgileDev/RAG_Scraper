"""PDF content extractor for PDF-based restaurant data extraction."""

from typing import Union
from pathlib import Path

from .base_import_processor import BaseContentExtractor


class PDFContentExtractor(BaseContentExtractor):
    """Extracts text content from PDF files."""
    
    def __init__(self):
        """Initialize PDF content extractor."""
        # Import PDF text extractor if available
        try:
            from src.processors.pdf_text_extractor import PDFTextExtractor
            self.pdf_extractor = PDFTextExtractor()
        except ImportError:
            self.pdf_extractor = None
    
    def extract_content(self, source: Union[str, bytes], source_identifier: str) -> str:
        """Extract text content from PDF source.
        
        Args:
            source: PDF file path or binary content
            source_identifier: Filename or identifier for the source
            
        Returns:
            Extracted text content
            
        Raises:
            ValueError: If source is invalid
            RuntimeError: If PDF extraction fails
        """
        if not self.validate_source(source):
            raise ValueError(f"Invalid PDF source: {source}")
        
        if self.pdf_extractor is None:
            raise RuntimeError("PDF text extractor not available")
        
        try:
            if isinstance(source, str):
                # Assume it's a file path
                result = self.pdf_extractor.extract_text_from_file(source)
            else:
                # Assume it's binary content
                result = self.pdf_extractor.extract_text_from_bytes(source)
            
            if result.success:
                return result.text
            else:
                raise RuntimeError(f"PDF extraction failed: {result.error}")
        
        except Exception as e:
            raise RuntimeError(f"PDF extraction error: {e}")
    
    def validate_source(self, source: Union[str, bytes]) -> bool:
        """Validate that the source is valid for PDF extraction.
        
        Args:
            source: Source data to validate
            
        Returns:
            True if source is valid for PDF extraction
        """
        if isinstance(source, str):
            # Check if it's a valid file path with PDF extension
            path = Path(source)
            return path.suffix.lower() == '.pdf' and (path.exists() or len(source) > 1000)
        elif isinstance(source, bytes):
            # Check if bytes start with PDF signature
            return source.startswith(b'%PDF-')
        
        return False