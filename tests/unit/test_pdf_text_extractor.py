"""Unit tests for PDF text extraction component."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

# Import the classes - tests should fail if implementation is incomplete
from src.file_processing.pdf_text_extractor import PDFTextExtractor, ExtractionResult, OCRProcessor


class TestPDFTextExtractor:
    """Test cases for PDFTextExtractor class."""

    @pytest.fixture
    def sample_pdf_content(self):
        """Sample PDF content for testing."""
        return b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Sample Restaurant Menu) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000205 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n286\n%%EOF"

    @pytest.fixture
    def sample_pdf_file(self, sample_pdf_content):
        """Create a temporary PDF file for testing."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(sample_pdf_content)
            temp_file.flush()
            yield temp_file.name
        os.unlink(temp_file.name)

    @pytest.fixture
    def mock_ocr_processor(self):
        """Mock OCR processor for testing."""
        processor = Mock(spec=OCRProcessor)
        processor.extract_text_from_image.return_value = "OCR extracted text from image"
        processor.is_scanned_pdf.return_value = False
        return processor

    @pytest.fixture
    def pdf_text_extractor(self, mock_ocr_processor):
        """Create PDFTextExtractor instance for testing."""
        return PDFTextExtractor(
            ocr_processor=mock_ocr_processor,
            fallback_libraries=['pymupdf', 'pdfplumber'],
            enable_table_extraction=True
        )

    def test_pdf_text_extractor_initialization(self):
        """Test PDFTextExtractor initializes correctly."""
        if PDFTextExtractor is None:
            pytest.skip("PDFTextExtractor not implemented yet (expected in RED phase)")
        
        extractor = PDFTextExtractor()
        assert extractor.fallback_libraries is not None
        assert extractor.enable_table_extraction is not None

    @patch('src.file_processing.pdf_text_extractor.pymupdf')
    def test_extract_text_with_pymupdf_success(self, mock_pymupdf, pdf_text_extractor, sample_pdf_file):
        """Test successful text extraction using PyMuPDF."""
        if PDFTextExtractor is None:
            pytest.skip("PDFTextExtractor not implemented yet (expected in RED phase)")
        
        # Mock PyMuPDF behavior
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Sample Restaurant Menu\nBurger - $12.99\nPizza - $15.99"
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.page_count = 1
        mock_pymupdf.open.return_value = mock_doc
        
        result = pdf_text_extractor.extract_text(sample_pdf_file, method='pymupdf')
        
        assert isinstance(result, ExtractionResult)
        assert result.success is True
        assert "Sample Restaurant Menu" in result.text
        assert "Burger - $12.99" in result.text
        assert result.method_used == 'pymupdf'
        assert result.page_count == 1

    @patch('src.file_processing.pdf_text_extractor.pdfplumber')
    def test_extract_text_with_pdfplumber_success(self, mock_pdfplumber, pdf_text_extractor, sample_pdf_file):
        """Test successful text extraction using pdfplumber."""
        if PDFTextExtractor is None:
            pytest.skip("PDFTextExtractor not implemented yet (expected in RED phase)")
        
        # Mock pdfplumber behavior
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample Restaurant Menu\nBurger - $12.99\nPizza - $15.99"
        mock_pdf.pages = [mock_page]
        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf
        
        result = pdf_text_extractor.extract_text(sample_pdf_file, method='pdfplumber')
        
        assert isinstance(result, ExtractionResult)
        assert result.success is True
        assert "Sample Restaurant Menu" in result.text
        assert result.method_used == 'pdfplumber'

    def test_extract_text_with_fallback_chain(self, pdf_text_extractor, sample_pdf_file):
        """Test text extraction with fallback library chain."""
        if PDFTextExtractor is None:
            pytest.skip("PDFTextExtractor not implemented yet (expected in RED phase)")
        
        with patch('src.file_processing.pdf_text_extractor.pymupdf') as mock_pymupdf, \
             patch('src.file_processing.pdf_text_extractor.pdfplumber') as mock_pdfplumber:
            
            # Make PyMuPDF fail
            mock_pymupdf.open.side_effect = Exception("PyMuPDF failed")
            
            # Make pdfplumber succeed
            mock_pdf = MagicMock()
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Fallback extraction successful"
            mock_pdf.pages = [mock_page]
            mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf
            
            result = pdf_text_extractor.extract_text(sample_pdf_file)
            
            assert result.success is True
            assert result.method_used == 'pdfplumber'
            assert "Fallback extraction successful" in result.text

    def test_extract_text_from_scanned_pdf_with_ocr(self, pdf_text_extractor, sample_pdf_file, mock_ocr_processor):
        """Test text extraction from scanned PDF using OCR."""
        if PDFTextExtractor is None:
            pytest.skip("PDFTextExtractor not implemented yet (expected in RED phase)")
        
        # Configure OCR processor to detect scanned PDF
        mock_ocr_processor.is_scanned_pdf.return_value = True
        mock_ocr_processor.extract_text_from_pdf.return_value = "OCR extracted: Restaurant Menu\nSteak - $25.99"
        
        result = pdf_text_extractor.extract_text(sample_pdf_file)
        
        assert result.success is True
        assert result.method_used == 'ocr'
        assert "OCR extracted" in result.text
        assert "Restaurant Menu" in result.text

    @patch('src.file_processing.pdf_text_extractor.pdfplumber')
    def test_extract_tables_from_pdf(self, mock_pdfplumber, pdf_text_extractor, sample_pdf_file):
        """Test table extraction from PDF."""
        if PDFTextExtractor is None:
            pytest.skip("PDFTextExtractor not implemented yet (expected in RED phase)")
        
        # Mock pdfplumber with table data
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Menu with tables"
        mock_page.extract_tables.return_value = [
            [['Item', 'Price'], ['Burger', '$12.99'], ['Pizza', '$15.99']],
            [['Appetizer', 'Cost'], ['Wings', '$8.99'], ['Nachos', '$9.99']]
        ]
        mock_pdf.pages = [mock_page]
        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf
        
        result = pdf_text_extractor.extract_text(sample_pdf_file, extract_tables=True)
        
        assert result.success is True
        assert len(result.tables) == 2
        assert result.tables[0] == [['Item', 'Price'], ['Burger', '$12.99'], ['Pizza', '$15.99']]
        assert "Burger" in str(result.tables)

    def test_extract_text_with_coordinate_mapping(self, pdf_text_extractor, sample_pdf_file):
        """Test text extraction with coordinate mapping."""
        if PDFTextExtractor is None:
            pytest.skip("PDFTextExtractor not implemented yet (expected in RED phase)")
        
        with patch('src.file_processing.pdf_text_extractor.pymupdf') as mock_pymupdf:
            mock_doc = MagicMock()
            mock_page = MagicMock()
            
            # Mock text extraction with coordinates
            mock_page.get_text.return_value = "Sample text"
            mock_page.get_text_dict.return_value = {
                'blocks': [
                    {
                        'type': 0,  # Text block
                        'lines': [
                            {
                                'spans': [
                                    {
                                        'text': 'Restaurant Name',
                                        'bbox': [100, 700, 200, 720]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            mock_doc.__iter__.return_value = [mock_page]
            mock_pymupdf.open.return_value = mock_doc
            
            result = pdf_text_extractor.extract_text(sample_pdf_file, include_coordinates=True)
            
            assert result.success is True
            assert result.coordinates is not None
            assert len(result.coordinates) > 0

    def test_extract_text_from_multiple_pages(self, pdf_text_extractor, sample_pdf_file):
        """Test text extraction from multi-page PDF."""
        if PDFTextExtractor is None:
            pytest.skip("PDFTextExtractor not implemented yet (expected in RED phase)")
        
        with patch('src.file_processing.pdf_text_extractor.pymupdf') as mock_pymupdf:
            mock_doc = MagicMock()
            mock_page1 = MagicMock()
            mock_page2 = MagicMock()
            
            mock_page1.get_text.return_value = "Page 1: Restaurant Menu"
            mock_page2.get_text.return_value = "Page 2: Dessert Menu"
            
            mock_doc.__iter__.return_value = [mock_page1, mock_page2]
            mock_doc.page_count = 2
            mock_pymupdf.open.return_value = mock_doc
            
            result = pdf_text_extractor.extract_text(sample_pdf_file)
            
            assert result.success is True
            assert result.page_count == 2
            assert "Page 1: Restaurant Menu" in result.text
            assert "Page 2: Dessert Menu" in result.text

    def test_extract_text_failure_all_methods(self, pdf_text_extractor, sample_pdf_file):
        """Test text extraction failure when all methods fail."""
        if PDFTextExtractor is None:
            pytest.skip("PDFTextExtractor not implemented yet (expected in RED phase)")
        
        with patch('src.file_processing.pdf_text_extractor.pymupdf') as mock_pymupdf, \
             patch('src.file_processing.pdf_text_extractor.pdfplumber') as mock_pdfplumber:
            
            # Make all methods fail
            mock_pymupdf.open.side_effect = Exception("PyMuPDF failed")
            mock_pdfplumber.open.side_effect = Exception("pdfplumber failed")
            
            # Make OCR fail too
            pdf_text_extractor.ocr_processor.extract_text_from_pdf.side_effect = Exception("OCR failed")
            
            result = pdf_text_extractor.extract_text(sample_pdf_file)
            
            assert result.success is False
            assert "failed" in result.error_message.lower()
            assert result.text == ""

    def test_extract_metadata_from_pdf(self, pdf_text_extractor, sample_pdf_file):
        """Test metadata extraction from PDF."""
        if PDFTextExtractor is None:
            pytest.skip("PDFTextExtractor not implemented yet (expected in RED phase)")
        
        with patch('src.file_processing.pdf_text_extractor.pymupdf') as mock_pymupdf:
            mock_doc = MagicMock()
            mock_doc.metadata = {
                'title': 'Restaurant Menu',
                'author': 'Chef John',
                'creator': 'Menu Creator',
                'producer': 'PDF Producer',
                'creationDate': 'D:20240101000000',
                'modDate': 'D:20240101000000'
            }
            mock_doc.page_count = 1
            mock_pymupdf.open.return_value = mock_doc
            
            metadata = pdf_text_extractor.extract_metadata(sample_pdf_file)
            
            assert metadata['title'] == 'Restaurant Menu'
            assert metadata['author'] == 'Chef John'
            assert metadata['page_count'] == 1

    def test_detect_text_encoding(self, pdf_text_extractor):
        """Test text encoding detection."""
        if PDFTextExtractor is None:
            pytest.skip("PDFTextExtractor not implemented yet (expected in RED phase)")
        
        # Test various encodings
        utf8_text = "Restaurant Café"
        latin1_text = "Restaurant Café".encode('latin1').decode('latin1')
        
        assert pdf_text_extractor.detect_encoding(utf8_text.encode('utf-8')) == 'utf-8'
        assert pdf_text_extractor.detect_encoding(latin1_text.encode('latin1')) in ['latin1', 'iso-8859-1']

    def test_clean_extracted_text(self, pdf_text_extractor):
        """Test text cleaning and normalization."""
        if PDFTextExtractor is None:
            pytest.skip("PDFTextExtractor not implemented yet (expected in RED phase)")
        
        dirty_text = "  Restaurant   Menu  \n\n\n  Burger   -   $12.99  \n\n  Pizza - $15.99  \n  "
        clean_text = pdf_text_extractor.clean_text(dirty_text)
        
        assert "Restaurant Menu" in clean_text
        assert "Burger - $12.99" in clean_text
        assert "Pizza - $15.99" in clean_text
        # Should remove excessive whitespace and newlines
        assert "\n\n\n" not in clean_text

    def test_extract_from_password_protected_pdf(self, pdf_text_extractor, sample_pdf_file):
        """Test handling of password-protected PDFs."""
        if PDFTextExtractor is None:
            pytest.skip("PDFTextExtractor not implemented yet (expected in RED phase)")
        
        with patch('src.file_processing.pdf_text_extractor.pymupdf') as mock_pymupdf, \
             patch('src.file_processing.pdf_text_extractor.pdfplumber') as mock_pdfplumber:
            
            # Simulate password-protected PDF - both libraries should fail
            mock_pymupdf.open.side_effect = Exception("cannot authenticate")
            mock_pdfplumber.open.side_effect = Exception("password required for encrypted PDF")
            
            result = pdf_text_extractor.extract_text(sample_pdf_file)
            
            assert result.success is False
            assert "password" in result.error_message.lower() or "authenticate" in result.error_message.lower()

    def test_extract_text_with_progress_callback(self, pdf_text_extractor, sample_pdf_file):
        """Test text extraction with progress callback."""
        if PDFTextExtractor is None:
            pytest.skip("PDFTextExtractor not implemented yet (expected in RED phase)")
        
        progress_updates = []
        
        def progress_callback(percentage, status):
            progress_updates.append({'percentage': percentage, 'status': status})
        
        with patch('src.file_processing.pdf_text_extractor.pymupdf') as mock_pymupdf:
            mock_doc = MagicMock()
            mock_page = MagicMock()
            mock_page.get_text.return_value = "Sample text"
            mock_doc.__iter__.return_value = [mock_page]
            mock_doc.page_count = 1
            mock_pymupdf.open.return_value = mock_doc
            
            result = pdf_text_extractor.extract_text(
                sample_pdf_file,
                progress_callback=progress_callback
            )
            
            assert result.success is True
            assert len(progress_updates) > 0
            assert progress_updates[-1]['percentage'] == 100

    def test_batch_extract_from_multiple_files(self, pdf_text_extractor, sample_pdf_content):
        """Test batch text extraction from multiple files."""
        if PDFTextExtractor is None:
            pytest.skip("PDFTextExtractor not implemented yet (expected in RED phase)")
        
        # Create multiple temporary files
        temp_files = []
        for i in range(3):
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_file.write(sample_pdf_content)
            temp_file.close()
            temp_files.append(temp_file.name)
        
        try:
            with patch('src.file_processing.pdf_text_extractor.pymupdf') as mock_pymupdf:
                mock_doc = MagicMock()
                mock_page = MagicMock()
                mock_page.get_text.return_value = "Sample menu text"
                mock_doc.__iter__.return_value = [mock_page]
                mock_doc.page_count = 1
                mock_pymupdf.open.return_value = mock_doc
                
                results = pdf_text_extractor.extract_text_batch(temp_files)
                
                assert len(results) == 3
                for result in results:
                    assert result.success is True
                    assert "Sample menu text" in result.text
        finally:
            # Cleanup
            for temp_file in temp_files:
                os.unlink(temp_file)

    def test_real_tesseract_ocr_integration(self, sample_pdf_file):
        """Test real Tesseract OCR integration for scanned PDFs."""
        from src.file_processing.pdf_text_extractor import PDFTextExtractor, OCRProcessor
        
        # Create an OCR processor that should use real Tesseract
        real_ocr_processor = OCRProcessor()
        
        # Configure it to force OCR on this PDF
        real_ocr_processor.is_scanned_pdf = Mock(return_value=True)
        
        # Create extractor with real OCR processor
        extractor = PDFTextExtractor(ocr_processor=real_ocr_processor)
        
        # This should fail because extract_text_from_pdf is still returning mock data
        result = extractor.extract_text(sample_pdf_file)
        
        assert result.success is True
        assert result.method_used == 'ocr'
        
        # This test should fail because real Tesseract should extract actual text from PDF
        # Not return hardcoded "OCR extracted: Restaurant Menu\nSteak - $25.99"
        assert "OCR extracted: Restaurant Menu" not in result.text  # Should fail - we don't want hardcoded text
        assert result.text != "OCR extracted: Restaurant Menu\nSteak - $25.99"  # Should fail - no hardcoded text

    def test_tesseract_availability_detection(self):
        """Test that OCR processor correctly detects Tesseract availability."""
        from src.file_processing.pdf_text_extractor import OCRProcessor
        
        ocr_processor = OCRProcessor()
        
        # Should detect that Tesseract is available on this system
        assert ocr_processor.tesseract_available is True
        assert ocr_processor.pytesseract is not None
        assert ocr_processor.PIL_Image is not None


class TestExtractionResult:
    """Test cases for ExtractionResult class."""

    def test_extraction_result_success(self):
        """Test ExtractionResult for successful extraction."""
        if ExtractionResult is None:
            pytest.skip("ExtractionResult not implemented yet (expected in RED phase)")
        
        result = ExtractionResult(
            success=True,
            text="Sample restaurant menu text",
            method_used='pymupdf',
            page_count=2,
            tables=[],
            coordinates=[],
            metadata={'title': 'Menu'},
            processing_time=1.5
        )
        
        assert result.success is True
        assert result.text == "Sample restaurant menu text"
        assert result.method_used == 'pymupdf'
        assert result.page_count == 2
        assert result.processing_time == 1.5

    def test_extraction_result_failure(self):
        """Test ExtractionResult for failed extraction."""
        if ExtractionResult is None:
            pytest.skip("ExtractionResult not implemented yet (expected in RED phase)")
        
        result = ExtractionResult(
            success=False,
            text="",
            method_used=None,
            error_message="Could not extract text from PDF",
            processing_time=0.5
        )
        
        assert result.success is False
        assert result.text == ""
        assert result.method_used is None
        assert "Could not extract text" in result.error_message
        assert result.processing_time == 0.5

    def test_extraction_result_to_dict(self):
        """Test ExtractionResult to dictionary conversion."""
        if ExtractionResult is None:
            pytest.skip("ExtractionResult not implemented yet (expected in RED phase)")
        
        result = ExtractionResult(
            success=True,
            text="Sample text",
            method_used='pymupdf',
            page_count=1
        )
        
        result_dict = result.to_dict()
        
        assert result_dict['success'] is True
        assert result_dict['text'] == "Sample text"
        assert result_dict['method_used'] == 'pymupdf'
        assert result_dict['page_count'] == 1

    def test_extraction_result_string_representation(self):
        """Test string representation of ExtractionResult."""
        if ExtractionResult is None:
            pytest.skip("ExtractionResult not implemented yet (expected in RED phase)")
        
        result = ExtractionResult(
            success=True,
            text="Sample text",
            method_used='pymupdf'
        )
        
        str_repr = str(result)
        assert "Sample text" in str_repr
        assert "pymupdf" in str_repr