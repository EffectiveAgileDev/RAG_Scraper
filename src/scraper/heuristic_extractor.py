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
try:
    from ..wteg.wteg_extractor import WTEGExtractor
except ImportError:
    WTEGExtractor = None


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
        self.wteg_extractor = WTEGExtractor() if WTEGExtractor else None

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

    def extract_from_html(self, html_content: str, url: Optional[str] = None) -> List[HeuristicExtractionResult]:
        """Extract restaurant data from HTML using heuristic patterns."""
        if not html_content or not html_content.strip():
            return []

        try:
            soup = BeautifulSoup(html_content, "html.parser")
        except Exception:
            return []

        # Check if this is a WTEG URL and use specialized extractor
        if url and 'mobimag.co/wteg' in url:
            wteg_result = self._extract_with_wteg(html_content, url)
            if wteg_result:
                return [wteg_result]

        # First try to extract from JavaScript pageData (for sites like mobimag.co)
        js_extraction_result = self._extract_from_javascript(html_content, url)
        if js_extraction_result:
            return [js_extraction_result]

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
            r"sushi",
            r"rolls?",
            r"sashimi",
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
            r"popular",
            r"dishes?",
            r"signature",
            # Added patterns for cheese/specialty sections
            r"cheese",
            r"salumi",
            r"selection",
            r"antipasti",
            r"antipasto",
            r"charcuterie",
            r"board",
            r"tasting",
            r"specialty",
            r"specialties",
            # Italian menu sections
            r"entrées?",
            r"entree",
            r"insalate",
            r"zuppe",
            r"panini",
            r"dolce",
            r"vino",
            r"bianco",
            r"rosso",
            r"pizze",
        ]

        # Find all h2, h3, h4, h5, h6 headers (expanded for menu sections and items)
        all_headers = soup.find_all(["h2", "h3", "h4", "h5", "h6"])
        
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
                
                # Special handling for WordPress - look for all food-menu divs in the section
                if header_elem.name == "h2":
                    # For h2 sections, collect all WordPress menu items until next h2
                    next_section_header = None
                    for next_header in header_elem.find_all_next(["h2"]):
                        next_text = next_header.get_text().strip().lower()
                        if any(re.search(pattern, next_text, re.I) for pattern in section_patterns) or \
                           any(keyword in next_text for keyword in menu_keywords):
                            next_section_header = next_header
                            break
                    
                    # Find all WordPress menu divs between this header and the next
                    wp_divs_in_section = []
                    current = header_elem
                    while current and current != next_section_header:
                        if (current.name == 'div' and 'food-menu-content-top-holder' in 
                            ' '.join(current.get('class', [])).lower()):
                            wp_divs_in_section.append(current)
                        current = current.find_next()
                    
                    
                    # Extract from WordPress divs
                    item_count = 0
                    for wp_div in wp_divs_in_section[:20]:  # Limit to prevent memory issues
                        cms_extracted = self._extract_cms_menu_items(wp_div, menu_items, section_name, item_count)
                        if cms_extracted > 0:
                            item_count += cms_extracted
                    
                    # Skip to next sibling processing if we found WordPress content
                    if wp_divs_in_section:
                        continue
                
                # Look for menu items after this header
                current_elem = header_elem.find_next_sibling()
                item_count = 0
                
                while current_elem and item_count < 50:  # Increased limit for WordPress menus
                    # Stop at next section header (h1, h2 are section breaks, but h3 can be menu items in WordPress)
                    if current_elem.name in ["h1", "h2"] and current_elem != header_elem:
                        # Check if this is another menu section
                        next_header_text = current_elem.get_text().strip().lower()
                        if any(re.search(pattern, next_header_text, re.I) for pattern in section_patterns):
                            break
                        if any(keyword in next_header_text for keyword in menu_keywords):
                            break
                    
                    # PRIORITY 1: Look inside div containers for CMS-specific menu items FIRST
                    # This ensures WordPress structures are processed before basic headers
                    if current_elem.name == "div":
                        cms_extracted = self._extract_cms_menu_items(current_elem, menu_items, section_name, item_count)
                        if cms_extracted > 0:
                            item_count += cms_extracted
                        current_elem = current_elem.find_next_sibling()
                        continue
                    
                    # PRIORITY 2: Look for h3, h4, h5, h6 elements (commonly used for individual menu items)
                    elif current_elem.name in ["h3", "h4", "h5", "h6"]:
                        item_text = current_elem.get_text().strip()
                        if item_text and len(item_text) < 100:
                            # Clean up the item name (remove prices, asterisks, etc.)
                            item_name = re.split(r"[*]?\s*\$", item_text)[0].strip()
                            item_name = re.sub(r"\*+$", "", item_name).strip()  # Remove trailing asterisks
                            
                            if item_name and len(item_name) > 2:  # Reasonable item name length
                                menu_items[section_name].append(item_name)
                                item_count += 1
                    
                    # Look for p elements with menu-like content
                    elif current_elem.name == "p":
                        item_text = current_elem.get_text().strip()
                        if item_text and len(item_text) < 500:  # Increased limit for descriptive content
                            
                            # Enhanced menu detection patterns for rich descriptions
                            menu_indicators = [
                                'burger', 'fries', 'drink', 'sandwich', '$', 'menu', 'special',
                                # Food descriptors that indicate menu content
                                'cheese', 'milk', 'sauce', 'bread', 'pasta', 'meat', 'beef', 'chicken',
                                'salad', 'soup', 'rice', 'vegetable', 'fresh', 'grilled', 'roasted',
                                'served with', 'topped with', 'marinated', 'seasoned', 'organic',
                                # Cooking methods and descriptions common in menus
                                'braised', 'sautéed', 'baked', 'fried', 'steamed', 'poached',
                                # Italian food terms for restaurants like Piattino
                                'alla', 'con', 'del', 'della', 'di', 'parmigiano', 'pecorino',
                                'prosciutto', 'mozzarella', 'basil', 'tomato', 'garlic'
                            ]
                            
                            # Check for colon-separated menu items (common format: "Item: description")
                            has_colon_format = ':' in item_text and not item_text.startswith('http')
                            has_menu_indicators = any(indicator in item_text.lower() for indicator in menu_indicators)
                            
                            # In menu section context, be more lenient - capture most paragraph content
                            # as it's likely a menu item if we're already in a recognized menu section
                            is_likely_menu_item = (has_colon_format or has_menu_indicators or 
                                                  ('-' in item_text and len(item_text.split()) >= 2))
                            
                            if is_likely_menu_item:
                                # Handle different content formats
                                if '$' in item_text:
                                    # Item with price - remove price but keep full description
                                    item_content = re.split(r"[*]?\s*\$", item_text)[0].strip()
                                else:
                                    # Item without price - keep full text
                                    item_content = item_text
                                
                                # Clean up asterisks and extra whitespace
                                item_content = re.sub(r"\*+$", "", item_content).strip()
                                
                                # Validate item content quality
                                if (item_content and len(item_content) > 5 and 
                                    len(item_content) < 300 and  # Reasonable upper limit
                                    not item_content.lower().startswith(('copyright', 'all rights', 'terms', 'privacy'))):
                                    
                                    menu_items[section_name].append(item_content)
                                    item_count += 1
                    
                    # PRIORITY 3: Try remaining div containers for CMS patterns that weren't caught in PRIORITY 1
                    elif current_elem.name == "div":
                        cms_extracted = self._extract_cms_menu_items(current_elem, menu_items, section_name, item_count)
                        if cms_extracted > 0:
                            item_count += cms_extracted
                        
                        # Look for traditional header elements within divs
                        inner_headers = current_elem.find_all(["h3", "h4", "h5", "h6"])
                        for header_elem in inner_headers:
                            if item_count >= 20:
                                break
                            item_text = header_elem.get_text().strip()
                            if item_text and len(item_text) < 100:
                                
                                # For WordPress, check if the next sibling has descriptive content
                                next_elem = header_elem.find_next_sibling()
                                description = ""
                                
                                if next_elem:
                                    # Check if next element contains description
                                    next_text = next_elem.get_text().strip()
                                    if (next_text and len(next_text) > 20 and 
                                        (':' in next_text or any(food_word in next_text.lower() 
                                                               for food_word in ['milk', 'cheese', 'flavor', 'aroma', 'fresh']))):
                                        description = next_text
                                
                                # Clean up the item name (remove prices, asterisks, etc.)
                                item_name = re.split(r"[*]?\s*\$", item_text)[0].strip()
                                item_name = re.sub(r"\*+$", "", item_name).strip()  # Remove trailing asterisks
                                
                                if item_name and len(item_name) > 2:  # Reasonable item name length
                                    # If we found a description, combine them
                                    if description:
                                        # Remove price from description too
                                        if '$' in description:
                                            description = re.split(r"[*]?\s*\$", description)[0].strip()
                                        
                                        full_item = f"{item_name}: {description}" if ':' not in description else description
                                        menu_items[section_name].append(full_item)
                                    else:
                                        menu_items[section_name].append(item_name)
                                    item_count += 1
                    
                    
                    current_elem = current_elem.find_next_sibling()
                
                # Remove empty sections
                if not menu_items[section_name]:
                    del menu_items[section_name]

        # Fallback: If no menu sections found, look for standalone h4, h5, h6 elements with prices
        if not menu_items:
            print("DEBUG: No menu sections found, trying fallback extraction of standalone menu items...")
            standalone_items = []
            
            # Look for any h4, h5, h6 elements that contain price indicators
            potential_menu_items = soup.find_all(["h4", "h5", "h6"])
            for header in potential_menu_items:
                item_text = header.get_text().strip()
                # Look for price patterns or food-related keywords
                if (item_text and len(item_text) < 100 and 
                    ('$' in item_text or 
                     any(food_word in item_text.lower() for food_word in 
                         ['pizza', 'pasta', 'burger', 'salad', 'sandwich', 'soup', 'chicken', 'beef', 'fish', 'pork']))):
                    
                    # Clean up the item name (remove prices, asterisks, etc.)
                    item_name = re.split(r"[*]?\s*\$", item_text)[0].strip()
                    item_name = re.sub(r"\*+$", "", item_name).strip()
                    
                    if item_name and len(item_name) > 2 and len(item_name) < 80:
                        standalone_items.append(item_name)
                        if len(standalone_items) >= 10:  # Reduced limit to allow CMS fallback to run
                            break
            
            # Also look for CMS food menu structures (always try for better content)
            print("DEBUG: Trying CMS food menu structure extraction...")
            
            # Look for CMS-specific menu containers in fallback
            cms_patterns = [
                # WordPress
                {'selector': 'div', 'class_contains': ['food-menu-content-top-holder'], 'name': 'WordPress'},
                # Squarespace
                {'selector': 'div', 'class_contains': ['sqs-block-content', 'menu-item'], 'name': 'Squarespace'},
                # Wix
                {'selector': 'div', 'class_contains': ['wix-rich-text'], 'name': 'Wix'},
                # BentoBox
                {'selector': 'div', 'class_contains': ['bento-menu', 'bento-item'], 'name': 'BentoBox'},
                # Generic semantic
                {'selector': 'div', 'class_contains': ['menu-item', 'dish-item', 'food-item'], 'name': 'Semantic'},
            ]
            
            for pattern in cms_patterns:
                if len(standalone_items) >= 50:
                    break  # Found enough items
                    
                cms_items = []
                for class_keyword in pattern['class_contains']:
                    items = soup.find_all(pattern['selector'], 
                                        class_=lambda x: x and class_keyword in ' '.join(x).lower())
                    cms_items.extend(items)
                
                if cms_items:
                    print(f"DEBUG: Found {len(cms_items)} {pattern['name']} menu items in fallback")
                    
                    for item_div in cms_items:
                        extracted_text = None
                        
                        if pattern['name'] == 'WordPress':
                            # WordPress-specific extraction
                            title_holder = item_div.find(class_='food-menu-content-title-holder')
                            desc_div = item_div.find_next_sibling(class_='food-menu-desc')
                            
                            if title_holder and desc_div:
                                title_elem = title_holder.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                                if title_elem:
                                    title_text = title_elem.get_text().strip()
                                    desc_text = desc_div.get_text().strip()
                                    if title_text and desc_text and len(desc_text) > 10:
                                        extracted_text = f"{title_text}: {desc_text}"
                            
                        elif pattern['name'] == 'Squarespace':
                            # Squarespace-specific extraction
                            content = item_div.get_text().strip()
                            if ':' in content and len(content) > 20 and len(content) < 300:
                                extracted_text = content
                        
                        elif pattern['name'] == 'Wix':
                            # Wix-specific extraction
                            rich_content = item_div.get_text().strip()
                            if ':' in rich_content and len(rich_content) > 20:
                                extracted_text = rich_content
                        
                        else:
                            # Generic extraction for BentoBox and Semantic
                            content = item_div.get_text().strip()
                            if (':' in content and len(content) > 20 and len(content) < 300 and
                                any(food_word in content.lower() for food_word in 
                                    ['cheese', 'fresh', 'served', 'grilled', 'sauce'])):
                                extracted_text = content
                            
                        if extracted_text:
                            # Clean up
                            if '$' in extracted_text:
                                extracted_text = re.split(r"[*]?\s*\$", extracted_text)[0].strip()
                            extracted_text = re.sub(r"\*+$", "", extracted_text).strip()
                            
                            if (len(extracted_text) > 10 and len(extracted_text) < 400 and
                                not extracted_text.lower().startswith(('copyright', 'all rights', 'terms'))):
                                standalone_items.append(extracted_text)
                                if len(standalone_items) >= 50:
                                    break
                
                # Fallback to paragraph extraction if CMS structures didn't work
                if len(standalone_items) < 10:
                    print("DEBUG: Trying paragraph fallback for descriptive menu content...")
                    potential_paragraphs = soup.find_all("p")
                    for para in potential_paragraphs:
                        para_text = para.get_text().strip()
                        
                        # Check for colon-separated content or food-related terms
                        if (para_text and len(para_text) < 400 and len(para_text) > 10):
                            has_colon = ':' in para_text and not para_text.startswith('http')
                            has_food_terms = any(term in para_text.lower() for term in [
                                'cheese', 'milk', 'sauce', 'pasta', 'meat', 'beef', 'chicken',
                                'salad', 'fresh', 'grilled', 'roasted', 'organic', 'basil',
                                'tomato', 'garlic', 'bread', 'wine', 'served'
                            ])
                            
                            if has_colon or has_food_terms:
                                # Clean up content (remove price if present)
                                if '$' in para_text:
                                    content = re.split(r"[*]?\s*\$", para_text)[0].strip()
                                else:
                                    content = para_text
                                    
                                content = re.sub(r"\*+$", "", content).strip()
                                
                                if (content and len(content) > 10 and 
                                    not content.lower().startswith(('copyright', 'all rights', 'terms', 'privacy'))):
                                    standalone_items.append(content)
                                    if len(standalone_items) >= 30:  # More items for descriptive content
                                        break
            
            if standalone_items:
                print(f"DEBUG: Found {len(standalone_items)} standalone menu items")
                menu_items["Menu Items"] = standalone_items
            else:
                print("DEBUG: No standalone menu items found either")

        
        return menu_items

    def _extract_cms_menu_items(self, current_elem, menu_items: Dict[str, List[str]], section_name: str, item_count: int) -> int:
        """Extract menu items from CMS-specific div structures. Returns number of items extracted."""
        items_extracted = 0
        
        # Check for CMS and platform-specific menu classes
        div_classes = current_elem.get('class', [])
        class_string = ' '.join(div_classes).lower()
        
        # WordPress patterns - be more specific to avoid false positives
        is_wp_food_menu = any(keyword in class_string for keyword in 
                           ['food-menu', 'food-menu-item', 'menu-content', 'food-dish', 'item-title', 'item-description'])
        
        # Squarespace patterns
        is_squarespace_menu = any(keyword in class_string for keyword in 
                               ['sqs-block-content', 'menu-item-title', 'menu-item-description', 'menu-section'])
        
        # Wix patterns  
        is_wix_menu = any(keyword in class_string for keyword in 
                        ['wix-rich-text', 'txtNew', 'wix-menu-item'])
        
        # BentoBox patterns
        is_bentobox_menu = any(keyword in class_string for keyword in 
                             ['bento-menu', 'bento-item', 'menu-category'])
        
        # Bootstrap-based restaurant templates - simplified to avoid false negatives
        is_bootstrap_menu = any(keyword in class_string for keyword in ['card', 'list-group-item', 'media', 'media-heading', 'media-body'])
        
        # Generic semantic menu patterns
        is_semantic_menu = any(keyword in class_string for keyword in 
                             ['menu-category', 'menu-section', 'dish-item', 'food-item', 'product-title'])
        
        is_cms_food_menu = (is_wp_food_menu or is_squarespace_menu or is_wix_menu or 
                          is_bentobox_menu or is_bootstrap_menu or is_semantic_menu)
        
        if is_cms_food_menu:
            extracted_item = None
            
            # WordPress patterns
            if is_wp_food_menu:
                # FIRST: Check for special Piattino WordPress structure
                if 'food-menu-content-top-holder' in class_string:
                    title_holder = current_elem.find(class_='food-menu-content-title-holder')
                    # Description is a sibling of the entire content-top-holder div
                    desc_sibling = current_elem.find_next_sibling(class_='food-menu-desc')
                    
                    if title_holder:
                        title_elem = title_holder.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                        if title_elem:
                            title_text = title_elem.get_text().strip()
                            
                            if desc_sibling:
                                desc_text = desc_sibling.get_text().strip()
                                if desc_text and len(desc_text) > 10:
                                    extracted_item = f"{title_text}: {desc_text}"
                            else:
                                # Fallback - just use title
                                extracted_item = title_text
                                
                # FALLBACK: Standard WordPress food menu plugin pattern
                else:
                    title_elem = current_elem.find(class_=lambda x: x and 'title' in str(x).lower())
                    desc_elem = current_elem.find(class_=lambda x: x and any(word in str(x).lower() 
                                                 for word in ['desc', 'content', 'text', 'detail']))
                    
                    if title_elem and desc_elem:
                        title_text = title_elem.get_text().strip()
                        desc_text = desc_elem.get_text().strip()
                        if title_text and desc_text and len(desc_text) > 10:
                            extracted_item = f"{title_text}: {desc_text}"
            
            # Squarespace patterns
            elif is_squarespace_menu:
                title_elem = current_elem.find(class_=lambda x: x and 'menu-item-title' in str(x).lower())
                desc_elem = current_elem.find(class_=lambda x: x and 'menu-item-description' in str(x).lower())
                
                if not title_elem:  # Fallback to content within sqs-block-content
                    # Check if the current element itself contains colon-separated content
                    content_text = current_elem.get_text().strip()
                    if ':' in content_text and len(content_text) > 20:
                        extracted_item = content_text
                elif title_elem and desc_elem:
                    title_text = title_elem.get_text().strip()
                    desc_text = desc_elem.get_text().strip()
                    if title_text and desc_text:
                        extracted_item = f"{title_text}: {desc_text}"
            
            # Wix patterns
            elif is_wix_menu:
                # Check if current element itself is the Wix container
                text_content = current_elem.get_text().strip()
                if ':' in text_content and len(text_content) > 20:
                    extracted_item = text_content
            
            # BentoBox patterns
            elif is_bentobox_menu:
                item_name = current_elem.find(class_=lambda x: x and ('item-name' in str(x).lower() or 
                                                                     ('item' in str(x).lower() and 'name' in str(x).lower())))
                item_desc = current_elem.find(class_=lambda x: x and ('item-desc' in str(x).lower() or 
                                                                      'item-description' in str(x).lower() or
                                                                      'desc' in str(x).lower()))
                
                if item_name and item_desc:
                    name_text = item_name.get_text().strip()
                    desc_text = item_desc.get_text().strip()
                    if name_text and desc_text:
                        extracted_item = f"{name_text}: {desc_text}"
            
            # Bootstrap/semantic patterns
            elif is_bootstrap_menu or is_semantic_menu:
                # Look for title and body within card/list-item
                title_selectors = ['.card-title', '.list-group-item-heading', '.media-heading', 
                                  '.dish-name', '.item-name', '.product-title',
                                  'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
                body_selectors = ['.card-text', '.list-group-item-text', '.media-body', 
                                 '.dish-description', '.item-description', '.product-description',
                                 'p', 'span', 'div']
                
                title_elem = None
                body_elem = None
                
                for selector in title_selectors:
                    title_elem = current_elem.select_one(selector)
                    if title_elem:
                        break
                
                for selector in body_selectors:
                    body_elem = current_elem.select_one(selector)
                    if body_elem:
                        break
                
                if title_elem and body_elem:
                    title_text = title_elem.get_text().strip()
                    body_text = body_elem.get_text().strip()
                    if title_text and body_text and len(body_text) > 10:
                        extracted_item = f"{title_text}: {body_text}"
            
            # Clean up and add the extracted item
            if extracted_item:
                # Remove price if present
                if '$' in extracted_item:
                    extracted_item = re.split(r"[*]?\s*\$", extracted_item)[0].strip()
                
                # Clean up and validate
                extracted_item = re.sub(r"\*+$", "", extracted_item).strip()
                
                if (len(extracted_item) > 10 and len(extracted_item) < 400 and
                    not extracted_item.lower().startswith(('copyright', 'all rights', 'terms', 'privacy'))):
                    
                    menu_items[section_name].append(extracted_item)
                    items_extracted = 1
        
        return items_extracted

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

        # Heuristic extraction can be quite reliable with good data
        if filled_count >= 4:
            return "high"   # High confidence when we have most fields
        elif filled_count >= 3:
            return "medium"
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
        # First, clean up the address
        address = address.strip()
        
        # Fix common spacing issues
        # Add space before city name (e.g., "AvenuePortland" -> "Avenue Portland")
        address = re.sub(r'([a-z])([A-Z])', r'\1 \2', address)
        
        # Add space before state abbreviation (e.g., "Portland, OR97232" -> "Portland, OR 97232")
        address = re.sub(r',\s*([A-Z]{2})(\d{5})', r', \1 \2', address)
        
        # Ensure proper spacing after commas
        address = re.sub(r',\s*', ', ', address)
        
        # Clean up multiple spaces
        address = re.sub(r'\s+', ' ', address)
        
        return address.strip()

    def normalize_hours(self, hours: str) -> str:
        """Normalize hours format."""
        hours = hours.strip()
        
        # Fix common truncation issues where first letter is missing or prefix remains
        if hours and hours.startswith('Hours'):
            # Remove "Hours" prefix if present
            hours = re.sub(r'^Hours\s*', '', hours)
        
        # Clean up spacing around day ranges and times
        hours = re.sub(r'([A-Za-z]+day)\s*-\s*([A-Za-z]+day)', r'\1-\2', hours)
        hours = re.sub(r'(\d+:\d+)(am|pm)\s*-\s*(\d+:\d+)(am|pm)', r'\1\2-\3\4', hours)
        
        return hours.strip()

    def normalize_price_range(self, price_range: str) -> str:
        """Normalize price range format."""
        return price_range.strip()

    def is_restaurant_keyword(self, keyword: str) -> bool:
        """Check if keyword is restaurant-related."""
        return keyword.lower() in self.RESTAURANT_KEYWORDS

    def _extract_from_javascript(self, html_content: str, url: Optional[str] = None) -> Optional[HeuristicExtractionResult]:
        """Extract restaurant data from JavaScript pageData (for sites like mobimag.co)."""
        try:
            # Look for pageData in JavaScript
            import json
            from urllib.parse import unquote
            
            # Pattern to find pageData JSON
            pattern = r'pageData = JSON\.parse\(decodeURIComponent\("([^"]+)"\)\)'
            match = re.search(pattern, html_content)
            
            if not match:
                return None
            
            # Decode and parse the JSON data
            encoded_data = match.group(1)
            decoded_data = unquote(encoded_data)
            page_data = json.loads(decoded_data)
            
            if not isinstance(page_data, list) or len(page_data) == 0:
                return None
            
            # Extract restaurant ID from URL if provided
            restaurant_index = 0  # Default to first restaurant
            if url:
                restaurant_id = self._extract_restaurant_id_from_url(url)
                if restaurant_id:
                    # Find the restaurant by pageID or array index
                    restaurant_index = self._find_restaurant_index(page_data, restaurant_id)
            
            # Get the specific restaurant data
            if restaurant_index < len(page_data):
                restaurant_data = page_data[restaurant_index]
                
                # Extract data from the JavaScript object
                extraction_data = self._extract_data_from_js_object(restaurant_data)
                
                if extraction_data.get("name"):
                    # Calculate confidence - higher for structured JS data
                    confidence = "high"
                    return self._create_extraction_result(extraction_data, confidence)
            
            return None
            
        except Exception as e:
            # Log error but continue with normal extraction
            print(f"JavaScript extraction error: {e}")
            return None

    def _extract_restaurant_id_from_url(self, url: str) -> Optional[str]:
        """Extract restaurant ID from URL path."""
        try:
            path_parts = url.split('/')
            if path_parts and path_parts[-1].isdigit():
                return path_parts[-1]
            return None
        except Exception:
            return None

    def _find_restaurant_index(self, page_data: List[Dict], restaurant_id: str) -> int:
        """Find restaurant index in pageData array."""
        try:
            # Method 1: Try to find by pageID field
            for i, item in enumerate(page_data):
                if isinstance(item, dict):
                    if str(item.get("pageID", "")) == restaurant_id:
                        return i
            
            # Method 2: Try array index (1-based to 0-based conversion)
            try:
                index = int(restaurant_id) - 1
                if 0 <= index < len(page_data):
                    return index
            except ValueError:
                pass
            
            # Method 3: Try direct array index
            try:
                index = int(restaurant_id)
                if 0 <= index < len(page_data):
                    return index
            except ValueError:
                pass
            
            # Default to first item
            return 0
            
        except Exception:
            return 0

    def _extract_data_from_js_object(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract restaurant data from JavaScript object."""
        extraction_data = {}
        
        # Map JavaScript fields to our data structure
        field_mappings = {
            "name": ["name", "restaurantName", "businessName", "title"],
            "address": ["address", "location", "addr", "street"],
            "phone": ["phone", "telephone", "phoneNumber", "tel"],
            "hours": ["hours", "openingHours", "businessHours", "operatingHours"],
            "price_range": ["priceRange", "pricing", "cost", "price"],
            "cuisine": ["cuisine", "cuisineType", "foodType", "category"],
        }
        
        # Extract basic fields
        for our_field, js_fields in field_mappings.items():
            for js_field in js_fields:
                if js_field in restaurant_data and restaurant_data[js_field]:
                    extraction_data[our_field] = str(restaurant_data[js_field])
                    break
        
        # Extract menu items
        menu_items = {}
        if "menu" in restaurant_data:
            menu_data = restaurant_data["menu"]
            if isinstance(menu_data, list):
                # Simple list of menu items
                menu_items["Menu Items"] = menu_data
            elif isinstance(menu_data, dict):
                # Structured menu with sections
                menu_items = menu_data
        
        # Also check for menuItems field
        elif "menuItems" in restaurant_data:
            menu_data = restaurant_data["menuItems"]
            if isinstance(menu_data, list):
                menu_items["Menu Items"] = menu_data
            elif isinstance(menu_data, dict):
                menu_items = menu_data
        
        extraction_data["menu_items"] = menu_items
        
        # Extract social media (look for website, social fields)
        social_media = []
        for field in ["website", "socialMedia", "social", "facebook", "instagram", "twitter"]:
            if field in restaurant_data and restaurant_data[field]:
                value = restaurant_data[field]
                if isinstance(value, str):
                    social_media.append(value)
                elif isinstance(value, list):
                    social_media.extend(value)
        
        extraction_data["social_media"] = social_media
        
        return extraction_data

    def _extract_with_wteg(self, html_content: str, url: str) -> Optional[HeuristicExtractionResult]:
        """Extract data using simplified WTEG approach for mobimag.co URLs."""
        try:
            # Since PDFs aren't accessible, extract what we can from the pageData
            import json
            from urllib.parse import unquote
            
            # Extract pageData
            pattern = r'pageData = JSON\.parse\(decodeURIComponent\("([^"]+)"\)\)'
            match = re.search(pattern, html_content)
            
            if not match:
                return None
            
            # Decode pageData
            encoded_data = match.group(1)
            decoded_data = unquote(encoded_data)
            page_data = json.loads(decoded_data)
            
            # Extract restaurant ID from URL
            restaurant_id = self._extract_restaurant_id_from_url(url)
            if not restaurant_id:
                return None
                
            # Find restaurant by URL ID (convert to 0-based index)
            try:
                index = int(restaurant_id) - 1
                if 0 <= index < len(page_data):
                    restaurant_data = page_data[index]
                else:
                    return None
            except (ValueError, IndexError):
                return None
            
            # Extract basic information available
            restaurant_name = restaurant_data.get("name", "")
            if not restaurant_name or restaurant_name in ["None", None]:
                return None
            
            # Create extraction data with available information
            extraction_data = {
                "name": restaurant_name,
                "address": "⚠️ REQUIRES PDF PROCESSING: Contact details available in PDF format",
                "phone": "⚠️ REQUIRES PDF PROCESSING: Phone number available in PDF format",
                "hours": "⚠️ REQUIRES PDF PROCESSING: Operating hours available in PDF format", 
                "price_range": "⚠️ REQUIRES PDF PROCESSING: Pricing available in PDF format",
                "cuisine": "⚠️ REQUIRES PDF PROCESSING: Cuisine details available in PDF format",
                "menu_items": {"PDF Processing Required": [
                    "✅ Restaurant confirmed in WTEG Portland guide",
                    f"📄 PDF available at mobimag.co: {restaurant_data.get('pdfFilePath', 'Unknown path')}",
                    "🔧 Next step: Implement PDF text extraction to access full restaurant data",
                    "💡 Alternative: Manual extraction or OCR processing of PDF content"
                ]},
                "social_media": [],
                "pdf_available": True,
                "data_source": "mobimag_pagedata",
                "pdf_path": restaurant_data.get('pdfFilePath', ''),
                "page_id": restaurant_data.get('pageID', ''),
                "implementation_status": "PARTIAL - Name extraction working, PDF processing needed for complete data"
            }
            
            # Add detailed next steps
            extraction_data["next_steps"] = [
                "1. Implement PDF text extraction library (PyMuPDF, pdfplumber, or similar)",
                "2. Download PDF from mobimag.co with proper authentication/session handling",
                "3. Extract structured data: address, phone, hours, menu items, services",
                "4. Map extracted text to WTEG schema fields",
                "5. Validate extraction against known restaurant data"
            ]
            
            # Create extraction result with medium confidence (since we have limited data)
            return self._create_extraction_result(extraction_data, "medium")
            
        except Exception as e:
            print(f"WTEG simplified extraction error: {e}")
            return None
