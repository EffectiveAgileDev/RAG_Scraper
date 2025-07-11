"""HTML WTEG processor for converting HTML content to WTEG schema."""

from typing import Union

from src.wteg.wteg_schema import WTEGRestaurantData
from .base_import_processor import BaseWTEGProcessor, BaseContentExtractor, BasePatternRecognizer
from .html_content_extractor import HTMLContentExtractor
from .html_pattern_recognizer import HTMLPatternRecognizer
from .menu_section_identifier import MenuSectionIdentifier
from .hours_parser import HoursParser
from .service_extractor import ServiceExtractor


class HTMLWTEGProcessor(BaseWTEGProcessor):
    """Processes HTML content and converts to WTEG schema format."""
    
    def _create_content_extractor(self) -> BaseContentExtractor:
        """Create HTML content extractor instance."""
        return HTMLContentExtractor()
    
    def _create_pattern_recognizer(self) -> BasePatternRecognizer:
        """Create HTML pattern recognizer instance."""
        return HTMLPatternRecognizer()
    
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
        """Process HTML source and convert to WTEG schema.
        
        Args:
            source: URL string or HTML content
            source_identifier: URL or identifier for the source
            
        Returns:
            WTEGRestaurantData object with extracted information
        """
        # Extract content from HTML source
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
            extraction_method="HTML_WTEG_PROCESSING"
        )
    
    def process_url_to_wteg_schema(self, url: str) -> WTEGRestaurantData:
        """Process URL and convert to WTEG schema.
        
        Args:
            url: URL to process
            
        Returns:
            WTEGRestaurantData object with extracted information
        """
        return self.process_to_wteg_schema(url, url)
    
    def process_html_to_wteg_schema(self, html_content: str, source_identifier: str) -> WTEGRestaurantData:
        """Process HTML content and convert to WTEG schema.
        
        Args:
            html_content: HTML content to process
            source_identifier: Identifier for the source
            
        Returns:
            WTEGRestaurantData object with extracted information
        """
        return self.process_to_wteg_schema(html_content, source_identifier)
    
    def extract_structured_data(self, source: Union[str, bytes], source_identifier: str) -> dict:
        """Extract structured data from HTML source.
        
        Args:
            source: URL string or HTML content
            source_identifier: URL or identifier for the source
            
        Returns:
            Dictionary with structured data
        """
        if hasattr(self.content_extractor, 'extract_structured_content'):
            return self.content_extractor.extract_structured_content(source, source_identifier)
        else:
            # Fallback to basic content extraction
            content = self.content_extractor.extract_content(source, source_identifier)
            return {'text_content': content}
    
    def process_multiple_restaurants(self, source: Union[str, bytes], source_identifier: str) -> list:
        """Process HTML content that contains multiple restaurants.
        
        Args:
            source: URL string or HTML content
            source_identifier: URL or identifier for the source
            
        Returns:
            List of WTEGRestaurantData objects
        """
        # For now, treat as single restaurant
        # TODO: Implement logic to split multiple restaurants
        single_restaurant = self.process_to_wteg_schema(source, source_identifier)
        return [single_restaurant]
    
    def validate_html_source(self, source: Union[str, bytes]) -> bool:
        """Validate that the source is valid for HTML processing.
        
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
            'supported_sources': ['URL', 'HTML content'],
            'supported_patterns': self.pattern_recognizer.get_supported_patterns(),
            'can_extract_structured_data': True,
            'can_extract_json_ld': True,
            'can_extract_microdata': True,
            'extraction_method': 'HTML_WTEG_PROCESSING'
        }