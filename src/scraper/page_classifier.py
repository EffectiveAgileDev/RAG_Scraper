"""Page type classification for multi-page restaurant websites."""
import re
from typing import Dict, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup


class PageClassifier:
    """Classifies web pages by their content type for restaurant data extraction."""

    # URL patterns for different page types
    URL_PATTERNS = {
        "menu": [
            r"/menu/?$",
            r"/food/?$",
            r"/dining/?$",
            r"/eat/?$",
            r"/menus/?$",
            r"/drinks/?$",
            r"/beverages/?$",
        ],
        "contact": [
            r"/contact/?$",
            r"/contacts/?$",
            r"/reach/?$",
            r"/touch/?$",
            r"/info/?$",
            r"/information/?$",
            r"/location/?$",
            r"/locations/?$",
        ],
        "about": [
            r"/about/?$",
            r"/story/?$",
            r"/history/?$",
            r"/our[-_]story/?$",
            r"/who[-_]we[-_]are/?$",
            r"/background/?$",
            r"/bio/?$",
        ],
        "hours": [
            r"/hours/?$",
            r"/time/?$",
            r"/times/?$",
            r"/schedule/?$",
            r"/when/?$",
            r"/open/?$",
            r"/operating/?$",
        ],
        "home": [r"/?$", r"/index/?$", r"/home/?$", r"/main/?$"],
    }

    # Content indicators for different page types
    CONTENT_INDICATORS = {
        "menu": {
            "headings": [
                "menu",
                "food",
                "drinks",
                "appetizers",
                "entrees",
                "desserts",
                "beverages",
            ],
            "classes": [
                "menu",
                "food-menu",
                "restaurant-menu",
                "menu-section",
                "menu-item",
            ],
            "keywords": [
                "price",
                "$",
                "appetizer",
                "entree",
                "dessert",
                "beverage",
                "wine",
                "beer",
            ],
        },
        "contact": {
            "headings": [
                "contact",
                "reach us",
                "get in touch",
                "find us",
                "location",
                "address",
            ],
            "classes": ["contact", "contact-info", "address", "phone", "location"],
            "keywords": [
                "phone",
                "address",
                "email",
                "hours",
                "directions",
                "map",
                "location",
            ],
        },
        "about": {
            "headings": ["about", "our story", "history", "who we are", "background"],
            "classes": ["about", "story", "history", "bio", "background"],
            "keywords": [
                "story",
                "history",
                "founded",
                "family",
                "tradition",
                "chef",
                "owner",
            ],
        },
        "hours": {
            "headings": ["hours", "open", "schedule", "operating hours"],
            "classes": ["hours", "schedule", "operating-hours"],
            "keywords": [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
                "open",
                "closed",
                "am",
                "pm",
                "hours",
            ],
        },
        "home": {
            "headings": ["welcome", "home", "restaurant"],
            "classes": ["hero", "welcome", "home", "main"],
            "keywords": ["welcome", "restaurant", "cuisine", "dining", "experience"],
        },
    }

    def classify_page(self, url: str, html_content: str) -> str:
        """Classify a page based on its URL and content.

        Args:
            url: URL of the page
            html_content: HTML content of the page

        Returns:
            Page type classification ('menu', 'contact', 'about', 'hours', 'home', 'unknown')
        """
        # First try URL-based classification
        url_classification = self.classify_by_url(url)
        if url_classification != "unknown":
            return url_classification

        # Then try content-based classification
        content_classification = self.classify_by_content(html_content)

        return content_classification

    def classify_by_url(self, url: str) -> str:
        """Classify page type based on URL patterns.

        Args:
            url: URL to classify

        Returns:
            Page type or 'unknown' if no pattern matches
        """
        path = urlparse(url).path.lower()

        for page_type, patterns in self.URL_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, path):
                    return page_type

        return "unknown"

    def classify_by_content(self, html_content: str) -> str:
        """Classify page type based on HTML content analysis.

        Args:
            html_content: HTML content to analyze

        Returns:
            Page type or 'unknown' if classification is unclear
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Score each page type based on content indicators
        type_scores = {}

        for page_type, indicators in self.CONTENT_INDICATORS.items():
            score = 0

            # Check headings
            score += self._score_headings(soup, indicators["headings"])

            # Check CSS classes
            score += self._score_classes(soup, indicators["classes"])

            # Check keyword density
            score += self._score_keywords(soup, indicators["keywords"])

            type_scores[page_type] = score

        # Return the page type with highest score if above threshold
        max_score = max(type_scores.values()) if type_scores else 0
        if max_score > 0:
            # Find page type with highest score
            for page_type, score in type_scores.items():
                if score == max_score:
                    return page_type

        return "unknown"

    def _score_headings(self, soup: BeautifulSoup, heading_keywords: list) -> int:
        """Score page based on heading content.

        Args:
            soup: BeautifulSoup object
            heading_keywords: List of keywords to look for in headings

        Returns:
            Score based on heading matches
        """
        score = 0
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])

        for heading in headings:
            heading_text = heading.get_text().lower()
            for keyword in heading_keywords:
                if keyword in heading_text:
                    # Higher score for h1 tags
                    if heading.name == "h1":
                        score += 3
                    elif heading.name in ["h2", "h3"]:
                        score += 2
                    else:
                        score += 1

        return score

    def _score_classes(self, soup: BeautifulSoup, class_keywords: list) -> int:
        """Score page based on CSS class names.

        Args:
            soup: BeautifulSoup object
            class_keywords: List of class keywords to look for

        Returns:
            Score based on class matches
        """
        score = 0

        for element in soup.find_all(class_=True):
            classes = element.get("class", [])
            class_text = " ".join(classes).lower()

            for keyword in class_keywords:
                if keyword in class_text:
                    score += 1

        return score

    def _score_keywords(self, soup: BeautifulSoup, keywords: list) -> int:
        """Score page based on keyword density.

        Args:
            soup: BeautifulSoup object
            keywords: List of keywords to look for

        Returns:
            Score based on keyword density
        """
        # Get text content
        text_content = soup.get_text().lower()
        score = 0

        for keyword in keywords:
            # Count occurrences of keyword
            count = text_content.count(keyword)
            # Cap the score per keyword to avoid over-weighting
            score += min(count, 3)

        return score

    def get_page_confidence(self, url: str, html_content: str) -> Dict[str, float]:
        """Get confidence scores for all page types.

        Args:
            url: URL of the page
            html_content: HTML content of the page

        Returns:
            Dictionary mapping page types to confidence scores (0-1)
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Calculate raw scores for each page type
        raw_scores = {}
        for page_type, indicators in self.CONTENT_INDICATORS.items():
            score = 0
            score += self._score_headings(soup, indicators["headings"])
            score += self._score_classes(soup, indicators["classes"])
            score += self._score_keywords(soup, indicators["keywords"])
            raw_scores[page_type] = score

        # Also consider URL-based classification
        url_classification = self.classify_by_url(url)
        if url_classification != "unknown":
            raw_scores[url_classification] = raw_scores.get(url_classification, 0) + 5

        # Normalize scores to confidence percentages
        total_score = sum(raw_scores.values())
        if total_score == 0:
            return {page_type: 0.0 for page_type in self.CONTENT_INDICATORS.keys()}

        confidence_scores = {}
        for page_type, score in raw_scores.items():
            confidence_scores[page_type] = score / total_score

        return confidence_scores

    def is_restaurant_related(self, html_content: str) -> bool:
        """Check if a page appears to be restaurant-related.

        Args:
            html_content: HTML content to analyze

        Returns:
            True if page appears restaurant-related
        """
        soup = BeautifulSoup(html_content, "html.parser")
        text_content = soup.get_text().lower()

        # Restaurant-related keywords
        restaurant_keywords = [
            "restaurant",
            "dining",
            "cuisine",
            "chef",
            "food",
            "menu",
            "eat",
            "drink",
            "bar",
            "grill",
            "cafe",
            "bistro",
            "eatery",
            "kitchen",
            "culinary",
            "taste",
            "flavor",
            "dish",
            "meal",
        ]

        keyword_count = 0
        for keyword in restaurant_keywords:
            if keyword in text_content:
                keyword_count += 1

        # Consider page restaurant-related if it has multiple restaurant keywords
        return keyword_count >= 2
