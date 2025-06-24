"""RAG metadata generation for optimized content embedding and retrieval."""
from datetime import datetime
from typing import List, Dict, Any

from src.scraper.multi_strategy_scraper import RestaurantData


class RAGMetadataGenerator:
    """Generates RAG-optimized metadata for restaurant entities."""

    def generate_metadata_header(self, restaurant: RestaurantData) -> str:
        """Generate YAML front matter metadata header."""
        metadata = {
            "entity_type": "restaurant",
            "name": restaurant.name,
            "cuisine": restaurant.cuisine or "Unknown",
            "extraction_sources": restaurant.sources,
            "generation_timestamp": datetime.now().isoformat(),
            "embedding_optimized": True,
        }

        # Add optional fields if available
        if restaurant.address:
            metadata["address"] = restaurant.address
        if restaurant.phone:
            metadata["phone"] = restaurant.phone
        if restaurant.price_range:
            metadata["price_range"] = restaurant.price_range

        header = "---\n"
        for key, value in metadata.items():
            if isinstance(value, list):
                header += f"{key}:\n"
                for item in value:
                    header += f"  - {item}\n"
            else:
                header += f"{key}: {value}\n"
        header += "---"

        return header

    def generate_search_metadata(self, restaurant: RestaurantData) -> Dict[str, Any]:
        """Generate search metadata for RAG systems."""
        keywords = []

        # Extract keywords from restaurant data
        if restaurant.name:
            keywords.extend(restaurant.name.split())
        if restaurant.cuisine:
            keywords.append(restaurant.cuisine)
        if restaurant.menu_items:
            for items in restaurant.menu_items.values():
                if isinstance(items, list):
                    keywords.extend(items)

        # Remove duplicates and clean
        keywords = list(set(k.lower().strip() for k in keywords if k.strip()))

        return {
            "keywords": keywords,
            "categories": [restaurant.cuisine] if restaurant.cuisine else [],
            "embedding_hints": self._generate_embedding_hints(restaurant),
        }

    def optimize_for_embedding_models(self, content: str) -> str:
        """Optimize content format for embedding models."""
        # Ensure consistent formatting
        lines = content.split("\n")
        optimized_lines = []

        for line in lines:
            line = line.strip()
            if line:
                # Ensure sentences end with periods for better embeddings
                if line and not line.endswith((".", "!", "?", ":")):
                    line += "."
                optimized_lines.append(line)
            else:
                optimized_lines.append("")

        return "\n".join(optimized_lines)

    def _generate_embedding_hints(self, restaurant: RestaurantData) -> List[str]:
        """Generate hints for embedding model optimization."""
        hints = ["restaurant", "dining", "food"]

        if restaurant.cuisine:
            hints.append(restaurant.cuisine.lower())

        if restaurant.menu_items:
            if "appetizers" in restaurant.menu_items:
                hints.append("appetizers")
            if any(k in restaurant.menu_items for k in ["entrees", "mains"]):
                hints.append("main_course")
            if "desserts" in restaurant.menu_items:
                hints.append("desserts")

        return hints