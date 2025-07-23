"""Converter for enhanced CMS extraction output to WTEG schema format."""

from typing import Dict, List, Any, Optional
from datetime import datetime

from .wteg_schema import (
    WTEGRestaurantData, WTEGLocation, WTEGMenuItem, WTEGServices,
    WTEGContactInfo, WTEGOnlineOrdering, WTEGWebLinks
)
from ..scraper.multi_strategy_scraper import RestaurantData


class CMSToWTEGConverter:
    """Converts enhanced CMS extraction output to WTEG schema format."""
    
    def __init__(self):
        """Initialize the converter."""
        pass
    
    def convert_restaurant_data(self, cms_data: RestaurantData) -> WTEGRestaurantData:
        """Convert RestaurantData from multi-strategy scraper to WTEG format.
        
        Args:
            cms_data: RestaurantData object from enhanced CMS extraction
            
        Returns:
            WTEGRestaurantData object with converted information
        """
        # Convert location
        location = self._convert_location(cms_data)
        
        # Convert menu items (the key enhancement)
        menu_items = self._convert_menu_items(cms_data.menu_items)
        
        # Convert contact info
        contact_info = self._convert_contact_info(cms_data)
        
        # Convert services (inferred from data)
        services = self._convert_services(cms_data)
        
        # Convert web links
        web_links = self._convert_web_links(cms_data)
        
        # Create WTEG restaurant data
        wteg_restaurant = WTEGRestaurantData(
            location=location,
            cuisine=cms_data.cuisine,
            brief_description=cms_data.name,
            menu_items=menu_items,
            click_to_call=contact_info,
            click_to_link=[],  # No online ordering in CMS data
            services_offered=services,
            click_for_website=web_links,
            click_for_map=WTEGWebLinks(),
            source_url=cms_data.website,
            extraction_timestamp=datetime.now().isoformat(),
            confidence_score=self._calculate_confidence_from_cms(cms_data),
            extraction_method="enhanced_cms_extraction"
        )
        
        return wteg_restaurant
    
    def _convert_location(self, cms_data: RestaurantData) -> WTEGLocation:
        """Convert address string to WTEGLocation object."""
        location = WTEGLocation()
        
        if cms_data.address:
            # Try to parse common address formats
            # Example: "1420 SE Stark St, Portland, OR 97214"
            address_parts = cms_data.address.split(", ")
            
            if len(address_parts) >= 1:
                location.street_address = address_parts[0].strip()
            
            if len(address_parts) >= 2:
                location.city = address_parts[1].strip()
            
            if len(address_parts) >= 3:
                # Try to parse "OR 97214" format
                state_zip = address_parts[2].strip().split()
                if len(state_zip) >= 1:
                    location.state = state_zip[0].strip()
                if len(state_zip) >= 2:
                    location.zip_code = state_zip[1].strip()
        
        return location
    
    def _convert_menu_items(self, cms_menu_items: Dict[str, List[str]]) -> List[WTEGMenuItem]:
        """Convert enhanced CMS menu items to WTEG format.
        
        This is the key method that handles the enhanced format:
        "Taleggio: cow milk, semi-soft, wash rind, strong, bold aroma with an unusual fruity tang"
        """
        wteg_menu_items = []
        
        for section_name, items in cms_menu_items.items():
            for item_str in items:
                menu_item = self._parse_enhanced_cms_item(item_str, section_name)
                wteg_menu_items.append(menu_item)
        
        return wteg_menu_items
    
    def _parse_enhanced_cms_item(self, item_str: str, category: str) -> WTEGMenuItem:
        """Parse enhanced CMS item string into WTEGMenuItem.
        
        Handles formats:
        - "Item Name: detailed description"
        - "Item Name - $Price"
        - "Item Name"
        """
        # Enhanced CMS format: "Item Name: detailed description"
        if ": " in item_str and not item_str.startswith("$"):
            parts = item_str.split(": ", 1)  # Split only on first colon
            return WTEGMenuItem(
                item_name=parts[0].strip(),
                description=parts[1].strip() if len(parts) > 1 else "",
                price="",
                category=category,
                dietary_info="",
                preparation_notes=""
            )
        
        # Traditional price format: "Item Name - $Price"
        elif " - $" in item_str or " - £" in item_str or " - €" in item_str:
            parts = item_str.split(" - ", 1)
            return WTEGMenuItem(
                item_name=parts[0].strip(),
                description="",
                price=parts[1].strip() if len(parts) > 1 else "",
                category=category,
                dietary_info="",
                preparation_notes=""
            )
        
        # Simple item name only
        else:
            return WTEGMenuItem(
                item_name=item_str.strip(),
                description="",
                price="",
                category=category,
                dietary_info="",
                preparation_notes=""
            )
    
    def _convert_contact_info(self, cms_data: RestaurantData) -> WTEGContactInfo:
        """Convert phone number to WTEG contact format."""
        contact = WTEGContactInfo()
        
        if cms_data.phone:
            contact.primary_phone = cms_data.phone
            contact.formatted_display = cms_data.phone
            # Create clickable link
            clean_phone = ''.join(c for c in cms_data.phone if c.isdigit())
            if clean_phone:
                contact.clickable_link = f"tel:{clean_phone}"
        
        return contact
    
    def _convert_services(self, cms_data: RestaurantData) -> WTEGServices:
        """Infer services from CMS data."""
        services = WTEGServices()
        
        # Try to infer services from AI analysis if available
        if hasattr(cms_data, 'ai_analysis') and cms_data.ai_analysis:
            ai_data = cms_data.ai_analysis
            
            # Check customer amenities
            amenities = ai_data.get('customer_amenities', {})
            if amenities:
                # Map common amenities to services
                if 'delivery' in str(amenities).lower():
                    services.delivery_available = True
                if 'takeout' in str(amenities).lower() or 'pickup' in str(amenities).lower():
                    services.takeout_available = True
                if 'outdoor' in str(amenities).lower() or 'patio' in str(amenities).lower():
                    services.outdoor_seating = True
                if 'reservation' in str(amenities).lower():
                    services.reservations_accepted = True
        
        return services
    
    def _convert_web_links(self, cms_data: RestaurantData) -> WTEGWebLinks:
        """Convert website and social media to WTEG format."""
        web_links = WTEGWebLinks()
        
        if cms_data.website:
            web_links.official_website = cms_data.website
        
        if cms_data.social_media:
            web_links.social_media_links = cms_data.social_media
        
        return web_links
    
    def _calculate_confidence_from_cms(self, cms_data: RestaurantData) -> float:
        """Calculate confidence score based on CMS data completeness."""
        score = 0.0
        
        # Base score from CMS confidence
        if cms_data.confidence == "high":
            score += 0.4
        elif cms_data.confidence == "medium":
            score += 0.3
        else:
            score += 0.1
        
        # Bonus for rich data
        if cms_data.name:
            score += 0.1
        if cms_data.address:
            score += 0.1
        if cms_data.phone:
            score += 0.1
        if cms_data.menu_items:
            score += 0.2
            # Extra bonus for detailed menu descriptions
            total_descriptions = sum(
                1 for items in cms_data.menu_items.values() 
                for item in items if ": " in item and len(item) > 20
            )
            if total_descriptions > 0:
                score += min(0.1, total_descriptions * 0.02)  # Up to 0.1 bonus
        
        if hasattr(cms_data, 'ai_analysis') and cms_data.ai_analysis:
            score += 0.1  # Bonus for AI enhancement
        
        return min(1.0, score)
    
    def convert_multiple_restaurants(self, cms_restaurants: List[RestaurantData]) -> List[WTEGRestaurantData]:
        """Convert multiple CMS restaurants to WTEG format."""
        return [self.convert_restaurant_data(restaurant) for restaurant in cms_restaurants]
    
    def validate_conversion(self, cms_data: RestaurantData, wteg_data: WTEGRestaurantData) -> Dict[str, Any]:
        """Validate the conversion quality."""
        validation_report = {
            "conversion_successful": True,
            "data_preserved": {},
            "enhancements": {},
            "issues": []
        }
        
        # Check data preservation
        validation_report["data_preserved"]["name"] = bool(wteg_data.brief_description)
        validation_report["data_preserved"]["menu_items"] = len(wteg_data.menu_items) > 0
        validation_report["data_preserved"]["contact"] = bool(
            wteg_data.click_to_call and wteg_data.click_to_call.primary_phone
        )
        validation_report["data_preserved"]["location"] = bool(
            wteg_data.location and wteg_data.location.street_address
        )
        
        # Check enhancements
        detailed_descriptions = sum(
            1 for item in wteg_data.menu_items 
            if item.description and len(item.description) > 10
        )
        validation_report["enhancements"]["detailed_menu_descriptions"] = detailed_descriptions
        validation_report["enhancements"]["confidence_score"] = wteg_data.confidence_score
        
        # Identify issues
        if not wteg_data.menu_items:
            validation_report["issues"].append("No menu items converted")
        if not wteg_data.brief_description:
            validation_report["issues"].append("No restaurant name/description")
        
        validation_report["conversion_successful"] = len(validation_report["issues"]) == 0
        
        return validation_report