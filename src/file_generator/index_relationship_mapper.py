"""Index relationship mapper for mapping entity relationships."""
from typing import List, Dict, Any, Optional
from collections import defaultdict

from src.scraper.multi_strategy_scraper import RestaurantData


class IndexRelationshipMapper:
    """Maps entity relationships for index files."""

    def map_entity_relationships(
        self, restaurant_data: List[RestaurantData]
    ) -> List[Dict[str, Any]]:
        """Map relationships between restaurant entities."""
        relationships = []

        for i, restaurant1 in enumerate(restaurant_data):
            for j, restaurant2 in enumerate(restaurant_data):
                if i != j:
                    relationship = self._analyze_relationship(restaurant1, restaurant2)
                    if relationship:
                        relationships.append(relationship)

        return self.handle_circular_references(relationships)

    def create_bidirectional_mappings(
        self, relationships: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Create bidirectional relationship mappings."""
        bidirectional_map = defaultdict(list)

        for relationship in relationships:
            source = relationship["source"]
            target = relationship["target"]
            rel_type = relationship["type"]

            # Add forward relationship
            bidirectional_map[source].append(
                {"target": target, "type": rel_type, "direction": "outgoing"}
            )

            # Add reverse relationship for certain types
            if rel_type in ["parent-child", "related"]:
                reverse_type = (
                    "child-parent" if rel_type == "parent-child" else "related"
                )
                bidirectional_map[target].append(
                    {"target": source, "type": reverse_type, "direction": "incoming"}
                )

        return dict(bidirectional_map)

    def handle_circular_references(
        self, relationships: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Handle circular references in relationships."""
        # Simple approach: track visited pairs to avoid infinite loops
        visited_pairs = set()
        resolved_relationships = []

        for relationship in relationships:
            source = relationship["source"]
            target = relationship["target"]
            pair = tuple(sorted([source, target]))

            if pair not in visited_pairs:
                visited_pairs.add(pair)
                resolved_relationships.append(relationship)

        return resolved_relationships

    def _analyze_relationship(
        self, restaurant1: RestaurantData, restaurant2: RestaurantData
    ) -> Optional[Dict[str, Any]]:
        """Analyze relationship between two restaurants."""
        # Check for parent-child relationship (same name base)
        name1_base = (
            restaurant1.name.split(" - ")[0]
            if " - " in restaurant1.name
            else restaurant1.name
        )
        name2_base = (
            restaurant2.name.split(" - ")[0]
            if " - " in restaurant2.name
            else restaurant2.name
        )

        if name1_base == name2_base and restaurant1.name != restaurant2.name:
            # Determine parent-child based on name length (parent usually shorter)
            if len(restaurant1.name) < len(restaurant2.name):
                return {
                    "source": restaurant1.name,
                    "target": restaurant2.name,
                    "type": "parent-child",
                }
            else:
                return {
                    "source": restaurant2.name,
                    "target": restaurant1.name,
                    "type": "parent-child",
                }

        # Check for sibling relationship (same cuisine, different names)
        if (
            restaurant1.cuisine
            and restaurant2.cuisine
            and restaurant1.cuisine == restaurant2.cuisine
            and restaurant1.name != restaurant2.name
        ):
            return {
                "source": restaurant1.name,
                "target": restaurant2.name,
                "type": "related",
            }

        return None