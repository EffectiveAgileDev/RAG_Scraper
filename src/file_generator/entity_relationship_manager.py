"""Entity relationship management for restaurant data analysis."""
from typing import List, Dict, Any, Optional

from src.scraper.multi_strategy_scraper import RestaurantData


class EntityRelationshipManager:
    """Manages entity relationships and hierarchies."""

    def detect_relationships(
        self, restaurant_data: List[RestaurantData]
    ) -> List[Dict[str, Any]]:
        """Detect relationships between restaurant entities."""
        relationships = []

        for i, restaurant1 in enumerate(restaurant_data):
            for j, restaurant2 in enumerate(restaurant_data):
                if i != j:
                    relationship = self._analyze_relationship(restaurant1, restaurant2)
                    if relationship:
                        relationships.append(relationship)

        return relationships

    def build_relationship_graph(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Dict[str, Any]]:
        """Build relationship graph for restaurants."""
        graph = {}

        for restaurant in restaurant_data:
            restaurant_id = restaurant.name
            graph[restaurant_id] = {
                "entity": restaurant,
                "parent": None,
                "children": [],
                "siblings": [],
            }

        # Detect parent-child relationships
        relationships = self.detect_relationships(restaurant_data)
        for relationship in relationships:
            if relationship["type"] == "parent-child":
                parent_id = relationship["source"]
                child_id = relationship["target"]

                if parent_id in graph and child_id in graph:
                    graph[child_id]["parent"] = parent_id
                    graph[parent_id]["children"].append(child_id)

        return graph

    def resolve_circular_references(
        self, relationships: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Resolve circular references in relationships."""
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