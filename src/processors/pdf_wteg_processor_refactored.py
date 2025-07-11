"""Refactored PDF WTEG processor for converting PDF content to WTEG schema."""

from typing import Union

from src.wteg.wteg_schema import WTEGRestaurantData
from .base_import_processor import BaseWTEGProcessor, BaseContentExtractor, BasePatternRecognizer
from .pdf_content_extractor import PDFContentExtractor
from .pattern_recognizer import PatternRecognizer
from .menu_section_identifier import MenuSectionIdentifier
from .hours_parser import HoursParser
from .service_extractor import ServiceExtractor


class RefactoredPDFWTEGProcessor(BaseWTEGProcessor):
    """Processes PDF content and converts to WTEG schema format using base classes."""
    
    def _create_content_extractor(self) -> BaseContentExtractor:
        """Create PDF content extractor instance."""
        return PDFContentExtractor()
    
    def _create_pattern_recognizer(self) -> BasePatternRecognizer:
        """Create PDF pattern recognizer instance."""
        return PatternRecognizer()
    
    def _create_menu_section_identifier(self):
        """Create menu section identifier instance."""
        return MenuSectionIdentifier()
    
    def _create_hours_parser(self):
        """Create hours parser instance."""
        return HoursParser()
    
    def _create_service_extractor(self):
        """Create service extractor instance."""
        return ServiceExtractor()
    
    def process_to_wteg_schema(self, source: Union[str, bytes], source_identifier: str) -> WTEGRestaurantData:
        """Process PDF source and convert to WTEG schema.
        
        Args:
            source: PDF file path or binary content
            source_identifier: Filename or identifier for the source
            
        Returns:
            WTEGRestaurantData object with extracted information
        """
        # Extract content from PDF source
        content = self.content_extractor.extract_content(source, source_identifier)
        
        # Extract patterns from content
        patterns = self.pattern_recognizer.recognize_patterns(content)
        
        # Extract menu sections
        menu_sections = self.menu_section_identifier.identify_menu_sections(content)
        
        # Extract services
        services = self.service_extractor.extract_services_from_text(content)
        
        # Create and return WTEG restaurant data
        return self._create_wteg_restaurant_data(
            patterns=patterns,
            menu_sections=menu_sections,
            services=services,
            source_identifier=source_identifier,
            extraction_method="PDF_WTEG_PROCESSING"
        )
    
    def process_pdf_to_wteg_schema(self, pdf_content: str, filename: str) -> WTEGRestaurantData:
        """Process PDF content and convert to WTEG schema (legacy method).
        
        Args:
            pdf_content: Extracted text from PDF
            filename: Name of the PDF file
            
        Returns:
            WTEGRestaurantData object with extracted information
        """
        # Create patterns from content
        patterns = self.pattern_recognizer.recognize_patterns(pdf_content)
        
        # Extract menu sections
        menu_sections = self.menu_section_identifier.identify_menu_sections(pdf_content)
        
        # Extract services
        services = self.service_extractor.extract_services_from_text(pdf_content)
        
        # Create and return WTEG restaurant data
        return self._create_wteg_restaurant_data(
            patterns=patterns,
            menu_sections=menu_sections,
            services=services,
            source_identifier=f"file://{filename}",
            extraction_method="PDF_WTEG_PROCESSING"
        )
    
    def process_multiple_restaurants(self, source: Union[str, bytes], source_identifier: str) -> list:
        """Process PDF content that contains multiple restaurants.
        
        Args:
            source: PDF file path or binary content
            source_identifier: Filename or identifier for the source
            
        Returns:
            List of WTEGRestaurantData objects
        """
        # For now, treat as single restaurant
        # TODO: Implement logic to split multiple restaurants
        single_restaurant = self.process_to_wteg_schema(source, source_identifier)
        return [single_restaurant]
    
    def validate_pdf_source(self, source: Union[str, bytes]) -> bool:
        """Validate that the source is valid for PDF processing.
        
        Args:
            source: Source data to validate
            
        Returns:
            True if valid, False otherwise
        """
        return self.content_extractor.validate_source(source)
    
    def get_extraction_capabilities(self) -> dict:
        """Get information about extraction capabilities.
        
        Returns:
            Dictionary with capability information
        """
        return {
            'supported_sources': ['PDF file path', 'PDF binary content'],
            'supported_patterns': self.pattern_recognizer.get_supported_patterns(),
            'can_extract_structured_data': False,
            'can_extract_json_ld': False,
            'can_extract_microdata': False,
            'extraction_method': 'PDF_WTEG_PROCESSING'
        }