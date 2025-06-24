"""Index file builder for generating comprehensive index files with various features."""
import os
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from collections import defaultdict

from src.scraper.multi_strategy_scraper import RestaurantData
from src.file_generator.index_search_metadata_generator import IndexSearchMetadataGenerator
from src.file_generator.index_statistics_generator import IndexStatisticsGenerator
from src.file_generator.index_relationship_mapper import IndexRelationshipMapper
from src.file_generator.index_integrity_validator import IndexIntegrityValidator


class IndexFileBuilder:
    """Builder class responsible for generating various types of index files."""

    def __init__(self, config):
        """Initialize index file builder with configuration and helper components."""
        self.config = config
        
        # Initialize helper components
        self.search_metadata_generator = IndexSearchMetadataGenerator()
        self.statistics_generator = IndexStatisticsGenerator()
        self.relationship_mapper = IndexRelationshipMapper()
        self.integrity_validator = IndexIntegrityValidator()

    def generate_master_index(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, str]:
        """Generate master index file listing all entities."""
        self._validate_input_data(restaurant_data)

        master_index_data = {
            "schema_version": self.config.schema_version,
            "generation_timestamp": datetime.now().isoformat(),
            "total_entities": len(restaurant_data),
            "entities": [],
        }

        # Add each restaurant entity
        for i, restaurant in enumerate(restaurant_data):
            entity_data = {
                "id": f"restaurant_{i}",
                "name": restaurant.name,
                "cuisine": restaurant.cuisine,
                "address": restaurant.address,
                "phone": restaurant.phone,
                "file_path": self._generate_relative_file_path(restaurant),
                "sources": restaurant.sources,
            }

            if self.config.include_search_metadata:
                entity_data[
                    "search_metadata"
                ] = self.search_metadata_generator.generate_search_keywords(restaurant)

            master_index_data["entities"].append(entity_data)

        # Add statistics if requested
        if self.config.include_statistics:
            master_index_data[
                "statistics"
            ] = self.statistics_generator.calculate_entity_statistics(restaurant_data)

        # Add relationships if requested
        if self.config.include_relationships:
            master_index_data[
                "relationships"
            ] = self.relationship_mapper.map_entity_relationships(restaurant_data)

        # Generate JSON file
        result = {}
        if self.config.generate_json:
            json_file_path = os.path.join(
                self.config.output_directory, "master_index.json"
            )
            self._handle_file_exists(json_file_path)

            with open(json_file_path, "w", encoding="utf-8") as f:
                json.dump(master_index_data, f, indent=2, ensure_ascii=False)

            result["master_index.json"] = json_file_path

        # Generate text file
        if self.config.generate_text:
            text_file_path = os.path.join(
                self.config.output_directory, "master_index.txt"
            )
            text_content = self._format_master_index_as_text(master_index_data)
            self._handle_file_exists(text_file_path)

            with open(text_file_path, "w", encoding="utf-8") as f:
                f.write(text_content)

            result["master_index.txt"] = text_file_path

        return result

    def generate_category_indices(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Dict[str, str]]:
        """Generate category-specific index files."""
        self._validate_input_data(restaurant_data)

        # Group restaurants by cuisine
        cuisine_groups = defaultdict(list)
        for restaurant in restaurant_data:
            cuisine = restaurant.cuisine or "Unknown"
            cuisine_groups[cuisine].append(restaurant)

        category_indices = {}

        for cuisine, restaurants in cuisine_groups.items():
            category_index_data = {
                "schema_version": self.config.schema_version,
                "generation_timestamp": datetime.now().isoformat(),
                "category": cuisine,
                "entity_count": len(restaurants),
                "entities": [],
            }

            # Add restaurants in this category
            for i, restaurant in enumerate(restaurants):
                entity_data = {
                    "id": f"{cuisine.lower()}_{i}",
                    "name": restaurant.name,
                    "address": restaurant.address,
                    "phone": restaurant.phone,
                    "file_path": self._generate_relative_file_path(restaurant),
                    "sources": restaurant.sources,
                }

                if self.config.include_search_metadata:
                    entity_data[
                        "search_metadata"
                    ] = self.search_metadata_generator.generate_search_keywords(
                        restaurant
                    )

                category_index_data["entities"].append(entity_data)

            # Add category-specific statistics
            if self.config.include_statistics:
                category_index_data[
                    "statistics"
                ] = self.statistics_generator.calculate_entity_statistics(restaurants)

            # Generate files for this category
            category_files = {}

            if self.config.generate_json:
                json_filename = f"{cuisine}_index.json"
                json_file_path = os.path.join(
                    self.config.output_directory, json_filename
                )
                self._handle_file_exists(json_file_path)

                with open(json_file_path, "w", encoding="utf-8") as f:
                    json.dump(category_index_data, f, indent=2, ensure_ascii=False)

                category_files["json"] = json_file_path

            if self.config.generate_text:
                txt_filename = f"{cuisine}_index.txt"
                txt_file_path = os.path.join(self.config.output_directory, txt_filename)
                text_content = self._format_category_index_as_text(category_index_data)
                self._handle_file_exists(txt_file_path)

                with open(txt_file_path, "w", encoding="utf-8") as f:
                    f.write(text_content)

                category_files["text"] = txt_file_path

            category_indices[cuisine] = category_files

        return category_indices

    def generate_indices_with_relationships(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate index files with relationship mapping."""
        # Generate base indices
        master_index = self.generate_master_index(restaurant_data)
        category_indices = self.generate_category_indices(restaurant_data)

        # Add relationship mapping
        relationships = self.relationship_mapper.map_entity_relationships(
            restaurant_data
        )
        bidirectional_map = self.relationship_mapper.create_bidirectional_mappings(
            relationships
        )

        return {
            "master_index": master_index,
            "category_indices": category_indices,
            "relationships": relationships,
            "bidirectional_map": bidirectional_map,
        }

    def generate_indices_with_search_metadata(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate index files with enhanced search metadata."""
        # Use the standard generation but ensure search metadata is enabled
        original_setting = self.config.include_search_metadata
        self.config.include_search_metadata = True

        try:
            result = {
                "master_index": self.generate_master_index(restaurant_data),
                "category_indices": self.generate_category_indices(restaurant_data),
            }

            # Add comprehensive search metadata
            search_metadata = {}
            for restaurant in restaurant_data:
                restaurant_id = restaurant.name
                search_metadata[restaurant_id] = {
                    "keywords": self.search_metadata_generator.generate_search_keywords(
                        restaurant
                    ),
                    "location_data": self.search_metadata_generator.generate_location_search_data(
                        restaurant
                    ),
                    "fuzzy_data": self.search_metadata_generator.generate_fuzzy_match_data(
                        restaurant
                    ),
                }

            result["search_metadata"] = search_metadata
            return result

        finally:
            self.config.include_search_metadata = original_setting

    def generate_json_indices(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, str]:
        """Generate JSON format indices for programmatic access."""
        original_settings = (self.config.generate_json, self.config.generate_text)
        self.config.generate_json = True
        self.config.generate_text = False

        try:
            master_index = self.generate_master_index(restaurant_data)
            category_indices = self.generate_category_indices(restaurant_data)

            return {
                "master_index": master_index.get("master_index.json"),
                "category_indices": {
                    k: v.get("json") for k, v in category_indices.items()
                },
            }

        finally:
            self.config.generate_json, self.config.generate_text = original_settings

    def generate_text_indices(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, str]:
        """Generate text format indices for human readability."""
        original_settings = (self.config.generate_json, self.config.generate_text)
        self.config.generate_json = False
        self.config.generate_text = True

        try:
            master_index = self.generate_master_index(restaurant_data)
            category_indices = self.generate_category_indices(restaurant_data)

            return {
                "master_index": master_index.get("master_index.txt"),
                "category_indices": {
                    k: v.get("text") for k, v in category_indices.items()
                },
            }

        finally:
            self.config.generate_json, self.config.generate_text = original_settings

    def generate_indices_with_statistics(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate index files with comprehensive statistics."""
        original_setting = self.config.include_statistics
        self.config.include_statistics = True

        try:
            result = {
                "master_index": self.generate_master_index(restaurant_data),
                "category_indices": self.generate_category_indices(restaurant_data),
            }

            # Add detailed statistics
            result["detailed_statistics"] = {
                "entity_stats": self.statistics_generator.calculate_entity_statistics(
                    restaurant_data
                ),
                "quality_metrics": self.statistics_generator.calculate_data_quality_metrics(
                    restaurant_data
                ),
                "generation_metadata": self.statistics_generator.generate_generation_metadata(),
            }

            return result

        finally:
            self.config.include_statistics = original_setting

    def generate_comprehensive_indices(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate comprehensive index files with all features enabled."""
        self._validate_input_data(restaurant_data)
        self._validate_write_permissions()

        result = {
            "master_index": self.generate_master_index(restaurant_data),
            "category_indices": self.generate_category_indices(restaurant_data),
        }

        if self.config.include_relationships:
            relationships = self.relationship_mapper.map_entity_relationships(
                restaurant_data
            )
            result["relationships"] = relationships

        if self.config.include_statistics:
            result[
                "statistics"
            ] = self.statistics_generator.calculate_entity_statistics(restaurant_data)

        return result

    def update_indices_incrementally(
        self, new_entities: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Update indices incrementally with new entities."""
        if not new_entities:
            return {"status": "no_updates_needed"}

        # Load existing indices
        existing_master_path = os.path.join(
            self.config.output_directory, "master_index.json"
        )

        if os.path.exists(existing_master_path):
            with open(existing_master_path, "r", encoding="utf-8") as f:
                existing_master = json.load(f)
        else:
            existing_master = {
                "schema_version": self.config.schema_version,
                "entities": [],
                "total_entities": 0,
            }

        # Add new entities
        for entity in new_entities:
            entity_data = {
                "id": f"restaurant_{existing_master['total_entities']}",
                "name": entity.name,
                "cuisine": entity.cuisine,
                "address": entity.address,
                "phone": entity.phone,
                "file_path": self._generate_relative_file_path(entity),
                "sources": entity.sources,
            }
            existing_master["entities"].append(entity_data)
            existing_master["total_entities"] += 1

        # Update timestamps
        existing_master["generation_timestamp"] = datetime.now().isoformat()

        # Write updated master index
        with open(existing_master_path, "w", encoding="utf-8") as f:
            json.dump(existing_master, f, indent=2, ensure_ascii=False)

        return {
            "status": "updated",
            "new_entities_added": len(new_entities),
            "total_entities": existing_master["total_entities"],
        }

    # Multi-page index generation methods

    def generate_master_index_with_provenance(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate master index with page provenance tracking."""
        # Start with regular master index
        master_index = self.generate_master_index(restaurant_data)

        if not self.config.include_provenance:
            return master_index

        # Add provenance metadata
        provenance_data = {"source_pages": [], "extraction_metadata": {}}

        for restaurant in restaurant_data:
            if hasattr(restaurant, "page_metadata") and restaurant.page_metadata:
                page_meta = restaurant.page_metadata
                source_page = {
                    "entity_id": page_meta.get("entity_id"),
                    "source_url": page_meta.get("source_url"),
                    "page_type": page_meta.get("page_type"),
                    "extraction_timestamp": page_meta.get("extraction_timestamp"),
                    "parent_id": page_meta.get("parent_id"),
                }
                provenance_data["source_pages"].append(source_page)

        # Add provenance to master index
        if isinstance(master_index, dict):
            master_index["provenance"] = provenance_data
        else:
            # Handle string format
            result = json.loads(master_index) if isinstance(master_index, str) else {}
            result["provenance"] = provenance_data
            return result

        return master_index

    def generate_indices_with_cross_page_relationships(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate indices with cross-page entity relationships."""
        # Start with regular indices
        indices = self.generate_indices_with_relationships(restaurant_data)

        if not self.config.track_cross_page_relationships:
            return indices

        # Build cross-page relationship mappings
        cross_page_relationships = {
            "parent_child_mappings": {},
            "page_type_relationships": {},
            "cross_page_references": [],
        }

        # Group entities by page relationships
        page_entities = {}
        for restaurant in restaurant_data:
            if hasattr(restaurant, "page_metadata") and restaurant.page_metadata:
                page_meta = restaurant.page_metadata
                entity_id = page_meta.get("entity_id")
                parent_id = page_meta.get("parent_id")
                page_type = page_meta.get("page_type")

                if entity_id:
                    page_entities[entity_id] = {
                        "name": restaurant.name,
                        "parent_id": parent_id,
                        "page_type": page_type,
                        "entity": restaurant,
                    }

        # Build parent-child mappings
        for entity_id, entity_info in page_entities.items():
            parent_id = entity_info.get("parent_id")
            if parent_id and parent_id in page_entities:
                if parent_id not in cross_page_relationships["parent_child_mappings"]:
                    cross_page_relationships["parent_child_mappings"][parent_id] = []
                cross_page_relationships["parent_child_mappings"][parent_id].append(
                    entity_id
                )

        indices["cross_page_relationships"] = cross_page_relationships
        return indices

    def generate_unified_indices_from_multipage_data(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate unified index entries from multi-page data aggregation."""
        unified_entities = {}

        # Group restaurants by entity ID from page metadata
        for restaurant in restaurant_data:
            if hasattr(restaurant, "page_metadata") and restaurant.page_metadata:
                entity_id = restaurant.page_metadata.get("entity_id")
                if entity_id:
                    if entity_id not in unified_entities:
                        unified_entities[entity_id] = {
                            "name": restaurant.name,
                            "aggregated_data": {},
                            "data_sources": [],
                            "data_aggregation_metadata": {
                                "page_contributions": {},
                                "conflict_resolutions": [],
                                "aggregation_timestamp": datetime.now().isoformat(),
                            },
                        }

                    # Aggregate data from this page
                    entity = unified_entities[entity_id]
                    page_type = restaurant.page_metadata.get("page_type", "unknown")

                    # Add data contributions metadata
                    entity["data_aggregation_metadata"]["page_contributions"][
                        page_type
                    ] = {
                        "address": restaurant.address if restaurant.address else None,
                        "phone": restaurant.phone if restaurant.phone else None,
                        "menu_items": restaurant.menu_items
                        if restaurant.menu_items
                        else None,
                        "price_range": restaurant.price_range
                        if restaurant.price_range
                        else None,
                    }

                    # Apply page hierarchy rules for conflict resolution
                    # Detail pages override directory pages
                    if page_type == "detail" or not entity["aggregated_data"]:
                        entity["aggregated_data"].update(
                            {
                                "address": restaurant.address
                                or entity["aggregated_data"].get("address", ""),
                                "phone": restaurant.phone
                                or entity["aggregated_data"].get("phone", ""),
                                "cuisine": restaurant.cuisine
                                or entity["aggregated_data"].get("cuisine", ""),
                                "menu_items": restaurant.menu_items
                                or entity["aggregated_data"].get("menu_items", {}),
                                "price_range": restaurant.price_range
                                or entity["aggregated_data"].get("price_range", ""),
                            }
                        )

        return {
            "unified_entities": list(unified_entities.values()),
            "aggregation_summary": {
                "total_unified_entities": len(unified_entities),
                "aggregation_timestamp": datetime.now().isoformat(),
            },
        }

    def generate_indices_with_temporal_awareness(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate index files with temporal awareness of extraction times."""
        # Start with regular indices
        indices = self.generate_master_index(restaurant_data)

        if not self.config.enable_temporal_awareness:
            return indices

        temporal_metadata = {
            "extraction_timeline": {},
            "most_recent_data": {},
            "stale_data_flags": [],
            "temporal_analysis_timestamp": datetime.now().isoformat(),
        }

        # Analyze extraction timestamps
        entity_timestamps = {}
        for restaurant in restaurant_data:
            if hasattr(restaurant, "page_metadata") and restaurant.page_metadata:
                entity_id = restaurant.page_metadata.get("entity_id")
                timestamp = restaurant.page_metadata.get("extraction_timestamp")
                if entity_id and timestamp:
                    if entity_id not in entity_timestamps:
                        entity_timestamps[entity_id] = []
                    entity_timestamps[entity_id].append(
                        {"timestamp": timestamp, "restaurant": restaurant}
                    )

        # Identify most recent data and stale data
        current_time = datetime.now()
        stale_threshold_hours = 48  # Data older than 48 hours is considered stale

        for entity_id, timestamps in entity_timestamps.items():
            # Sort by timestamp to find most recent
            sorted_timestamps = sorted(
                timestamps, key=lambda x: x["timestamp"], reverse=True
            )
            most_recent = sorted_timestamps[0]
            temporal_metadata["most_recent_data"][entity_id] = {
                "timestamp": most_recent["timestamp"],
                "restaurant_name": most_recent["restaurant"].name,
            }

            # Check for stale data
            try:
                extraction_time = datetime.fromisoformat(
                    most_recent["timestamp"].replace("Z", "+00:00")
                )
                hours_old = (
                    current_time - extraction_time.replace(tzinfo=None)
                ).total_seconds() / 3600
                if hours_old > stale_threshold_hours:
                    temporal_metadata["stale_data_flags"].append(
                        {
                            "entity_id": entity_id,
                            "hours_old": hours_old,
                            "last_extraction": most_recent["timestamp"],
                        }
                    )
            except (ValueError, AttributeError):
                # Handle timestamp parsing errors
                temporal_metadata["stale_data_flags"].append(
                    {
                        "entity_id": entity_id,
                        "error": "Unable to parse timestamp",
                        "timestamp": most_recent["timestamp"],
                    }
                )

        # Add temporal metadata to indices
        if isinstance(indices, dict):
            indices["temporal_metadata"] = temporal_metadata
        else:
            result = json.loads(indices) if isinstance(indices, str) else {}
            result["temporal_metadata"] = temporal_metadata
            return result

        return indices

    def generate_indices_with_context_inheritance(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate indices with context inheritance tracking from parent pages."""
        # Start with regular indices
        indices = self.generate_master_index(restaurant_data)

        context_inheritance = {
            "inheritance_rules": {},
            "child_overrides": {},
            "context_provenance": {},
        }

        # Build context inheritance mappings
        parent_contexts = {}
        child_contexts = {}

        for restaurant in restaurant_data:
            if hasattr(restaurant, "page_metadata") and restaurant.page_metadata:
                page_meta = restaurant.page_metadata
                entity_id = page_meta.get("entity_id")
                page_type = page_meta.get("page_type")
                parent_id = page_meta.get("parent_id")

                # Collect parent contexts
                if page_type == "directory" and "common_context" in page_meta:
                    parent_contexts[entity_id] = page_meta["common_context"]

                # Collect child contexts and inheritance data
                if parent_id:
                    child_contexts[entity_id] = {
                        "parent_id": parent_id,
                        "inherited_context": page_meta.get("inherited_context", {}),
                        "child_overrides": page_meta.get("child_overrides", {}),
                        "restaurant_name": restaurant.name,
                    }

        # Build inheritance rules
        context_inheritance["inheritance_rules"] = parent_contexts

        # Map child overrides
        for child_id, child_info in child_contexts.items():
            parent_id = child_info["parent_id"]
            if parent_id in parent_contexts:
                context_inheritance["child_overrides"][child_id] = {
                    "parent_context": parent_contexts[parent_id],
                    "inherited_context": child_info["inherited_context"],
                    "child_specific_overrides": child_info["child_overrides"],
                    "restaurant_name": child_info["restaurant_name"],
                }

                # Track context provenance
                context_inheritance["context_provenance"][child_id] = {
                    "inherited_from": parent_id,
                    "inheritance_timestamp": datetime.now().isoformat(),
                }

        # Add context inheritance to indices
        if isinstance(indices, dict):
            indices["context_inheritance"] = context_inheritance
        else:
            result = json.loads(indices) if isinstance(indices, str) else {}
            result["context_inheritance"] = context_inheritance
            return result

        return indices

    # Private helper methods

    def _validate_input_data(self, restaurant_data: List[RestaurantData]) -> None:
        """Validate input restaurant data."""
        if not restaurant_data:
            raise ValueError("Restaurant data cannot be empty")
        
        if not isinstance(restaurant_data, list):
            raise TypeError("Restaurant data must be a list")

    def _validate_write_permissions(self) -> None:
        """Validate write permissions for output directory."""
        if not os.path.exists(self.config.output_directory):
            os.makedirs(self.config.output_directory, exist_ok=True)
        
        if not os.access(self.config.output_directory, os.W_OK):
            raise PermissionError(f"No write permission for directory: {self.config.output_directory}")

    def _handle_file_exists(self, file_path: str) -> None:
        """Handle existing file based on config."""
        if os.path.exists(file_path) and not self.config.allow_overwrite:
            raise FileExistsError(f"File already exists and overwrite not allowed: {file_path}")

    def _generate_relative_file_path(self, restaurant: RestaurantData) -> str:
        """Generate relative file path for a restaurant."""
        cuisine = restaurant.cuisine or "Unknown"
        safe_name = restaurant.name.replace(" ", "_").replace("/", "_")
        return f"{cuisine}/{safe_name}.txt"

    def _format_master_index_as_text(self, index_data: Dict[str, Any]) -> str:
        """Format master index data as human-readable text."""
        lines = [
            "Master Index - All Restaurant Entities",
            "=" * 40,
            "",
            f"Generated: {index_data['generation_timestamp']}",
            f"Total Entities: {index_data['total_entities']}",
            f"Schema Version: {index_data['schema_version']}",
            "",
            "Restaurant Listings:",
            "-" * 20,
            "",
        ]

        for i, entity in enumerate(index_data["entities"], 1):
            lines.append(f"{i}. {entity['name']}")
            if entity.get("cuisine"):
                lines.append(f"   Cuisine: {entity['cuisine']}")
            if entity.get("address"):
                lines.append(f"   Address: {entity['address']}")
            if entity.get("phone"):
                lines.append(f"   Phone: {entity['phone']}")
            lines.append(f"   File: {entity['file_path']}")
            lines.append("")

        # Add statistics if available
        if "statistics" in index_data:
            lines.extend(self._format_statistics_as_text(index_data["statistics"]))

        return "\n".join(lines)

    def _format_category_index_as_text(self, index_data: Dict[str, Any]) -> str:
        """Format category index data as human-readable text."""
        category = index_data["category"]
        lines = [
            f"{category} Category Index",
            "=" * (len(category) + 15),
            "",
            f"Generated: {index_data['generation_timestamp']}",
            f"Category: {category}",
            f"Entity Count: {index_data['entity_count']}",
            "",
            f"{category} Restaurants:",
            "-" * (len(category) + 13),
            "",
        ]

        for i, entity in enumerate(index_data["entities"], 1):
            lines.append(f"{i}. {entity['name']}")
            if entity.get("address"):
                lines.append(f"   Address: {entity['address']}")
            if entity.get("phone"):
                lines.append(f"   Phone: {entity['phone']}")
            lines.append(f"   File: {entity['file_path']}")
            lines.append("")

        return "\n".join(lines)

    def _format_statistics_as_text(self, statistics: Dict[str, Any]) -> List[str]:
        """Format statistics as text lines."""
        lines = [
            "",
            "Statistics:",
            "-" * 12,
            f"Total Restaurants: {statistics.get('total_entities', 0)}",
        ]

        if "cuisine_breakdown" in statistics:
            lines.append("")
            lines.append("Cuisine Breakdown:")
            for cuisine, count in statistics["cuisine_breakdown"].items():
                lines.append(f"  {cuisine}: {count}")

        return lines