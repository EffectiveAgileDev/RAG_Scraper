"""Unit tests for SemanticStructurer - the main semantic structuring component."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

# Import will fail until we implement - expected for RED phase
try:
    from src.semantic.semantic_structurer import SemanticStructurer, SemanticResult
except ImportError:
    SemanticStructurer = None
    SemanticResult = None


class TestSemanticStructurer:
    """Test the main SemanticStructurer class."""
    
    def test_semantic_structurer_initialization(self):
        """Test SemanticStructurer can be initialized with default config."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        structurer = SemanticStructurer()
        assert structurer is not None
        assert hasattr(structurer, 'chunk_size')
        assert hasattr(structurer, 'config')
        assert structurer.chunk_size == 512  # Default chunk size
    
    def test_semantic_structurer_custom_config(self):
        """Test SemanticStructurer with custom configuration."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        config = {
            'chunk_size': 256,
            'overlap_size': 50,
            'enable_summaries': True
        }
        
        structurer = SemanticStructurer(config=config)
        assert structurer.chunk_size == 256
        assert structurer.overlap_size == 50
        assert structurer.enable_summaries is True
    
    def test_structure_for_rag_basic(self):
        """Test basic structure_for_rag functionality."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        structurer = SemanticStructurer()
        restaurant_data = {
            "name": "Test Restaurant",
            "description": "A great place to eat with excellent food and service."
        }
        
        result = structurer.structure_for_rag(restaurant_data)
        
        assert isinstance(result, dict)
        assert "chunks" in result
        assert "metadata" in result
        assert "relationships" in result
        assert len(result["chunks"]) > 0
        
        # Verify first chunk
        first_chunk = result["chunks"][0]
        assert "id" in first_chunk
        assert "content" in first_chunk
        assert "metadata" in first_chunk
        assert "type" in first_chunk
    
    def test_structure_for_rag_with_metadata_enrichment(self):
        """Test structure_for_rag with metadata enrichment enabled."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        structurer = SemanticStructurer()
        restaurant_data = {
            "name": "Test Restaurant",
            "cuisine": "Italian",
            "price_range": "$$"
        }
        
        result = structurer.structure_for_rag(restaurant_data, enrich_metadata=True)
        
        assert "chunks" in result
        chunk = result["chunks"][0]
        metadata = chunk["metadata"]
        
        # Should have enriched metadata
        assert "source_type" in metadata
        assert "entity_name" in metadata
        assert "confidence_score" in metadata
        assert "timestamp" in metadata
        assert metadata["source_type"] == "restaurant"
        assert metadata["entity_name"] == "Test Restaurant"
    
    def test_structure_for_rag_respects_chunk_size(self):
        """Test that chunks respect the configured size limit."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        structurer = SemanticStructurer(config={'chunk_size': 10})  # Very small for testing
        
        long_description = " ".join(["word"] * 50)  # 50 words
        restaurant_data = {
            "name": "Test Restaurant",
            "description": long_description
        }
        
        result = structurer.structure_for_rag(restaurant_data)
        
        for chunk in result["chunks"]:
            # Simple word count check (real implementation uses proper tokenization)
            word_count = len(chunk["content"].split())
            assert word_count <= 10, f"Chunk exceeds size limit: {word_count} words"
    
    def test_structure_for_rag_maintains_semantic_coherence(self):
        """Test that chunks maintain semantic coherence."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        structurer = SemanticStructurer()
        restaurant_data = {
            "name": "Test Restaurant",
            "description": "This is a sentence. This is another sentence. Final sentence here."
        }
        
        result = structurer.structure_for_rag(restaurant_data)
        
        for chunk in result["chunks"]:
            content = chunk["content"].strip()
            if len(content) > 20:  # Only check longer chunks
                # Should end with sentence terminator
                assert content.endswith(('.', '!', '?')), f"Chunk doesn't end properly: {content}"
    
    def test_create_relationships_basic(self):
        """Test basic relationship creation."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        structurer = SemanticStructurer()
        restaurant_data = {
            "name": "Test Restaurant",
            "menu": {"appetizers": ["Salad"]},
            "hours": {"monday": "9-17"},
            "contact": {"phone": "555-1234"}
        }
        
        result = structurer.create_relationships(restaurant_data)
        
        assert "relationships" in result
        relationships = result["relationships"]
        assert len(relationships) > 0
        
        # Check for expected relationship types
        rel_types = {rel["type"] for rel in relationships}
        expected_types = {"has_menu", "has_hours", "has_contact"}
        assert any(rt in rel_types for rt in expected_types)
    
    def test_generate_embedding_hints(self):
        """Test embedding hints generation."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        structurer = SemanticStructurer()
        restaurant_data = {
            "name": "Italian Bistro",
            "cuisine": "Italian",
            "ambiance": {"description": "Romantic setting with candles"}
        }
        
        result = structurer.generate_embedding_hints(restaurant_data)
        
        assert "chunks" in result
        for chunk in result["chunks"]:
            assert "embedding_hints" in chunk
            hints = chunk["embedding_hints"]
            
            assert "semantic_context" in hints
            assert "domain_keywords" in hints
            assert "importance_weight" in hints
            assert isinstance(hints["importance_weight"], (int, float))
    
    def test_export_json_format(self):
        """Test JSON export functionality."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        structurer = SemanticStructurer()
        structured_data = {
            "chunks": [{"id": "1", "content": "Test content"}],
            "metadata": {"version": "1.0"},
            "relationships": []
        }
        
        result = structurer.export(structured_data, format="json")
        
        assert result is not None
        # Should be valid JSON string or dict
        import json
        if isinstance(result, str):
            parsed = json.loads(result)
            assert "chunks" in parsed
        else:
            assert "chunks" in result
    
    def test_export_jsonl_format(self):
        """Test JSONL export functionality."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        structurer = SemanticStructurer()
        structured_data = {
            "chunks": [
                {"id": "1", "content": "First chunk"},
                {"id": "2", "content": "Second chunk"}
            ],
            "metadata": {"version": "1.0"},
            "relationships": []
        }
        
        result = structurer.export(structured_data, format="jsonl")
        
        assert isinstance(result, str)
        lines = result.strip().split('\n')
        assert len(lines) == 2  # One line per chunk
        
        # Each line should be valid JSON
        import json
        for line in lines:
            parsed = json.loads(line)
            assert "id" in parsed
            assert "content" in parsed
    
    def test_structure_multimodal_content(self):
        """Test structuring of multi-modal content."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        structurer = SemanticStructurer()
        multimodal_data = {
            "name": "Test Restaurant",
            "text_content": "Great food and atmosphere",
            "images": [
                {"url": "menu.jpg", "description": "Menu items", "type": "menu"}
            ],
            "pdfs": [
                {"url": "wine.pdf", "content": "Wine selection"}
            ]
        }
        
        result = structurer.structure_multimodal(multimodal_data)
        
        assert "chunks" in result
        chunks = result["chunks"]
        
        # Should have different types of chunks
        chunk_types = {chunk["type"] for chunk in chunks}
        assert "text" in chunk_types
        assert "image" in chunk_types or "visual" in chunk_types
        assert "pdf" in chunk_types or "document" in chunk_types
    
    def test_chunk_intelligently_respects_boundaries(self):
        """Test intelligent chunking respects natural boundaries."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        structurer = SemanticStructurer(config={'chunk_size': 20})
        
        # Text with clear paragraph boundaries
        text_data = {
            "description": "First paragraph with some content.\n\nSecond paragraph here.\n\nThird paragraph content."
        }
        
        result = structurer.chunk_intelligently(text_data)
        
        chunks = result["chunks"]
        assert len(chunks) > 0
        
        # Chunks should not break mid-sentence
        for chunk in chunks:
            content = chunk["content"].strip()
            if len(content) > 10:
                # Should end properly
                assert content.endswith(('.', '!', '?', '\n')) or len(content.split()) < 5
    
    def test_generate_summary_creates_summary_chunk(self):
        """Test summary generation creates appropriate summary chunk."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        structurer = SemanticStructurer()
        restaurant_data = {
            "name": "Bistro Deluxe",
            "cuisine": "French",
            "price_range": "$$$",
            "location": {"address": "123 Main St"},
            "description": "Fine dining establishment with excellent service."
        }
        
        result = structurer.generate_summary(restaurant_data)
        
        assert "chunks" in result
        chunks = result["chunks"]
        
        # Find summary chunk
        summary_chunks = [c for c in chunks if c.get("type") == "summary"]
        assert len(summary_chunks) >= 1
        
        summary = summary_chunks[0]
        content = summary["content"]
        
        # Should contain key information
        assert "Bistro Deluxe" in content
        assert "French" in content or "cuisine" in content
        assert "$$$" in content or "price" in content


    def test_export_with_version_field(self):
        """Test JSON export includes version field in RAG-ready schema."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        structurer = SemanticStructurer()
        structured_data = {
            "chunks": [{"id": "1", "content": "Test"}],
            "metadata": {"version": "1.0"},
            "relationships": []
        }
        
        result = structurer.export(structured_data, format="json")
        
        import json
        if isinstance(result, str):
            data = json.loads(result)
        else:
            data = result
        
        # Must include version for RAG-ready schema
        assert "version" in data
        assert "chunks" in data
        assert isinstance(data["chunks"], list)
    
    def test_structure_temporal_data(self):
        """Test structure_temporal method for time-sensitive information."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        structurer = SemanticStructurer()
        temporal_data = {
            "name": "Test Restaurant", 
            "hours": {
                "monday": "11:00-22:00",
                "tuesday": "11:00-22:00"
            },
            "special_events": [
                {"name": "Wine Tasting", "date": "2024-02-14", "time": "18:00-20:00"}
            ]
        }
        
        result = structurer.structure_temporal(temporal_data)
        
        assert "chunks" in result
        chunks = result["chunks"]
        
        # Check for temporal metadata
        hours_chunks = [c for c in chunks if "hours" in c.get("content", "").lower()]
        for chunk in hours_chunks:
            metadata = chunk.get("metadata", {})
            assert metadata.get("temporal_type") == "recurring_schedule"
        
        event_chunks = [c for c in chunks if "event" in c.get("content", "").lower() or "Wine Tasting" in c.get("content", "")]
        for chunk in event_chunks:
            metadata = chunk.get("metadata", {})
            assert metadata.get("temporal_type") == "specific_date"
    
    def test_create_hierarchy_method(self):
        """Test create_hierarchy method for hierarchical chunk organization."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        structurer = SemanticStructurer()
        nested_data = {
            "name": "Test Restaurant",
            "menu": {
                "appetizers": {
                    "salads": ["Caesar - $12", "Greek - $10"],
                    "soups": ["French Onion - $8", "Bisque - $9"]
                },
                "main_courses": {
                    "seafood": ["Salmon - $24", "Lobster - $32"],
                    "meat": ["Steak - $28", "Lamb - $26"]
                }
            }
        }
        
        result = structurer.create_hierarchy(nested_data)
        
        assert "chunks" in result
        chunks = result["chunks"]
        
        # Should have parent and child chunks
        parent_chunks = [c for c in chunks if c.get("hierarchy_level") == 0 or c.get("is_parent", False)]
        child_chunks = [c for c in chunks if c.get("hierarchy_level", 0) > 0 or c.get("parent_id") is not None]
        
        assert len(parent_chunks) > 0
        assert len(child_chunks) > 0
        
        # Check hierarchy depth doesn't exceed limit
        max_level = max(chunk.get("hierarchy_level", 0) for chunk in chunks)
        assert max_level <= 3
    
    def test_structure_for_rag_with_handle_missing_parameter(self):
        """Test structure_for_rag supports handle_missing parameter."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        structurer = SemanticStructurer()
        incomplete_data = {
            "name": "Test Restaurant",
            "location": {
                "address": "Main St",  # Missing number
                "city": "Downtown"
                # Missing state, zip
            },
            "contact": {
                "email": "info@test.com"
                # Missing phone
            }
        }
        
        result = structurer.structure_for_rag(incomplete_data, handle_missing=True)
        
        assert "chunks" in result
        chunks = result["chunks"]
        assert len(chunks) > 0
        
        # Should mark missing fields in metadata
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            if "missing_fields" in metadata:
                assert isinstance(metadata["missing_fields"], list)
        
        # Should still create chunks for available data
        email_found = any("email" in chunk["content"].lower() for chunk in chunks)
        assert email_found
    
    def test_structure_for_rag_with_custom_config_parameter(self):
        """Test structure_for_rag accepts and uses custom config parameter."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        structurer = SemanticStructurer()
        restaurant_data = {
            "name": "Test Restaurant",
            "description": " ".join(["word"] * 100)  # 100 words
        }
        
        custom_config = {"chunk_size": 25}  # Small chunk size
        
        result = structurer.structure_for_rag(restaurant_data, config=custom_config)
        
        chunks = result["chunks"]
        
        # All chunks should respect the custom chunk size
        for chunk in chunks:
            tokens = len(chunk["content"].split())
            assert tokens <= 25
        
        # Configuration should be stored in metadata
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            assert "chunk_config" in metadata or "config" in metadata or len(chunks) == 1  # Single chunk might not store config
    
    def test_chunk_intelligently_adds_overlap_metadata(self):
        """Test chunk_intelligently adds overlap metadata for context continuity."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        structurer = SemanticStructurer(config={'chunk_size': 5})  # Small chunks to force multiple
        
        # Text that will definitely create multiple chunks
        long_text = "First paragraph content here.\n\nSecond paragraph with more content here.\n\nThird paragraph content."
        text_data = {"description": long_text}
        
        result = structurer.chunk_intelligently(text_data)
        
        chunks = result["chunks"]
        
        # Should have multiple chunks
        assert len(chunks) > 1, "Should create multiple chunks for testing overlap"
        
        # Check overlap metadata
        for i in range(len(chunks) - 1):
            current_chunk = chunks[i]
            next_chunk = chunks[i + 1]
            
            # Current chunk should have overlap_with_next
            assert current_chunk.get("metadata", {}).get("overlap_with_next") is True
            # Next chunk should have overlap_with_previous
            assert next_chunk.get("metadata", {}).get("overlap_with_previous") is True
    
    def test_export_with_profile_parameter(self):
        """Test export method supports profile parameter for optimization."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        structurer = SemanticStructurer()
        structured_data = {
            "chunks": [{"id": "1", "content": "Test content"}],
            "metadata": {"version": "1.0"},
            "relationships": []
        }
        
        # Test different profiles
        profiles = ["chatbot", "search", "analytics"]
        
        for profile in profiles:
            result = structurer.export(structured_data, format="json", profile=profile)
            
            import json
            if isinstance(result, str):
                data = json.loads(result)
            else:
                data = result
            
            # Should include profile in metadata
            assert "metadata" in data
            assert "profile" in data["metadata"]
            assert data["metadata"]["profile"] == profile
    
    def test_handle_missing_data_helper_method(self):
        """Test _handle_missing_data helper method marks missing fields correctly."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        structurer = SemanticStructurer()
        
        # Create chunks to modify
        chunks = [
            {
                "id": "chunk_1",
                "content": "Test Restaurant",
                "metadata": {"chunk_type": "name"}
            }
        ]
        
        # Incomplete restaurant data
        incomplete_data = {
            "name": "Test Restaurant",
            "contact": {"email": "test@test.com"}  # Missing phone
            # Missing description, cuisine, price_range, location, hours, menu
        }
        
        # Call the helper method directly
        structurer._handle_missing_data(chunks, incomplete_data)
        
        # Check that missing fields are marked
        chunk = chunks[0]
        metadata = chunk["metadata"]
        
        assert "missing_fields" in metadata
        assert isinstance(metadata["missing_fields"], list)
        assert len(metadata["missing_fields"]) > 0
        
        # Should include missing high-level fields
        missing_fields = metadata["missing_fields"]
        expected_missing = ["description", "cuisine", "price_range", "location", "hours", "menu"]
        for expected in expected_missing:
            assert expected in missing_fields
        
        # Should also include missing contact sub-field
        assert "contact.phone" in missing_fields
        
        # Confidence should be reduced for incomplete data
        assert metadata["confidence_score"] < 0.9
    
    def test_create_child_chunks_helper_method(self):
        """Test _create_child_chunks helper method creates proper hierarchy."""
        if not SemanticStructurer:
            pytest.skip("SemanticStructurer not implemented yet")
        
        structurer = SemanticStructurer()
        
        # Test data with nested structure
        nested_data = {
            "appetizers": {
                "salads": ["Caesar - $12", "Greek - $10"],
                "soups": ["Onion - $8", "Bisque - $9"]
            },
            "main_courses": ["Salmon - $24", "Steak - $28"]
        }
        
        chunks = []
        
        # Call helper method
        structurer._create_child_chunks(
            nested_data=nested_data,
            parent_key="menu",
            parent_id="parent_1",
            chunks=chunks,
            start_id=1,
            level=1
        )
        
        # Should create child chunks
        assert len(chunks) > 0
        
        # Check hierarchy levels and parent relationships
        for chunk in chunks:
            assert chunk.get("hierarchy_level") >= 1  # Should be at level 1 or deeper
            assert chunk.get("parent_id") is not None  # Should have parent
            assert chunk.get("type") in ["child", "child_parent"]  # Should be child type
            
            # Check metadata
            metadata = chunk.get("metadata", {})
            assert "chunk_type" in metadata
            assert metadata["chunk_type"].startswith("menu_")  # Should include parent key
        
        # Should respect hierarchy depth limit (max 3 levels)
        max_level = max(chunk.get("hierarchy_level", 0) for chunk in chunks)
        assert max_level <= 3


