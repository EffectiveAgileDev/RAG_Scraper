"""Index file generator for enhanced text files with comprehensive indexing features."""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from src.scraper.multi_strategy_scraper import RestaurantData
from src.common.generator_base import BaseFileGenerator, BaseGeneratorConfig
from src.common.validation_utils import ValidationUtils
from src.file_generator.index_file_builder import IndexFileBuilder


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

        # Initialize the index file builder
        self.builder = IndexFileBuilder(config)

    def generate_file(self, restaurant_data: List[RestaurantData], **kwargs) -> str:
        """Generate index files from restaurant data."""
        return self.builder.generate_comprehensive_indices(restaurant_data, **kwargs)

    def generate_master_index(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, str]:
        """Generate master index file listing all entities."""
        return self.builder.generate_master_index(restaurant_data)

    def generate_category_indices(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Dict[str, str]]:
        """Generate category-specific index files."""
        return self.builder.generate_category_indices(restaurant_data)

    def generate_indices_with_relationships(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate index files with relationship mapping."""
        return self.builder.generate_indices_with_relationships(restaurant_data)

    def generate_indices_with_search_metadata(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate index files with enhanced search metadata."""
        return self.builder.generate_indices_with_search_metadata(restaurant_data)

    def generate_json_indices(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, str]:
        """Generate JSON format indices for programmatic access."""
        return self.builder.generate_json_indices(restaurant_data)

    def generate_text_indices(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, str]:
        """Generate text format indices for human readability."""
        return self.builder.generate_text_indices(restaurant_data)

    def generate_indices_with_statistics(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate index files with comprehensive statistics."""
        return self.builder.generate_indices_with_statistics(restaurant_data)

    def generate_comprehensive_indices(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate comprehensive index files with all features enabled."""
        return self.builder.generate_comprehensive_indices(restaurant_data)

    def validate_index_integrity(self) -> Dict[str, Any]:
        """Validate index file integrity and consistency."""
        return self.builder.integrity_validator.validate_comprehensive_integrity(
            self.config.output_directory
        )

    def update_indices_incrementally(
        self, new_entities: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Update indices incrementally with new entities."""
        return self.builder.update_indices_incrementally(new_entities)

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
        return self.builder.generate_master_index_with_provenance(restaurant_data)

    def generate_indices_with_cross_page_relationships(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate indices with cross-page entity relationships."""
        return self.builder.generate_indices_with_cross_page_relationships(restaurant_data)

    def generate_unified_indices_from_multipage_data(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate unified index entries from multi-page data aggregation."""
        return self.builder.generate_unified_indices_from_multipage_data(restaurant_data)

    def generate_indices_with_temporal_awareness(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate index files with temporal awareness of extraction times."""
        return self.builder.generate_indices_with_temporal_awareness(restaurant_data)

    def generate_indices_with_context_inheritance(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate indices with context inheritance tracking from parent pages."""
        return self.builder.generate_indices_with_context_inheritance(restaurant_data)
