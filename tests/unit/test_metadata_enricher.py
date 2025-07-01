"""Unit tests for MetadataEnricher - enriches chunks with additional metadata."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

# Import will fail until we implement - expected for RED phase
try:
    from src.semantic.metadata_enricher import MetadataEnricher
except ImportError:
    MetadataEnricher = None


class TestMetadataEnricher:
    """Test the MetadataEnricher class."""
    
    def test_metadata_enricher_initialization(self):
        """Test MetadataEnricher can be initialized."""
        if not MetadataEnricher:
            pytest.skip("MetadataEnricher not implemented yet")
        
        enricher = MetadataEnricher()
        assert enricher is not None
        assert hasattr(enricher, 'config')
    
    def test_metadata_enricher_custom_config(self):
        """Test MetadataEnricher with custom configuration."""
        if not MetadataEnricher:
            pytest.skip("MetadataEnricher not implemented yet")
        
        config = {
            'add_timestamps': True,
            'add_confidence_scores': True,
            'add_extraction_metadata': True,
            'add_domain_keywords': True
        }
        
        enricher = MetadataEnricher(config=config)
        assert enricher.config['add_timestamps'] is True
        assert enricher.config['add_confidence_scores'] is True
        assert enricher.config['add_extraction_metadata'] is True
        assert enricher.config['add_domain_keywords'] is True
    
    def test_enrich_chunk_adds_basic_metadata(self):
        """Test enriching a chunk with basic metadata."""
        if not MetadataEnricher:
            pytest.skip("MetadataEnricher not implemented yet")
        
        enricher = MetadataEnricher()
        
        chunk = {
            "id": "chunk_1",
            "content": "Great Italian restaurant with authentic cuisine",
            "type": "text",
            "source_field": "description"
        }
        
        original_data = {
            "name": "Bistro Romano",
            "cuisine": "Italian",
            "_metadata": {
                "extraction_method": "heuristic",
                "confidence": 0.85,
                "url": "https://bistroromano.com"
            }
        }
        
        enriched_chunk = enricher.enrich_chunk(chunk, original_data)
        
        assert "metadata" in enriched_chunk
        metadata = enriched_chunk["metadata"]
        
        # Should have basic enrichment
        assert "entity_name" in metadata
        assert "source_type" in metadata
        assert "confidence_score" in metadata
        assert metadata["entity_name"] == "Bistro Romano"
        assert metadata["source_type"] == "restaurant"
    
    def test_enrich_chunk_adds_timestamps(self):
        """Test enriching chunks with timestamp metadata."""
        if not MetadataEnricher:
            pytest.skip("MetadataEnricher not implemented yet")
        
        enricher = MetadataEnricher(config={'add_timestamps': True})
        
        chunk = {
            "id": "chunk_1",
            "content": "Test content",
            "type": "text"
        }
        
        enriched_chunk = enricher.enrich_chunk(chunk, {})
        
        metadata = enriched_chunk["metadata"]
        assert "timestamp" in metadata
        assert "processing_date" in metadata
        
        # Should be valid ISO format timestamp
        timestamp = metadata["timestamp"]
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    def test_enrich_chunk_adds_extraction_metadata(self):
        """Test enriching chunks with extraction metadata."""
        if not MetadataEnricher:
            pytest.skip("MetadataEnricher not implemented yet")
        
        enricher = MetadataEnricher(config={'add_extraction_metadata': True})
        
        chunk = {
            "id": "chunk_1",
            "content": "Test content",
            "type": "text"
        }
        
        original_data = {
            "_metadata": {
                "extraction_method": "structured_data",
                "confidence": 0.95,
                "url": "https://example.com",
                "scrape_timestamp": "2024-01-01T10:00:00Z"
            }
        }
        
        enriched_chunk = enricher.enrich_chunk(chunk, original_data)
        
        metadata = enriched_chunk["metadata"]
        assert "extraction_method" in metadata
        assert "confidence_score" in metadata
        assert "source_url" in metadata
        assert "scrape_timestamp" in metadata
        assert metadata["extraction_method"] == "structured_data"
        assert metadata["confidence_score"] == 0.95
    
    def test_enrich_chunk_adds_domain_keywords(self):
        """Test enriching chunks with domain-specific keywords."""
        if not MetadataEnricher:
            pytest.skip("MetadataEnricher not implemented yet")
        
        enricher = MetadataEnricher(config={'add_domain_keywords': True})
        
        # Test restaurant cuisine chunk
        chunk = {
            "id": "chunk_1",
            "content": "Authentic Italian cuisine with fresh pasta",
            "type": "text",
            "source_field": "cuisine"
        }
        
        enriched_chunk = enricher.enrich_chunk(chunk, {"cuisine": "Italian"})
        
        metadata = enriched_chunk["metadata"]
        assert "domain_keywords" in metadata
        keywords = metadata["domain_keywords"]
        
        # Should contain cuisine-related keywords
        assert any("food" in keywords for keywords in [keywords] if isinstance(keywords, list))
        assert any("dining" in keywords for keywords in [keywords] if isinstance(keywords, list))
    
    def test_enrich_chunk_calculates_content_metrics(self):
        """Test enriching chunks with content analysis metrics."""
        if not MetadataEnricher:
            pytest.skip("MetadataEnricher not implemented yet")
        
        enricher = MetadataEnricher(config={'add_content_metrics': True})
        
        chunk = {
            "id": "chunk_1",
            "content": "This restaurant serves excellent Italian food. Great pasta dishes!",
            "type": "text"
        }
        
        enriched_chunk = enricher.enrich_chunk(chunk, {})
        
        metadata = enriched_chunk["metadata"]
        assert "word_count" in metadata
        assert "sentence_count" in metadata
        assert "readability_score" in metadata
        
        assert metadata["word_count"] == 9
        assert metadata["sentence_count"] == 2
        assert isinstance(metadata["readability_score"], (int, float))
    
    def test_enrich_chunks_batch_processing(self):
        """Test enriching multiple chunks in batch."""
        if not MetadataEnricher:
            pytest.skip("MetadataEnricher not implemented yet")
        
        enricher = MetadataEnricher()
        
        chunks = [
            {"id": "chunk_1", "content": "First chunk", "type": "text"},
            {"id": "chunk_2", "content": "Second chunk", "type": "text"},
            {"id": "chunk_3", "content": "Third chunk", "type": "text"}
        ]
        
        original_data = {"name": "Test Restaurant"}
        
        enriched_chunks = enricher.enrich_chunks(chunks, original_data)
        
        assert len(enriched_chunks) == 3
        
        for chunk in enriched_chunks:
            assert "metadata" in chunk
            assert "entity_name" in chunk["metadata"]
            assert chunk["metadata"]["entity_name"] == "Test Restaurant"
    
    def test_add_relationship_hints(self):
        """Test adding relationship hints to chunks."""
        if not MetadataEnricher:
            pytest.skip("MetadataEnricher not implemented yet")
        
        enricher = MetadataEnricher(config={'add_relationship_hints': True})
        
        chunk = {
            "id": "chunk_1",
            "content": "Menu items include pasta and pizza",
            "type": "text",
            "source_field": "menu"
        }
        
        original_data = {
            "name": "Restaurant",
            "menu": ["pasta", "pizza"],
            "location": {"address": "123 Main St"}
        }
        
        enriched_chunk = enricher.enrich_chunk(chunk, original_data)
        
        metadata = enriched_chunk["metadata"]
        assert "relationship_hints" in metadata
        hints = metadata["relationship_hints"]
        
        # Should suggest relationships to other data fields
        assert "related_fields" in hints
        assert any("location" in hint for hint in hints.get("related_fields", []))
    
    def test_add_embedding_optimization_hints(self):
        """Test adding hints for embedding optimization."""
        if not MetadataEnricher:
            pytest.skip("MetadataEnricher not implemented yet")
        
        enricher = MetadataEnricher(config={'add_embedding_hints': True})
        
        chunk = {
            "id": "chunk_1",
            "content": "Romantic Italian restaurant with candlelit tables",
            "type": "text",
            "source_field": "ambiance"
        }
        
        enriched_chunk = enricher.enrich_chunk(chunk, {"ambiance": "romantic"})
        
        metadata = enriched_chunk["metadata"]
        assert "embedding_hints" in metadata
        hints = metadata["embedding_hints"]
        
        assert "semantic_context" in hints
        assert "importance_weight" in hints
        assert "query_templates" in hints
        assert isinstance(hints["importance_weight"], (int, float))
    
    def test_calculate_chunk_importance(self):
        """Test calculating chunk importance scores."""
        if not MetadataEnricher:
            pytest.skip("MetadataEnricher not implemented yet")
        
        enricher = MetadataEnricher()
        
        # High importance chunk (name)
        name_chunk = {
            "id": "chunk_1",
            "content": "Bistro Romano",
            "source_field": "name"
        }
        
        # Lower importance chunk (hours)
        hours_chunk = {
            "id": "chunk_2", 
            "content": "Open 9-5",
            "source_field": "hours"
        }
        
        name_importance = enricher.calculate_chunk_importance(name_chunk, {})
        hours_importance = enricher.calculate_chunk_importance(hours_chunk, {})
        
        assert isinstance(name_importance, (int, float))
        assert isinstance(hours_importance, (int, float))
        assert name_importance > hours_importance  # Name should be more important
    
    def test_add_temporal_metadata(self):
        """Test adding temporal metadata for time-sensitive information."""
        if not MetadataEnricher:
            pytest.skip("MetadataEnricher not implemented yet")
        
        enricher = MetadataEnricher(config={'add_temporal_metadata': True})
        
        chunk = {
            "id": "chunk_1",
            "content": "Special menu for December 2024",
            "type": "text",
            "source_field": "specials"
        }
        
        enriched_chunk = enricher.enrich_chunk(chunk, {})
        
        metadata = enriched_chunk["metadata"]
        assert "temporal_relevance" in metadata
        assert "expiry_hint" in metadata
        
        # Should detect time-sensitive content
        temporal = metadata["temporal_relevance"]
        assert temporal in ["high", "medium", "low"]
    
    def test_handle_missing_metadata_gracefully(self):
        """Test handling chunks with missing or incomplete metadata."""
        if not MetadataEnricher:
            pytest.skip("MetadataEnricher not implemented yet")
        
        enricher = MetadataEnricher()
        
        # Chunk with minimal data
        chunk = {
            "id": "chunk_1",
            "content": "Test content"
        }
        
        # Original data with missing metadata
        original_data = {}
        
        enriched_chunk = enricher.enrich_chunk(chunk, original_data)
        
        # Should not crash and should provide default metadata
        assert "metadata" in enriched_chunk
        metadata = enriched_chunk["metadata"]
        assert "entity_name" in metadata
        assert "source_type" in metadata
        
        # Should have sensible defaults
        assert metadata["entity_name"] == "Unknown"
        assert metadata["source_type"] == "restaurant"
    
    def test_preserve_existing_metadata(self):
        """Test that existing metadata is preserved and enhanced."""
        if not MetadataEnricher:
            pytest.skip("MetadataEnricher not implemented yet")
        
        enricher = MetadataEnricher()
        
        chunk = {
            "id": "chunk_1",
            "content": "Test content",
            "metadata": {
                "existing_field": "existing_value",
                "chunk_type": "description"
            }
        }
        
        enriched_chunk = enricher.enrich_chunk(chunk, {"name": "Test Restaurant"})
        
        metadata = enriched_chunk["metadata"]
        
        # Should preserve existing metadata
        assert metadata["existing_field"] == "existing_value"
        assert metadata["chunk_type"] == "description"
        
        # Should add new metadata
        assert "entity_name" in metadata
        assert metadata["entity_name"] == "Test Restaurant"