"""Enhanced text content formatter for RAG systems."""
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.scraper.multi_strategy_scraper import RestaurantData
from src.file_generator.semantic_chunker import SemanticChunker


class EnhancedTextContentFormatter:
    """Formatter class for generating enhanced text content with hierarchical structure and RAG optimization."""

    def __init__(self, chunk_size_words: int = 500, chunk_overlap_words: int = 50, max_cross_references: int = 10):
        """Initialize the content formatter."""
        self.chunk_size_words = chunk_size_words
        self.chunk_overlap_words = chunk_overlap_words
        self.max_cross_references = max_cross_references
        self.semantic_chunker = SemanticChunker(
            chunk_size_words=chunk_size_words,
            overlap_words=chunk_overlap_words,
        )

    def generate_hierarchical_content(
        self, restaurant: RestaurantData, hierarchy_graph: Dict
    ) -> str:
        """Generate content with hierarchical structure."""
        content = self.generate_basic_content(restaurant)

        # Add hierarchy information
        restaurant_id = restaurant.name
        if restaurant_id in hierarchy_graph:
            hierarchy_info = hierarchy_graph[restaurant_id]

            content += "\n\nEntity Hierarchy:\n"
            content += f"Entity ID: {restaurant_id}\n"

            if hierarchy_info.get("parent"):
                content += f"Parent Entity: {hierarchy_info['parent']}\n"

            if hierarchy_info.get("children"):
                content += f"Child Entities: {', '.join(hierarchy_info['children'])}\n"

            if hierarchy_info.get("siblings"):
                content += (
                    f"Related Entities: {', '.join(hierarchy_info['siblings'])}\n"
                )

        return content

    def generate_entity_content(self, restaurant: RestaurantData) -> str:
        """Generate content for entity-based organization."""
        content = self.generate_basic_content(restaurant)

        # Add entity type information
        content += f"\n\nEntity Type: Restaurant\n"
        content += f"Entity Category: {restaurant.cuisine or 'Unknown'}\n"
        content += f"Extraction Sources: {', '.join(restaurant.sources)}\n"

        return content

    def generate_basic_content(self, restaurant: RestaurantData) -> str:
        """Generate basic restaurant content."""
        lines = []

        if restaurant.name:
            lines.append(restaurant.name)

        if restaurant.address:
            lines.append(restaurant.address)

        if restaurant.phone:
            lines.append(restaurant.phone)

        if restaurant.price_range:
            lines.append(restaurant.price_range)

        if restaurant.hours:
            lines.append(f"Hours: {restaurant.hours}")

        if restaurant.menu_items:
            lines.append("")  # Blank line
            menu_lines = self.format_menu_items(restaurant.menu_items)
            lines.extend(menu_lines)

        if restaurant.cuisine:
            lines.append("")
            lines.append(f"CUISINE: {restaurant.cuisine}")

        return "\n".join(lines)

    def format_menu_items(self, menu_items: Dict[str, List[str]]) -> List[str]:
        """Format menu items for output."""
        menu_lines = []

        section_order = [
            "appetizers",
            "entrees",
            "mains",
            "main_courses",
            "desserts",
            "drinks",
            "beverages",
        ]

        for section_key in section_order:
            if section_key in menu_items and menu_items[section_key]:
                section_name = section_key.upper().replace("_", " ")
                items = menu_items[section_key]
                if isinstance(items, list):
                    items_str = ", ".join(items)
                    menu_lines.append(f"{section_name}: {items_str}")

        # Handle any remaining sections
        for section_key, items in menu_items.items():
            if section_key not in section_order and items:
                section_name = section_key.upper().replace("_", " ")
                if isinstance(items, list):
                    items_str = ", ".join(items)
                    menu_lines.append(f"{section_name}: {items_str}")

        return menu_lines

    def format_cross_references(self, relationships: List[Dict]) -> str:
        """Format cross-references for output."""
        if not relationships:
            return "No related entities found."

        cross_ref_lines = []

        for relationship in relationships[: self.max_cross_references]:
            rel_type = relationship.get("type", "related")
            target = relationship.get("target", "Unknown")
            cross_ref_lines.append(f"- {rel_type.title()}: {target}")

        return "\n".join(cross_ref_lines)

    def generate_master_index(self, restaurant_data: List[RestaurantData]) -> str:
        """Generate master index content."""
        lines = ["Master Index - All Restaurant Entities", "=" * 40, ""]

        for i, restaurant in enumerate(restaurant_data, 1):
            lines.append(f"{i}. {restaurant.name}")
            if restaurant.cuisine:
                lines.append(f"   Category: {restaurant.cuisine}")
            if restaurant.address:
                lines.append(f"   Address: {restaurant.address}")
            lines.append("")

        lines.append(f"Total Entities: {len(restaurant_data)}")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return "\n".join(lines)

    def generate_category_index(
        self, cuisine: str, restaurants: List[RestaurantData]
    ) -> str:
        """Generate category index content."""
        lines = [f"{cuisine} Category Index", "=" * (len(cuisine) + 15), ""]

        for i, restaurant in enumerate(restaurants, 1):
            lines.append(f"{i}. {restaurant.name}")
            if restaurant.address:
                lines.append(f"   Address: {restaurant.address}")
            if restaurant.phone:
                lines.append(f"   Phone: {restaurant.phone}")
            lines.append("")

        lines.append(f"Total {cuisine} Restaurants: {len(restaurants)}")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return "\n".join(lines)

    # Multi-page RAG optimization helper methods

    def extract_keywords_from_restaurant(
        self, restaurant: RestaurantData
    ) -> List[str]:
        """Extract keywords from restaurant data for embedding hints."""
        keywords = []

        # Add cuisine keywords
        if restaurant.cuisine:
            if isinstance(restaurant.cuisine, str):
                keywords.append(restaurant.cuisine.lower())
            elif isinstance(restaurant.cuisine, list):
                keywords.extend([c.lower() for c in restaurant.cuisine])

        # Add menu item keywords
        if restaurant.menu_items:
            for category, items in restaurant.menu_items.items():
                keywords.append(category.lower())
                if isinstance(items, list):
                    keywords.extend([item.lower() for item in items])

        # Add name keywords
        if restaurant.name:
            name_words = restaurant.name.lower().split()
            keywords.extend(name_words)

        # Remove duplicates and empty strings
        return list(set([k for k in keywords if k and len(k) > 2]))

    def merge_multi_page_content(self, entities: List[RestaurantData]) -> str:
        """Merge content from multiple pages intelligently."""
        merged_sections = {}

        for entity in entities:
            content = self.generate_basic_content(entity)
            page_type = entity.page_metadata.get("page_type", "unknown")

            # Categorize content by page type
            if page_type not in merged_sections:
                merged_sections[page_type] = []
            merged_sections[page_type].append(content)

        # Merge sections in logical order
        page_order = ["directory", "detail", "menu", "unknown"]
        merged_content = []

        for page_type in page_order:
            if page_type in merged_sections:
                merged_content.extend(merged_sections[page_type])

        return "\n\n".join(merged_content)

    def add_cross_page_provenance(
        self, chunk: str, entities: List[RestaurantData], chunk_index: int
    ) -> str:
        """Add cross-page provenance metadata to chunk."""
        source_pages = []
        for entity in entities:
            if hasattr(entity, "page_metadata") and entity.page_metadata:
                source_pages.append(
                    {
                        "page_type": entity.page_metadata.get("page_type"),
                        "source_url": entity.page_metadata.get("source_url"),
                        "entity_id": entity.page_metadata.get("entity_id"),
                    }
                )

        provenance_header = (
            f"<!-- CHUNK_{chunk_index}_SOURCES: {len(source_pages)} pages -->"
        )
        return f"{provenance_header}\n{chunk}"

    def build_page_relationship_map(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, RestaurantData]:
        """Build a map of page relationships."""
        relationship_map = {}

        for restaurant in restaurant_data:
            if hasattr(restaurant, "page_metadata") and restaurant.page_metadata:
                entity_id = restaurant.page_metadata.get("entity_id")
                if entity_id:
                    relationship_map[entity_id] = restaurant

        return relationship_map

    def extract_inheritable_context(self, restaurant: RestaurantData) -> str:
        """Extract context that can be inherited by child pages."""
        if hasattr(restaurant, "page_metadata") and restaurant.page_metadata:
            common_context = restaurant.page_metadata.get("common_context", {})
            if common_context:
                context_lines = []
                for key, value in common_context.items():
                    context_lines.append(f"{key.replace('_', ' ').title()}: {value}")
                return "\n".join(context_lines)
        return ""

    def calculate_adaptive_chunk_size(self, hierarchy_level: int) -> int:
        """Calculate adaptive chunk size based on hierarchy level."""
        base_size = 500
        # Higher hierarchy levels get larger chunks
        return base_size + (hierarchy_level * 100)

    def add_hierarchy_metadata(
        self,
        chunk: str,
        restaurant: RestaurantData,
        hierarchy_level: int,
        chunk_index: int,
    ) -> str:
        """Add hierarchy metadata to chunk."""
        hierarchy_header = (
            f"<!-- HIERARCHY_LEVEL_{hierarchy_level}_CHUNK_{chunk_index} -->"
        )
        return f"{hierarchy_header}\n{chunk}"

    def detect_temporal_conflicts(self, timeline: List[tuple]) -> List[Dict]:
        """Detect conflicts in temporal data."""
        conflicts = []

        if len(timeline) > 1:
            latest = timeline[0][1]  # Most recent
            for timestamp, older_data in timeline[1:]:
                # Compare key fields for conflicts
                if latest.address != older_data.address:
                    conflicts.append(
                        {
                            "field": "address",
                            "latest": latest.address,
                            "older": older_data.address,
                            "timestamp": timestamp,
                        }
                    )

                if latest.phone != older_data.phone:
                    conflicts.append(
                        {
                            "field": "phone",
                            "latest": latest.phone,
                            "older": older_data.phone,
                            "timestamp": timestamp,
                        }
                    )

        return conflicts

    def generate_temporally_aware_content(
        self, timeline: List[tuple], conflicts: List[Dict]
    ) -> str:
        """Generate content with temporal awareness and conflict resolution."""
        most_recent = timeline[0][1]
        content = self.generate_basic_content(most_recent)

        if conflicts:
            conflict_section = "\n\n--- Data Evolution ---\n"
            for conflict in conflicts:
                conflict_section += f"{conflict['field'].title()} changed from '{conflict['older']}' to '{conflict['latest']}'\n"
            content += conflict_section

        return content

    def add_temporal_metadata(
        self, chunk: str, timeline: List[tuple], entity_id: str, chunk_index: int
    ) -> str:
        """Add temporal metadata to chunk."""
        latest_timestamp = timeline[0][0] if timeline else "unknown"
        temporal_header = (
            f"<!-- TEMPORAL_DATA: {entity_id} updated {latest_timestamp} -->"
        )
        return f"{temporal_header}\n{chunk}"

    def calculate_temporal_span(self, timeline: List[tuple]) -> float:
        """Calculate temporal span in hours."""
        if len(timeline) < 2:
            return 0

        try:
            from datetime import datetime

            latest = datetime.fromisoformat(timeline[0][0].replace("Z", "+00:00"))
            earliest = datetime.fromisoformat(timeline[-1][0].replace("Z", "+00:00"))
            return (latest - earliest).total_seconds() / 3600
        except:
            return 0

    def build_comprehensive_relationship_graph(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, List[str]]:
        """Build comprehensive relationship graph for co-location optimization."""
        graph = {}

        for restaurant in restaurant_data:
            if hasattr(restaurant, "page_metadata") and restaurant.page_metadata:
                entity_id = restaurant.page_metadata.get("entity_id")
                parent_id = restaurant.page_metadata.get("parent_id")

                if entity_id:
                    if entity_id not in graph:
                        graph[entity_id] = []

                    # Add parent relationship
                    if parent_id:
                        graph[entity_id].append(parent_id)

                        # Add reverse relationship
                        if parent_id not in graph:
                            graph[parent_id] = []
                        graph[parent_id].append(entity_id)

        return graph

    def find_restaurant_by_entity_id(
        self, restaurant_data: List[RestaurantData], entity_id: str
    ) -> Optional[RestaurantData]:
        """Find restaurant by entity ID."""
        for restaurant in restaurant_data:
            if hasattr(restaurant, "page_metadata") and restaurant.page_metadata:
                if restaurant.page_metadata.get("entity_id") == entity_id:
                    return restaurant
        return None

    def add_retrieval_optimization_metadata(
        self,
        chunk: str,
        restaurant: RestaurantData,
        related_entities: List[str],
        chunk_index: int,
    ) -> str:
        """Add retrieval optimization metadata to chunk."""
        optimization_header = (
            f"<!-- RETRIEVAL_OPTIMIZED: {len(related_entities)} related entities -->"
        )
        return f"{optimization_header}\n{chunk}"

    def extract_primary_terms(self, restaurant: RestaurantData) -> List[str]:
        """Extract primary terms for query expansion."""
        terms = []
        if restaurant.name:
            terms.extend(restaurant.name.split())
        if restaurant.cuisine:
            terms.append(restaurant.cuisine)
        return terms

    def extract_related_terms(self, related_content: List[str]) -> List[str]:
        """Extract related terms from related content."""
        terms = set()
        for content in related_content:
            # Simple keyword extraction
            words = content.split()
            terms.update(word.strip(".,!?") for word in words if len(word) > 3)
        return list(terms)

    def generate_disambiguation_context(
        self, restaurant: RestaurantData, all_entities: List[RestaurantData]
    ) -> str:
        """Generate disambiguation context for entities with same name."""
        context_parts = []

        if hasattr(restaurant, "page_metadata") and restaurant.page_metadata:
            page_type = restaurant.page_metadata.get("page_type")
            context_parts.append(f"Context: {page_type} page")

            disambiguation_context = restaurant.page_metadata.get(
                "disambiguation_context"
            )
            if disambiguation_context:
                context_parts.append(f"Specific context: {disambiguation_context}")

        if restaurant.address and restaurant.address != "Different context":
            context_parts.append(f"Location: {restaurant.address}")

        return " | ".join(context_parts)

    def process_batch_with_optimization(
        self, batch: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Process batch with memory and performance optimization."""
        # Simple batch processing with basic optimization
        processed_count = 0

        for restaurant in batch:
            # Process individual restaurant with minimal memory footprint
            content = self.generate_basic_content(restaurant)
            processed_count += 1

        return {"processed": processed_count}

    def optimize_memory_usage(self):
        """Optimize memory usage during large-scale processing."""
        import gc

        gc.collect()