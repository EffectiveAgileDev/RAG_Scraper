"""Unit tests for IndexFileBuilder class."""
import os
import json
import tempfile
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

from src.scraper.multi_strategy_scraper import RestaurantData


class TestIndexFileBuilder:
    """Test cases for IndexFileBuilder class."""

    def test_init_with_helper_components(self):
        """Test initialization with helper components."""
        from src.file_generator.index_file_builder import IndexFileBuilder
        from src.file_generator.index_file_generator import IndexFileConfig

        config = IndexFileConfig()
        builder = IndexFileBuilder(config)

        assert builder is not None
        assert builder.config == config
        assert hasattr(builder, 'search_metadata_generator')
        assert hasattr(builder, 'statistics_generator')
        assert hasattr(builder, 'relationship_mapper')
        assert hasattr(builder, 'integrity_validator')

    def test_generate_master_index_json_format(self):
        """Test generation of master index in JSON format."""
        from src.file_generator.index_file_builder import IndexFileBuilder
        from src.file_generator.index_file_generator import IndexFileConfig

        with tempfile.TemporaryDirectory() as temp_dir:
            config = IndexFileConfig(output_directory=temp_dir, generate_json=True)
            builder = IndexFileBuilder(config)

            restaurant_data = [
                RestaurantData(
                    name="Test Restaurant 1", cuisine="Italian", sources=["json-ld"]
                ),
                RestaurantData(
                    name="Test Restaurant 2", cuisine="Mexican", sources=["heuristic"]
                ),
            ]

            result = builder.generate_master_index(restaurant_data)

            assert result is not None
            assert "master_index.json" in result

            # Verify JSON file was created
            json_file = os.path.join(temp_dir, "master_index.json")
            assert os.path.exists(json_file)

    def test_generate_category_indices(self):
        """Test generation of category-specific index files."""
        from src.file_generator.index_file_builder import IndexFileBuilder
        from src.file_generator.index_file_generator import IndexFileConfig

        with tempfile.TemporaryDirectory() as temp_dir:
            config = IndexFileConfig(output_directory=temp_dir)
            builder = IndexFileBuilder(config)

            restaurant_data = [
                RestaurantData(
                    name="Italian Rest 1", cuisine="Italian", sources=["json-ld"]
                ),
                RestaurantData(
                    name="Italian Rest 2", cuisine="Italian", sources=["json-ld"]
                ),
                RestaurantData(
                    name="Mexican Rest 1", cuisine="Mexican", sources=["json-ld"]
                ),
            ]

            result = builder.generate_category_indices(restaurant_data)

            # Should generate indices for each cuisine category
            assert isinstance(result, dict)
            assert "Italian" in result
            assert "Mexican" in result

    def test_generate_indices_with_relationships(self):
        """Test generation of indices with relationship mapping."""
        from src.file_generator.index_file_builder import IndexFileBuilder
        from src.file_generator.index_file_generator import IndexFileConfig

        config = IndexFileConfig()
        builder = IndexFileBuilder(config)

        # Create restaurants with parent-child relationship
        parent_restaurant = RestaurantData(
            name="Tony's Italian Restaurant", sources=["json-ld"]
        )
        child_restaurant = RestaurantData(
            name="Tony's Italian Restaurant - Downtown", sources=["json-ld"]
        )

        restaurant_data = [parent_restaurant, child_restaurant]

        result = builder.generate_indices_with_relationships(restaurant_data)

        assert result is not None
        assert "master_index" in result
        assert "category_indices" in result
        assert "relationships" in result

    def test_generate_indices_with_search_metadata(self):
        """Test generation of indices with enhanced search metadata."""
        from src.file_generator.index_file_builder import IndexFileBuilder
        from src.file_generator.index_file_generator import IndexFileConfig

        config = IndexFileConfig()
        builder = IndexFileBuilder(config)

        restaurant_data = [
            RestaurantData(
                name="Search Test Restaurant",
                cuisine="Italian",
                address="123 Main St",
                menu_items={"entrees": ["pasta", "pizza"]},
                sources=["json-ld"],
            )
        ]

        result = builder.generate_indices_with_search_metadata(restaurant_data)

        assert result is not None
        assert "master_index" in result
        assert "category_indices" in result
        assert "search_metadata" in result

    def test_generate_json_indices(self):
        """Test JSON format generation for programmatic access."""
        from src.file_generator.index_file_builder import IndexFileBuilder
        from src.file_generator.index_file_generator import IndexFileConfig

        with tempfile.TemporaryDirectory() as temp_dir:
            config = IndexFileConfig(output_directory=temp_dir, generate_json=True)
            builder = IndexFileBuilder(config)

            restaurant_data = [
                RestaurantData(name="JSON Test Restaurant", sources=["json-ld"])
            ]

            result = builder.generate_json_indices(restaurant_data)

            # Should generate valid JSON structure
            assert result is not None
            assert "master_index" in result
            assert "category_indices" in result

    def test_generate_text_indices(self):
        """Test text format generation for human readability."""
        from src.file_generator.index_file_builder import IndexFileBuilder
        from src.file_generator.index_file_generator import IndexFileConfig

        with tempfile.TemporaryDirectory() as temp_dir:
            config = IndexFileConfig(output_directory=temp_dir, generate_text=True)
            builder = IndexFileBuilder(config)

            restaurant_data = [
                RestaurantData(name="Text Format Restaurant", sources=["json-ld"])
            ]

            result = builder.generate_text_indices(restaurant_data)

            assert result is not None
            assert "master_index" in result
            assert "category_indices" in result

    def test_generate_indices_with_statistics(self):
        """Test generation of indices with comprehensive statistics."""
        from src.file_generator.index_file_builder import IndexFileBuilder
        from src.file_generator.index_file_generator import IndexFileConfig

        config = IndexFileConfig(include_statistics=True)
        builder = IndexFileBuilder(config)

        restaurant_data = [
            RestaurantData(
                name="Stats Restaurant 1", cuisine="Italian", sources=["json-ld"]
            ),
            RestaurantData(
                name="Stats Restaurant 2", cuisine="Mexican", sources=["json-ld"]
            ),
            RestaurantData(
                name="Stats Restaurant 3", cuisine="Italian", sources=["json-ld"]
            ),
        ]

        result = builder.generate_indices_with_statistics(restaurant_data)

        assert result is not None
        assert "master_index" in result
        assert "category_indices" in result
        assert "detailed_statistics" in result

    def test_generate_comprehensive_indices(self):
        """Test generation of comprehensive index files with all features enabled."""
        from src.file_generator.index_file_builder import IndexFileBuilder
        from src.file_generator.index_file_generator import IndexFileConfig

        with tempfile.TemporaryDirectory() as temp_dir:
            config = IndexFileConfig(output_directory=temp_dir)
            builder = IndexFileBuilder(config)

            restaurant_data = [
                RestaurantData(
                    name="Comprehensive Test Restaurant", 
                    cuisine="Italian", 
                    sources=["json-ld"]
                )
            ]

            result = builder.generate_comprehensive_indices(restaurant_data)

            assert result is not None
            assert "master_index" in result
            assert "category_indices" in result

    def test_update_indices_incrementally(self):
        """Test incremental index updates."""
        from src.file_generator.index_file_builder import IndexFileBuilder
        from src.file_generator.index_file_generator import IndexFileConfig

        with tempfile.TemporaryDirectory() as temp_dir:
            config = IndexFileConfig(output_directory=temp_dir)
            builder = IndexFileBuilder(config)

            # Add new entities
            new_entities = [
                RestaurantData(
                    name="New Restaurant", cuisine="French", sources=["json-ld"]
                )
            ]

            result = builder.update_indices_incrementally(new_entities)

            assert result is not None
            assert "status" in result

    def test_format_master_index_as_text(self):
        """Test formatting master index data as human-readable text."""
        from src.file_generator.index_file_builder import IndexFileBuilder
        from src.file_generator.index_file_generator import IndexFileConfig

        config = IndexFileConfig()
        builder = IndexFileBuilder(config)

        index_data = {
            "generation_timestamp": "2024-03-15T10:30:00Z",
            "total_entities": 2,
            "schema_version": "1.0.0",
            "entities": [
                {
                    "name": "Test Restaurant",
                    "cuisine": "Italian",
                    "address": "123 Main St",
                    "phone": "555-0123",
                    "file_path": "Italian/Test_Restaurant.txt"
                }
            ]
        }

        result = builder._format_master_index_as_text(index_data)

        assert isinstance(result, str)
        assert "Master Index" in result
        assert "Test Restaurant" in result

    def test_format_category_index_as_text(self):
        """Test formatting category index data as human-readable text."""
        from src.file_generator.index_file_builder import IndexFileBuilder
        from src.file_generator.index_file_generator import IndexFileConfig

        config = IndexFileConfig()
        builder = IndexFileBuilder(config)

        index_data = {
            "generation_timestamp": "2024-03-15T10:30:00Z",
            "category": "Italian",
            "entity_count": 1,
            "entities": [
                {
                    "name": "Test Italian Restaurant",
                    "address": "123 Main St",
                    "phone": "555-0123",
                    "file_path": "Italian/Test_Italian_Restaurant.txt"
                }
            ]
        }

        result = builder._format_category_index_as_text(index_data)

        assert isinstance(result, str)
        assert "Italian Category Index" in result
        assert "Test Italian Restaurant" in result

    # Multi-page generation methods tests

    def test_generate_master_index_with_provenance(self):
        """Test generation of master index with page provenance tracking."""
        from src.file_generator.index_file_builder import IndexFileBuilder
        from src.file_generator.index_file_generator import IndexFileConfig

        config = IndexFileConfig(include_provenance=True)
        builder = IndexFileBuilder(config)

        restaurant_data = [
            RestaurantData(
                name="Provenance Test Restaurant",
                cuisine="Italian",
                sources=["json-ld"]
            )
        ]

        # Add page metadata
        restaurant_data[0].page_metadata = {
            "page_type": "detail",
            "source_url": "/restaurants/test",
            "entity_id": "rest_001",
            "extraction_timestamp": "2025-06-24T10:00:00Z"
        }

        result = builder.generate_master_index_with_provenance(restaurant_data)

        assert result is not None
        # Should include provenance data when config enabled

    def test_generate_indices_with_cross_page_relationships(self):
        """Test generation of indices with cross-page entity relationships."""
        from src.file_generator.index_file_builder import IndexFileBuilder
        from src.file_generator.index_file_generator import IndexFileConfig

        config = IndexFileConfig(track_cross_page_relationships=True)
        builder = IndexFileBuilder(config)

        restaurant_data = [
            RestaurantData(name="Parent Restaurant", sources=["json-ld"]),
            RestaurantData(name="Child Restaurant", sources=["json-ld"])
        ]

        # Add page metadata for parent-child relationship
        restaurant_data[0].page_metadata = {"entity_id": "parent_001", "page_type": "directory"}
        restaurant_data[1].page_metadata = {"entity_id": "child_001", "parent_id": "parent_001", "page_type": "detail"}

        result = builder.generate_indices_with_cross_page_relationships(restaurant_data)

        assert result is not None
        # Should include cross-page relationships when config enabled

    def test_generate_unified_indices_from_multipage_data(self):
        """Test generation of unified index entries from multi-page data aggregation."""
        from src.file_generator.index_file_builder import IndexFileBuilder
        from src.file_generator.index_file_generator import IndexFileConfig

        config = IndexFileConfig()
        builder = IndexFileBuilder(config)

        restaurant_data = [
            RestaurantData(name="Unified Restaurant", cuisine="Italian", sources=["json-ld"])
        ]

        # Add page metadata
        restaurant_data[0].page_metadata = {
            "entity_id": "unified_001",
            "page_type": "detail"
        }

        result = builder.generate_unified_indices_from_multipage_data(restaurant_data)

        assert result is not None
        assert "unified_entities" in result

    def test_generate_indices_with_temporal_awareness(self):
        """Test generation of indices with temporal awareness of extraction times."""
        from src.file_generator.index_file_builder import IndexFileBuilder
        from src.file_generator.index_file_generator import IndexFileConfig

        config = IndexFileConfig(enable_temporal_awareness=True)
        builder = IndexFileBuilder(config)

        restaurant_data = [
            RestaurantData(name="Temporal Restaurant", sources=["json-ld"])
        ]

        # Add page metadata with timestamp
        restaurant_data[0].page_metadata = {
            "entity_id": "temporal_001",
            "extraction_timestamp": "2025-06-24T10:00:00Z"
        }

        result = builder.generate_indices_with_temporal_awareness(restaurant_data)

        assert result is not None
        # Should include temporal metadata when config enabled

    def test_generate_indices_with_context_inheritance(self):
        """Test generation of indices with context inheritance tracking from parent pages."""
        from src.file_generator.index_file_builder import IndexFileBuilder
        from src.file_generator.index_file_generator import IndexFileConfig

        config = IndexFileConfig(support_context_inheritance=True)
        builder = IndexFileBuilder(config)

        restaurant_data = [
            RestaurantData(name="Context Restaurant", sources=["json-ld"])
        ]

        # Add page metadata with context inheritance
        restaurant_data[0].page_metadata = {
            "entity_id": "context_001",
            "parent_id": "parent_001",
            "inherited_context": {"location": "Downtown"}
        }

        result = builder.generate_indices_with_context_inheritance(restaurant_data)

        assert result is not None
        # Should include context inheritance data when config enabled