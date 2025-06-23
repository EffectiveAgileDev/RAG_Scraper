"""Index file generator for enhanced text files with comprehensive indexing features."""
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from collections import defaultdict

from src.scraper.multi_strategy_scraper import RestaurantData
from src.common.generator_base import BaseFileGenerator, BaseGeneratorConfig
from src.common.validation_utils import ValidationUtils


@dataclass
class IndexFileConfig(BaseGeneratorConfig):
    """Configuration for index file generation."""

    generate_json: bool = True
    generate_text: bool = True
    include_statistics: bool = True
    include_relationships: bool = True
    include_search_metadata: bool = True
    schema_version: str = "1.0.0"
    # Multi-page support options
    include_provenance: bool = False
    track_cross_page_relationships: bool = False
    enable_temporal_awareness: bool = False
    support_context_inheritance: bool = False

    def validate(self) -> None:
        """Validate configuration values."""
        validation_error = ValidationUtils.validate_not_empty(
            self.output_directory, "output_directory"
        )
        if validation_error:
            raise ValueError(validation_error)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "output_directory": self.output_directory,
            "allow_overwrite": self.allow_overwrite,
            "filename_pattern": self.filename_pattern,
            "generate_json": self.generate_json,
            "generate_text": self.generate_text,
            "include_statistics": self.include_statistics,
            "include_relationships": self.include_relationships,
            "include_search_metadata": self.include_search_metadata,
            "schema_version": self.schema_version,
            "include_provenance": self.include_provenance,
            "track_cross_page_relationships": self.track_cross_page_relationships,
            "enable_temporal_awareness": self.enable_temporal_awareness,
            "support_context_inheritance": self.support_context_inheritance,
        }


class IndexFileGenerator(BaseFileGenerator):
    """Index file generator with comprehensive indexing capabilities."""

    def __init__(self, config: Optional[IndexFileConfig] = None):
        """Initialize index file generator."""
        if config is None:
            config = IndexFileConfig()

        super().__init__(config)
        self.config = config

        # Initialize helper components
        self.search_metadata_generator = IndexSearchMetadataGenerator()
        self.statistics_generator = IndexStatisticsGenerator()
        self.relationship_mapper = IndexRelationshipMapper()
        self.integrity_validator = IndexIntegrityValidator()

    def generate_file(self, restaurant_data: List[RestaurantData], **kwargs) -> str:
        """Generate index files from restaurant data."""
        return self.generate_comprehensive_indices(restaurant_data, **kwargs)

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

    def validate_index_integrity(self) -> Dict[str, Any]:
        """Validate index file integrity and consistency."""
        return self.integrity_validator.validate_comprehensive_integrity(
            self.config.output_directory
        )

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


