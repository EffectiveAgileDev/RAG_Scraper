"""Enhanced text file generator for RAG systems with advanced features."""
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from src.scraper.multi_strategy_scraper import RestaurantData
from src.common.generator_base import BaseFileGenerator, BaseGeneratorConfig
from src.common.validation_utils import ValidationUtils


@dataclass
class EnhancedTextFileConfig(BaseGeneratorConfig):
    """Enhanced configuration for text file generation."""

    hierarchical_structure: bool = True
    entity_organization: bool = True
    cross_references: bool = True
    rag_metadata: bool = True
    category_directories: bool = True
    comprehensive_indices: bool = True
    semantic_chunking: bool = True
    context_preservation: bool = True
    chunk_size_words: int = 500
    chunk_overlap_words: int = 50
    max_cross_references: int = 10

    def validate(self) -> None:
        """Validate configuration values."""
        validation_error = ValidationUtils.validate_not_empty(
            self.output_directory, "output_directory"
        )
        if validation_error:
            raise ValueError(validation_error)

        validation_error = ValidationUtils.validate_positive_number(
            self.chunk_size_words, "chunk_size_words"
        )
        if validation_error:
            raise ValueError(validation_error)

        validation_error = ValidationUtils.validate_positive_number(
            self.chunk_overlap_words, "chunk_overlap_words"
        )
        if validation_error:
            raise ValueError(validation_error)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "output_directory": self.output_directory,
            "allow_overwrite": self.allow_overwrite,
            "filename_pattern": self.filename_pattern,
            "hierarchical_structure": self.hierarchical_structure,
            "entity_organization": self.entity_organization,
            "cross_references": self.cross_references,
            "rag_metadata": self.rag_metadata,
            "category_directories": self.category_directories,
            "comprehensive_indices": self.comprehensive_indices,
            "semantic_chunking": self.semantic_chunking,
            "context_preservation": self.context_preservation,
            "chunk_size_words": self.chunk_size_words,
            "chunk_overlap_words": self.chunk_overlap_words,
            "max_cross_references": self.max_cross_references,
        }


