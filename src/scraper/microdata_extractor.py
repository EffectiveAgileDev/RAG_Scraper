"""Microdata extraction engine for restaurant information."""
import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup


class MicrodataExtractionResult:
    """Result of microdata extraction with restaurant data."""

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
        source: str = "microdata",
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


class MicrodataExtractor:
    """Extracts restaurant data from microdata markup."""

    RELEVANT_ITEMTYPES = {
        "http://schema.org/restaurant",
        "http://schema.org/foodestablishment",
        "http://schema.org/localbusiness",
        "https://schema.org/restaurant",
        "https://schema.org/foodestablishment",
        "https://schema.org/localbusiness",
    }

    def extract_from_html(self, html_content: str) -> List[MicrodataExtractionResult]:
        """Extract restaurant data from HTML containing microdata."""
        if not html_content or not html_content.strip():
            return []

        try:
            soup = BeautifulSoup(html_content, "html.parser")
        except Exception:
            return []

        results = []

        # Find all elements with relevant itemscope and itemtype
        microdata_elements = soup.find_all(attrs={"itemscope": True, "itemtype": True})

        for element in microdata_elements:
            itemtype = element.get("itemtype", "").strip()

            if self.is_relevant_itemtype(itemtype):
                result = self.extract_restaurant_data(element)
                if result and result.is_valid():
                    results.append(result)

        return results

    def is_relevant_itemtype(self, itemtype: str) -> bool:
        """Check if itemtype is relevant for restaurant extraction."""
        return itemtype.lower() in self.RELEVANT_ITEMTYPES

    def extract_restaurant_data(self, element) -> Optional[MicrodataExtractionResult]:
        """Extract restaurant data from microdata element."""
        # Extract basic information
        name = self._extract_name(element)
        if not name:
            return None

        address = self._extract_address(element)
        phone = self._extract_phone(element)
        hours = self._extract_hours(element)
        price_range = self._extract_price_range(element)
        cuisine = self._extract_cuisine(element)
        menu_items = self._extract_menu(element)
        social_media = self._extract_social_media(element)

        # Calculate confidence based on data completeness
        confidence = self._calculate_confidence(
            {
                "name": name,
                "address": address,
                "phone": phone,
                "hours": hours,
                "price_range": price_range,
                "cuisine": cuisine,
                "menu_items": menu_items,
            }
        )

        return MicrodataExtractionResult(
            name=name,
            address=address,
            phone=phone,
            hours=hours,
            price_range=price_range,
            cuisine=cuisine,
            menu_items=menu_items,
            social_media=social_media,
            confidence=confidence,
            source="microdata",
        )

    def _extract_name(self, element) -> str:
        """Extract restaurant name from microdata."""
        name_elements = element.find_all(attrs={"itemprop": "name"})
        for name_elem in name_elements:
            name = name_elem.get_text(strip=True)
            if name:
                return name
        return ""

    def _extract_address(self, element) -> str:
        """Extract and normalize address from microdata."""
        # Look for nested address with PostalAddress itemtype
        address_elements = element.find_all(attrs={"itemprop": "address"})

        for addr_elem in address_elements:
            # Check if it's a nested PostalAddress
            if (
                addr_elem.get("itemtype")
                and "postaladdress" in addr_elem.get("itemtype", "").lower()
            ):
                return self._extract_postal_address(addr_elem)
            else:
                # Simple address string
                addr_text = addr_elem.get_text(strip=True)
                if addr_text:
                    return addr_text

        return ""

    def _extract_postal_address(self, address_element) -> str:
        """Extract address from PostalAddress microdata."""
        parts = []

        # Street address
        street_elem = address_element.find(attrs={"itemprop": "streetAddress"})
        if street_elem:
            street = street_elem.get_text(strip=True)
            if street:
                parts.append(street)

        # City, State ZIP format
        city_elem = address_element.find(attrs={"itemprop": "addressLocality"})
        state_elem = address_element.find(attrs={"itemprop": "addressRegion"})
        zip_elem = address_element.find(attrs={"itemprop": "postalCode"})

        location_parts = []
        if city_elem:
            city = city_elem.get_text(strip=True)
            if city:
                location_parts.append(city)

        if state_elem:
            state = state_elem.get_text(strip=True)
            if state:
                if location_parts:
                    location_parts.append(f", {state}")
                else:
                    location_parts.append(state)

        if zip_elem:
            zip_code = zip_elem.get_text(strip=True)
            if zip_code:
                location_parts.append(f" {zip_code}")

        if location_parts:
            parts.append("".join(location_parts))

        return ", ".join(parts)

    def _extract_phone(self, element) -> str:
        """Extract phone number from microdata."""
        phone_elements = element.find_all(attrs={"itemprop": "telephone"})
        for phone_elem in phone_elements:
            phone = phone_elem.get_text(strip=True)
            if phone:
                return phone
        return ""

    def _extract_hours(self, element) -> str:
        """Extract operating hours from microdata."""
        hours_elements = element.find_all(attrs={"itemprop": "openingHours"})
        hours_list = []

        for hours_elem in hours_elements:
            hours = hours_elem.get_text(strip=True)
            if hours:
                hours_list.append(hours)

        return ", ".join(hours_list)

    def _extract_price_range(self, element) -> str:
        """Extract price range from microdata."""
        price_elements = element.find_all(attrs={"itemprop": "priceRange"})
        for price_elem in price_elements:
            price = price_elem.get_text(strip=True)
            if price:
                return price
        return ""

    def _extract_cuisine(self, element) -> str:
        """Extract cuisine types from microdata."""
        cuisine_elements = element.find_all(attrs={"itemprop": "servesCuisine"})
        cuisines = []

        for cuisine_elem in cuisine_elements:
            cuisine = cuisine_elem.get_text(strip=True)
            if cuisine:
                cuisines.append(cuisine)

        return ", ".join(cuisines)

    def _extract_menu(self, element) -> Dict[str, List[str]]:
        """Extract menu items from microdata."""
        menu_items = {}

        # Find menu elements
        menu_elements = element.find_all(attrs={"itemprop": "hasMenu"})

        for menu_elem in menu_elements:
            # Find menu sections
            section_elements = menu_elem.find_all(attrs={"itemprop": "hasMenuSection"})

            for section_elem in section_elements:
                section_name_elem = section_elem.find(attrs={"itemprop": "name"})
                section_name = "Menu Items"  # Default section name

                if section_name_elem:
                    section_name = (
                        section_name_elem.get_text(strip=True) or "Menu Items"
                    )

                menu_items[section_name] = []

                # Find menu items in this section
                item_elements = section_elem.find_all(attrs={"itemprop": "hasMenuItem"})

                for item_elem in item_elements:
                    item_name_elem = item_elem.find(attrs={"itemprop": "name"})
                    if item_name_elem:
                        item_name = item_name_elem.get_text(strip=True)
                        if item_name:
                            menu_items[section_name].append(item_name)

        return menu_items

    def _extract_social_media(self, element) -> List[str]:
        """Extract social media links from microdata."""
        social_links = []

        # Look for sameAs properties
        same_as_elements = element.find_all(attrs={"itemprop": "sameAs"})

        for elem in same_as_elements:
            # Check for href attribute (link elements)
            href = elem.get("href", "").strip()
            if href:
                social_links.append(href)
            else:
                # Check for text content
                link = elem.get_text(strip=True)
                if link and (link.startswith("http") or link.startswith("https")):
                    social_links.append(link)

        return social_links

    def _calculate_confidence(self, data: Dict[str, Any]) -> str:
        """Calculate confidence score based on data completeness."""
        important_fields = [
            "address",
            "phone",
            "hours",
            "price_range",
            "cuisine",
            "menu_items",
        ]

        filled_count = sum(
            1
            for field in important_fields
            if data.get(field)
            and (
                isinstance(data[field], str)
                and data[field].strip()
                or isinstance(data[field], dict)
                and data[field]
                or isinstance(data[field], list)
                and data[field]
            )
        )

        # Microdata is structured, so we can be generous with confidence
        if filled_count >= 3:
            return "high"
        elif filled_count >= 1:
            return "high"  # Still high for microdata
        else:
            return "medium"
