"""WTEG-specific data extractor for mobimag.co JavaScript content.

This module provides specialized extraction for WTEG (Where To Eat Guide)
format to solve the critical client issue with incomplete data extraction.
"""
import re
import json
from urllib.parse import unquote
from typing import Optional, Dict, Any, List
from datetime import datetime

from .wteg_schema import (
    WTEGRestaurantData, WTEGLocation, WTEGMenuItem, WTEGServices,
    WTEGContactInfo, WTEGOnlineOrdering, WTEGWebLinks
)
from .wteg_url_patterns import WTEGURLPatternParser


class WTEGExtractor:
    """Specialized extractor for WTEG restaurant data from mobimag.co."""
    
    def __init__(self):
        """Initialize WTEG extractor."""
        self.url_parser = WTEGURLPatternParser()
        
        # Regex patterns for data extraction
        self.pagedata_pattern = re.compile(
            r'pageData = JSON\.parse\(decodeURIComponent\("([^"]+)"\)\)', re.DOTALL
        )
        
        # Alternative patterns for different JavaScript formats
        self.pagedata_patterns = [
            re.compile(r'pageData = JSON\.parse\(decodeURIComponent\("([^"]+)"\)\)', re.DOTALL),
            re.compile(r'const pageData = JSON\.parse\(decodeURIComponent\("([^"]+)"\)\)', re.DOTALL),
            re.compile(r'var pageData = JSON\.parse\(decodeURIComponent\("([^"]+)"\)\)', re.DOTALL),
            re.compile(r'pageData\s*=\s*JSON\.parse\(decodeURIComponent\("([^"]+)"\)\)', re.DOTALL)
        ]
    
    def extract_wteg_data(self, html_content: str, url: str) -> Optional[WTEGRestaurantData]:
        """Extract WTEG restaurant data from HTML content and URL."""
        try:
            # Validate this is a WTEG URL
            if not self.url_parser.is_wteg_url(url):
                return None
            
            # Extract pageData from JavaScript
            page_data = self._extract_pagedata_from_html(html_content)
            if not page_data:
                return None
            
            # Get the specific restaurant based on URL
            restaurant_data = self._select_restaurant_by_url(page_data, url)
            if not restaurant_data:
                return None
            
            # Convert to WTEG schema
            wteg_restaurant = self._convert_to_wteg_schema(restaurant_data, url)
            
            return wteg_restaurant
            
        except Exception as e:
            print(f"WTEG extraction error for {url}: {e}")
            return None
    
    def _extract_pagedata_from_html(self, html_content: str) -> Optional[List[Dict[str, Any]]]:
        """Extract pageData array from HTML JavaScript."""
        try:
            # Try all pageData patterns
            for pattern in self.pagedata_patterns:
                match = pattern.search(html_content)
                if match:
                    encoded_data = match.group(1)
                    decoded_data = unquote(encoded_data)
                    page_data = json.loads(decoded_data)
                    
                    if isinstance(page_data, list) and len(page_data) > 0:
                        return page_data
            
            return None
            
        except (json.JSONDecodeError, IndexError, AttributeError) as e:
            print(f"PageData extraction error: {e}")
            return None
    
    def _select_restaurant_by_url(self, page_data: List[Dict[str, Any]], url: str) -> Optional[Dict[str, Any]]:
        """Select the correct restaurant from pageData based on URL."""
        try:
            # Parse URL to get page ID
            url_info = self.url_parser.parse_url(url)
            target_page_id = url_info["page_id"]
            
            # Method 1: Find by exact pageID match
            for restaurant in page_data:
                if restaurant.get("pageID") == target_page_id:
                    return restaurant
            
            # Method 2: Find by pageID as string
            for restaurant in page_data:
                if str(restaurant.get("pageID", "")) == target_page_id:
                    return restaurant
            
            # Method 3: Try array index (1-based to 0-based conversion)
            try:
                index = int(target_page_id) - 1
                if 0 <= index < len(page_data):
                    return page_data[index]
            except ValueError:
                pass
            
            # Method 4: Try direct array index (0-based)
            try:
                index = int(target_page_id)
                if 0 <= index < len(page_data):
                    return page_data[index]
            except ValueError:
                pass
            
            # Fallback: Return first restaurant with a warning
            if page_data:
                print(f"Warning: Could not find restaurant with pageID {target_page_id}, using first restaurant")
                return page_data[0]
            
            return None
            
        except Exception as e:
            print(f"Restaurant selection error: {e}")
            return None
    
    def _convert_to_wteg_schema(self, restaurant_data: Dict[str, Any], url: str) -> WTEGRestaurantData:
        """Convert raw restaurant data to WTEG schema."""
        # Extract and parse location
        location = self._parse_location(restaurant_data.get("location", ""))
        
        # Extract menu items
        menu_items = self._parse_menu_items(restaurant_data.get("menu", []))
        
        # Extract contact info
        contact_info = self._parse_contact_info(restaurant_data)
        
        # Extract services
        services = self._parse_services(restaurant_data)
        
        # Extract online ordering
        online_ordering = self._parse_online_ordering(restaurant_data)
        
        # Extract web links
        web_links = self._parse_web_links(restaurant_data)
        map_links = self._parse_map_links(restaurant_data)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(restaurant_data)
        
        # Create WTEG restaurant data
        wteg_restaurant = WTEGRestaurantData(
            location=location,
            cuisine=restaurant_data.get("cuisine", ""),
            brief_description=restaurant_data.get("description", restaurant_data.get("name", "")),
            menu_items=menu_items,
            click_to_call=contact_info,
            click_to_link=online_ordering,
            services_offered=services,
            click_for_website=web_links,
            click_for_map=map_links,
            source_url=url,
            extraction_timestamp=datetime.now().isoformat(),
            confidence_score=confidence,
            extraction_method="wteg_specific"
        )
        
        return wteg_restaurant
    
    def _parse_location(self, location_str: str) -> WTEGLocation:
        """Parse location string into WTEGLocation components."""
        location = WTEGLocation()
        
        if not location_str:
            return location
        
        # Try to parse common address formats
        # Example: "1420 SE Stark St, Portland, OR 97214"
        location_parts = location_str.split(", ")
        
        if len(location_parts) >= 1:
            location.street_address = location_parts[0].strip()
        
        if len(location_parts) >= 2:
            location.city = location_parts[1].strip()
        
        if len(location_parts) >= 3:
            # Try to parse "OR 97214" format
            state_zip = location_parts[2].strip().split()
            if len(state_zip) >= 1:
                location.state = state_zip[0].strip()
            if len(state_zip) >= 2:
                location.zip_code = state_zip[1].strip()
        
        return location
    
    def _parse_menu_items(self, menu_data: Any) -> List[WTEGMenuItem]:
        """Parse menu data into WTEGMenuItem objects."""
        menu_items = []
        
        if isinstance(menu_data, list):
            for item in menu_data:
                if isinstance(item, str):
                    menu_item = self._parse_menu_item_string(item)
                    menu_items.append(menu_item)
                elif isinstance(item, dict):
                    # Handle structured menu item
                    menu_item = WTEGMenuItem(
                        item_name=item.get("name", ""),
                        description=item.get("description", ""),
                        price=item.get("price", ""),
                        category=item.get("category", "Menu Items"),
                        dietary_info=item.get("dietary", ""),
                        preparation_notes=item.get("notes", "")
                    )
                    menu_items.append(menu_item)
        
        return menu_items
    
    def _parse_menu_item_string(self, item_str: str) -> WTEGMenuItem:
        """Parse menu item string in various formats."""
        # Enhanced CMS format: "Item Name: detailed description"
        if ": " in item_str and " - $" not in item_str:
            parts = item_str.split(": ", 1)  # Split only on first colon
            return WTEGMenuItem(
                item_name=parts[0].strip(),
                description=parts[1].strip() if len(parts) > 1 else "",
                price="",
                category="Menu Items"
            )
        
        # Traditional price format: "Item Name - $Price"
        elif " - " in item_str:
            parts = item_str.split(" - ")
            return WTEGMenuItem(
                item_name=parts[0].strip(),
                price=parts[1].strip() if len(parts) > 1 else "",
                description="",
                category="Menu Items"
            )
        
        # Simple item name only
        else:
            return WTEGMenuItem(
                item_name=item_str.strip(),
                description="",
                price="",
                category="Menu Items"
            )
    
    def _parse_contact_info(self, restaurant_data: Dict[str, Any]) -> WTEGContactInfo:
        """Parse contact information."""
        contact = WTEGContactInfo()
        
        phone = restaurant_data.get("phone", "")
        if phone:
            contact.primary_phone = phone
            contact.formatted_display = phone
            # Create clickable link (tel: format)
            clean_phone = re.sub(r'[^\d]', '', phone)
            if clean_phone:
                contact.clickable_link = f"tel:{clean_phone}"
        
        return contact
    
    def _parse_services(self, restaurant_data: Dict[str, Any]) -> WTEGServices:
        """Parse services offered."""
        services = WTEGServices()
        
        services_data = restaurant_data.get("services", {})
        if isinstance(services_data, dict):
            services.delivery_available = services_data.get("delivery", False)
            services.takeout_available = services_data.get("takeout", False)
            services.catering_available = services_data.get("catering", False)
            services.reservations_accepted = services_data.get("reservations", False)
            services.online_ordering = services_data.get("onlineOrdering", False)
            services.curbside_pickup = services_data.get("curbside", False)
            services.outdoor_seating = services_data.get("outdoor", False)
            services.private_dining = services_data.get("privateDining", False)
        
        return services
    
    def _parse_online_ordering(self, restaurant_data: Dict[str, Any]) -> List[WTEGOnlineOrdering]:
        """Parse online ordering platforms."""
        ordering_list = []
        
        ordering_data = restaurant_data.get("onlineOrdering", [])
        if isinstance(ordering_data, list):
            for platform in ordering_data:
                if isinstance(platform, dict):
                    ordering = WTEGOnlineOrdering(
                        platform_name=platform.get("platform", ""),
                        ordering_url=platform.get("url", ""),
                        platform_type=platform.get("type", ""),
                        delivery_fee=platform.get("fee", ""),
                        minimum_order=platform.get("minimum", ""),
                        estimated_delivery_time=platform.get("deliveryTime", "")
                    )
                    ordering_list.append(ordering)
        
        return ordering_list
    
    def _parse_web_links(self, restaurant_data: Dict[str, Any]) -> WTEGWebLinks:
        """Parse website and web links."""
        web_links = WTEGWebLinks()
        
        web_links.official_website = restaurant_data.get("website", "")
        web_links.menu_pdf_url = restaurant_data.get("menuPdf", "")
        
        # Parse social media links
        social_data = restaurant_data.get("social", [])
        if isinstance(social_data, list):
            web_links.social_media_links = social_data
        elif isinstance(social_data, str):
            web_links.social_media_links = [social_data]
        
        return web_links
    
    def _parse_map_links(self, restaurant_data: Dict[str, Any]) -> WTEGWebLinks:
        """Parse map and direction links."""
        map_links = WTEGWebLinks()
        
        map_links.map_url = restaurant_data.get("mapUrl", "")
        map_links.directions_url = restaurant_data.get("directionsUrl", "")
        
        return map_links
    
    def _calculate_confidence(self, restaurant_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on data completeness."""
        # Define core fields and their weights
        core_fields = {
            "name": 0.2,
            "description": 0.15,
            "location": 0.15,
            "cuisine": 0.1,
            "phone": 0.15,
            "menu": 0.15,
            "website": 0.1
        }
        
        confidence = 0.0
        
        for field, weight in core_fields.items():
            value = restaurant_data.get(field)
            if value:
                if isinstance(value, str) and value.strip():
                    confidence += weight
                elif isinstance(value, list) and len(value) > 0:
                    confidence += weight
                elif isinstance(value, dict) and value:
                    confidence += weight
        
        # Bonus for additional fields
        bonus_fields = ["services", "onlineOrdering", "social", "mapUrl"]
        bonus_weight = 0.025
        
        for field in bonus_fields:
            if restaurant_data.get(field):
                confidence += bonus_weight
        
        # Ensure confidence is between 0.0 and 1.0
        return min(1.0, max(0.0, confidence))
    
    def extract_multiple_restaurants(self, html_content: str, base_url: str, page_ids: List[str]) -> List[WTEGRestaurantData]:
        """Extract multiple restaurants for different page IDs."""
        results = []
        
        # Extract pageData once
        page_data = self._extract_pagedata_from_html(html_content)
        if not page_data:
            return results
        
        # Extract each restaurant
        for page_id in page_ids:
            url = base_url.replace('/1', f'/{page_id}')  # Simple URL modification
            restaurant_data = self._select_restaurant_by_url(page_data, url)
            
            if restaurant_data:
                wteg_restaurant = self._convert_to_wteg_schema(restaurant_data, url)
                results.append(wteg_restaurant)
        
        return results
    
    def validate_extraction_quality(self, wteg_data: WTEGRestaurantData) -> Dict[str, Any]:
        """Validate quality of WTEG extraction."""
        quality_report = {
            "is_complete": True,
            "missing_fields": [],
            "quality_score": 0.0,
            "issues": []
        }
        
        # Check required fields
        required_fields = [
            ("brief_description", wteg_data.brief_description),
            ("cuisine", wteg_data.cuisine),
            ("location.street_address", wteg_data.location.street_address if wteg_data.location else ""),
            ("click_to_call.primary_phone", wteg_data.click_to_call.primary_phone if wteg_data.click_to_call else "")
        ]
        
        missing_count = 0
        for field_name, field_value in required_fields:
            if not field_value or not str(field_value).strip():
                quality_report["missing_fields"].append(field_name)
                missing_count += 1
        
        # Check menu items
        if not wteg_data.menu_items or len(wteg_data.menu_items) == 0:
            quality_report["missing_fields"].append("menu_items")
            missing_count += 1
        
        # Calculate quality score
        total_fields = len(required_fields) + 1  # +1 for menu_items
        quality_report["quality_score"] = max(0.0, (total_fields - missing_count) / total_fields)
        
        # Mark as incomplete if missing critical fields
        if missing_count > 0:
            quality_report["is_complete"] = False
        
        # Add specific issues
        if not wteg_data.brief_description:
            quality_report["issues"].append("Missing restaurant description")
        if not wteg_data.menu_items:
            quality_report["issues"].append("Missing menu items - critical for RAG system")
        if not wteg_data.click_to_call or not wteg_data.click_to_call.primary_phone:
            quality_report["issues"].append("Missing phone number - needed for Click to Call")
        
        return quality_report