"""Abstract base classes for generic import processing."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from src.wteg.wteg_schema import WTEGRestaurantData


class BaseContentExtractor(ABC):
    """Abstract base class for content extraction from various sources."""
    
    @abstractmethod
    def extract_content(self, source: Union[str, bytes], source_identifier: str) -> str:
        """Extract text content from source.
        
        Args:
            source: Source data (file path, URL, or content)
            source_identifier: Identifier for the source (filename, URL, etc.)
            
        Returns:
            Extracted text content
        """
        pass
    
    @abstractmethod
    def validate_source(self, source: Union[str, bytes]) -> bool:
        """Validate that the source is valid for this extractor.
        
        Args:
            source: Source data to validate
            
        Returns:
            True if source is valid for this extractor
        """
        pass


class BasePatternRecognizer(ABC):
    """Abstract base class for pattern recognition in extracted content."""
    
    @abstractmethod
    def recognize_patterns(self, content: str) -> Dict[str, Any]:
        """Recognize patterns in content.
        
        Args:
            content: Text content to analyze
            
        Returns:
            Dictionary with recognized patterns
        """
        pass
    
    @abstractmethod
    def get_supported_patterns(self) -> List[str]:
        """Get list of supported pattern types.
        
        Returns:
            List of pattern type names
        """
        pass


class BaseWTEGProcessor(ABC):
    """Abstract base class for WTEG schema processing."""
    
    def __init__(self):
        """Initialize base WTEG processor."""
        self.content_extractor = self._create_content_extractor()
        self.pattern_recognizer = self._create_pattern_recognizer()
        self.menu_section_identifier = self._create_menu_section_identifier()
        self.hours_parser = self._create_hours_parser()
        self.service_extractor = self._create_service_extractor()
    
    @abstractmethod
    def _create_content_extractor(self) -> BaseContentExtractor:
        """Create content extractor instance."""
        pass
    
    @abstractmethod
    def _create_pattern_recognizer(self) -> BasePatternRecognizer:
        """Create pattern recognizer instance."""
        pass
    
    @abstractmethod
    def _create_menu_section_identifier(self):
        """Create menu section identifier instance."""
        pass
    
    @abstractmethod
    def _create_hours_parser(self):
        """Create hours parser instance."""
        pass
    
    @abstractmethod
    def _create_service_extractor(self):
        """Create service extractor instance."""
        pass
    
    @abstractmethod
    def process_to_wteg_schema(self, source: Union[str, bytes], source_identifier: str) -> WTEGRestaurantData:
        """Process source content and convert to WTEG schema.
        
        Args:
            source: Source data (file path, URL, or content)
            source_identifier: Identifier for the source
            
        Returns:
            WTEGRestaurantData object with extracted information
        """
        pass
    
    def _create_wteg_restaurant_data(self, patterns: Dict[str, Any], menu_sections: List[Dict[str, Any]], 
                                   services, source_identifier: str, extraction_method: str) -> WTEGRestaurantData:
        """Create WTEG restaurant data from extracted components.
        
        Args:
            patterns: Extracted patterns dictionary
            menu_sections: Menu sections
            services: Services object
            source_identifier: Source identifier
            extraction_method: Method used for extraction
            
        Returns:
            WTEGRestaurantData object
        """
        from src.wteg.wteg_schema import WTEGLocation, WTEGMenuItem, WTEGContactInfo, WTEGWebLinks
        
        # Create WTEG restaurant data
        restaurant_data = WTEGRestaurantData()
        
        # Set basic information
        restaurant_data.brief_description = patterns.get('restaurant_name', '')
        restaurant_data.cuisine = patterns.get('cuisine_type', '')
        restaurant_data.source_url = source_identifier
        restaurant_data.extraction_timestamp = datetime.now().isoformat()
        restaurant_data.extraction_method = extraction_method
        
        # Set location information
        restaurant_data.location = self._create_location_from_patterns(patterns)
        
        # Set contact information
        restaurant_data.click_to_call = self._create_contact_from_patterns(patterns)
        
        # Set menu items
        restaurant_data.menu_items = self._create_menu_items_from_sections(menu_sections)
        
        # Set services
        restaurant_data.services_offered = services
        
        # Set web links
        restaurant_data.click_for_website = self._create_web_links_from_patterns(patterns)
        
        # Calculate confidence score
        restaurant_data.confidence_score = self._calculate_confidence_score(patterns, menu_sections, services)
        
        return restaurant_data
    
    def _create_location_from_patterns(self, patterns: Dict[str, Any]):
        """Create location object from extracted patterns."""
        from src.wteg.wteg_schema import WTEGLocation
        
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
        """Parse address into components."""
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
    
    def _create_contact_from_patterns(self, patterns: Dict[str, Any]):
        """Create contact info from extracted patterns."""
        from src.wteg.wteg_schema import WTEGContactInfo
        
        contact = WTEGContactInfo()
        
        phone = patterns.get('phone', '')
        if phone:
            contact.primary_phone = phone
            contact.formatted_display = phone
            contact.clickable_link = contact.format_phone_link()
        
        return contact
    
    def _create_menu_items_from_sections(self, menu_sections: List[Dict[str, Any]]):
        """Create menu items from menu sections."""
        from src.wteg.wteg_schema import WTEGMenuItem
        
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
    
    def _create_web_links_from_patterns(self, patterns: Dict[str, Any]):
        """Create web links from extracted patterns."""
        from src.wteg.wteg_schema import WTEGWebLinks
        
        web_links = WTEGWebLinks()
        
        website = patterns.get('website', '')
        if website:
            web_links.official_website = website
        
        social_media = patterns.get('social_media', [])
        if social_media:
            web_links.social_media_links = social_media
        
        return web_links
    
    def _calculate_confidence_score(self, patterns: Dict[str, Any], menu_sections: List[Dict[str, Any]], 
                                   services) -> float:
        """Calculate confidence score for extraction."""
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
        if hasattr(services, 'delivery_available') and any([
            services.delivery_available, services.takeout_available, 
            services.catering_available, services.reservations_accepted
        ]):
            score += 0.1
        
        # Additional information
        if patterns.get('cuisine_type'):
            score += 0.05
        
        if patterns.get('website'):
            score += 0.05
        
        return min(1.0, score)