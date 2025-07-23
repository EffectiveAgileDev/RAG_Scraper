"""Formatters for WTEG data - Clean Code separation of concerns."""
from typing import Dict, Any, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .wteg_schema import WTEGRestaurantData


class WTEGRAGFormatter:
    """Formats WTEG data for RAG system consumption."""
    
    def __init__(self, restaurant: 'WTEGRestaurantData'):
        """Initialize formatter with restaurant data."""
        self.restaurant = restaurant
    
    def format(self) -> Dict[str, Any]:
        """Format restaurant data for RAG system."""
        return {
            "restaurant_name": self.restaurant.get_restaurant_name(),
            "location_summary": self._format_location(),
            "cuisine_type": self.restaurant.cuisine,
            "description": self.restaurant.brief_description,
            "menu_summary": self._format_menu(),
            "contact_methods": self._format_contacts(),
            "ordering_options": self._format_ordering(),
            "services_summary": self._format_services(),
            "web_presence": self._format_web_presence(),
            "searchable_content": self._create_searchable_text(),
            "metadata": self._format_metadata()
        }
    
    def _format_location(self) -> str:
        """Format location information."""
        if not self.restaurant.location:
            return ""
        return self.restaurant.location.format_full_address()
    
    def _format_menu(self) -> str:
        """Format menu summary with descriptions."""
        if not self.restaurant.menu_items:
            return "Menu information not available"
        
        # Group items by category
        categories = self._group_menu_by_category()
        
        # Format each category
        formatted_sections = []
        for category, items in categories.items():
            item_details = []
            for item in items[:5]:  # Limit to 5 per category
                # Include description if available for enhanced CMS extraction compatibility
                if item.description and item.description.strip():
                    item_details.append(f"{item.item_name}: {item.description}")
                elif item.price and item.price.strip():
                    item_details.append(f"{item.item_name} ({item.price})")
                else:
                    item_details.append(item.item_name)
            formatted_sections.append(f"{category}: {', '.join(item_details)}")
        
        return "; ".join(formatted_sections)
    
    def _group_menu_by_category(self) -> Dict[str, List]:
        """Group menu items by category."""
        categories = {}
        
        for item in self.restaurant.menu_items:
            category = item.category or "General"
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        return categories
    
    def _format_contacts(self) -> str:
        """Format contact information."""
        if not self.restaurant.click_to_call:
            return "Contact information not available"
        
        contact = self.restaurant.click_to_call
        if contact.primary_phone:
            return f"Phone: {contact.primary_phone}"
        
        return "Contact information not available"
    
    def _format_ordering(self) -> str:
        """Format online ordering options."""
        if not self.restaurant.click_to_link:
            return "Online ordering not available"
        
        platforms = [link.platform_name for link in self.restaurant.click_to_link if link.platform_name]
        
        if platforms:
            return f"Online ordering via: {', '.join(platforms)}"
        
        return "Online ordering not available"
    
    def _format_services(self) -> str:
        """Format available services."""
        if not self.restaurant.services_offered:
            return "Service information not available"
        
        services = self.restaurant.services_offered.get_available_services()
        
        if services:
            return f"Services: {', '.join(services)}"
        
        return "Service information not available"
    
    def _format_web_presence(self) -> str:
        """Format web presence information."""
        parts = []
        
        if self.restaurant.click_for_website and self.restaurant.click_for_website.official_website:
            parts.append(f"Website: {self.restaurant.click_for_website.official_website}")
        
        if self.restaurant.click_for_map and self.restaurant.click_for_map.map_url:
            parts.append(f"Map: {self.restaurant.click_for_map.map_url}")
        
        return ", ".join(parts) if parts else "Web information not available"
    
    def _create_searchable_text(self) -> str:
        """Create comprehensive searchable text for embeddings."""
        components = [
            self.restaurant.brief_description,
            f"Cuisine: {self.restaurant.cuisine}",
            self._format_location(),
            self._format_menu(),
            self._format_contacts(),
            self._format_ordering(),
            self._format_services()
        ]
        
        # Filter empty components and join
        return " | ".join(c for c in components if c and "not available" not in c)
    
    def _format_metadata(self) -> Dict[str, Any]:
        """Format metadata for RAG system."""
        return {
            "source": self.restaurant.source_url,
            "extraction_method": self.restaurant.extraction_method,
            "confidence": self.restaurant.confidence_score,
            "timestamp": self.restaurant.extraction_timestamp
        }


class WTEGTextFormatter:
    """Formats WTEG data as human-readable text."""
    
    @staticmethod
    def format_restaurant_summary(restaurant: 'WTEGRestaurantData') -> str:
        """Format restaurant as human-readable summary."""
        lines = []
        
        # Name and description
        name = restaurant.get_restaurant_name()
        lines.append(f"=== {name} ===")
        
        if restaurant.brief_description:
            lines.append(restaurant.brief_description)
        
        # Location
        if restaurant.location:
            address = restaurant.location.format_full_address()
            if address:
                lines.append(f"Location: {address}")
        
        # Contact
        if restaurant.click_to_call and restaurant.click_to_call.primary_phone:
            lines.append(f"Phone: {restaurant.click_to_call.primary_phone}")
        
        # Cuisine
        if restaurant.cuisine:
            lines.append(f"Cuisine: {restaurant.cuisine}")
        
        # Services
        if restaurant.services_offered:
            services = restaurant.services_offered.get_available_services()
            if services:
                lines.append(f"Services: {', '.join(services)}")
        
        return "\n".join(lines)


class WTEGJSONFormatter:
    """Formats WTEG data for JSON export."""
    
    @staticmethod
    def format_for_export(restaurants: List['WTEGRestaurantData']) -> Dict[str, Any]:
        """Format restaurants for JSON export."""
        return {
            "metadata": {
                "format_version": "1.0",
                "restaurant_count": len(restaurants),
                "export_timestamp": datetime.now().isoformat()
            },
            "restaurants": [
                restaurant.to_dict() for restaurant in restaurants
            ]
        }
    
    @staticmethod
    def format_minimal(restaurant: 'WTEGRestaurantData') -> Dict[str, Any]:
        """Format minimal restaurant data for quick lookup."""
        return {
            "name": restaurant.get_restaurant_name(),
            "cuisine": restaurant.cuisine,
            "location": restaurant.location.city if restaurant.location else "",
            "phone": restaurant.click_to_call.primary_phone if restaurant.click_to_call else "",
            "confidence": restaurant.confidence_score
        }