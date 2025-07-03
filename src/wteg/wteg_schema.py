"""WTEG-specific restaurant data schema - Refactored version.

Clean Code refactoring with improved organization and reduced duplication.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

from .wteg_base import WTEGSerializable, WTEGConstants


@dataclass
class WTEGLocation(WTEGSerializable):
    """Location information for WTEG restaurants."""
    
    street_address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    neighborhood: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    def format_full_address(self) -> str:
        """Format complete address string."""
        parts = [
            self.street_address,
            self.city,
            f"{self.state} {self.zip_code}".strip()
        ]
        return ", ".join(p for p in parts if p.strip())


@dataclass
class WTEGMenuItem(WTEGSerializable):
    """Menu item information for WTEG restaurants."""
    
    item_name: str = ""
    description: str = ""
    price: str = ""
    category: str = ""
    dietary_info: str = ""
    preparation_notes: str = ""
    
    def format_display(self) -> str:
        """Format menu item for display."""
        if self.price:
            return f"{self.item_name} - {self.price}"
        return self.item_name


@dataclass
class WTEGServices(WTEGSerializable):
    """Services offered by WTEG restaurants."""
    
    delivery_available: bool = False
    takeout_available: bool = False
    catering_available: bool = False
    reservations_accepted: bool = False
    online_ordering: bool = False
    curbside_pickup: bool = False
    outdoor_seating: bool = False
    private_dining: bool = False
    
    def get_available_services(self) -> List[str]:
        """Get list of available services."""
        service_map = {
            'delivery_available': 'Delivery',
            'takeout_available': 'Takeout',
            'catering_available': 'Catering',
            'reservations_accepted': 'Reservations',
            'online_ordering': 'Online Ordering',
            'curbside_pickup': 'Curbside Pickup',
            'outdoor_seating': 'Outdoor Seating',
            'private_dining': 'Private Dining'
        }
        
        return [
            service_map[attr] 
            for attr, display in service_map.items() 
            if getattr(self, attr)
        ]


@dataclass
class WTEGContactInfo(WTEGSerializable):
    """Contact information for WTEG restaurants."""
    
    primary_phone: str = ""
    secondary_phone: str = ""
    formatted_display: str = ""
    clickable_link: str = ""
    extension: str = ""
    
    def format_phone_link(self) -> str:
        """Format phone number as clickable tel: link."""
        if not self.primary_phone:
            return ""
        
        # Extract digits for tel: link
        digits = ''.join(c for c in self.primary_phone if c.isdigit())
        if digits:
            return f"tel:{digits}"
        return ""


@dataclass
class WTEGOnlineOrdering(WTEGSerializable):
    """Online ordering platform information."""
    
    platform_name: str = ""
    ordering_url: str = ""
    platform_type: str = ""
    delivery_fee: str = ""
    minimum_order: str = ""
    estimated_delivery_time: str = ""
    
    def format_summary(self) -> str:
        """Format ordering platform summary."""
        parts = [self.platform_name]
        if self.delivery_fee:
            parts.append(f"Fee: {self.delivery_fee}")
        if self.minimum_order:
            parts.append(f"Min: {self.minimum_order}")
        return " | ".join(parts)


@dataclass
class WTEGWebLinks(WTEGSerializable):
    """Website and mapping links for WTEG restaurants."""
    
    official_website: str = ""
    menu_pdf_url: str = ""
    map_url: str = ""
    directions_url: str = ""
    social_media_links: List[str] = field(default_factory=list)
    
    def has_web_presence(self) -> bool:
        """Check if restaurant has any web presence."""
        return bool(
            self.official_website or 
            self.menu_pdf_url or 
            self.social_media_links
        )


@dataclass
class WTEGRestaurantData(WTEGSerializable):
    """Complete WTEG restaurant data structure."""
    
    # Core WTEG fields
    location: Optional[WTEGLocation] = None
    cuisine: str = ""
    brief_description: str = ""
    menu_items: List[WTEGMenuItem] = field(default_factory=list)
    click_to_call: Optional[WTEGContactInfo] = None
    click_to_link: List[WTEGOnlineOrdering] = field(default_factory=list)
    services_offered: Optional[WTEGServices] = None
    click_for_website: Optional[WTEGWebLinks] = None
    click_for_map: Optional[WTEGWebLinks] = None
    
    # Metadata
    source_url: str = ""
    extraction_timestamp: str = ""
    confidence_score: float = 0.0
    extraction_method: str = WTEGConstants.EXTRACTION_WTEG
    
    def __post_init__(self):
        """Initialize default objects if None."""
        self._initialize_defaults()
    
    def _initialize_defaults(self):
        """Initialize default values for optional fields."""
        if self.location is None:
            self.location = WTEGLocation()
        if self.click_to_call is None:
            self.click_to_call = WTEGContactInfo()
        if self.services_offered is None:
            self.services_offered = WTEGServices()
        if self.click_for_website is None:
            self.click_for_website = WTEGWebLinks()
        if self.click_for_map is None:
            self.click_for_map = WTEGWebLinks()
    
    def get_restaurant_name(self) -> str:
        """Extract restaurant name from available data."""
        if not self.brief_description:
            return "Restaurant Name Not Found"
        
        # Try to extract from description
        for separator in [' - ', '. ', ' is ']:
            if separator in self.brief_description:
                return self.brief_description.split(separator)[0].strip()
        
        # Return first few words as fallback
        words = self.brief_description.split()[:3]
        return " ".join(words)
    
    def to_rag_format(self) -> Dict[str, Any]:
        """Convert to RAG-optimized format."""
        from .wteg_formatters import WTEGRAGFormatter
        formatter = WTEGRAGFormatter(self)
        return formatter.format()
    
    def _extract_name_from_description(self) -> str:
        """Legacy method for compatibility - delegates to get_restaurant_name."""
        return self.get_restaurant_name()
    
    def _create_location_summary(self) -> str:
        """Create location summary for RAG queries."""
        if not self.location:
            return ""
        return self.location.format_full_address()
    
    def _create_menu_summary(self) -> str:
        """Create menu summary for RAG queries."""
        if not self.menu_items:
            return "Menu information not available"
        
        from .wteg_formatters import WTEGRAGFormatter
        formatter = WTEGRAGFormatter(self)
        return formatter._format_menu()
    
    def _create_contact_summary(self) -> str:
        """Create contact summary for RAG queries."""
        from .wteg_formatters import WTEGRAGFormatter
        formatter = WTEGRAGFormatter(self)
        return formatter._format_contacts()
    
    def _create_ordering_summary(self) -> str:
        """Create ordering options summary for RAG queries."""
        from .wteg_formatters import WTEGRAGFormatter
        formatter = WTEGRAGFormatter(self)
        return formatter._format_ordering()
    
    def _create_services_summary(self) -> str:
        """Create services summary for RAG queries."""
        from .wteg_formatters import WTEGRAGFormatter
        formatter = WTEGRAGFormatter(self)
        return formatter._format_services()
    
    def _create_web_summary(self) -> str:
        """Create web presence summary for RAG queries."""
        from .wteg_formatters import WTEGRAGFormatter
        formatter = WTEGRAGFormatter(self)
        return formatter._format_web_presence()
    
    def _create_searchable_text(self) -> str:
        """Create comprehensive searchable text for RAG embedding."""
        from .wteg_formatters import WTEGRAGFormatter
        formatter = WTEGRAGFormatter(self)
        return formatter._create_searchable_text()