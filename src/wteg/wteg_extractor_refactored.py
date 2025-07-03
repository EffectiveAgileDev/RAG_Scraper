"""WTEG-specific data extractor - Refactored for Clean Code.

Improved organization with smaller, focused methods and clear separation of concerns.
"""
import re
import json
from urllib.parse import unquote
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

from .wteg_schema_refactored import (
    WTEGRestaurantData, WTEGLocation, WTEGMenuItem, WTEGServices,
    WTEGContactInfo, WTEGOnlineOrdering, WTEGWebLinks
)
from .wteg_url_patterns import WTEGURLPatternParser
from .wteg_base import WTEGConstants, WTEGValidator


class WTEGJavaScriptParser:
    """Handles JavaScript pageData extraction."""
    
    # Regex patterns for different JavaScript formats
    PAGEDATA_PATTERNS = [
        re.compile(r'pageData = JSON\.parse\(decodeURIComponent\("([^"]+)"\)\)', re.DOTALL),
        re.compile(r'const pageData = JSON\.parse\(decodeURIComponent\("([^"]+)"\)\)', re.DOTALL),
        re.compile(r'var pageData = JSON\.parse\(decodeURIComponent\("([^"]+)"\)\)', re.DOTALL),
        re.compile(r'pageData\s*=\s*JSON\.parse\(decodeURIComponent\("([^"]+)"\)\)', re.DOTALL)
    ]
    
    def extract_pagedata(self, html_content: str) -> Optional[List[Dict[str, Any]]]:
        """Extract pageData array from HTML JavaScript."""
        for pattern in self.PAGEDATA_PATTERNS:
            match = pattern.search(html_content)
            if match:
                return self._decode_pagedata(match.group(1))
        return None
    
    def _decode_pagedata(self, encoded_data: str) -> Optional[List[Dict[str, Any]]]:
        """Decode and parse pageData JSON."""
        try:
            decoded_data = unquote(encoded_data)
            page_data = json.loads(decoded_data)
            
            if isinstance(page_data, list) and page_data:
                return page_data
            return None
            
        except (json.JSONDecodeError, IndexError, AttributeError) as e:
            print(f"PageData decoding error: {e}")
            return None


class WTEGRestaurantSelector:
    """Handles restaurant selection from pageData based on URL."""
    
    def __init__(self, url_parser: WTEGURLPatternParser):
        """Initialize with URL parser."""
        self.url_parser = url_parser
    
    def select_restaurant(self, page_data: List[Dict[str, Any]], url: str) -> Optional[Dict[str, Any]]:
        """Select the correct restaurant from pageData based on URL."""
        try:
            url_info = self.url_parser.parse_url(url)
            target_page_id = url_info["page_id"]
            
            # Try multiple selection strategies
            strategies = [
                self._select_by_exact_pageid,
                self._select_by_string_pageid,
                self._select_by_array_index_offset,
                self._select_by_array_index_direct
            ]
            
            for strategy in strategies:
                restaurant = strategy(page_data, target_page_id)
                if restaurant:
                    return restaurant
            
            # Fallback with warning
            if page_data:
                print(f"Warning: Could not find restaurant with pageID {target_page_id}, using first")
                return page_data[0]
            
            return None
            
        except Exception as e:
            print(f"Restaurant selection error: {e}")
            return None
    
    def _select_by_exact_pageid(self, page_data: List[Dict], page_id: str) -> Optional[Dict]:
        """Select by exact pageID match."""
        for restaurant in page_data:
            if restaurant.get("pageID") == page_id:
                return restaurant
        return None
    
    def _select_by_string_pageid(self, page_data: List[Dict], page_id: str) -> Optional[Dict]:
        """Select by string pageID match."""
        for restaurant in page_data:
            if str(restaurant.get("pageID", "")) == page_id:
                return restaurant
        return None
    
    def _select_by_array_index_offset(self, page_data: List[Dict], page_id: str) -> Optional[Dict]:
        """Select by array index with 1-based offset."""
        try:
            index = int(page_id) - 1
            if 0 <= index < len(page_data):
                return page_data[index]
        except ValueError:
            pass
        return None
    
    def _select_by_array_index_direct(self, page_data: List[Dict], page_id: str) -> Optional[Dict]:
        """Select by direct array index."""
        try:
            index = int(page_id)
            if 0 <= index < len(page_data):
                return page_data[index]
        except ValueError:
            pass
        return None


