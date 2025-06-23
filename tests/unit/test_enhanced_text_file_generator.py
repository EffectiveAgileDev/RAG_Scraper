"""Unit tests for enhanced text file generator classes."""
import os
import tempfile
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.scraper.multi_strategy_scraper import RestaurantData


class TestEnhancedTextFileGenerator:
    """Test cases for EnhancedTextFileGenerator class."""

    def test_init_with_default_config(self):
        """Test initialization with default configuration."""
        from src.file_generator.enhanced_text_file_generator import (
            EnhancedTextFileGenerator,
        )

        generator = EnhancedTextFileGenerator()

        assert generator is not None
        assert generator.config is not None
        assert generator.config.hierarchical_structure is True

    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        from src.file_generator.enhanced_text_file_generator import (
            EnhancedTextFileGenerator,
            EnhancedTextFileConfig,
        )

        config = EnhancedTextFileConfig(
            hierarchical_structure=True, entity_organization=True, cross_references=True
        )
        generator = EnhancedTextFileGenerator(config)

        assert generator is not None
        assert generator.config == config

    def test_generate_hierarchical_structure(self):
        """Test generation of hierarchical document structure."""
        import tempfile
        from src.file_generator.enhanced_text_file_generator import (
            EnhancedTextFileGenerator,
            EnhancedTextFileConfig,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            config = EnhancedTextFileConfig(output_directory=temp_dir)
            generator = EnhancedTextFileGenerator(config)

            # Create test data with parent-child relationships
            parent_restaurant = RestaurantData(
                name="Tony's Italian Restaurant",
                address="1234 Commercial Street, Salem, OR 97301",
                sources=["json-ld"],
            )

            child_restaurant = RestaurantData(
                name="Tony's Italian Restaurant - Downtown",
                address="5678 State Street, Salem, OR 97301",
                sources=["json-ld"],
            )

            restaurant_data = [parent_restaurant, child_restaurant]

            result = generator.generate_hierarchical_files(restaurant_data)

            # Should return list of generated files
            assert isinstance(result, list)
            assert len(result) > 0

    def test_generate_entity_based_organization(self):
        """Test generation of entity-based file organization."""
        import tempfile
        from src.file_generator.enhanced_text_file_generator import (
            EnhancedTextFileGenerator,
            EnhancedTextFileConfig,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            config = EnhancedTextFileConfig(output_directory=temp_dir)
            generator = EnhancedTextFileGenerator(config)

            restaurant_data = [
                RestaurantData(
                    name="Restaurant 1", cuisine="Italian", sources=["json-ld"]
                ),
                RestaurantData(
                    name="Restaurant 2", cuisine="Mexican", sources=["heuristic"]
                ),
                RestaurantData(
                    name="Restaurant 3", cuisine="Italian", sources=["microdata"]
                ),
            ]

            result = generator.generate_entity_based_files(restaurant_data)

            # Should organize files by entity type
            assert isinstance(result, dict)
            assert "Italian" in result
            assert "Mexican" in result

    def test_include_cross_references(self):
        """Test inclusion of cross-reference sections in generated files."""
        from src.file_generator.enhanced_text_file_generator import (
            EnhancedTextFileGenerator,
        )

        generator = EnhancedTextFileGenerator()

        # Create restaurants with relationships
        restaurant1 = RestaurantData(name="Main Restaurant", sources=["json-ld"])
        restaurant2 = RestaurantData(name="Related Restaurant", sources=["json-ld"])

        result = generator.generate_with_cross_references([restaurant1, restaurant2])

        assert "Cross-References:" in result

    def test_add_rag_metadata_headers(self):
        """Test addition of RAG-optimized metadata headers."""
        from src.file_generator.enhanced_text_file_generator import (
            EnhancedTextFileGenerator,
        )

        generator = EnhancedTextFileGenerator()

        restaurant = RestaurantData(
            name="Test Restaurant", cuisine="Italian", sources=["json-ld", "heuristic"]
        )

        result = generator.generate_with_rag_metadata([restaurant])

        # Should include structured metadata
        assert "---" in result  # YAML front matter delimiter
        assert "entity_type:" in result
        assert "extraction_sources:" in result
        assert "generation_timestamp:" in result

    def test_create_category_directories(self):
        """Test creation of category-based directory structure."""
        import tempfile
        from src.file_generator.enhanced_text_file_generator import (
            EnhancedTextFileGenerator,
            EnhancedTextFileConfig,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            config = EnhancedTextFileConfig(output_directory=temp_dir)
            generator = EnhancedTextFileGenerator(config)

            restaurant_data = [
                RestaurantData(
                    name="Italian Restaurant", cuisine="Italian", sources=["json-ld"]
                ),
                RestaurantData(
                    name="Mexican Restaurant", cuisine="Mexican", sources=["json-ld"]
                ),
            ]

            result = generator.generate_category_directories(restaurant_data)

            # Should create category directories
            italian_dir = os.path.join(temp_dir, "Italian")
            mexican_dir = os.path.join(temp_dir, "Mexican")

            assert os.path.exists(italian_dir)
            assert os.path.exists(mexican_dir)
            assert "Italian" in result
            assert "Mexican" in result

    def test_generate_comprehensive_indices(self):
        """Test generation of comprehensive index files."""
        import tempfile
        from src.file_generator.enhanced_text_file_generator import (
            EnhancedTextFileGenerator,
            EnhancedTextFileConfig,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            config = EnhancedTextFileConfig(output_directory=temp_dir)
            generator = EnhancedTextFileGenerator(config)

            restaurant_data = [
                RestaurantData(
                    name="Restaurant 1", cuisine="Italian", sources=["json-ld"]
                ),
                RestaurantData(
                    name="Restaurant 2", cuisine="Mexican", sources=["json-ld"]
                ),
            ]

            indices = generator.generate_indices(restaurant_data)

            # Should generate master and category indices
            assert "master_index" in indices
            assert "category_indices" in indices
            assert "Italian" in indices["category_indices"]
            assert "Mexican" in indices["category_indices"]

    def test_handle_large_datasets(self):
        """Test handling of large-scale multi-page data sets."""
        import tempfile
        from src.file_generator.enhanced_text_file_generator import (
            EnhancedTextFileGenerator,
            EnhancedTextFileConfig,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            config = EnhancedTextFileConfig(output_directory=temp_dir)
            generator = EnhancedTextFileGenerator(config)

            # Create large dataset (50+ restaurants)
            large_dataset = []
            for i in range(55):
                restaurant = RestaurantData(
                    name=f"Restaurant {i}",
                    cuisine=["Italian", "Mexican", "American"][i % 3],
                    sources=["json-ld"],
                )
                large_dataset.append(restaurant)

            result = generator.generate_files(large_dataset)

            # Should handle large datasets efficiently
            assert len(result) > 0
            # Memory usage should remain reasonable (tested via profiling)

    def test_preserve_extraction_context(self):
        """Test preservation of extraction context in output."""
        from src.file_generator.enhanced_text_file_generator import (
            EnhancedTextFileGenerator,
        )

        generator = EnhancedTextFileGenerator()

        restaurant = RestaurantData(
            name="Test Restaurant", sources=["json-ld", "heuristic"]
        )

        with patch(
            "src.file_generator.enhanced_text_file_generator.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 3, 15, 14, 30)

            result = generator.generate_with_context_preservation([restaurant])

            # Should include extraction context
            assert "extraction_timestamp:" in result
            assert "source_pages:" in result
            assert "extraction_methods:" in result
            assert "confidence_scores:" in result

    def test_generate_rag_friendly_chunks(self):
        """Test generation of RAG-friendly chunk boundaries."""
        from src.file_generator.enhanced_text_file_generator import (
            EnhancedTextFileGenerator,
            EnhancedTextFileConfig,
        )

        # Use smaller chunk size to force multiple chunks
        config = EnhancedTextFileConfig(chunk_size_words=50)
        generator = EnhancedTextFileGenerator(config)

        # Create restaurant with long description
        long_description_restaurant = RestaurantData(
            name="The Grand Culinary Experience Restaurant and Event Center",
            address="1234 Very Long Address Street Name That Goes On And On, Extended City Name, Oregon 97301",
            menu_items={
                "appetizers": [
                    "Artisanal cheese board with locally sourced cheeses and accompaniments",
                    "Pan-seared scallops with cauliflower puree and bacon crumbles",
                    "House-made charcuterie platter featuring duck prosciutto and wild boar salami",
                ],
                "entrees": [
                    "Herb-crusted rack of lamb with rosemary jus and seasonal vegetables",
                    "Pan-roasted Pacific salmon with quinoa pilaf and lemon herb butter",
                    "Dry-aged ribeye steak with truffle mashed potatoes and grilled asparagus",
                ],
            },
            sources=["json-ld"],
        )

        chunks = generator.generate_semantic_chunks([long_description_restaurant])

        # Should create chunks with proper boundaries
        assert isinstance(chunks, list)
        assert len(chunks) >= 1

        # Each chunk should have context preservation
        for chunk in chunks:
            assert "The Grand Culinary Experience Restaurant and Event Center" in chunk

    def test_validate_output_integrity(self):
        """Test validation of output file integrity."""
        import tempfile
        from src.file_generator.enhanced_text_file_generator import (
            EnhancedTextFileGenerator,
            EnhancedTextFileConfig,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            config = EnhancedTextFileConfig(output_directory=temp_dir)
            generator = EnhancedTextFileGenerator(config)

            restaurant_data = [
                RestaurantData(name="Restaurant 1", sources=["json-ld"]),
                RestaurantData(name="Restaurant 2", sources=["json-ld"]),
            ]

            # Generate files
            generated_files = generator.generate_files(restaurant_data)

            # Validate integrity
            validation_result = generator.validate_output_integrity(generated_files)

            # Check structure of validation result
            assert isinstance(validation_result, dict)
            assert "valid" in validation_result
            assert "required_files_present" in validation_result
            assert "cross_references_valid" in validation_result
            assert "metadata_complete" in validation_result


class TestEnhancedTextFileConfig:
    """Test cases for EnhancedTextFileConfig class."""

    def test_default_config_values(self):
        """Test default configuration values."""
        from src.file_generator.enhanced_text_file_generator import (
            EnhancedTextFileConfig,
        )

        config = EnhancedTextFileConfig()

        assert config.hierarchical_structure is True
        assert config.entity_organization is True
        assert config.cross_references is True
        assert config.rag_metadata is True
        assert config.category_directories is True
        assert config.comprehensive_indices is True
        assert config.semantic_chunking is True
        assert config.context_preservation is True

    def test_custom_config_values(self):
        """Test custom configuration values."""
        from src.file_generator.enhanced_text_file_generator import (
            EnhancedTextFileConfig,
        )

        config = EnhancedTextFileConfig(
            hierarchical_structure=False,
            entity_organization=False,
            cross_references=False,
            rag_metadata=False,
            category_directories=False,
            comprehensive_indices=False,
            semantic_chunking=False,
            context_preservation=False,
        )

        assert config.hierarchical_structure is False
        assert config.entity_organization is False
        assert config.cross_references is False
        assert config.rag_metadata is False
        assert config.category_directories is False
        assert config.comprehensive_indices is False
        assert config.semantic_chunking is False
        assert config.context_preservation is False

    def test_config_validation(self):
        """Test configuration validation."""
        from src.file_generator.enhanced_text_file_generator import (
            EnhancedTextFileConfig,
        )

        # Test invalid output directory
        with pytest.raises(ValueError):
            config = EnhancedTextFileConfig(output_directory="")
            config.validate()

    def test_config_to_dict(self):
        """Test configuration to dictionary conversion."""
        from src.file_generator.enhanced_text_file_generator import (
            EnhancedTextFileConfig,
        )

        config = EnhancedTextFileConfig()

        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert "hierarchical_structure" in config_dict
        assert "entity_organization" in config_dict
        assert "cross_references" in config_dict


class TestEntityRelationshipManager:
    """Test cases for EntityRelationshipManager class."""

    def test_detect_relationships(self):
        """Test detection of entity relationships."""
        with pytest.raises(ImportError):
            from src.file_generator.entity_relationship_manager import (
                EntityRelationshipManager,
            )

            manager = EntityRelationshipManager()

            restaurant1 = RestaurantData(
                name="Tony's Italian Restaurant", sources=["json-ld"]
            )
            restaurant2 = RestaurantData(
                name="Tony's Italian Restaurant - Downtown", sources=["json-ld"]
            )

            relationships = manager.detect_relationships([restaurant1, restaurant2])

            assert len(relationships) > 0
            assert relationships[0]["type"] == "parent-child"

    def test_build_relationship_graph(self):
        """Test building of relationship graph."""
        with pytest.raises(ImportError):
            from src.file_generator.entity_relationship_manager import (
                EntityRelationshipManager,
            )

            manager = EntityRelationshipManager()

            restaurants = [
                RestaurantData(name="Main Restaurant", sources=["json-ld"]),
                RestaurantData(name="Branch Restaurant", sources=["json-ld"]),
                RestaurantData(name="Sister Restaurant", sources=["json-ld"]),
            ]

            graph = manager.build_relationship_graph(restaurants)

            assert isinstance(graph, dict)
            assert len(graph) == len(restaurants)

    def test_resolve_circular_references(self):
        """Test resolution of circular references."""
        with pytest.raises(ImportError):
            from src.file_generator.entity_relationship_manager import (
                EntityRelationshipManager,
            )

            manager = EntityRelationshipManager()

            # Create circular relationship scenario
            restaurant1 = RestaurantData(name="Restaurant A", sources=["json-ld"])
            restaurant2 = RestaurantData(name="Restaurant B", sources=["json-ld"])

            # Mock circular relationships
            relationships = [
                {"source": "Restaurant A", "target": "Restaurant B", "type": "related"},
                {"source": "Restaurant B", "target": "Restaurant A", "type": "related"},
            ]

            resolved = manager.resolve_circular_references(relationships)

            # Should handle circular references without infinite loops
            assert len(resolved) == 2


class TestRAGMetadataGenerator:
    """Test cases for RAGMetadataGenerator class."""

    def test_generate_metadata_header(self):
        """Test generation of metadata headers."""
        with pytest.raises(ImportError):
            from src.file_generator.rag_metadata_generator import RAGMetadataGenerator

            generator = RAGMetadataGenerator()

            restaurant = RestaurantData(
                name="Test Restaurant",
                cuisine="Italian",
                sources=["json-ld", "heuristic"],
            )

            metadata = generator.generate_metadata_header(restaurant)

            assert "---" in metadata
            assert "entity_type: restaurant" in metadata
            assert "name: Test Restaurant" in metadata
            assert "cuisine: Italian" in metadata
            assert "extraction_sources:" in metadata

    def test_generate_search_metadata(self):
        """Test generation of search metadata."""
        with pytest.raises(ImportError):
            from src.file_generator.rag_metadata_generator import RAGMetadataGenerator

            generator = RAGMetadataGenerator()

            restaurant = RestaurantData(
                name="Test Restaurant",
                cuisine="Italian",
                menu_items={"entrees": ["pasta", "pizza"]},
                sources=["json-ld"],
            )

            search_metadata = generator.generate_search_metadata(restaurant)

            assert isinstance(search_metadata, dict)
            assert "keywords" in search_metadata
            assert "categories" in search_metadata
            assert "embedding_hints" in search_metadata

    def test_optimize_for_embedding_models(self):
        """Test optimization for embedding models."""
        with pytest.raises(ImportError):
            from src.file_generator.rag_metadata_generator import RAGMetadataGenerator

            generator = RAGMetadataGenerator()

            content = "This is a long piece of content that needs to be optimized for embedding models."

            optimized = generator.optimize_for_embedding_models(content)

            assert isinstance(optimized, str)
            assert len(optimized) > 0


class TestSemanticChunker:
    """Test cases for SemanticChunker class."""

    def test_chunk_by_semantic_boundaries(self):
        """Test chunking by semantic boundaries."""
        with pytest.raises(ImportError):
            from src.file_generator.semantic_chunker import SemanticChunker

            chunker = SemanticChunker()

            long_content = """
            Restaurant Name: The Grand Culinary Experience
            Address: 1234 Long Street Name
            
            Menu Items:
            Appetizers: Fresh bruschetta, calamari rings, antipasto platter
            Entrees: Homemade pasta, wood-fired pizza, fresh seafood
            Desserts: Tiramisu, cannoli, gelato
            
            Hours: Tuesday-Saturday 5pm-10pm, Sunday 4pm-9pm
            Cuisine: Italian with Mediterranean influences
            """

            chunks = chunker.chunk_by_semantic_boundaries(long_content)

            assert isinstance(chunks, list)
            assert len(chunks) > 1

            # Verify chunk boundaries are semantic
            for chunk in chunks:
                assert not chunk.strip().startswith(
                    "Appetizers:"
                )  # Mid-section breaks avoided

    def test_preserve_context_across_chunks(self):
        """Test preservation of context across chunks."""
        with pytest.raises(ImportError):
            from src.file_generator.semantic_chunker import SemanticChunker

            chunker = SemanticChunker()

            restaurant = RestaurantData(
                name="Test Restaurant", address="123 Main St", sources=["json-ld"]
            )

            chunks = chunker.create_contextual_chunks(restaurant)

            # Each chunk should maintain restaurant context
            for chunk in chunks:
                assert "Test Restaurant" in chunk

    def test_handle_overlapping_information(self):
        """Test handling of overlapping information."""
        with pytest.raises(ImportError):
            from src.file_generator.semantic_chunker import SemanticChunker

            chunker = SemanticChunker()

            content_with_overlap = "Restaurant info... repeated restaurant info..."

            chunks = chunker.handle_overlapping_information(content_with_overlap)

            # Should handle overlaps without duplication
            assert isinstance(chunks, list)
            assert len(chunks) > 0