class TestSemanticResult:
    """Test the SemanticResult data structure."""
    
    def test_semantic_result_creation(self):
        """Test SemanticResult can be created."""
        if not SemanticResult:
            pytest.skip("SemanticResult not implemented yet")
        
        result = SemanticResult(
            chunks=[],
            metadata={},
            relationships=[],
            processing_time=0.1
        )
        
        assert result.chunks == []
        assert result.metadata == {}
        assert result.relationships == []
        assert result.processing_time == 0.1
    
    def test_semantic_result_to_dict(self):
        """Test SemanticResult conversion to dictionary."""
        if not SemanticResult:
            pytest.skip("SemanticResult not implemented yet")
        
        result = SemanticResult(
            chunks=[{"id": "1", "content": "test"}],
            metadata={"version": "1.0"},
            relationships=[],
            processing_time=0.1
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert "chunks" in result_dict
        assert "metadata" in result_dict
        assert "relationships" in result_dict
        assert "processing_time" in result_dict
    
    def test_semantic_result_validation(self):
        """Test SemanticResult validates its data."""
        if not SemanticResult:
            pytest.skip("SemanticResult not implemented yet")
        
        # Should validate that chunks is a list
        with pytest.raises((ValueError, TypeError)):
            SemanticResult(
                chunks="not a list",  # Should be list
                metadata={},
                relationships=[],
                processing_time=0.1
            )
        
        # Should validate processing_time is non-negative
        with pytest.raises((ValueError, TypeError)):
            SemanticResult(
                chunks=[],
                metadata={},
                relationships=[],
                processing_time=-1.0  # Should be non-negative
            )