class EnhancedTextFileGenerator(BaseFileGenerator):
    """Enhanced text file generator with hierarchical structure and RAG optimization."""

    def __init__(self, config: Optional[EnhancedTextFileConfig] = None):
        """Initialize enhanced text file generator."""
        if config is None:
            config = EnhancedTextFileConfig()

        super().__init__(config)
        self.config = config

        # Initialize helper components
        self.relationship_manager = EntityRelationshipManager()
        self.metadata_generator = RAGMetadataGenerator()
        self.semantic_chunker = SemanticChunker(
            chunk_size_words=config.chunk_size_words,
            overlap_words=config.chunk_overlap_words,
        )

    def generate_file(self, restaurant_data: List[RestaurantData], **kwargs) -> str:
        """Generate enhanced text files from restaurant data."""
        return self.generate_files(restaurant_data, **kwargs)

    def generate_files(
        self, restaurant_data: List[RestaurantData], **kwargs
    ) -> List[str]:
        """Generate enhanced text files with all enabled features."""
        self._validate_input_data(restaurant_data)
        self._validate_write_permissions()

        generated_files = []

        if self.config.entity_organization:
            generated_files.extend(self.generate_entity_based_files(restaurant_data))

        if self.config.hierarchical_structure:
            generated_files.extend(self.generate_hierarchical_files(restaurant_data))

        if self.config.comprehensive_indices:
            index_files = self.generate_indices(restaurant_data)
            generated_files.extend(index_files.get("all_files", []))

        return generated_files

    def generate_hierarchical_files(
        self, restaurant_data: List[RestaurantData]
    ) -> List[str]:
        """Generate files with hierarchical document structure."""
        relationships = self.relationship_manager.detect_relationships(restaurant_data)
        hierarchy_graph = self.relationship_manager.build_relationship_graph(
            restaurant_data
        )

        generated_files = []

        # Generate files for each hierarchy level
        for restaurant in restaurant_data:
            content = self._generate_hierarchical_content(restaurant, hierarchy_graph)

            if self.config.rag_metadata:
                content = self.generate_with_rag_metadata([restaurant], content)

            file_path = self._generate_output_path("txt")
            self._handle_file_exists(file_path)

            written_file = self._write_with_error_handling(file_path, content)
            generated_files.append(written_file)

        return generated_files

    def generate_entity_based_files(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, List[str]]:
        """Generate files organized by entity type."""
        # Group restaurants by cuisine type
        cuisine_groups = {}
        for restaurant in restaurant_data:
            cuisine = restaurant.cuisine or "Unknown"
            if cuisine not in cuisine_groups:
                cuisine_groups[cuisine] = []
            cuisine_groups[cuisine].append(restaurant)

        generated_files = {}

        if self.config.category_directories:
            base_dir = self.config.output_directory
            for cuisine, restaurants in cuisine_groups.items():
                cuisine_dir = os.path.join(base_dir, cuisine)
                Path(cuisine_dir).mkdir(parents=True, exist_ok=True)

                cuisine_files = []
                for restaurant in restaurants:
                    content = self._generate_entity_content(restaurant)

                    if self.config.cross_references:
                        content = self.generate_with_cross_references(
                            [restaurant], content
                        )

                    file_path = os.path.join(
                        cuisine_dir, f"{restaurant.name.replace(' ', '_')}.txt"
                    )
                    self._handle_file_exists(file_path)

                    written_file = self._write_with_error_handling(file_path, content)
                    cuisine_files.append(written_file)

                generated_files[cuisine] = cuisine_files

        return generated_files

    def generate_with_cross_references(
        self, restaurant_data: List[RestaurantData], content: Optional[str] = None
    ) -> str:
        """Generate content with cross-reference sections."""
        if content is None:
            content = self._generate_basic_content(restaurant_data[0])

        if len(restaurant_data) > 1:
            relationships = self.relationship_manager.detect_relationships(
                restaurant_data
            )
            cross_refs = self._format_cross_references(relationships)
            content += f"\n\nCross-References:\n{cross_refs}"

        return content

    def generate_with_rag_metadata(
        self, restaurant_data: List[RestaurantData], content: Optional[str] = None
    ) -> str:
        """Generate content with RAG-optimized metadata headers."""
        if content is None:
            content = self._generate_basic_content(restaurant_data[0])

        restaurant = restaurant_data[0]
        metadata_header = self.metadata_generator.generate_metadata_header(restaurant)

        return f"{metadata_header}\n\n{content}"

    def generate_category_directories(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, str]:
        """Create category-based output directory structure."""
        base_dir = self.config.output_directory
        created_directories = {}

        # Get unique cuisine types
        cuisines = set(r.cuisine for r in restaurant_data if r.cuisine)

        for cuisine in cuisines:
            cuisine_dir = os.path.join(base_dir, cuisine)
            Path(cuisine_dir).mkdir(parents=True, exist_ok=True)
            created_directories[cuisine] = cuisine_dir

        return created_directories

    def generate_indices(self, restaurant_data: List[RestaurantData]) -> Dict[str, Any]:
        """Generate comprehensive index files."""
        # Master index
        master_index_content = self._generate_master_index(restaurant_data)
        master_index_path = os.path.join(
            self.config.output_directory, "master_index.txt"
        )
        self._write_with_error_handling(master_index_path, master_index_content)

        # Category indices
        category_indices = {}
        cuisine_groups = {}
        for restaurant in restaurant_data:
            cuisine = restaurant.cuisine or "Unknown"
            if cuisine not in cuisine_groups:
                cuisine_groups[cuisine] = []
            cuisine_groups[cuisine].append(restaurant)

        for cuisine, restaurants in cuisine_groups.items():
            category_index_content = self._generate_category_index(cuisine, restaurants)
            category_index_path = os.path.join(
                self.config.output_directory, f"{cuisine}_index.txt"
            )
            self._write_with_error_handling(category_index_path, category_index_content)
            category_indices[cuisine] = category_index_path

        return {
            "master_index": master_index_path,
            "category_indices": category_indices,
            "all_files": [master_index_path] + list(category_indices.values()),
        }

    def generate_with_context_preservation(
        self, restaurant_data: List[RestaurantData]
    ) -> str:
        """Generate content preserving extraction context."""
        restaurant = restaurant_data[0]

        context_info = {
            "extraction_timestamp": datetime.now().isoformat(),
            "source_pages": getattr(restaurant, "source_urls", []),
            "extraction_methods": restaurant.sources,
            "confidence_scores": getattr(restaurant, "confidence_scores", {}),
        }

        context_header = "---\n"
        for key, value in context_info.items():
            context_header += f"{key}: {value}\n"
        context_header += "---\n"

        content = self._generate_basic_content(restaurant)

        return f"{context_header}\n{content}"

    def generate_semantic_chunks(
        self, restaurant_data: List[RestaurantData]
    ) -> List[str]:
        """Generate RAG-friendly semantic chunks."""
        chunks = []

        for restaurant in restaurant_data:
            content = self._generate_basic_content(restaurant)
            restaurant_chunks = self.semantic_chunker.chunk_by_semantic_boundaries(
                content
            )

            # Add context preservation to each chunk
            contextual_chunks = []
            for i, chunk in enumerate(restaurant_chunks):
                chunk_with_context = self.semantic_chunker.create_contextual_chunks(
                    restaurant, chunk, i
                )
                contextual_chunks.append(chunk_with_context)

            chunks.extend(contextual_chunks)

        return chunks

    def validate_output_integrity(self, generated_files: List[str]) -> Dict[str, Any]:
        """Validate output file integrity."""
        validation_result = {
            "valid": True,
            "required_files_present": True,
            "cross_references_valid": True,
            "metadata_complete": True,
            "issues": [],
        }

        # Check that all files exist
        for file_path in generated_files:
            if not os.path.exists(file_path):
                validation_result["required_files_present"] = False
                validation_result["issues"].append(f"Missing file: {file_path}")

        # Validate file contents
        for file_path in generated_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    if not content.strip():
                        validation_result["issues"].append(f"Empty file: {file_path}")

                except Exception as e:
                    validation_result["issues"].append(
                        f"Error reading file {file_path}: {str(e)}"
                    )

        validation_result["valid"] = len(validation_result["issues"]) == 0

        return validation_result

    def _generate_hierarchical_content(
        self, restaurant: RestaurantData, hierarchy_graph: Dict
    ) -> str:
        """Generate content with hierarchical structure."""
        content = self._generate_basic_content(restaurant)

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

    def _generate_entity_content(self, restaurant: RestaurantData) -> str:
        """Generate content for entity-based organization."""
        content = self._generate_basic_content(restaurant)

        # Add entity type information
        content += f"\n\nEntity Type: Restaurant\n"
        content += f"Entity Category: {restaurant.cuisine or 'Unknown'}\n"
        content += f"Extraction Sources: {', '.join(restaurant.sources)}\n"

        return content

    def _generate_basic_content(self, restaurant: RestaurantData) -> str:
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
            menu_lines = self._format_menu_items(restaurant.menu_items)
            lines.extend(menu_lines)

        if restaurant.cuisine:
            lines.append("")
            lines.append(f"CUISINE: {restaurant.cuisine}")

        return "\n".join(lines)

    def _format_menu_items(self, menu_items: Dict[str, List[str]]) -> List[str]:
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

    def _format_cross_references(self, relationships: List[Dict]) -> str:
        """Format cross-references for output."""
        if not relationships:
            return "No related entities found."

        cross_ref_lines = []

        for relationship in relationships[: self.config.max_cross_references]:
            rel_type = relationship.get("type", "related")
            target = relationship.get("target", "Unknown")
            cross_ref_lines.append(f"- {rel_type.title()}: {target}")

        return "\n".join(cross_ref_lines)

    def _generate_master_index(self, restaurant_data: List[RestaurantData]) -> str:
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

    def _generate_category_index(
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


class SemanticChunker:
    """Handles semantic chunking of restaurant content."""

    def __init__(self, chunk_size_words: int = 500, overlap_words: int = 50):
        """Initialize semantic chunker."""
        self.chunk_size_words = chunk_size_words
        self.overlap_words = overlap_words

    def chunk_by_semantic_boundaries(self, content: str) -> List[str]:
        """Chunk content by semantic boundaries."""
        # Split content into sections based on double newlines
        sections = content.split("\n\n")

        chunks = []
        current_chunk = []
        current_word_count = 0

        for section in sections:
            section_words = len(section.split())

            # If adding this section would exceed chunk size, finalize current chunk
            if (
                current_word_count + section_words > self.chunk_size_words
                and current_chunk
            ):
                chunk_content = "\n\n".join(current_chunk)
                chunks.append(f"CHUNK_START\n{chunk_content}\nCHUNK_END")

                # Start new chunk with overlap from previous chunk
                if self.overlap_words > 0 and current_chunk:
                    overlap_text = current_chunk[-1]
                    overlap_word_count = len(overlap_text.split())
                    if overlap_word_count <= self.overlap_words:
                        current_chunk = [overlap_text]
                        current_word_count = overlap_word_count
                    else:
                        current_chunk = []
                        current_word_count = 0
                else:
                    current_chunk = []
                    current_word_count = 0

            current_chunk.append(section)
            current_word_count += section_words

        # Add final chunk if there's remaining content
        if current_chunk:
            chunk_content = "\n\n".join(current_chunk)
            chunks.append(f"CHUNK_START\n{chunk_content}\nCHUNK_END")

        return chunks

    def create_contextual_chunks(
        self,
        restaurant: RestaurantData,
        chunk_content: Optional[str] = None,
        chunk_index: int = 0,
    ) -> str:
        """Create chunks with preserved context."""
        if chunk_content is None:
            # Generate chunk from restaurant data
            content_parts = []

            content_parts.append(f"Restaurant: {restaurant.name}")

            if restaurant.address:
                content_parts.append(f"Address: {restaurant.address}")

            if restaurant.cuisine:
                content_parts.append(f"Cuisine: {restaurant.cuisine}")

            chunk_content = "\n".join(content_parts)

        # Add context header to chunk
        context_header = f"[CHUNK {chunk_index + 1} - {restaurant.name}]"

        return f"{context_header}\n{chunk_content}"

    def handle_overlapping_information(self, content: str) -> List[str]:
        """Handle overlapping information in chunks."""
        # Simple deduplication approach
        lines = content.split("\n")
        unique_lines = []
        seen_lines = set()

        for line in lines:
            line_normalized = line.strip().lower()
            if line_normalized and line_normalized not in seen_lines:
                unique_lines.append(line)
                seen_lines.add(line_normalized)
            elif not line.strip():  # Keep empty lines for formatting
                unique_lines.append(line)

        return ["\n".join(unique_lines)]
