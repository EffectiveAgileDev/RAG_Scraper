"""Pattern matching classes for extracting restaurant data from HTML."""
import re
from typing import List, Optional
from bs4 import BeautifulSoup


class BasePatternMatcher:
    """Base class for pattern matchers."""
    
    def extract(self, soup: BeautifulSoup) -> str:
        """Extract data from HTML soup."""
        raise NotImplementedError
    
    def normalize(self, value: str) -> str:
        """Normalize extracted value."""
        return value.strip()


class PhonePatternMatcher(BasePatternMatcher):
    """Extracts phone numbers using regex patterns."""
    
    PHONE_PATTERNS = [
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (503) 555-1234, 503-555-1234, etc.
        r'\+?1[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'  # +1-503-555-1234
    ]
    
    def extract(self, soup: BeautifulSoup) -> str:
        """Extract phone number from HTML."""
        text_content = soup.get_text()
        
        for pattern in self.PHONE_PATTERNS:
            matches = re.finditer(pattern, text_content)
            for match in matches:
                phone = match.group().strip()
                if re.search(r'\d{10}', re.sub(r'[^\d]', '', phone)):
                    return self.normalize_phone(phone)
        
        return ""
    
    def normalize_phone(self, phone: str) -> str:
        """Normalize phone number format."""
        digits = re.sub(r'[^\d]', '', phone)
        
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        
        return phone


class AddressPatternMatcher(BasePatternMatcher):
    """Extracts addresses using location patterns."""
    
    ADDRESS_PATTERNS = [
        r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Place|Pl)[\s,]+[A-Za-z\s]+,?\s*[A-Za-z]{2,}\s*\d{5}',
        r'\d+\s+[A-Za-z\s]+,\s*[A-Za-z\s]+,?\s*[A-Za-z]{2,}\s*\d{5}',
        r'(?:at|located at|address:?)\s*\d+\s+[A-Za-z\s,]+\d{5}'
    ]
    
    def extract(self, soup: BeautifulSoup) -> str:
        """Extract address from HTML."""
        text_content = soup.get_text()
        
        for pattern in self.ADDRESS_PATTERNS:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                address = match.group().strip()
                address = re.sub(r'^(?:at|located at|address:?)\s*', '', address, flags=re.IGNORECASE).strip()
                return self.normalize(address)
        
        # Try semantic class names
        address_classes = ['address', 'location', 'contact-address']
        for class_name in address_classes:
            elements = soup.find_all(class_=re.compile(class_name, re.I))
            for elem in elements:
                text = elem.get_text().strip()
                if 10 < len(text) < 200:
                    return self.normalize(text)
        
        return ""


class HoursPatternMatcher(BasePatternMatcher):
    """Extracts operating hours using time patterns."""
    
    HOURS_PATTERNS = [
        r'(?:Hours?|Open|Business Hours?):?\s*[^\n\.!]{5,80}(?:am|pm|AM|PM)',
        r'(?:Monday|Mon)[-–\s]+(?:Friday|Fri)[^\.!\n]{5,40}(?:am|pm|AM|PM)',
        r'(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[-–]\s*(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[^\.!\n]{5,40}(?:am|pm|AM|PM)',
        r'\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)\s*[-–]\s*\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)\s*(?:daily|every day)',
        r'(?:We\'?re\s*)?open\s+(?:Monday|Mon)\s+through\s+(?:Friday|Fri)\s+from\s+\d{1,2}\s+to\s+\d{1,2}',
        r'\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?\s*[-–]\s*\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?\s*(?:daily|every day|daily)'
    ]
    
    def extract(self, soup: BeautifulSoup) -> str:
        """Extract hours from HTML."""
        # First try specific selectors
        hours_selectors = [
            '[class*="hour"]', '[class*="time"]', '[class*="open"]',
            '[id*="hour"]', '[id*="time"]', '[id*="open"]'
        ]
        
        for selector in hours_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text().strip()
                if re.search(r'\d+\s*(?:am|pm)', text, re.IGNORECASE) and len(text) < 200:
                    return self.normalize(text)
        
        # Try patterns on individual elements
        for elem in soup.find_all(['p', 'div', 'span', 'td', 'li']):
            elem_text = elem.get_text().strip()
            if not elem_text:
                continue
                
            for pattern in self.HOURS_PATTERNS:
                matches = re.finditer(pattern, elem_text, re.IGNORECASE)
                for match in matches:
                    hours = match.group().strip()
                    hours = re.sub(r'^(?:Hours?|Open|Business Hours?):?\s*', '', hours, flags=re.IGNORECASE).strip()
                    if hours and len(hours) < 100:
                        return self.normalize(hours)
        
        return ""


class RestaurantNameExtractor:
    """Specialized extractor for restaurant names with multiple strategies."""
    
    def extract(self, soup: BeautifulSoup) -> str:
        """Extract restaurant name using multiple strategies."""
        # Strategy 1: Title tag
        name = self._extract_from_title(soup)
        if name:
            return name
        
        # Strategy 2: H1 tags
        name = self._extract_from_headers(soup)
        if name:
            return name
        
        # Strategy 3: Semantic classes
        name = self._extract_from_classes(soup)
        if name:
            return name
        
        # Strategy 4: Meta tags
        name = self._extract_from_meta(soup)
        if name:
            return name
        
        return ""
    
    def _extract_from_title(self, soup: BeautifulSoup) -> str:
        """Extract name from title tag."""
        title = soup.find('title')
        if title:
            title_text = title.get_text().strip()
            return self._clean_restaurant_name(title_text)
        return ""
    
    def _extract_from_headers(self, soup: BeautifulSoup) -> str:
        """Extract name from header tags."""
        h1_tags = soup.find_all('h1')
        for h1 in h1_tags:
            text = h1.get_text().strip()
            if self._looks_like_restaurant_name(text):
                return text
        return ""
    
    def _extract_from_classes(self, soup: BeautifulSoup) -> str:
        """Extract name from semantic class names."""
        name_classes = ['restaurant-name', 'business-name', 'site-title', 'logo']
        for class_name in name_classes:
            elements = soup.find_all(class_=re.compile(class_name, re.I))
            for elem in elements:
                text = elem.get_text().strip()
                if text and len(text) < 100:
                    return text
        return ""
    
    def _extract_from_meta(self, soup: BeautifulSoup) -> str:
        """Extract name from meta tags."""
        meta_title = soup.find('meta', property='og:title')
        if meta_title and meta_title.get('content'):
            return self._clean_restaurant_name(meta_title['content'])
        return ""
    
    def _clean_restaurant_name(self, title_text: str) -> str:
        """Clean title text to extract restaurant name."""
        suffixes = [
            r'\s*[-|–]\s*.*$',
            r'\s*\|\s*.*$',
            r'\s*-\s*.*$',
        ]
        
        cleaned = title_text
        for suffix_pattern in suffixes:
            cleaned = re.sub(suffix_pattern, '', cleaned, flags=re.IGNORECASE)
        
        return cleaned.strip()
    
    def _looks_like_restaurant_name(self, text: str) -> bool:
        """Check if text looks like a restaurant name."""
        if len(text) > 100:
            return False
        
        exclude_phrases = ['welcome', 'home', 'about', 'contact', 'menu only']
        return not any(phrase in text.lower() for phrase in exclude_phrases)