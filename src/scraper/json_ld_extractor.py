"""JSON-LD data extraction engine for restaurant information."""
import json
import re
from typing import List, Dict, Any, Optional, Union
from bs4 import BeautifulSoup


class JSONLDExtractionResult:
    """Result of JSON-LD extraction with restaurant data."""

    def __init__(
        self,
        name: str = "",
        address: str = "",
        phone: str = "",
        hours: str = "",
        price_range: str = "",
        cuisine: str = "",
        menu_items: Optional[Dict[str, List[str]]] = None,
        social_media: Optional[List[str]] = None,
        confidence: str = "medium",
        source: str = "json-ld",
    ):
        self.name = name
        self.address = address
        self.phone = phone
        self.hours = hours
        self.price_range = price_range
        self.cuisine = cuisine
        self.menu_items = menu_items or {}
        self.social_media = social_media or []
        self.confidence = confidence
        self.source = source

    def is_valid(self) -> bool:
        """Check if extraction result has valid data."""
        return bool(self.name and self.name.strip())

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "hours": self.hours,
            "price_range": self.price_range,
            "cuisine": self.cuisine,
            "menu_items": self.menu_items,
            "social_media": self.social_media,
            "confidence": self.confidence,
            "source": self.source,
        }


class JSONLDExtractor:
    """Extracts restaurant data from JSON-LD structured markup."""

    RELEVANT_TYPES = {
        "restaurant",
        "foodestablishment",
        "localbusiness",
        "Restaurant",
        "FoodEstablishment",
        "LocalBusiness",
    }

    def extract_from_html(self, html_content: str) -> List[JSONLDExtractionResult]:
        """Extract restaurant data from HTML containing JSON-LD."""
        try:
            soup = BeautifulSoup(html_content, "html.parser")
        except Exception:
            return []

        results = []

        # Find all JSON-LD script tags
        json_ld_scripts = soup.find_all("script", type="application/ld+json")

        for script in json_ld_scripts:
            try:
                json_data = json.loads(script.string or script.text or "")

                # Handle both single objects and arrays
                if isinstance(json_data, list):
                    for item in json_data:
                        result = self.extract_restaurant_data(item)
                        if result and result.is_valid():
                            results.append(result)
                else:
                    result = self.extract_restaurant_data(json_data)
                    if result and result.is_valid():
                        results.append(result)

            except (json.JSONDecodeError, AttributeError):
                continue

        return results

    def extract_restaurant_data(
        self, json_data: Any
    ) -> Optional[JSONLDExtractionResult]:
        """Extract restaurant data from JSON-LD object."""
        if not isinstance(json_data, dict):
            return None

        # Check if this is a relevant schema type
        schema_type = json_data.get("@type", "")
        if not self.is_relevant_schema_type(schema_type):
            return None

        # Extract basic information
        name = json_data.get("name", "").strip()
        if not name:
            return None

        address = self._extract_address(json_data)
        phone = self._extract_phone(json_data)
        hours = self._extract_hours(json_data)
        price_range = self._extract_price_range(json_data)
        cuisine = self._extract_cuisine(json_data)
        menu_items = self._extract_menu(json_data)
        social_media = self._extract_social_media(json_data)

        # Calculate confidence based on data completeness
        confidence = self._calculate_confidence(json_data)

        return JSONLDExtractionResult(
            name=name,
            address=address,
            phone=phone,
            hours=hours,
            price_range=price_range,
            cuisine=cuisine,
            menu_items=menu_items,
            social_media=social_media,
            confidence=confidence,
            source="json-ld",
        )

    def is_relevant_schema_type(self, schema_type: str) -> bool:
        """Check if schema type is relevant for restaurant extraction."""
        if isinstance(schema_type, list):
            return any(
                t.lower() in {"restaurant", "foodestablishment", "localbusiness"}
                for t in schema_type
            )
        return schema_type.lower() in {
            "restaurant",
            "foodestablishment",
            "localbusiness",
        }

    def normalize_address(self, address_data: Union[str, Dict[str, Any]]) -> str:
        """Normalize address to standard format."""
        if isinstance(address_data, str):
            return address_data.strip()

        if isinstance(address_data, dict):
            parts = []

            # Street address
            street = address_data.get("streetAddress", "").strip()
            if street:
                parts.append(street)

            # City, State ZIP format
            city = address_data.get("addressLocality", "").strip()
            state = address_data.get("addressRegion", "").strip()
            postal_code = address_data.get("postalCode", "").strip()

            # Combine city, state, and zip in standard format with comma between city and state
            location_parts = []
            if city:
                location_parts.append(city)
            if state:
                if city:
                    location_parts.append(f", {state}")
                else:
                    location_parts.append(state)
            if postal_code:
                location_parts.append(f" {postal_code}")

            if location_parts:
                parts.append("".join(location_parts))

            return ", ".join(parts)

        return ""

    def normalize_hours(self, hours_data: Union[str, List[str]]) -> str:
        """Normalize operating hours to standard format."""
        if isinstance(hours_data, str):
            return hours_data.strip()

        if isinstance(hours_data, list):
            return ", ".join(str(h).strip() for h in hours_data if h)

        return ""

    def normalize_price_range(self, price_data: str) -> str:
        """Normalize price range to standard format."""
        if not price_data:
            return ""

        price_str = str(price_data).strip()

        # Return as-is for now - could add more normalization logic
        return price_str

    def _extract_address(self, json_data: Dict[str, Any]) -> str:
        """Extract and normalize address from JSON-LD."""
        address_data = json_data.get("address")
        if address_data:
            return self.normalize_address(address_data)
        return ""

    def _extract_phone(self, json_data: Dict[str, Any]) -> str:
        """Extract phone number from JSON-LD."""
        return json_data.get("telephone", "").strip()

    def _extract_hours(self, json_data: Dict[str, Any]) -> str:
        """Extract operating hours from JSON-LD."""
        hours_data = json_data.get("openingHours")
        if hours_data:
            return self.normalize_hours(hours_data)
        return ""

    def _extract_price_range(self, json_data: Dict[str, Any]) -> str:
        """Extract price range from JSON-LD."""
        price_data = json_data.get("priceRange")
        if price_data:
            return self.normalize_price_range(price_data)
        return ""

    def _extract_cuisine(self, json_data: Dict[str, Any]) -> str:
        """Extract cuisine type from JSON-LD."""
        cuisine = json_data.get("servesCuisine")
        if isinstance(cuisine, list):
            return ", ".join(str(c).strip() for c in cuisine if c)
        elif isinstance(cuisine, str):
            return cuisine.strip()
        return ""

    def _extract_menu(self, json_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract menu items from JSON-LD."""
        menu_items = {}

        menu_data = json_data.get("hasMenu")
        if not menu_data:
            return menu_items

        menu_sections = menu_data.get("hasMenuSection", [])
        if not isinstance(menu_sections, list):
            menu_sections = [menu_sections]

        for section in menu_sections:
            if not isinstance(section, dict):
                continue

            section_name = section.get("name", "Menu Items")
            menu_items[section_name] = []

            menu_items_list = section.get("hasMenuItem", [])
            if not isinstance(menu_items_list, list):
                menu_items_list = [menu_items_list]

            for item in menu_items_list:
                if isinstance(item, dict):
                    item_name = item.get("name", "").strip()
                    if item_name:
                        menu_items[section_name].append(item_name)

        return menu_items

    def _extract_social_media(self, json_data: Dict[str, Any]) -> List[str]:
        """Extract social media links from JSON-LD."""
        same_as = json_data.get("sameAs", [])
        if isinstance(same_as, str):
            return [same_as]
        elif isinstance(same_as, list):
            return [str(url).strip() for url in same_as if url]
        return []

    def _calculate_confidence(self, json_data: Dict[str, Any]) -> str:
        """Calculate confidence score based on data completeness."""
        required_fields = ["name"]
        important_fields = [
            "address",
            "telephone",
            "openingHours",
            "priceRange",
            "servesCuisine",
            "hasMenu",
        ]

        has_required = all(json_data.get(field) for field in required_fields)
        if not has_required:
            return "low"

        important_count = sum(1 for field in important_fields if json_data.get(field))

        # More lenient scoring for high confidence - JSON-LD is inherently structured
        if important_count >= 1:
            return "high"
        else:
            return "medium"
