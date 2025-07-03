"""WTEG-specific restaurant data schema for raw data extraction.

This module defines the data structures for extracting restaurant information
from WTEG (Where To Eat Guide) format without AI interpretation, preserving
raw data for client RAG system usage.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import json


@dataclass
class WTEGLocation:
    """Location information for WTEG restaurants."""
    
    street_address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    neighborhood: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert location to dictionary."""
        return {
            "street_address": self.street_address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "neighborhood": self.neighborhood,
            "latitude": self.latitude,
            "longitude": self.longitude
        }


@dataclass
class WTEGMenuItem:
    """Menu item information for WTEG restaurants."""
    
    item_name: str = ""
    description: str = ""
    price: str = ""
    category: str = ""
    dietary_info: str = ""
    preparation_notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert menu item to dictionary."""
        return {
            "item_name": self.item_name,
            "description": self.description,
            "price": self.price,
            "category": self.category,
            "dietary_info": self.dietary_info,
            "preparation_notes": self.preparation_notes
        }


@dataclass
class WTEGServices:
    """Services offered by WTEG restaurants."""
    
    delivery_available: bool = False
    takeout_available: bool = False
    catering_available: bool = False
    reservations_accepted: bool = False
    online_ordering: bool = False
    curbside_pickup: bool = False
    outdoor_seating: bool = False
    private_dining: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert services to dictionary."""
        return {
            "delivery_available": self.delivery_available,
            "takeout_available": self.takeout_available,
            "catering_available": self.catering_available,
            "reservations_accepted": self.reservations_accepted,
            "online_ordering": self.online_ordering,
            "curbside_pickup": self.curbside_pickup,
            "outdoor_seating": self.outdoor_seating,
            "private_dining": self.private_dining
        }


@dataclass
class WTEGContactInfo:
    """Contact information for WTEG restaurants (Click to Call)."""
    
    primary_phone: str = ""
    secondary_phone: str = ""
    formatted_display: str = ""
    clickable_link: str = ""
    extension: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert contact info to dictionary."""
        return {
            "primary_phone": self.primary_phone,
            "secondary_phone": self.secondary_phone,
            "formatted_display": self.formatted_display,
            "clickable_link": self.clickable_link,
            "extension": self.extension
        }


@dataclass
class WTEGOnlineOrdering:
    """Online ordering platform information (Click to Link)."""
    
    platform_name: str = ""
    ordering_url: str = ""
    platform_type: str = ""
    delivery_fee: str = ""
    minimum_order: str = ""
    estimated_delivery_time: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert online ordering to dictionary."""
        return {
            "platform_name": self.platform_name,
            "ordering_url": self.ordering_url,
            "platform_type": self.platform_type,
            "delivery_fee": self.delivery_fee,
            "minimum_order": self.minimum_order,
            "estimated_delivery_time": self.estimated_delivery_time
        }


