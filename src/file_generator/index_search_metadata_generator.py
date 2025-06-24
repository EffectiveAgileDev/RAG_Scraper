"""Index search metadata generator for enhanced search capabilities."""
from typing import List, Dict, Any

from src.scraper.multi_strategy_scraper import RestaurantData


class IndexSearchMetadataGenerator:
    """Generates search metadata for restaurant entities."""

    def generate_search_keywords(self, restaurant: RestaurantData) -> List[str]:
        """Generate searchable keywords from restaurant data."""
        keywords = []

        # Extract from name
        if restaurant.name:
            keywords.extend(restaurant.name.lower().split())

        # Extract from cuisine
        if restaurant.cuisine:
            keywords.append(restaurant.cuisine.lower())

        # Extract from menu items
        if restaurant.menu_items:
            for category, items in restaurant.menu_items.items():
                if isinstance(items, list):
                    for item in items:
                        keywords.extend(item.lower().split())

        # Extract from address
        if restaurant.address:
            # Extract city, state from address
            address_parts = restaurant.address.split(",")
            for part in address_parts:
                keywords.extend(part.strip().lower().split())

        # Remove duplicates and common stop words
        stop_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
        }
        unique_keywords = list(
            set(k for k in keywords if k not in stop_words and len(k) > 2)
        )

        return unique_keywords

    def generate_location_search_data(
        self, restaurant: RestaurantData
    ) -> Dict[str, Any]:
        """Generate location-based search data."""
        location_data = {}

        if restaurant.address:
            # Parse address components
            address_parts = restaurant.address.split(",")
            location_data["address_components"] = [
                part.strip() for part in address_parts
            ]

            # Extract searchable location terms
            searchable_terms = []
            for part in address_parts:
                searchable_terms.extend(part.strip().split())

            location_data["searchable_terms"] = searchable_terms

        return location_data

    def generate_fuzzy_match_data(self, restaurant: RestaurantData) -> Dict[str, Any]:
        """Generate data for fuzzy matching support."""
        fuzzy_data = {}

        if restaurant.name:
            # Generate phonetic representations (simplified)
            fuzzy_data["name_variations"] = [
                restaurant.name.lower(),
                restaurant.name.lower().replace(" ", ""),
                restaurant.name.lower().replace("'", ""),
            ]

        if restaurant.cuisine:
            fuzzy_data["cuisine_variations"] = [
                restaurant.cuisine.lower(),
                restaurant.cuisine.lower().replace(" ", ""),
            ]

        return fuzzy_data