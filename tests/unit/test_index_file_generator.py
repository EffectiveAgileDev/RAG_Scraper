"""Unit tests for index file generator classes."""
import os
import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.scraper.multi_strategy_scraper import RestaurantData


class TestIndexFileGenerator:
    """Test cases for IndexFileGenerator class."""

    def test_init_with_default_config(self):
        """Test initialization with default configuration."""
        from src.file_generator.index_file_generator import (
            IndexFileGenerator,
        )

        generator = IndexFileGenerator()

        assert generator is not None
        assert generator.config is not None

    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        from src.file_generator.index_file_generator import (
            IndexFileGenerator,
            IndexFileConfig,
        )

        config = IndexFileConfig(
            generate_json=True,
            generate_text=True,
            include_statistics=True,
            include_relationships=True,
        )
        generator = IndexFileGenerator(config)

        assert generator is not None
        assert generator.config == config

    def test_generate_master_index_json_format(self):
        """Test generation of master index in JSON format."""
        import tempfile
        from src.file_generator.index_file_generator import (
            IndexFileGenerator,
            IndexFileConfig,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            config = IndexFileConfig(output_directory=temp_dir, generate_json=True)
            generator = IndexFileGenerator(config)

            restaurant_data = [
                RestaurantData(
                    name="Test Restaurant 1", cuisine="Italian", sources=["json-ld"]
                ),
                RestaurantData(
                    name="Test Restaurant 2", cuisine="Mexican", sources=["heuristic"]
                ),
            ]

            result = generator.generate_master_index(restaurant_data)

            assert result is not None
            assert "master_index.json" in result

            # Verify JSON file was created
            json_file = os.path.join(temp_dir, "master_index.json")
            assert os.path.exists(json_file)

    def test_generate_category_indices(self):
        """Test generation of category-specific index files."""
        import tempfile
        from src.file_generator.index_file_generator import (
            IndexFileGenerator,
            IndexFileConfig,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            config = IndexFileConfig(output_directory=temp_dir)
            generator = IndexFileGenerator(config)

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

            result = generator.generate_category_indices(restaurant_data)

            # Should generate indices for each cuisine category
            assert isinstance(result, dict)
            assert "Italian" in result
            assert "Mexican" in result

    def test_include_entity_relationship_maps(self):
        """Test inclusion of entity relationship maps in indices."""
        from src.file_generator.index_file_generator import (
            IndexFileGenerator,
        )

        generator = IndexFileGenerator()

        # Create restaurants with parent-child relationship
        parent_restaurant = RestaurantData(
            name="Tony's Italian Restaurant", sources=["json-ld"]
        )
        child_restaurant = RestaurantData(
            name="Tony's Italian Restaurant - Downtown", sources=["json-ld"]
        )

        restaurant_data = [parent_restaurant, child_restaurant]

        result = generator.generate_indices_with_relationships(restaurant_data)

        assert result is not None
        # Should detect and map parent-child relationship

    def test_add_search_metadata(self):
        """Test addition of search metadata to index files."""
        from src.file_generator.index_file_generator import (
            IndexFileGenerator,
        )

        generator = IndexFileGenerator()

        restaurant_data = [
            RestaurantData(
                name="Search Test Restaurant",
                cuisine="Italian",
                address="123 Main St",
                menu_items={"entrees": ["pasta", "pizza"]},
                sources=["json-ld"],
            )
        ]

        result = generator.generate_indices_with_search_metadata(restaurant_data)

        assert result is not None
        # Should include searchable keywords, cuisine filters, etc.

    def test_json_format_programmatic_access(self):
        """Test JSON format generation for programmatic access."""
        import tempfile
        from src.file_generator.index_file_generator import (
            IndexFileGenerator,
            IndexFileConfig,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            config = IndexFileConfig(output_directory=temp_dir, generate_json=True)
            generator = IndexFileGenerator(config)

            restaurant_data = [
                RestaurantData(name="JSON Test Restaurant", sources=["json-ld"])
            ]

            result = generator.generate_json_indices(restaurant_data)

            # Should generate valid JSON structure
            assert result is not None

            # Verify JSON is valid by loading it
            json_file_path = result.get("master_index")
            if json_file_path and os.path.exists(json_file_path):
                with open(json_file_path, "r") as f:
                    json_data = json.load(f)
                assert isinstance(json_data, dict)

    def test_text_format_human_readability(self):
        """Test text format generation for human readability."""
        import tempfile
        from src.file_generator.index_file_generator import (
            IndexFileGenerator,
            IndexFileConfig,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            config = IndexFileConfig(output_directory=temp_dir, generate_text=True)
            generator = IndexFileGenerator(config)

            restaurant_data = [
                RestaurantData(name="Text Format Restaurant", sources=["json-ld"])
            ]

            result = generator.generate_text_indices(restaurant_data)

            assert result is not None
            # Should generate human-readable text format

    def test_include_comprehensive_statistics(self):
        """Test inclusion of comprehensive statistics in indices."""
        from src.file_generator.index_file_generator import (
            IndexFileGenerator,
            IndexFileConfig,
        )

        config = IndexFileConfig(include_statistics=True)
        generator = IndexFileGenerator(config)

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

        result = generator.generate_indices_with_statistics(restaurant_data)

        assert result is not None
        # Should include total counts, cuisine breakdown, etc.

    def test_handle_large_scale_data_efficiently(self):
        """Test handling of large-scale data sets efficiently."""
        import tempfile
        from src.file_generator.index_file_generator import (
            IndexFileGenerator,
            IndexFileConfig,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            config = IndexFileConfig(output_directory=temp_dir)
            generator = IndexFileGenerator(config)

            # Create large dataset (50+ restaurants)
            large_dataset = []
            for i in range(55):
                restaurant = RestaurantData(
                    name=f"Large Dataset Restaurant {i}",
                    cuisine=["Italian", "Mexican", "American"][i % 3],
                    sources=["json-ld"],
                )
                large_dataset.append(restaurant)

            result = generator.generate_comprehensive_indices(large_dataset)

            # Should handle large datasets efficiently
            assert result is not None
            assert len(large_dataset) == 55

    def test_validate_index_integrity(self):
        """Test validation of index file integrity."""
        import tempfile
        from src.file_generator.index_file_generator import (
            IndexFileGenerator,
            IndexFileConfig,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            config = IndexFileConfig(output_directory=temp_dir)
            generator = IndexFileGenerator(config)

            # Create some test data and indices
            restaurant_data = [
                RestaurantData(name="Integrity Test Restaurant", sources=["json-ld"])
            ]

            # Generate indices first
            generator.generate_comprehensive_indices(restaurant_data)

            # Now validate integrity
            validation_result = generator.validate_index_integrity()

            assert isinstance(validation_result, dict)
            assert "valid" in validation_result

    def test_incremental_index_updates(self):
        """Test incremental index updates."""
        import tempfile
        from src.file_generator.index_file_generator import (
            IndexFileGenerator,
            IndexFileConfig,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            config = IndexFileConfig(output_directory=temp_dir)
            generator = IndexFileGenerator(config)

            # Create initial data
            initial_data = [
                RestaurantData(name="Initial Restaurant", sources=["json-ld"])
            ]

            # Generate initial indices
            generator.generate_comprehensive_indices(initial_data)

            # Add new entities
            new_entities = [
                RestaurantData(
                    name="New Restaurant", cuisine="French", sources=["json-ld"]
                )
            ]

            result = generator.update_indices_incrementally(new_entities)

            assert result is not None
            # Should update indices without rebuilding from scratch


class TestIndexFileConfig:
    """Test cases for IndexFileConfig class."""

    def test_default_config_values(self):
        """Test default configuration values."""
        from src.file_generator.index_file_generator import (
            IndexFileConfig,
        )

        config = IndexFileConfig()

        assert config.generate_json is True
        assert config.generate_text is True
        assert config.include_statistics is True
        assert config.include_relationships is True

    def test_custom_config_values(self):
        """Test custom configuration values."""
        from src.file_generator.index_file_generator import (
            IndexFileConfig,
        )

        config = IndexFileConfig(
            generate_json=False,
            generate_text=False,
            include_statistics=False,
            include_relationships=False,
        )

        assert config.generate_json is False
        assert config.generate_text is False
        assert config.include_statistics is False
        assert config.include_relationships is False

    def test_config_validation(self):
        """Test configuration validation."""
        from src.file_generator.index_file_generator import (
            IndexFileConfig,
        )

        # Test invalid output directory
        with pytest.raises(ValueError):
            config = IndexFileConfig(output_directory="")
            config.validate()

    def test_config_to_dict(self):
        """Test configuration to dictionary conversion."""
        from src.file_generator.index_file_generator import (
            IndexFileConfig,
        )

        config = IndexFileConfig()

        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert "generate_json" in config_dict
        assert "generate_text" in config_dict
        assert "include_statistics" in config_dict


class TestIndexSearchMetadataGenerator:
    """Test cases for IndexSearchMetadataGenerator class."""

    def test_generate_search_keywords(self):
        """Test generation of search keywords."""
        from src.file_generator.index_file_generator import IndexSearchMetadataGenerator

        generator = IndexSearchMetadataGenerator()

        restaurant = RestaurantData(
            name="Keyword Test Restaurant",
            cuisine="Italian",
            menu_items={"entrees": ["pasta", "pizza", "risotto"]},
            sources=["json-ld"],
        )

        keywords = generator.generate_search_keywords(restaurant)

        assert isinstance(keywords, list)
        assert "italian" in [k.lower() for k in keywords]
        assert any("pasta" in k.lower() for k in keywords)

    def test_generate_location_search_data(self):
        """Test generation of location search data."""
        from src.file_generator.index_file_generator import IndexSearchMetadataGenerator

        generator = IndexSearchMetadataGenerator()

        restaurant = RestaurantData(
            name="Location Test Restaurant",
            address="123 Main Street, Salem, OR 97301",
            sources=["json-ld"],
        )

        location_data = generator.generate_location_search_data(restaurant)

        assert isinstance(location_data, dict)
        if restaurant.address:
            assert (
                "address_components" in location_data
                or "searchable_terms" in location_data
            )

    def test_generate_fuzzy_match_data(self):
        """Test generation of fuzzy matching data."""
        from src.file_generator.index_file_generator import IndexSearchMetadataGenerator

        generator = IndexSearchMetadataGenerator()

        restaurant = RestaurantData(
            name="Fuzzy Match Test Restaurant", cuisine="Italian", sources=["json-ld"]
        )

        fuzzy_data = generator.generate_fuzzy_match_data(restaurant)

        assert isinstance(fuzzy_data, dict)
        # Should include phonetic codes, alternate spellings, etc.


class TestIndexStatisticsGenerator:
    """Test cases for IndexStatisticsGenerator class."""

    def test_calculate_entity_statistics(self):
        """Test calculation of entity statistics."""
        from src.file_generator.index_file_generator import IndexStatisticsGenerator

        generator = IndexStatisticsGenerator()

        restaurant_data = [
            RestaurantData(name="Restaurant 1", cuisine="Italian", sources=["json-ld"]),
            RestaurantData(name="Restaurant 2", cuisine="Mexican", sources=["json-ld"]),
            RestaurantData(name="Restaurant 3", cuisine="Italian", sources=["json-ld"]),
        ]

        stats = generator.calculate_entity_statistics(restaurant_data)

        assert isinstance(stats, dict)
        assert stats["total_entities"] == 3
        assert "cuisine_breakdown" in stats
        assert stats["cuisine_breakdown"]["Italian"] == 2
        assert stats["cuisine_breakdown"]["Mexican"] == 1

    def test_calculate_file_size_statistics(self):
        """Test calculation of file size statistics."""
        import tempfile
        from src.file_generator.index_file_generator import IndexStatisticsGenerator

        generator = IndexStatisticsGenerator()

        # Create some mock files
        with tempfile.TemporaryDirectory() as temp_dir:
            test_files = []
            for i in range(3):
                file_path = os.path.join(temp_dir, f"test_file_{i}.txt")
                with open(file_path, "w") as f:
                    f.write(
                        f"Test content {i}" * 100
                    )  # Create files of different sizes
                test_files.append(file_path)

            stats = generator.calculate_file_size_statistics(test_files)

            assert isinstance(stats, dict)
            assert "total_size" in stats
            assert "average_size" in stats
            assert "file_count" in stats
            assert stats["file_count"] == 3

    def test_calculate_data_quality_metrics(self):
        """Test calculation of data quality metrics."""
        from src.file_generator.index_file_generator import IndexStatisticsGenerator

        generator = IndexStatisticsGenerator()

        restaurant_data = [
            RestaurantData(
                name="Complete Restaurant",
                address="123 Main St",
                phone="555-1234",
                cuisine="Italian",
                menu_items={"entrees": ["pasta"]},
                sources=["json-ld"],
            ),
            RestaurantData(name="Minimal Restaurant", sources=["heuristic"]),
        ]

        quality_metrics = generator.calculate_data_quality_metrics(restaurant_data)

        assert isinstance(quality_metrics, dict)
        assert "completeness_score" in quality_metrics
        assert "field_coverage" in quality_metrics

    def test_generate_generation_metadata(self):
        """Test generation of generation metadata."""
        from src.file_generator.index_file_generator import IndexStatisticsGenerator

        generator = IndexStatisticsGenerator()

        with patch("src.file_generator.index_file_generator.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 3, 15, 14, 30)

            metadata = generator.generate_generation_metadata()

            assert isinstance(metadata, dict)
            assert "generation_timestamp" in metadata
            assert "generator_version" in metadata


class TestIndexRelationshipMapper:
    """Test cases for IndexRelationshipMapper class."""

    def test_map_entity_relationships(self):
        """Test mapping of entity relationships."""
        from src.file_generator.index_file_generator import IndexRelationshipMapper

        mapper = IndexRelationshipMapper()

        # Create restaurants with relationships
        parent_restaurant = RestaurantData(
            name="Tony's Italian Restaurant", sources=["json-ld"]
        )
        child_restaurant = RestaurantData(
            name="Tony's Italian Restaurant - Downtown", sources=["json-ld"]
        )

        restaurant_data = [parent_restaurant, child_restaurant]

        relationship_map = mapper.map_entity_relationships(restaurant_data)

        assert isinstance(relationship_map, list)
        # Should detect parent-child relationship between Tony's restaurants
        assert len(relationship_map) > 0
        assert any(rel["type"] == "parent-child" for rel in relationship_map)

    def test_create_bidirectional_mappings(self):
        """Test creation of bidirectional relationship mappings."""
        from src.file_generator.index_file_generator import IndexRelationshipMapper

        mapper = IndexRelationshipMapper()

        # Mock relationships
        relationships = [
            {"source": "Restaurant A", "target": "Restaurant B", "type": "parent-child"}
        ]

        bidirectional_map = mapper.create_bidirectional_mappings(relationships)

        assert isinstance(bidirectional_map, dict)
        # Should include both A->B and B->A mappings where appropriate

    def test_handle_circular_references_in_mapping(self):
        """Test handling of circular references in relationship mapping."""
        from src.file_generator.index_file_generator import IndexRelationshipMapper

        mapper = IndexRelationshipMapper()

        # Create circular relationship scenario
        circular_relationships = [
            {"source": "Restaurant A", "target": "Restaurant B", "type": "related"},
            {"source": "Restaurant B", "target": "Restaurant A", "type": "related"},
        ]

        resolved_map = mapper.handle_circular_references(circular_relationships)

        assert isinstance(resolved_map, list)
        # Should handle circular references without infinite loops
        assert len(resolved_map) <= len(circular_relationships)
        # Should remove duplicates
        assert (
            len(resolved_map) == 1
        )  # Only one relationship should remain after deduplication


class TestIndexIntegrityValidator:
    """Test cases for IndexIntegrityValidator class."""

    def test_validate_file_references(self):
        """Test validation of file references in indices."""
        import tempfile
        from src.file_generator.index_file_generator import IndexIntegrityValidator

        validator = IndexIntegrityValidator()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files
            test_file = os.path.join(temp_dir, "test_restaurant.txt")
            with open(test_file, "w") as f:
                f.write("Test content")

            # Mock index data
            index_data = {
                "entities": [
                    {"id": "test_restaurant", "file_path": "test_restaurant.txt"}
                ]
            }

            validation_result = validator.validate_file_references(index_data, temp_dir)

            assert isinstance(validation_result, dict)
            assert "valid" in validation_result

    def test_validate_entity_id_consistency(self):
        """Test validation of entity ID consistency across indices."""
        from src.file_generator.index_file_generator import IndexIntegrityValidator

        validator = IndexIntegrityValidator()

        # Mock multiple index files
        master_index = {
            "entities": [
                {"id": "restaurant_1", "name": "Restaurant 1"},
                {"id": "restaurant_2", "name": "Restaurant 2"},
            ]
        }

        category_indices = {
            "Italian": {"entities": [{"id": "restaurant_1", "name": "Restaurant 1"}]}
        }

        consistency_result = validator.validate_entity_id_consistency(
            master_index, category_indices
        )

        assert isinstance(consistency_result, dict)
        assert "consistent" in consistency_result

    def test_validate_category_assignments(self):
        """Test validation of category assignments."""
        from src.file_generator.index_file_generator import IndexIntegrityValidator

        validator = IndexIntegrityValidator()

        restaurant_data = [
            RestaurantData(
                name="Italian Restaurant", cuisine="Italian", sources=["json-ld"]
            ),
            RestaurantData(
                name="Mexican Restaurant", cuisine="Mexican", sources=["json-ld"]
            ),
        ]

        # Mock category indices
        category_indices = {
            "Italian": ["Italian Restaurant"],
            "Mexican": ["Mexican Restaurant"],
        }

        validation_result = validator.validate_category_assignments(
            restaurant_data, category_indices
        )

        assert isinstance(validation_result, dict)
        assert "accurate" in validation_result

    def test_detect_orphaned_references(self):
        """Test detection of orphaned references."""
        from src.file_generator.index_file_generator import IndexIntegrityValidator

        validator = IndexIntegrityValidator()

        # Mock index with orphaned reference
        index_data = {
            "entities": [
                {"id": "restaurant_1", "related_to": ["restaurant_2", "restaurant_999"]}
            ]
        }

        all_entity_ids = ["restaurant_1", "restaurant_2"]  # restaurant_999 is missing

        orphaned_refs = validator.detect_orphaned_references(index_data, all_entity_ids)

        assert isinstance(orphaned_refs, list)
        # Should detect restaurant_999 as orphaned reference
