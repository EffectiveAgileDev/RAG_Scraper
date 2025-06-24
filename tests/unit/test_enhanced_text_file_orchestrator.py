"""Unit tests for EnhancedTextFileOrchestrator class."""
import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from src.scraper.multi_strategy_scraper import RestaurantData


class TestEnhancedTextFileOrchestrator:
    """Test cases for EnhancedTextFileOrchestrator class."""

    def test_init_with_dependencies(self):
        """Test initialization with required dependencies."""
        # This test will fail until we create the orchestrator
        from src.file_generator.enhanced_text_file_orchestrator import EnhancedTextFileOrchestrator
        
        # Mock dependencies
        mock_relationship_manager = Mock()
        mock_metadata_generator = Mock()
        mock_semantic_chunker = Mock()
        mock_content_formatter = Mock()
        
        orchestrator = EnhancedTextFileOrchestrator(
            relationship_manager=mock_relationship_manager,
            metadata_generator=mock_metadata_generator,
            semantic_chunker=mock_semantic_chunker,
            content_formatter=mock_content_formatter
        )
        
        assert orchestrator is not None
        assert orchestrator.relationship_manager == mock_relationship_manager
        assert orchestrator.metadata_generator == mock_metadata_generator
        assert orchestrator.semantic_chunker == mock_semantic_chunker
        assert orchestrator.content_formatter == mock_content_formatter

    def test_generate_hierarchical_files(self):
        """Test generation of hierarchical files."""
        from src.file_generator.enhanced_text_file_orchestrator import EnhancedTextFileOrchestrator
        
        # Mock dependencies
        mock_relationship_manager = Mock()
        mock_relationship_manager.detect_relationships.return_value = []
        mock_relationship_manager.build_relationship_graph.return_value = {}
        
        mock_content_formatter = Mock()
        mock_content_formatter.generate_hierarchical_content.return_value = "hierarchical content"
        
        orchestrator = EnhancedTextFileOrchestrator(
            relationship_manager=mock_relationship_manager,
            metadata_generator=Mock(),
            semantic_chunker=Mock(),
            content_formatter=mock_content_formatter
        )
        
        restaurant_data = [
            RestaurantData(name="Test Restaurant", sources=["json-ld"])
        ]
        
        # Mock the file writing methods
        with patch.object(orchestrator, '_generate_output_path', return_value="/tmp/test.txt"), \
             patch.object(orchestrator, '_handle_file_exists'), \
             patch.object(orchestrator, '_write_with_error_handling', return_value="/tmp/test.txt"):
            
            result = orchestrator.generate_hierarchical_files(restaurant_data, config=Mock())
            
            assert isinstance(result, list)
            assert len(result) > 0

    def test_generate_entity_based_files(self):
        """Test generation of entity-based files."""
        from src.file_generator.enhanced_text_file_orchestrator import EnhancedTextFileOrchestrator
        
        mock_content_formatter = Mock()
        mock_content_formatter.generate_entity_content.return_value = "entity content"
        
        orchestrator = EnhancedTextFileOrchestrator(
            relationship_manager=Mock(),
            metadata_generator=Mock(),
            semantic_chunker=Mock(),
            content_formatter=mock_content_formatter
        )
        
        restaurant_data = [
            RestaurantData(name="Italian Restaurant", cuisine="Italian", sources=["json-ld"]),
            RestaurantData(name="Mexican Restaurant", cuisine="Mexican", sources=["json-ld"])
        ]
        
        config = Mock()
        config.output_directory = "/tmp"
        config.category_directories = True
        config.cross_references = False
        
        with patch('os.path.join', return_value="/tmp/Italian"), \
             patch('pathlib.Path'), \
             patch.object(orchestrator, '_handle_file_exists'), \
             patch.object(orchestrator, '_write_with_error_handling', return_value="/tmp/test.txt"):
            
            result = orchestrator.generate_entity_based_files(restaurant_data, config)
            
            assert isinstance(result, dict)
            assert "Italian" in result
            assert "Mexican" in result

    def test_generate_with_cross_references(self):
        """Test generation with cross-references."""
        from src.file_generator.enhanced_text_file_orchestrator import EnhancedTextFileOrchestrator
        
        mock_relationship_manager = Mock()
        mock_relationship_manager.detect_relationships.return_value = [
            {"source": "Restaurant A", "target": "Restaurant B", "type": "related"}
        ]
        
        mock_content_formatter = Mock()
        mock_content_formatter.generate_basic_content.return_value = "basic content"
        mock_content_formatter.format_cross_references.return_value = "cross references"
        
        orchestrator = EnhancedTextFileOrchestrator(
            relationship_manager=mock_relationship_manager,
            metadata_generator=Mock(),
            semantic_chunker=Mock(),
            content_formatter=mock_content_formatter
        )
        
        restaurant_data = [
            RestaurantData(name="Restaurant A", sources=["json-ld"]),
            RestaurantData(name="Restaurant B", sources=["json-ld"])
        ]
        
        result = orchestrator.generate_with_cross_references(restaurant_data)
        
        assert "Cross-References:" in result
        assert "cross references" in result

    def test_generate_with_rag_metadata(self):
        """Test generation with RAG metadata."""
        from src.file_generator.enhanced_text_file_orchestrator import EnhancedTextFileOrchestrator
        
        mock_metadata_generator = Mock()
        mock_metadata_generator.generate_metadata_header.return_value = "metadata header"
        
        mock_content_formatter = Mock()
        mock_content_formatter.generate_basic_content.return_value = "basic content"
        
        orchestrator = EnhancedTextFileOrchestrator(
            relationship_manager=Mock(),
            metadata_generator=mock_metadata_generator,
            semantic_chunker=Mock(),
            content_formatter=mock_content_formatter
        )
        
        restaurant_data = [
            RestaurantData(name="Test Restaurant", sources=["json-ld"])
        ]
        
        result = orchestrator.generate_with_rag_metadata(restaurant_data)
        
        assert "metadata header" in result
        assert "basic content" in result

    def test_generate_category_directories(self):
        """Test creation of category directories."""
        from src.file_generator.enhanced_text_file_orchestrator import EnhancedTextFileOrchestrator
        
        orchestrator = EnhancedTextFileOrchestrator(
            relationship_manager=Mock(),
            metadata_generator=Mock(),
            semantic_chunker=Mock(),
            content_formatter=Mock()
        )
        
        restaurant_data = [
            RestaurantData(name="Italian Restaurant", cuisine="Italian", sources=["json-ld"]),
            RestaurantData(name="Mexican Restaurant", cuisine="Mexican", sources=["json-ld"])
        ]
        
        config = Mock()
        config.output_directory = "/tmp"
        
        with patch('pathlib.Path') as mock_path:
            result = orchestrator.generate_category_directories(restaurant_data, config)
            
            assert isinstance(result, dict)
            assert "Italian" in result
            assert "Mexican" in result

    def test_generate_indices(self):
        """Test generation of indices."""
        from src.file_generator.enhanced_text_file_orchestrator import EnhancedTextFileOrchestrator
        
        mock_content_formatter = Mock()
        mock_content_formatter.generate_master_index.return_value = "master index content"
        mock_content_formatter.generate_category_index.return_value = "category index content"
        
        orchestrator = EnhancedTextFileOrchestrator(
            relationship_manager=Mock(),
            metadata_generator=Mock(),
            semantic_chunker=Mock(),
            content_formatter=mock_content_formatter
        )
        
        restaurant_data = [
            RestaurantData(name="Italian Restaurant", cuisine="Italian", sources=["json-ld"]),
            RestaurantData(name="Mexican Restaurant", cuisine="Mexican", sources=["json-ld"])
        ]
        
        config = Mock()
        config.output_directory = "/tmp"
        
        with patch.object(orchestrator, '_write_with_error_handling', return_value="/tmp/index.txt"):
            result = orchestrator.generate_indices(restaurant_data, config)
            
            assert "master_index" in result
            assert "category_indices" in result
            assert "all_files" in result