class WTEGDataMapper:
    """Maps raw JavaScript data to WTEG schema."""
    
    def map_to_schema(self, restaurant_data: Dict[str, Any], url: str) -> WTEGRestaurantData:
        """Convert raw restaurant data to WTEG schema."""
        return WTEGRestaurantData(
            location=self._map_location(restaurant_data),
            cuisine=restaurant_data.get("cuisine", ""),
            brief_description=restaurant_data.get("description", restaurant_data.get("name", "")),
            menu_items=self._map_menu_items(restaurant_data),
            click_to_call=self._map_contact_info(restaurant_data),
            click_to_link=self._map_online_ordering(restaurant_data),
            services_offered=self._map_services(restaurant_data),
            click_for_website=self._map_web_links(restaurant_data),
            click_for_map=self._map_map_links(restaurant_data),
            source_url=url,
            extraction_timestamp=datetime.now().isoformat(),
            confidence_score=self._calculate_confidence(restaurant_data),
            extraction_method=WTEGConstants.EXTRACTION_WTEG
        )
    
    def _map_location(self, data: Dict[str, Any]) -> WTEGLocation:
        """Map location data to WTEGLocation."""
        location_str = data.get("location", "")
        
        if not location_str:
            return WTEGLocation()
        
        # Parse address components
        parser = AddressParser()
        return parser.parse(location_str)
    
    def _map_menu_items(self, data: Dict[str, Any]) -> List[WTEGMenuItem]:
        """Map menu data to WTEGMenuItem list."""
        menu_data = data.get("menu", [])
        menu_items = []
        
        if isinstance(menu_data, list):
            parser = MenuItemParser()
            for item in menu_data:
                menu_item = parser.parse(item)
                if menu_item:
                    menu_items.append(menu_item)
        
        return menu_items
    
    def _map_contact_info(self, data: Dict[str, Any]) -> WTEGContactInfo:
        """Map contact data to WTEGContactInfo."""
        contact = WTEGContactInfo()
        
        phone = data.get("phone", "")
        if phone:
            contact.primary_phone = phone
            contact.formatted_display = phone
            contact.clickable_link = self._create_phone_link(phone)
        
        return contact
    
    def _create_phone_link(self, phone: str) -> str:
        """Create clickable tel: link from phone number."""
        digits = ''.join(c for c in phone if c.isdigit())
        return f"tel:{digits}" if digits else ""
    
    def _map_services(self, data: Dict[str, Any]) -> WTEGServices:
        """Map services data to WTEGServices."""
        services = WTEGServices()
        services_data = data.get("services", {})
        
        if isinstance(services_data, dict):
            service_mappings = {
                "delivery": "delivery_available",
                "takeout": "takeout_available",
                "catering": "catering_available",
                "reservations": "reservations_accepted",
                "onlineOrdering": "online_ordering",
                "curbside": "curbside_pickup",
                "outdoor": "outdoor_seating",
                "privateDining": "private_dining"
            }
            
            for source_key, target_attr in service_mappings.items():
                if source_key in services_data:
                    setattr(services, target_attr, bool(services_data[source_key]))
        
        return services
    
    def _map_online_ordering(self, data: Dict[str, Any]) -> List[WTEGOnlineOrdering]:
        """Map online ordering data to WTEGOnlineOrdering list."""
        ordering_list = []
        ordering_data = data.get("onlineOrdering", [])
        
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
    
    def _map_web_links(self, data: Dict[str, Any]) -> WTEGWebLinks:
        """Map web link data to WTEGWebLinks."""
        web_links = WTEGWebLinks()
        
        web_links.official_website = data.get("website", "")
        web_links.menu_pdf_url = data.get("menuPdf", "")
        
        # Handle social media
        social_data = data.get("social", [])
        if isinstance(social_data, list):
            web_links.social_media_links = social_data
        elif isinstance(social_data, str):
            web_links.social_media_links = [social_data]
        
        return web_links
    
    def _map_map_links(self, data: Dict[str, Any]) -> WTEGWebLinks:
        """Map location/map links to WTEGWebLinks."""
        return WTEGWebLinks(
            map_url=data.get("mapUrl", ""),
            directions_url=data.get("directionsUrl", "")
        )
    
    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """Calculate confidence score based on data completeness."""
        calculator = ConfidenceCalculator()
        return calculator.calculate(data)


