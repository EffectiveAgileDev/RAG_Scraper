"""Heuristic pattern extraction engine for restaurant information."""
import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from dataclasses import dataclass
from ..common.extraction_base import BaseExtractionResult
from .pattern_matchers import (
    PhonePatternMatcher,
    AddressPatternMatcher,
    HoursPatternMatcher,
    RestaurantNameExtractor,
)


@dataclass
class HeuristicExtractionResult(BaseExtractionResult):
    """Result of heuristic extraction with restaurant data."""

    source: str = "heuristic"


class HeuristicExtractor:
    """Extracts restaurant data using heuristic patterns and text analysis."""

    def __init__(self):
        """Initialize pattern matchers."""
        self.phone_matcher = PhonePatternMatcher()
        self.address_matcher = AddressPatternMatcher()
        self.hours_matcher = HoursPatternMatcher()
        self.name_extractor = RestaurantNameExtractor()

    # Restaurant-specific keywords
    RESTAURANT_KEYWORDS = {
        "menu",
        "restaurant",
        "dining",
        "cuisine",
        "food",
        "chef",
        "kitchen",
        "appetizers",
        "entrees",
        "desserts",
        "reservations",
        "takeout",
        "delivery",
        "breakfast",
        "lunch",
        "dinner",
        "brunch",
        "catering",
        "bar",
        "grill",
        "bistro",
        "cafe",
        "diner",
        "eatery",
        "steakhouse",
        "pizzeria",
    }

    # Cuisine types
    CUISINE_KEYWORDS = {
        "italian",
        "mexican",
        "chinese",
        "japanese",
        "thai",
        "indian",
        "french",
        "american",
        "mediterranean",
        "greek",
        "korean",
        "vietnamese",
        "german",
        "spanish",
        "british",
        "russian",
        "middle eastern",
        "ethiopian",
        "cajun",
        "seafood",
        "steakhouse",
        "barbecue",
        "bbq",
        "pizza",
        "sushi",
        "tapas",
    }

    # Phone number patterns
    PHONE_PATTERNS = [
        r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",  # (503) 555-1234, 503-555-1234, etc.
        r"\+?1[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",  # +1-503-555-1234
    ]

    # Address patterns
    ADDRESS_PATTERNS = [
        r"\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Place|Pl)[\s,]+[A-Za-z\s]+,?\s*[A-Za-z]{2,}\s*\d{5}",
        r"\d+\s+[A-Za-z\s]+,\s*[A-Za-z\s]+,?\s*[A-Za-z]{2,}\s*\d{5}",
        r"(?:at|located at|address:?)\s*\d+\s+[A-Za-z\s,]+\d{5}",
    ]

    # Hours patterns
    HOURS_PATTERNS = [
        r"(?:Hours?|Open|Business Hours?):?\s*[^\n\.!]{5,80}(?:am|pm|AM|PM)",
        r"(?:Monday|Mon)[-–\s]+(?:Friday|Fri)[^\.!\n]{5,40}(?:am|pm|AM|PM)",
        r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[-–]\s*(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[^\.!\n]{5,40}(?:am|pm|AM|PM)",
        r"\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)\s*[-–]\s*\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)\s*(?:daily|every day)",
        r"(?:We\'?re\s*)?open\s+(?:Monday|Mon)\s+through\s+(?:Friday|Fri)\s+from\s+\d{1,2}\s+to\s+\d{1,2}",
        r"\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?\s*[-–]\s*\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?\s*(?:daily|every day|daily)",
    ]

    # Price range patterns
    PRICE_PATTERNS = [
        r"\$\d{1,3}[-–to\s]+\$?\d{1,3}",  # $15-$25, $15 to 25
        r"(?:Price\s*range|Entrees|Meals):?\s*\$\d{1,3}[-–to\s]+\$?\d{1,3}",
        r"(?:Average\s*cost|from):?\s*\$\d{1,3}[-–to\s]+\$?\d{1,3}",
    ]

    def extract_from_html(self, html_content: str) -> List[HeuristicExtractionResult]:
        """Extract restaurant data from HTML using heuristic patterns."""
        if not html_content or not html_content.strip():
            return []

        try:
            soup = BeautifulSoup(html_content, "html.parser")
        except Exception:
            return []

        # Check if this looks like a restaurant page
        if not self._is_restaurant_page(soup):
            return []

        # Extract data using pattern matchers
        extraction_data = self._extract_all_data(soup)

        # Validate that we have a name (minimum requirement)
        if not extraction_data.get("name"):
            return []

        # Calculate confidence and create result
        confidence = self._calculate_confidence(extraction_data)
        result = self._create_extraction_result(extraction_data, confidence)

        return [result]

    def _extract_all_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract all restaurant data using pattern matchers."""
        return {
            "name": self.name_extractor.extract(soup),
            "address": self.address_matcher.extract(soup),
            "phone": self.phone_matcher.extract(soup),
            "hours": self.hours_matcher.extract(soup),
            "price_range": self._extract_price_range(soup),
            "cuisine": self._extract_cuisine(soup),
            "menu_items": self._extract_menu_items(soup),
            "social_media": self._extract_social_media(soup),
        }

    def _create_extraction_result(
        self, data: Dict[str, Any], confidence: str
    ) -> HeuristicExtractionResult:
        """Create extraction result from data dictionary."""
        return HeuristicExtractionResult(
            name=data.get("name", ""),
            address=data.get("address", ""),
            phone=data.get("phone", ""),
            hours=data.get("hours", ""),
            price_range=data.get("price_range", ""),
            cuisine=data.get("cuisine", ""),
            menu_items=data.get("menu_items", {}),
            social_media=data.get("social_media", []),
            confidence=confidence,
            source="heuristic",
        )

    def _is_restaurant_page(self, soup: BeautifulSoup) -> bool:
        """Check if the page appears to be a restaurant website."""
        text_content = soup.get_text().lower()

        # Count restaurant-related keywords
        keyword_count = sum(
            1 for keyword in self.RESTAURANT_KEYWORDS if keyword in text_content
        )

        # Look for restaurant indicators in title
        title = soup.find("title")
        title_text = title.get_text().lower() if title else ""

        title_indicators = any(
            keyword in title_text
            for keyword in ["restaurant", "dining", "menu", "food"]
        )

        # Look for restaurant indicators in headings
        headings = soup.find_all(["h1", "h2", "h3"])
        heading_indicators = any("restaurant" in h.get_text().lower() for h in headings)

        # Look for restaurant indicators in meta tags
        meta_indicators = False
        meta_tags = soup.find_all("meta")
        for meta in meta_tags:
            content = meta.get("content", "").lower()
            if any(
                keyword in content
                for keyword in ["restaurant", "dining", "menu", "food"]
            ):
                meta_indicators = True
                break

        # More lenient criteria - accept if any strong indicator is present
        # For demonstration purposes, also try to extract from any page that has basic content
        has_content = len(text_content.strip()) > 100  # At least some content

        return (
            keyword_count >= 1
            or title_indicators
            or heading_indicators
            or meta_indicators
            or has_content
        )

    def _extract_name(self, soup: BeautifulSoup) -> str:
        """Extract restaurant name using various heuristics."""
        # Method 1: Try title tag
        title = soup.find("title")
        if title:
            title_text = title.get_text().strip()
            # Clean title text to extract just the restaurant name
            name = self._clean_restaurant_name(title_text)
            if name:
                return name

        # Method 2: Try h1 tags
        h1_tags = soup.find_all("h1")
        for h1 in h1_tags:
            text = h1.get_text().strip()
            if self._looks_like_restaurant_name(text):
                return text

        # Method 3: Try semantic class names
        name_classes = ["restaurant-name", "business-name", "site-title", "logo"]
        for class_name in name_classes:
            elements = soup.find_all(class_=re.compile(class_name, re.I))
            for elem in elements:
                text = elem.get_text().strip()
                if text and len(text) < 100:  # Reasonable name length
                    return text

        # Method 4: Try meta tags
        meta_title = soup.find("meta", property="og:title")
        if meta_title and meta_title.get("content"):
            return self._clean_restaurant_name(meta_title["content"])

        return ""

    def _clean_restaurant_name(self, title_text: str) -> str:
        """Clean title text to extract restaurant name."""
        # Remove common suffixes
        suffixes = [
            r"\s*[-|–]\s*.*$",  # Everything after dash
            r"\s*\|\s*.*$",  # Everything after pipe
            r"\s*-\s*.*$",  # Everything after hyphen
        ]

        cleaned = title_text
        for suffix_pattern in suffixes:
            cleaned = re.sub(suffix_pattern, "", cleaned, flags=re.IGNORECASE)

        return cleaned.strip()

    def _looks_like_restaurant_name(self, text: str) -> bool:
        """Check if text looks like a restaurant name."""
        if len(text) > 100:  # Too long
            return False

        # Should not contain common non-name phrases
        exclude_phrases = ["welcome", "home", "about", "contact", "menu only"]

        return not any(phrase in text.lower() for phrase in exclude_phrases)

    def _extract_phone(self, soup: BeautifulSoup) -> str:
        """Extract phone number using regex patterns."""
        text_content = soup.get_text()

        for pattern in self.PHONE_PATTERNS:
            matches = re.finditer(pattern, text_content)
            for match in matches:
                phone = match.group().strip()
                # Basic validation - should contain digits
                if re.search(r"\d{10}", re.sub(r"[^\d]", "", phone)):
                    return self.normalize_phone(phone)

        return ""

    def _extract_address(self, soup: BeautifulSoup) -> str:
        """Extract address using location patterns."""
        text_content = soup.get_text()

        for pattern in self.ADDRESS_PATTERNS:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                address = match.group().strip()
                # Clean up "at" or "located at" prefixes
                address = re.sub(
                    r"^(?:at|located at|address:?)\s*", "", address, flags=re.IGNORECASE
                ).strip()
                return self.normalize_address(address)

        # Try semantic class names
        address_classes = ["address", "location", "contact-address"]
        for class_name in address_classes:
            elements = soup.find_all(class_=re.compile(class_name, re.I))
            for elem in elements:
                text = elem.get_text().strip()
                if len(text) > 10 and len(text) < 200:  # Reasonable address length
                    return self.normalize_address(text)

        return ""

    def _extract_hours(self, soup: BeautifulSoup) -> str:
        """Extract operating hours using time patterns."""
        # First try to find hours in specific elements
        hours_selectors = [
            '[class*="hour"]',
            '[class*="time"]',
            '[class*="open"]',
            '[id*="hour"]',
            '[id*="time"]',
            '[id*="open"]',
        ]

        for selector in hours_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text().strip()
                if (
                    re.search(r"\d+\s*(?:am|pm)", text, re.IGNORECASE)
                    and len(text) < 200
                ):
                    return self.normalize_hours(text)

        # Then try patterns on individual elements instead of full text
        for elem in soup.find_all(["p", "div", "span", "td", "li"]):
            elem_text = elem.get_text().strip()
            if not elem_text:
                continue

            for pattern in self.HOURS_PATTERNS:
                matches = re.finditer(pattern, elem_text, re.IGNORECASE)
                for match in matches:
                    hours = match.group().strip()
                    # Clean up common prefixes
                    hours = re.sub(
                        r"^(?:Hours?|Open|Business Hours?):?\s*",
                        "",
                        hours,
                        flags=re.IGNORECASE,
                    ).strip()
                    if hours and len(hours) < 100:  # Reasonable length
                        return self.normalize_hours(hours)

        # Try semantic elements
        hours_classes = ["hours", "opening-hours", "business-hours"]
        for class_name in hours_classes:
            elements = soup.find_all(class_=re.compile(class_name, re.I))
            for elem in elements:
                text = elem.get_text().strip()
                if len(text) > 5 and len(text) < 200:
                    return self.normalize_hours(text)

        return ""

    def _extract_price_range(self, soup: BeautifulSoup) -> str:
        """Extract price range using currency patterns."""
        text_content = soup.get_text()

        for pattern in self.PRICE_PATTERNS:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                price = match.group().strip()
                return self.normalize_price_range(price)

        return ""

    def _extract_cuisine(self, soup: BeautifulSoup) -> str:
        """Extract cuisine types from content keywords."""
        text_content = soup.get_text().lower()
        found_cuisines = []

        for cuisine in self.CUISINE_KEYWORDS:
            if cuisine in text_content:
                found_cuisines.append(cuisine.title())

        return ", ".join(found_cuisines[:3])  # Limit to top 3

    def _extract_menu_items(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract menu items from section headers and content."""
        menu_items = {}

        # Enhanced menu section patterns for modern restaurant websites
        section_patterns = [
            # Traditional patterns
            r"appetizers?",
            r"entrees?",
            r"desserts?",
            r"beverages?",
            r"mains?",
            r"drinks?",
            r"cocktails?",
            # Modern/creative patterns
            r"shared plates?",
            r"small plates?",
            r"starters?",
            r"salads?",
            r"greens?",
            r"soups?",
            r"burgers?",
            r"sandwiches?",
            r"pizza",
            r"pasta",
            r"main plates?",
            r"brunch",
            r"lunch",
            r"dinner",
            r"sides?",
            r"kids?",
            r"wine",
            r"beer",
            r"favorites?",
            r"specials?",
            r"classics?",
        ]

        # Find all h2 and h3 headers (common for menu sections)
        all_headers = soup.find_all(["h2", "h3"])
        
        for header_elem in all_headers:
            header_text = header_elem.get_text().strip()
            
            # Check if this header matches any menu section pattern
            is_menu_section = False
            for pattern in section_patterns:
                if re.search(pattern, header_text, re.I):
                    is_menu_section = True
                    break
            
            # Also check for common menu-related words
            menu_keywords = ["menu", "food", "plate", "item", "dish"]
            if not is_menu_section:
                for keyword in menu_keywords:
                    if keyword in header_text.lower():
                        is_menu_section = True
                        break
            
            if is_menu_section:
                section_name = header_text.title()
                menu_items[section_name] = []
                
                # Look for menu items after this header
                current_elem = header_elem.find_next_sibling()
                item_count = 0
                
                while current_elem and item_count < 20:  # Increased limit for modern menus
                    # Stop at next section header
                    if current_elem.name in ["h1", "h2"] and current_elem != header_elem:
                        # Check if this is another menu section
                        next_header_text = current_elem.get_text().strip().lower()
                        if any(re.search(pattern, next_header_text, re.I) for pattern in section_patterns):
                            break
                        if any(keyword in next_header_text for keyword in menu_keywords):
                            break
                    
                    # Look for h3 elements (commonly used for individual menu items)
                    if current_elem.name == "h3":
                        item_text = current_elem.get_text().strip()
                        if item_text and len(item_text) < 100:
                            # Clean up the item name (remove prices, asterisks, etc.)
                            item_name = re.split(r"[*]?\s*\$", item_text)[0].strip()
                            item_name = re.sub(r"\*+$", "", item_name).strip()  # Remove trailing asterisks
                            
                            if item_name and len(item_name) > 2:  # Reasonable item name length
                                menu_items[section_name].append(item_name)
                                item_count += 1
                    
                    # Look inside div containers for h3 menu items (common pattern)
                    elif current_elem.name == "div":
                        inner_h3s = current_elem.find_all("h3")
                        for h3_elem in inner_h3s:
                            if item_count >= 20:
                                break
                            item_text = h3_elem.get_text().strip()
                            if item_text and len(item_text) < 100:
                                # Clean up the item name (remove prices, asterisks, etc.)
                                item_name = re.split(r"[*]?\s*\$", item_text)[0].strip()
                                item_name = re.sub(r"\*+$", "", item_name).strip()  # Remove trailing asterisks
                                
                                if item_name and len(item_name) > 2:  # Reasonable item name length
                                    menu_items[section_name].append(item_name)
                                    item_count += 1
                    
                    # Also check paragraphs for menu items (fallback)
                    elif current_elem.name == "p":
                        text = current_elem.get_text().strip()
                        if text and len(text) < 200 and "$" in text:  # Likely a menu item with price
                            # Extract item name (everything before price)
                            item_name = re.split(r"\$", text)[0].strip()
                            item_name = re.sub(r"\*+$", "", item_name).strip()
                            
                            if item_name and len(item_name) > 2 and len(item_name) < 80:
                                menu_items[section_name].append(item_name)
                                item_count += 1
                    
                    current_elem = current_elem.find_next_sibling()
                
                # Remove empty sections
                if not menu_items[section_name]:
                    del menu_items[section_name]

        return menu_items

    def _extract_social_media(self, soup: BeautifulSoup) -> List[str]:
        """Extract social media links from page content."""
        social_links = []

        # Look for social media URLs in links
        social_domains = ["facebook.com", "instagram.com", "twitter.com", "yelp.com"]

        links = soup.find_all("a", href=True)
        for link in links:
            href = link["href"]
            if any(domain in href for domain in social_domains):
                social_links.append(href)

        # Look for social media URLs in text
        text_content = soup.get_text()
        social_patterns = [
            r"https?://(?:www\.)?facebook\.com/[\w\.-]+",
            r"https?://(?:www\.)?instagram\.com/[\w\.-]+",
            r"https?://(?:www\.)?twitter\.com/[\w\.-]+",
        ]

        for pattern in social_patterns:
            matches = re.finditer(pattern, text_content)
            for match in matches:
                social_links.append(match.group())

        return list(set(social_links))  # Remove duplicates

    def _calculate_confidence(self, data: Dict[str, Any]) -> str:
        """Calculate confidence score based on extraction success."""
        fields = ["address", "phone", "hours", "price_range", "cuisine"]

        filled_count = sum(
            1
            for field in fields
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

        # Heuristic extraction is less reliable than structured data
        if filled_count >= 3:
            return "medium"  # Never high for heuristic
        elif filled_count >= 1:
            return "medium"
        else:
            return "low"

    def normalize_phone(self, phone: str) -> str:
        """Normalize phone number format."""
        # Remove all non-digits
        digits = re.sub(r"[^\d]", "", phone)

        # Format as (XXX) XXX-XXXX if 10 digits
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == "1":
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"

        return phone  # Return original if can't normalize

    def normalize_address(self, address: str) -> str:
        """Normalize address format."""
        return address.strip()

    def normalize_hours(self, hours: str) -> str:
        """Normalize hours format."""
        return hours.strip()

    def normalize_price_range(self, price_range: str) -> str:
        """Normalize price range format."""
        return price_range.strip()

    def is_restaurant_keyword(self, keyword: str) -> bool:
        """Check if keyword is restaurant-related."""
        return keyword.lower() in self.RESTAURANT_KEYWORDS
