"""Traditional fallback extractor for when AI services are unavailable."""

import logging
import re
from typing import Dict, List, Any
import json

logger = logging.getLogger(__name__)


class TraditionalFallbackExtractor:
    """Traditional extraction methods as fallback when AI is unavailable."""

    def __init__(self):
        """Initialize traditional fallback extractor."""
        self.heuristic_patterns = {
            "menu_items": [
                r'<[^>]*class="[^"]*menu[^"]*"[^>]*>(.*?)</[^>]*>',
                r'<[^>]*class="[^"]*dish[^"]*"[^>]*>(.*?)</[^>]*>',
                r'<[^>]*class="[^"]*item[^"]*"[^>]*>(.*?)</[^>]*>',
            ],
            "prices": [
                r"\$\d+(?:\.\d{2})?",
                r"\d+\.\d{2}",
            ],
            "restaurant_name": [
                r"<title>(.*?)</title>",
                r"<h1[^>]*>(.*?)</h1>",
                r'<[^>]*class="[^"]*name[^"]*"[^>]*>(.*?)</[^>]*>',
            ],
        }

    def extract_traditional(self, content: str) -> Dict[str, Any]:
        """Extract content using traditional heuristic methods.

        Args:
            content: Content to extract from

        Returns:
            Traditional extraction results
        """
        try:
            result = {
                "extraction_method": "traditional_heuristics",
                "menu_items": self._extract_menu_items(content),
                "restaurant_info": self._extract_restaurant_info(content),
                "prices": self._extract_prices(content),
                "quality_score": 0.75,  # Traditional methods baseline
                "confidence": 0.7,
                "extraction_techniques": [
                    "heuristic_patterns",
                    "regex_matching",
                    "html_parsing",
                ],
            }

            # Adjust quality score based on extraction success
            result["quality_score"] = self._calculate_quality_score(result)

            return result

        except Exception as e:
            logger.error(f"Traditional extraction failed: {str(e)}")
            return self._minimal_extraction_result()

    def _extract_menu_items(self, content: str) -> List[Dict[str, Any]]:
        """Extract menu items using heuristic patterns."""
        items = []

        for pattern in self.heuristic_patterns["menu_items"]:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)

            for match in matches:
                item = self._parse_menu_item_text(match)
                if item and item not in items:
                    items.append(item)

        # Also try JSON-LD extraction
        jsonld_items = self._extract_jsonld_menu_items(content)
        items.extend(jsonld_items)

        # Remove duplicates
        seen = set()
        unique_items = []
        for item in items:
            item_key = item.get("name", "").lower()
            if item_key and item_key not in seen:
                seen.add(item_key)
                unique_items.append(item)

        return unique_items[:20]  # Limit to prevent overwhelming results

    def _parse_menu_item_text(self, html_text: str) -> Dict[str, Any]:
        """Parse menu item from HTML text."""
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", " ", html_text).strip()

        if len(text) < 5 or len(text) > 300:
            return None

        # Look for price in the text
        price_match = re.search(r"\$\d+(?:\.\d{2})?", text)
        price = price_match.group() if price_match else None

        # Extract name (text before price or first meaningful portion)
        if price:
            name_part = text.split(price)[0].strip()
        else:
            # Take first sentence or up to first period
            name_part = text.split(".")[0].strip()

        # Clean up name
        name = re.sub(r"^\W+|\W+$", "", name_part)

        if len(name) < 3:
            return None

        item = {
            "name": name,
            "source": "traditional_extraction",
            "extraction_confidence": 0.7,
        }

        if price:
            item["price"] = price

        # Try to extract description
        if price:
            description = text.split(price)[-1].strip()
        else:
            parts = text.split(".")
            if len(parts) > 1:
                description = ".".join(parts[1:]).strip()
            else:
                description = ""

        if description and len(description) > 10:
            item["description"] = description[:200]  # Limit description length

        return item

    def _extract_jsonld_menu_items(self, content: str) -> List[Dict[str, Any]]:
        """Extract menu items from JSON-LD structured data."""
        items = []

        # Find JSON-LD scripts
        jsonld_pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
        jsonld_matches = re.findall(
            jsonld_pattern, content, re.DOTALL | re.IGNORECASE
        )

        for match in jsonld_matches:
            try:
                data = json.loads(match.strip())

                # Handle both single objects and arrays
                if isinstance(data, list):
                    for item in data:
                        menu_items = self._extract_from_jsonld_object(item)
                        items.extend(menu_items)
                else:
                    menu_items = self._extract_from_jsonld_object(data)
                    items.extend(menu_items)

            except json.JSONDecodeError:
                continue

        return items

    def _extract_from_jsonld_object(
        self, obj: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract menu items from a JSON-LD object."""
        items = []

        # Look for Restaurant schema with hasMenu
        if obj.get("@type") == "Restaurant" and "hasMenu" in obj:
            menu = obj["hasMenu"]
            if isinstance(menu, dict) and "hasMenuSection" in menu:
                sections = menu["hasMenuSection"]
                if not isinstance(sections, list):
                    sections = [sections]

                for section in sections:
                    if "hasMenuItem" in section:
                        menu_items = section["hasMenuItem"]
                        if not isinstance(menu_items, list):
                            menu_items = [menu_items]

                        for item in menu_items:
                            extracted_item = self._parse_jsonld_menu_item(item)
                            if extracted_item:
                                items.append(extracted_item)

        # Look for direct MenuItem objects
        elif obj.get("@type") == "MenuItem":
            extracted_item = self._parse_jsonld_menu_item(obj)
            if extracted_item:
                items.append(extracted_item)

        return items

    def _parse_jsonld_menu_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a single JSON-LD menu item."""
        if not isinstance(item, dict):
            return None

        result = {"source": "jsonld_extraction", "extraction_confidence": 0.9}

        # Extract name
        if "name" in item:
            result["name"] = item["name"]

        # Extract description
        if "description" in item:
            result["description"] = item["description"]

        # Extract price
        if "offers" in item:
            offers = item["offers"]
            if isinstance(offers, dict) and "price" in offers:
                result["price"] = f"${offers['price']}"
            elif isinstance(offers, list) and offers:
                if "price" in offers[0]:
                    result["price"] = f"${offers[0]['price']}"

        return result if "name" in result else None

    def _extract_restaurant_info(self, content: str) -> Dict[str, Any]:
        """Extract basic restaurant information."""
        info = {}

        # Extract restaurant name
        for pattern in self.heuristic_patterns["restaurant_name"]:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                name = re.sub(r"<[^>]+>", "", match.group(1)).strip()
                if len(name) > 0 and len(name) < 100:
                    info["name"] = name
                    break

        # Extract phone number
        phone_pattern = r"(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})"
        phone_match = re.search(phone_pattern, content)
        if phone_match:
            info["phone"] = phone_match.group(1)

        # Extract address (simplified)
        address_pattern = (
            r"\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd)"
        )
        address_match = re.search(address_pattern, content, re.IGNORECASE)
        if address_match:
            info["address"] = address_match.group()

        return info

    def _extract_prices(self, content: str) -> List[str]:
        """Extract price information."""
        prices = []

        for pattern in self.heuristic_patterns["prices"]:
            matches = re.findall(pattern, content)
            prices.extend(matches)

        # Clean and deduplicate prices
        clean_prices = []
        for price in prices:
            if not price.startswith("$"):
                price = "$" + price
            if price not in clean_prices:
                clean_prices.append(price)

        return clean_prices[:10]  # Limit results

    def _calculate_quality_score(self, result: Dict[str, Any]) -> float:
        """Calculate quality score based on extraction success."""
        base_score = 0.6

        # Bonus for menu items found
        if result.get("menu_items"):
            base_score += min(len(result["menu_items"]) * 0.05, 0.2)

        # Bonus for restaurant info
        if result.get("restaurant_info"):
            base_score += min(len(result["restaurant_info"]) * 0.02, 0.1)

        # Bonus for prices found
        if result.get("prices"):
            base_score += min(len(result["prices"]) * 0.01, 0.1)

        return min(base_score, 0.85)  # Cap at 0.85 for traditional methods

    def _minimal_extraction_result(self) -> Dict[str, Any]:
        """Return minimal extraction result when everything fails."""
        return {
            "extraction_method": "minimal_fallback",
            "menu_items": [],
            "restaurant_info": {},
            "prices": [],
            "quality_score": 0.3,
            "confidence": 0.3,
            "error": "Traditional extraction methods failed",
            "extraction_techniques": ["minimal_parsing"],
        }