class AddressParser:
    """Parses address strings into components."""
    
    def parse(self, address_str: str) -> WTEGLocation:
        """Parse address string into WTEGLocation."""
        location = WTEGLocation()
        
        if not address_str:
            return location
        
        # Split by comma for standard format
        parts = [p.strip() for p in address_str.split(",")]
        
        if len(parts) >= 1:
            location.street_address = parts[0]
        
        if len(parts) >= 2:
            location.city = parts[1]
        
        if len(parts) >= 3:
            # Parse state and zip
            state_zip = parts[2].strip()
            self._parse_state_zip(state_zip, location)
        
        return location
    
    def _parse_state_zip(self, state_zip: str, location: WTEGLocation) -> None:
        """Parse state and zip code from combined string."""
        parts = state_zip.split()
        if parts:
            location.state = parts[0]
            if len(parts) > 1:
                location.zip_code = parts[1]


class MenuItemParser:
    """Parses menu item data."""
    
    def parse(self, item_data: Any) -> Optional[WTEGMenuItem]:
        """Parse menu item from various formats."""
        if isinstance(item_data, str):
            return self._parse_string_item(item_data)
        elif isinstance(item_data, dict):
            return self._parse_dict_item(item_data)
        return None
    
    def _parse_string_item(self, item_str: str) -> WTEGMenuItem:
        """Parse menu item from string format (e.g., 'Item Name - $Price')."""
        parts = item_str.split(" - ")
        return WTEGMenuItem(
            item_name=parts[0].strip() if parts else item_str,
            price=parts[1].strip() if len(parts) > 1 else "",
            category="Menu Items"
        )
    
    def _parse_dict_item(self, item_dict: Dict[str, Any]) -> WTEGMenuItem:
        """Parse menu item from dictionary format."""
        return WTEGMenuItem(
            item_name=item_dict.get("name", ""),
            description=item_dict.get("description", ""),
            price=item_dict.get("price", ""),
            category=item_dict.get("category", "Menu Items"),
            dietary_info=item_dict.get("dietary", ""),
            preparation_notes=item_dict.get("notes", "")
        )


