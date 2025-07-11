"""WTEG PDF processor for converting PDF content to WTEG schema."""

from typing import Dict, List, Any, Optional
from datetime import datetime

from src.wteg.wteg_schema import (
    WTEGRestaurantData, WTEGLocation, WTEGMenuItem, WTEGServices, 
    WTEGContactInfo, WTEGOnlineOrdering, WTEGWebLinks
)
from .pattern_recognizer import PatternRecognizer
from .menu_section_identifier import MenuSectionIdentifier
from .hours_parser import HoursParser
from .service_extractor import ServiceExtractor


class WTEGPDFProcessor:
    """Processes PDF content and converts to WTEG schema format."""
    
    def __init__(self):
        """Initialize WTEG PDF processor."""
        self.pattern_recognizer = PatternRecognizer()
        self.menu_section_identifier = MenuSectionIdentifier()
        self.hours_parser = HoursParser()
        self.service_extractor = ServiceExtractor()
    
    def process_pdf_to_wteg_schema(self, pdf_content: str, filename: str) -> WTEGRestaurantData:
        """Process PDF content and convert to WTEG schema.
        
        Args:
            pdf_content: Extracted text from PDF
            filename: Name of the PDF file
            
        Returns:
            WTEGRestaurantData object with extracted information
        """
        # Extract patterns from content
        patterns = self.pattern_recognizer.recognize_patterns(pdf_content)
        
        # Extract menu sections
        menu_sections = self.menu_section_identifier.identify_menu_sections(pdf_content)
        
        # Extract services
        services = self.service_extractor.extract_services_from_text(pdf_content)
        
        # Create WTEG restaurant data
        restaurant_data = WTEGRestaurantData()
        
        # Set basic information
        restaurant_data.brief_description = patterns.get('restaurant_name', '')
        restaurant_data.cuisine = patterns.get('cuisine_type', '')
        restaurant_data.source_url = f"file://{filename}"
        restaurant_data.extraction_timestamp = datetime.now().isoformat()
        restaurant_data.extraction_method = "PDF_WTEG_PROCESSING"
        
        # Set location information
        restaurant_data.location = self._create_location_from_patterns(patterns)
        
        # Set contact information
        restaurant_data.click_to_call = self._create_contact_from_patterns(patterns)
        
        # Set menu items using improved pattern recognizer instead of menu sections
        restaurant_data.menu_items = self._create_menu_items_from_patterns(patterns)
        
        # Set services
        restaurant_data.services_offered = services
        
        # Set web links
        restaurant_data.click_for_website = self._create_web_links_from_patterns(patterns)
        
        # Calculate confidence score
        restaurant_data.confidence_score = self._calculate_confidence_score(patterns, menu_sections, services)
        
        return restaurant_data
    
    def _create_location_from_patterns(self, patterns: Dict[str, Any]) -> WTEGLocation:
        """Create location object from extracted patterns.
        
        Args:
            patterns: Extracted patterns dictionary
            
        Returns:
            WTEGLocation object
        """
        location = WTEGLocation()
        
        address = patterns.get('address', '')
        if address:
            # Try to parse address components
            address_parts = self._parse_address_components(address)
            location.street_address = address_parts.get('street', '')
            location.city = address_parts.get('city', '')
            location.state = address_parts.get('state', '')
            location.zip_code = address_parts.get('zip_code', '')
        
        return location
    
    def _parse_address_components(self, address: str) -> Dict[str, str]:
        """Parse address into components.
        
        Args:
            address: Full address string
            
        Returns:
            Dictionary with address components
        """
        import re
        
        # Pattern: Street, City, State ZIP
        match = re.search(r'^([^,]+),\s*([^,]+),\s*([A-Z]{2})\s*(\d{5})', address)
        if match:
            return {
                'street': match.group(1).strip(),
                'city': match.group(2).strip(),
                'state': match.group(3).strip(),
                'zip_code': match.group(4).strip()
            }
        
        # Fallback - use full address as street
        return {
            'street': address,
            'city': '',
            'state': '',
            'zip_code': ''
        }
    
    def _create_contact_from_patterns(self, patterns: Dict[str, Any]) -> WTEGContactInfo:
        """Create contact info from extracted patterns.
        
        Args:
            patterns: Extracted patterns dictionary
            
        Returns:
            WTEGContactInfo object
        """
        contact = WTEGContactInfo()
        
        phone = patterns.get('phone', '')
        if phone:
            contact.primary_phone = phone
            contact.formatted_display = phone
            contact.clickable_link = contact.format_phone_link()
        
        return contact
    
    def _create_menu_items_from_patterns(self, patterns: Dict[str, Any]) -> List[WTEGMenuItem]:
        """Create menu items from improved pattern recognizer results.
        
        Args:
            patterns: Extracted patterns from PatternRecognizer
            
        Returns:
            List of WTEGMenuItem objects
        """
        menu_items = []
        
        # Get menu items from improved pattern recognizer
        extracted_menu_items = patterns.get('menu_items', [])
        
        for item_name in extracted_menu_items:
            menu_item = WTEGMenuItem()
            menu_item.item_name = item_name
            menu_item.price = ""  # Price extraction can be added if needed
            menu_item.category = "Menu"  # Default category
            menu_items.append(menu_item)
        
        return menu_items
    
    def _create_menu_items_from_sections(self, menu_sections: List[Dict[str, Any]]) -> List[WTEGMenuItem]:
        """Create menu items from menu sections.
        
        Args:
            menu_sections: List of menu sections
            
        Returns:
            List of WTEGMenuItem objects
        """
        menu_items = []
        
        for section in menu_sections:
            section_name = section.get('name', 'Unknown')
            items = section.get('items', [])
            
            for item in items:
                menu_item = WTEGMenuItem()
                menu_item.item_name = item.get('name', '')
                menu_item.price = item.get('price', '')
                menu_item.category = section_name
                menu_items.append(menu_item)
        
        return menu_items
    
    def _create_web_links_from_patterns(self, patterns: Dict[str, Any]) -> WTEGWebLinks:
        """Create web links from extracted patterns.
        
        Args:
            patterns: Extracted patterns dictionary
            
        Returns:
            WTEGWebLinks object
        """
        web_links = WTEGWebLinks()
        
        website = patterns.get('website', '')
        if website:
            web_links.official_website = website
        
        social_media = patterns.get('social_media', [])
        if social_media:
            web_links.social_media_links = social_media
        
        return web_links
    
    def _calculate_confidence_score(self, patterns: Dict[str, Any], menu_sections: List[Dict[str, Any]], 
                                   services: WTEGServices) -> float:
        """Calculate confidence score for extraction.
        
        Args:
            patterns: Extracted patterns
            menu_sections: Menu sections
            services: Services object
            
        Returns:
            Confidence score between 0 and 1
        """
        score = 0.0
        
        # Restaurant name
        if patterns.get('restaurant_name'):
            score += 0.2
        
        # Address
        if patterns.get('address'):
            score += 0.2
        
        # Phone
        if patterns.get('phone'):
            score += 0.1
        
        # Menu items
        if menu_sections:
            score += 0.3
        
        # Services
        if any([services.delivery_available, services.takeout_available, 
                services.catering_available, services.reservations_accepted]):
            score += 0.1
        
        # Additional information
        if patterns.get('cuisine_type'):
            score += 0.05
        
        if patterns.get('website'):
            score += 0.05
        
        return min(1.0, score)
    
    def process_multiple_restaurants(self, pdf_content: str, filename: str) -> List[WTEGRestaurantData]:
        """Process PDF content that contains multiple restaurants.
        
        Args:
            pdf_content: Extracted text from PDF
            filename: Name of the PDF file
            
        Returns:
            List of WTEGRestaurantData objects
        """
        # For now, treat as single restaurant
        # TODO: Implement logic to split multiple restaurants
        single_restaurant = self.process_pdf_to_wteg_schema(pdf_content, filename)
        return [single_restaurant]
    
    def validate_wteg_schema(self, restaurant_data: WTEGRestaurantData) -> bool:
        """Validate extracted data against WTEG schema.
        
        Args:
            restaurant_data: WTEGRestaurantData object to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if not restaurant_data.brief_description:
            return False
        
        # Check that location is properly initialized
        if not restaurant_data.location:
            return False
        
        # Check that services are properly initialized
        if not restaurant_data.services_offered:
            return False
        
        # Check that contact info is properly initialized
        if not restaurant_data.click_to_call:
            return False
        
        return True