class IndexStatisticsGenerator:
    """Generates comprehensive statistics for index files."""

    def calculate_entity_statistics(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Calculate entity statistics."""
        stats = {
            "total_entities": len(restaurant_data),
            "cuisine_breakdown": defaultdict(int),
            "source_breakdown": defaultdict(int),
            "completeness_metrics": {},
        }

        # Calculate cuisine breakdown
        for restaurant in restaurant_data:
            cuisine = restaurant.cuisine or "Unknown"
            stats["cuisine_breakdown"][cuisine] += 1

        # Calculate source breakdown
        for restaurant in restaurant_data:
            for source in restaurant.sources:
                stats["source_breakdown"][source] += 1

        # Convert defaultdicts to regular dicts
        stats["cuisine_breakdown"] = dict(stats["cuisine_breakdown"])
        stats["source_breakdown"] = dict(stats["source_breakdown"])

        return stats

    def calculate_file_size_statistics(self, file_paths: List[str]) -> Dict[str, Any]:
        """Calculate file size statistics."""
        total_size = 0
        file_sizes = []

        for file_path in file_paths:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                total_size += size
                file_sizes.append(size)

        stats = {
            "total_size": total_size,
            "file_count": len(file_sizes),
            "average_size": total_size / len(file_sizes) if file_sizes else 0,
            "min_size": min(file_sizes) if file_sizes else 0,
            "max_size": max(file_sizes) if file_sizes else 0,
        }

        return stats

    def calculate_data_quality_metrics(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Calculate data quality metrics."""
        total_entities = len(restaurant_data)
        if total_entities == 0:
            return {"completeness_score": 0, "field_coverage": {}}

        field_counts = {
            "name": 0,
            "address": 0,
            "phone": 0,
            "cuisine": 0,
            "menu_items": 0,
            "price_range": 0,
            "hours": 0,
        }

        for restaurant in restaurant_data:
            if restaurant.name:
                field_counts["name"] += 1
            if restaurant.address:
                field_counts["address"] += 1
            if restaurant.phone:
                field_counts["phone"] += 1
            if restaurant.cuisine:
                field_counts["cuisine"] += 1
            if restaurant.menu_items:
                field_counts["menu_items"] += 1
            if restaurant.price_range:
                field_counts["price_range"] += 1
            if restaurant.hours:
                field_counts["hours"] += 1

        field_coverage = {
            field: count / total_entities for field, count in field_counts.items()
        }
        completeness_score = sum(field_coverage.values()) / len(field_coverage)

        return {
            "completeness_score": completeness_score,
            "field_coverage": field_coverage,
            "total_entities_analyzed": total_entities,
        }

    def generate_generation_metadata(self) -> Dict[str, Any]:
        """Generate metadata about the generation process."""
        return {
            "generation_timestamp": datetime.now().isoformat(),
            "generator_version": "1.0.0",
            "schema_version": "1.0.0",
        }


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


class IndexIntegrityValidator:
    """Validates index file integrity and consistency."""

    def validate_comprehensive_integrity(self, output_directory: str) -> Dict[str, Any]:
        """Validate comprehensive index integrity."""
        validation_result = {
            "valid": True,
            "file_references_valid": True,
            "entity_consistency_valid": True,
            "category_assignments_valid": True,
            "no_orphaned_references": True,
            "issues": [],
        }

        try:
            # Load master index
            master_index_path = os.path.join(output_directory, "master_index.json")
            if os.path.exists(master_index_path):
                with open(master_index_path, "r", encoding="utf-8") as f:
                    master_index = json.load(f)

                # Validate file references
                file_validation = self.validate_file_references(
                    master_index, output_directory
                )
                if not file_validation["valid"]:
                    validation_result["file_references_valid"] = False
                    validation_result["issues"].extend(
                        file_validation.get("issues", [])
                    )

            validation_result["valid"] = (
                validation_result["file_references_valid"]
                and validation_result["entity_consistency_valid"]
                and validation_result["category_assignments_valid"]
                and validation_result["no_orphaned_references"]
            )

        except Exception as e:
            validation_result["valid"] = False
            validation_result["issues"].append(f"Validation error: {str(e)}")

        return validation_result

    def validate_file_references(
        self, index_data: Dict[str, Any], base_directory: str
    ) -> Dict[str, Any]:
        """Validate that all file references in index exist."""
        validation_result = {"valid": True, "missing_files": [], "issues": []}

        for entity in index_data.get("entities", []):
            file_path = entity.get("file_path")
            if file_path:
                full_path = os.path.join(base_directory, file_path)
                if not os.path.exists(full_path):
                    validation_result["missing_files"].append(file_path)
                    validation_result["issues"].append(f"Missing file: {file_path}")

        validation_result["valid"] = len(validation_result["missing_files"]) == 0
        return validation_result

    def validate_entity_id_consistency(
        self, master_index: Dict[str, Any], category_indices: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate entity ID consistency across indices."""
        consistency_result = {"consistent": True, "inconsistencies": [], "issues": []}

        # Extract entity IDs from master index
        master_ids = set()
        for entity in master_index.get("entities", []):
            master_ids.add(entity.get("id"))

        # Check consistency with category indices
        for category, category_data in category_indices.items():
            for entity in category_data.get("entities", []):
                entity_id = entity.get("id")
                if entity_id not in master_ids:
                    consistency_result["inconsistencies"].append(
                        f"Entity {entity_id} in {category} not found in master index"
                    )

        consistency_result["consistent"] = (
            len(consistency_result["inconsistencies"]) == 0
        )
        return consistency_result

    def validate_category_assignments(
        self,
        restaurant_data: List[RestaurantData],
        category_indices: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        """Validate category assignments are accurate."""
        validation_result = {"accurate": True, "misassignments": [], "issues": []}

        # Check each restaurant's category assignment
        for restaurant in restaurant_data:
            expected_category = restaurant.cuisine or "Unknown"
            found_in_categories = []

            for category, restaurant_names in category_indices.items():
                if restaurant.name in restaurant_names:
                    found_in_categories.append(category)

            if expected_category not in found_in_categories:
                validation_result["misassignments"].append(
                    f"Restaurant {restaurant.name} expected in {expected_category}, found in {found_in_categories}"
                )

        validation_result["accurate"] = len(validation_result["misassignments"]) == 0
        return validation_result

    def detect_orphaned_references(
        self, index_data: Dict[str, Any], all_entity_ids: List[str]
    ) -> List[str]:
        """Detect orphaned references in index data."""
        orphaned_refs = []
        entity_id_set = set(all_entity_ids)

        for entity in index_data.get("entities", []):
            related_to = entity.get("related_to", [])
            for related_id in related_to:
                if related_id not in entity_id_set:
                    orphaned_refs.append(related_id)

        return orphaned_refs