class ConfidenceCalculator:
    """Calculates confidence scores for extracted data."""
    
    def calculate(self, restaurant_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on data completeness."""
        score = 0.0
        
        # Check core fields
        for field, weight in WTEGConstants.FIELD_WEIGHTS.items():
            if self._has_value(restaurant_data.get(field)):
                score += weight
        
        # Bonus for additional fields
        bonus_fields = ["services", "onlineOrdering", "social", "mapUrl"]
        bonus_weight = 0.025
        
        for field in bonus_fields:
            if self._has_value(restaurant_data.get(field)):
                score += bonus_weight
        
        return min(1.0, max(0.0, score))
    
    def _has_value(self, value: Any) -> bool:
        """Check if a value is considered present."""
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, (list, dict)):
            return bool(value)
        return True


class WTEGExtractor:
    """Main extractor class - simplified and delegating to specialized components."""
    
    def __init__(self):
        """Initialize WTEG extractor with components."""
        self.url_parser = WTEGURLPatternParser()
        self.js_parser = WTEGJavaScriptParser()
        self.restaurant_selector = WTEGRestaurantSelector(self.url_parser)
        self.data_mapper = WTEGDataMapper()
    
    def extract_wteg_data(self, html_content: str, url: str) -> Optional[WTEGRestaurantData]:
        """Extract WTEG restaurant data from HTML content and URL."""
        try:
            # Validate URL
            if not self.url_parser.is_wteg_url(url):
                return None
            
            # Extract JavaScript data
            page_data = self.js_parser.extract_pagedata(html_content)
            if not page_data:
                return None
            
            # Select restaurant
            restaurant_data = self.restaurant_selector.select_restaurant(page_data, url)
            if not restaurant_data:
                return None
            
            # Map to schema
            return self.data_mapper.map_to_schema(restaurant_data, url)
            
        except Exception as e:
            print(f"WTEG extraction error for {url}: {e}")
            return None
    
    def extract_multiple_restaurants(
        self, 
        html_content: str, 
        base_url: str, 
        page_ids: List[str]
    ) -> List[WTEGRestaurantData]:
        """Extract multiple restaurants for different page IDs."""
        results = []
        
        # Extract pageData once
        page_data = self.js_parser.extract_pagedata(html_content)
        if not page_data:
            return results
        
        # Process each page ID
        for page_id in page_ids:
            url = self._build_url_for_page(base_url, page_id)
            restaurant_data = self.restaurant_selector.select_restaurant(page_data, url)
            
            if restaurant_data:
                wteg_restaurant = self.data_mapper.map_to_schema(restaurant_data, url)
                results.append(wteg_restaurant)
        
        return results
    
    def _build_url_for_page(self, base_url: str, page_id: str) -> str:
        """Build URL for specific page ID."""
        # Simple replacement - could be enhanced
        if '/1' in base_url:
            return base_url.replace('/1', f'/{page_id}')
        return f"{base_url}/{page_id}"
    
    def validate_extraction_quality(self, wteg_data: WTEGRestaurantData) -> Dict[str, Any]:
        """Validate quality of WTEG extraction."""
        validator = WTEGExtractionValidator()
        return validator.validate(wteg_data)


class WTEGExtractionValidator:
    """Validates WTEG extraction quality."""
    
    def validate(self, wteg_data: WTEGRestaurantData) -> Dict[str, Any]:
        """Validate extraction quality and completeness."""
        return {
            "is_complete": self._check_completeness(wteg_data),
            "missing_fields": self._find_missing_fields(wteg_data),
            "quality_score": self._calculate_quality_score(wteg_data),
            "issues": self._identify_issues(wteg_data)
        }
    
    def _check_completeness(self, data: WTEGRestaurantData) -> bool:
        """Check if all critical fields are present."""
        critical_fields = [
            data.brief_description,
            data.cuisine,
            data.location.street_address if data.location else None,
            data.click_to_call.primary_phone if data.click_to_call else None
        ]
        
        return all(field for field in critical_fields)
    
    def _find_missing_fields(self, data: WTEGRestaurantData) -> List[str]:
        """Find which required fields are missing."""
        missing = []
        
        field_checks = [
            ("brief_description", data.brief_description),
            ("cuisine", data.cuisine),
            ("location.street_address", data.location.street_address if data.location else ""),
            ("click_to_call.primary_phone", data.click_to_call.primary_phone if data.click_to_call else ""),
            ("menu_items", data.menu_items)
        ]
        
        for field_name, field_value in field_checks:
            if not field_value:
                missing.append(field_name)
        
        return missing
    
    def _calculate_quality_score(self, data: WTEGRestaurantData) -> float:
        """Calculate overall quality score."""
        return data.get_completeness_score()
    
    def _identify_issues(self, data: WTEGRestaurantData) -> List[str]:
        """Identify specific quality issues."""
        issues = []
        
        if not data.brief_description:
            issues.append("Missing restaurant description")
        
        if not data.menu_items:
            issues.append("Missing menu items - critical for RAG system")
        
        if not data.click_to_call or not data.click_to_call.primary_phone:
            issues.append("Missing phone number - needed for Click to Call")
        
        if data.confidence_score < WTEGConstants.MEDIUM_CONFIDENCE:
            issues.append(f"Low confidence score: {data.confidence_score:.2f}")
        
        return issues