@dataclass
class WTEGWebLinks:
    """Website and mapping links for WTEG restaurants."""
    
    official_website: str = ""
    menu_pdf_url: str = ""
    map_url: str = ""
    directions_url: str = ""
    social_media_links: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert web links to dictionary."""
        return {
            "official_website": self.official_website,
            "menu_pdf_url": self.menu_pdf_url,
            "map_url": self.map_url,
            "directions_url": self.directions_url,
            "social_media_links": self.social_media_links
        }


@dataclass
class WTEGRestaurantData:
    """Complete WTEG restaurant data structure for raw extraction."""
    
    # Core WTEG fields as specified by client
    location: Optional[WTEGLocation] = None
    cuisine: str = ""
    brief_description: str = ""
    menu_items: List[WTEGMenuItem] = field(default_factory=list)
    click_to_call: Optional[WTEGContactInfo] = None
    click_to_link: List[WTEGOnlineOrdering] = field(default_factory=list)
    services_offered: Optional[WTEGServices] = None
    click_for_website: Optional[WTEGWebLinks] = None
    click_for_map: Optional[WTEGWebLinks] = None
    
    # Metadata for tracking and quality
    source_url: str = ""
    extraction_timestamp: str = ""
    confidence_score: float = 0.0
    extraction_method: str = "wteg_specific"
    
    def __post_init__(self):
        """Initialize default objects if None."""
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert complete restaurant data to dictionary."""
        return {
            "location": self.location.to_dict() if self.location else None,
            "cuisine": self.cuisine,
            "brief_description": self.brief_description,
            "menu_items": [item.to_dict() if hasattr(item, 'to_dict') else item for item in self.menu_items],
            "click_to_call": self.click_to_call.to_dict() if self.click_to_call else None,
            "click_to_link": [link.to_dict() if hasattr(link, 'to_dict') else link for link in self.click_to_link],
            "services_offered": self.services_offered.to_dict() if self.services_offered else None,
            "click_for_website": self.click_for_website.to_dict() if self.click_for_website else None,
            "click_for_map": self.click_for_map.to_dict() if self.click_for_map else None,
            "source_url": self.source_url,
            "extraction_timestamp": self.extraction_timestamp,
            "confidence_score": self.confidence_score,
            "extraction_method": self.extraction_method
        }
    
    def to_rag_format(self) -> Dict[str, Any]:
        """Convert to RAG-optimized format for client ChatBot."""
        # Create structured content for RAG system
        rag_data = {
            "restaurant_name": self._extract_name_from_description(),
            "location_summary": self._create_location_summary(),
            "cuisine_type": self.cuisine,
            "description": self.brief_description,
            "menu_summary": self._create_menu_summary(),
            "contact_methods": self._create_contact_summary(),
            "ordering_options": self._create_ordering_summary(),
            "services_summary": self._create_services_summary(),
            "web_presence": self._create_web_summary(),
            "searchable_content": self._create_searchable_text(),
            "metadata": {
                "source": self.source_url,
                "extraction_method": self.extraction_method,
                "confidence": self.confidence_score,
                "timestamp": self.extraction_timestamp
            }
        }
        return rag_data
    
    def _extract_name_from_description(self) -> str:
        """Extract restaurant name from description or other fields."""
        # For now, try to extract from brief description
        # This could be enhanced with more sophisticated extraction
        if self.brief_description:
            # Simple heuristic - restaurant name might be first part before dash or period
            parts = self.brief_description.split(' - ')
            if len(parts) > 1:
                return parts[0].strip()
            parts = self.brief_description.split('. ')
            if len(parts) > 1:
                return parts[0].strip()
        return "Restaurant Name Not Found"
    
    def _create_location_summary(self) -> str:
        """Create location summary for RAG queries."""
        if not self.location:
            return ""
        
        parts = []
        if self.location.street_address:
            parts.append(self.location.street_address)
        if self.location.neighborhood:
            parts.append(f"in {self.location.neighborhood}")
        if self.location.city:
            parts.append(self.location.city)
        if self.location.state:
            parts.append(self.location.state)
        
        return ", ".join(parts)
    
    def _create_menu_summary(self) -> str:
        """Create menu summary for RAG queries."""
        if not self.menu_items:
            return "Menu information not available"
        
        # Group by category and create summary
        categories = {}
        for item in self.menu_items:
            category = getattr(item, 'category', 'General') if hasattr(item, 'category') else 'General'
            if category not in categories:
                categories[category] = []
            
            item_name = getattr(item, 'item_name', '') if hasattr(item, 'item_name') else str(item.get('item_name', ''))
            if item_name:
                categories[category].append(item_name)
        
        summary_parts = []
        for category, items in categories.items():
            if items:
                summary_parts.append(f"{category}: {', '.join(items[:5])}")  # Limit to 5 items per category
        
        return "; ".join(summary_parts)
    
    def _create_contact_summary(self) -> str:
        """Create contact summary for RAG queries."""
        if not self.click_to_call:
            return "Contact information not available"
        
        contact_parts = []
        if self.click_to_call.primary_phone:
            contact_parts.append(f"Phone: {self.click_to_call.primary_phone}")
        if self.click_to_call.formatted_display:
            contact_parts.append(f"Display: {self.click_to_call.formatted_display}")
        
        return ", ".join(contact_parts) if contact_parts else "Contact information not available"
    
    def _create_ordering_summary(self) -> str:
        """Create ordering options summary for RAG queries."""
        if not self.click_to_link:
            return "Online ordering not available"
        
        platforms = []
        for link in self.click_to_link:
            platform_name = getattr(link, 'platform_name', '') if hasattr(link, 'platform_name') else str(link.get('platform_name', ''))
            if platform_name:
                platforms.append(platform_name)
        
        return f"Online ordering via: {', '.join(platforms)}" if platforms else "Online ordering not available"
    
    def _create_services_summary(self) -> str:
        """Create services summary for RAG queries."""
        if not self.services_offered:
            return "Service information not available"
        
        services = []
        service_mapping = {
            'delivery_available': 'Delivery',
            'takeout_available': 'Takeout',
            'catering_available': 'Catering',
            'reservations_accepted': 'Reservations',
            'outdoor_seating': 'Outdoor Seating',
            'private_dining': 'Private Dining'
        }
        
        for attr, display_name in service_mapping.items():
            if hasattr(self.services_offered, attr) and getattr(self.services_offered, attr):
                services.append(display_name)
        
        return f"Services: {', '.join(services)}" if services else "Service information not available"
    
    def _create_web_summary(self) -> str:
        """Create web presence summary for RAG queries."""
        web_parts = []
        
        if self.click_for_website and self.click_for_website.official_website:
            web_parts.append(f"Website: {self.click_for_website.official_website}")
        
        if self.click_for_map and self.click_for_map.map_url:
            web_parts.append(f"Map: {self.click_for_map.map_url}")
        
        return ", ".join(web_parts) if web_parts else "Web information not available"
    
    def _create_searchable_text(self) -> str:
        """Create comprehensive searchable text for RAG embedding."""
        text_parts = [
            self.brief_description,
            f"Cuisine: {self.cuisine}",
            self._create_location_summary(),
            self._create_menu_summary(),
            self._create_contact_summary(),
            self._create_ordering_summary(),
            self._create_services_summary(),
            self._create_web_summary()
        ]
        
        # Filter out empty parts and join
        searchable_text = " | ".join([part for part in text_parts if part.strip()])
        return searchable_text