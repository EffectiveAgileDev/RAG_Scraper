"""Data aggregation for multi-page restaurant data consolidation."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from src.scraper.multi_strategy_scraper import RestaurantData


@dataclass
class PageData:
    """Data extracted from a single page."""

    url: str
    page_type: str
    source: str
    restaurant_name: str = ""
    address: str = ""
    phone: str = ""
    hours: str = ""
    price_range: str = ""
    cuisine: str = ""
    menu_items: Dict[str, List[str]] = field(default_factory=dict)
    social_media: List[str] = field(default_factory=list)
    confidence: str = "medium"

    def to_dict(self) -> Dict[str, Any]:
        """Convert PageData to dictionary."""
        return {
            "url": self.url,
            "page_type": self.page_type,
            "source": self.source,
            "restaurant_name": self.restaurant_name,
            "address": self.address,
            "phone": self.phone,
            "hours": self.hours,
            "price_range": self.price_range,
            "cuisine": self.cuisine,
            "menu_items": self.menu_items,
            "social_media": self.social_media,
            "confidence": self.confidence,
        }


class DataAggregator:
    """Aggregates restaurant data from multiple pages with conflict resolution."""

    # Source priority (higher = more trustworthy)
    SOURCE_PRIORITY = {"json-ld": 3, "microdata": 2, "heuristic": 1}

    # Page type priority for specific fields
    PAGE_TYPE_PRIORITY = {
        "contact": {"phone": 10, "address": 10, "hours": 10},
        "hours": {"hours": 9},
        "about": {"cuisine": 8, "restaurant_name": 7},
        "menu": {"price_range": 8, "menu_items": 10},
        "home": {"restaurant_name": 9, "cuisine": 6},
    }

    def __init__(self):
        """Initialize data aggregator."""
        self.page_data: List[PageData] = []
        self.conflict_resolution_rules = {
            "restaurant_name": self._resolve_restaurant_name,
            "phone": self._resolve_contact_field,
            "address": self._resolve_contact_field,
            "hours": self._resolve_contact_field,
            "price_range": self._resolve_field_by_source,
            "cuisine": self._resolve_field_by_source,
            "menu_items": self._merge_menu_items,
            "social_media": self._merge_social_media,
        }

    def add_page_data(self, page_data: PageData) -> None:
        """Add data from a single page.

        Args:
            page_data: PageData object containing extracted information
        """
        self.page_data.append(page_data)

    def aggregate(self) -> Optional[RestaurantData]:
        """Aggregate all page data into a single RestaurantData object.

        Returns:
            Aggregated RestaurantData or None if no data available
        """
        if not self.page_data:
            return None

        # Initialize aggregated data
        aggregated = RestaurantData()

        # Collect all sources
        sources = list(set(page.source for page in self.page_data))
        aggregated.sources = sources

        # Resolve each field using appropriate strategy
        aggregated.name = self._resolve_restaurant_name()
        aggregated.phone = self._resolve_contact_field("phone")
        aggregated.address = self._resolve_contact_field("address")
        aggregated.hours = self._resolve_contact_field("hours")
        aggregated.price_range = self._resolve_field_by_source("price_range")
        aggregated.cuisine = self._resolve_field_by_source("cuisine")
        aggregated.menu_items = self._merge_menu_items()
        aggregated.social_media = self._merge_social_media()

        # Calculate overall confidence
        aggregated.confidence = self._calculate_overall_confidence()

        return aggregated

    def _resolve_restaurant_name(self) -> str:
        """Resolve restaurant name conflicts.

        Returns:
            Best restaurant name from all pages
        """
        candidates = []

        for page in self.page_data:
            if page.restaurant_name and page.restaurant_name.strip():
                source_priority = self.SOURCE_PRIORITY.get(page.source, 0)
                page_priority = self.PAGE_TYPE_PRIORITY.get(page.page_type, {}).get(
                    "restaurant_name", 5
                )

                candidates.append(
                    {
                        "name": page.restaurant_name.strip(),
                        "priority": source_priority + page_priority,
                        "source": page.source,
                        "page_type": page.page_type,
                    }
                )

        if not candidates:
            return ""

        # Sort by priority and return best match
        candidates.sort(key=lambda x: x["priority"], reverse=True)
        return candidates[0]["name"]

    def _resolve_contact_field(self, field_name: str) -> str:
        """Resolve contact field conflicts (phone, address, hours).

        Args:
            field_name: Name of the field to resolve

        Returns:
            Best value for the contact field
        """
        candidates = []

        for page in self.page_data:
            field_value = getattr(page, field_name, "")
            if field_value and field_value.strip():
                source_priority = self.SOURCE_PRIORITY.get(page.source, 0)
                page_priority = self.PAGE_TYPE_PRIORITY.get(page.page_type, {}).get(
                    field_name, 5
                )

                candidates.append(
                    {
                        "value": field_value.strip(),
                        "priority": source_priority + page_priority,
                        "source": page.source,
                        "page_type": page.page_type,
                    }
                )

        if not candidates:
            return ""

        # Sort by priority and return best match
        candidates.sort(key=lambda x: x["priority"], reverse=True)
        return candidates[0]["value"]

    def _resolve_field_by_source(self, field_name: str) -> str:
        """Resolve field conflicts primarily by source quality.

        Args:
            field_name: Name of the field to resolve

        Returns:
            Best value based on source priority
        """
        candidates = []

        for page in self.page_data:
            field_value = getattr(page, field_name, "")
            if field_value and field_value.strip():
                source_priority = self.SOURCE_PRIORITY.get(page.source, 0)

                candidates.append(
                    {
                        "value": field_value.strip(),
                        "priority": source_priority,
                        "source": page.source,
                    }
                )

        if not candidates:
            return ""

        # Sort by source priority and return best match
        candidates.sort(key=lambda x: x["priority"], reverse=True)
        return candidates[0]["value"]

    def _merge_menu_items(self) -> Dict[str, List[str]]:
        """Merge menu items from all pages.

        Returns:
            Consolidated menu items dictionary
        """
        merged_menu = {}

        for page in self.page_data:
            if not page.menu_items:
                continue

            for section, items in page.menu_items.items():
                if section not in merged_menu:
                    merged_menu[section] = []

                # Add unique items only
                for item in items:
                    if item and item not in merged_menu[section]:
                        merged_menu[section].append(item)

        return merged_menu

    def _merge_social_media(self) -> List[str]:
        """Merge social media links from all pages.

        Returns:
            List of unique social media links
        """
        all_links = set()

        for page in self.page_data:
            if page.social_media:
                for link in page.social_media:
                    if link and link.strip():
                        all_links.add(link.strip())

        return list(all_links)

    def _calculate_overall_confidence(self) -> str:
        """Calculate overall confidence based on sources and data quality.

        Returns:
            Confidence level ('high', 'medium', 'low')
        """
        if not self.page_data:
            return "low"

        # Count high-quality sources
        high_quality_sources = sum(
            1 for page in self.page_data if page.source in ["json-ld", "microdata"]
        )

        # Count number of unique sources
        unique_sources = len(set(page.source for page in self.page_data))

        # Count number of pages with data
        pages_with_data = sum(
            1
            for page in self.page_data
            if any(
                [
                    page.restaurant_name,
                    page.phone,
                    page.address,
                    page.hours,
                    page.cuisine,
                    page.menu_items,
                ]
            )
        )

        # Calculate confidence score
        confidence_score = 0

        # Bonus for structured data sources
        if high_quality_sources >= 2:
            confidence_score += 3
        elif high_quality_sources >= 1:
            confidence_score += 2

        # Bonus for multiple sources
        if unique_sources >= 3:
            confidence_score += 2
        elif unique_sources >= 2:
            confidence_score += 1

        # Bonus for multiple pages with data
        if pages_with_data >= 3:
            confidence_score += 2
        elif pages_with_data >= 2:
            confidence_score += 1

        # Determine confidence level
        if confidence_score >= 5:
            return "high"
        elif confidence_score >= 3:
            return "medium"
        else:
            return "low"

    def get_data_sources_summary(self) -> Dict[str, Any]:
        """Get summary of data sources and their contributions.

        Returns:
            Dictionary summarizing data sources
        """
        summary = {
            "total_pages": len(self.page_data),
            "sources": {},
            "page_types": {},
            "fields_found": set(),
        }

        for page in self.page_data:
            # Count sources
            if page.source not in summary["sources"]:
                summary["sources"][page.source] = 0
            summary["sources"][page.source] += 1

            # Count page types
            if page.page_type not in summary["page_types"]:
                summary["page_types"][page.page_type] = 0
            summary["page_types"][page.page_type] += 1

            # Track fields found
            if page.restaurant_name:
                summary["fields_found"].add("restaurant_name")
            if page.phone:
                summary["fields_found"].add("phone")
            if page.address:
                summary["fields_found"].add("address")
            if page.hours:
                summary["fields_found"].add("hours")
            if page.cuisine:
                summary["fields_found"].add("cuisine")
            if page.price_range:
                summary["fields_found"].add("price_range")
            if page.menu_items:
                summary["fields_found"].add("menu_items")
            if page.social_media:
                summary["fields_found"].add("social_media")

        # Convert set to list for JSON serialization
        summary["fields_found"] = list(summary["fields_found"])

        return summary
