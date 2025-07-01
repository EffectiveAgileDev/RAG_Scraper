"""Unit tests for RelationshipMapper - creates relationships between semantic chunks."""

import pytest
from unittest.mock import Mock, patch

# Import will fail until we implement - expected for RED phase
try:
    from src.semantic.relationship_mapper import RelationshipMapper
except ImportError:
    RelationshipMapper = None


class TestRelationshipMapper:
    """Test the RelationshipMapper class."""
    
    def test_relationship_mapper_initialization(self):
        """Test RelationshipMapper can be initialized."""
        if not RelationshipMapper:
            pytest.skip("RelationshipMapper not implemented yet")
        
        mapper = RelationshipMapper()
        assert mapper is not None
        assert hasattr(mapper, 'config')
    
    def test_relationship_mapper_custom_config(self):
        """Test RelationshipMapper with custom configuration."""
        if not RelationshipMapper:
            pytest.skip("RelationshipMapper not implemented yet")
        
        config = {
            'create_hierarchical': True,
            'create_semantic': True,
            'create_temporal': True,
            'confidence_threshold': 0.7
        }
        
        mapper = RelationshipMapper(config=config)
        assert mapper.config['create_hierarchical'] is True
        assert mapper.config['create_semantic'] is True
        assert mapper.config['create_temporal'] is True
        assert mapper.config['confidence_threshold'] == 0.7
    
    def test_create_relationships_basic_hierarchy(self):
        """Test creating basic hierarchical relationships."""
        if not RelationshipMapper:
            pytest.skip("RelationshipMapper not implemented yet")
        
        mapper = RelationshipMapper()
        
        chunks = [
            {"id": "chunk_1", "content": "Bistro Romano", "source_field": "name"},
            {"id": "chunk_2", "content": "Italian cuisine", "source_field": "cuisine"},
            {"id": "chunk_3", "content": "Pasta and pizza menu", "source_field": "menu"}
        ]
        
        original_data = {
            "name": "Bistro Romano",
            "cuisine": "Italian",
            "menu": ["pasta", "pizza"]
        }
        
        relationships = mapper.create_relationships(chunks, original_data)
        
        assert isinstance(relationships, list)
        assert len(relationships) > 0
        
        # Should have hierarchical relationships
        hierarchical_types = ["has_cuisine", "has_menu", "contains", "belongs_to"]
        hierarchical_rels = [rel for rel in relationships if rel["type"] in hierarchical_types]
        assert len(hierarchical_rels) > 0
        
        for rel in relationships:
            assert "from" in rel
            assert "to" in rel
            assert "type" in rel
    
    def test_create_hierarchical_relationships(self):
        """Test creating hierarchical parent-child relationships."""
        if not RelationshipMapper:
            pytest.skip("RelationshipMapper not implemented yet")
        
        mapper = RelationshipMapper(config={'create_hierarchical': True})
        
        chunks = [
            {"id": "restaurant_main", "content": "Main restaurant info", "source_field": "name"},
            {"id": "menu_section", "content": "Menu details", "source_field": "menu"},
            {"id": "location_info", "content": "Address details", "source_field": "location"}
        ]
        
        relationships = mapper.create_hierarchical_relationships(chunks, {})
        
        assert isinstance(relationships, list)
        
        # Should create parent-child relationships
        restaurant_children = [rel for rel in relationships if rel["from"] == "restaurant_main"]
        assert len(restaurant_children) >= 2  # Should link to menu and location
    
    def test_create_semantic_relationships(self):
        """Test creating semantic similarity relationships."""
        if not RelationshipMapper:
            pytest.skip("RelationshipMapper not implemented yet")
        
        mapper = RelationshipMapper(config={'create_semantic': True, 'confidence_threshold': 0.1})
        
        chunks = [
            {"id": "chunk_1", "content": "Italian cuisine with pasta", "source_field": "cuisine"},
            {"id": "chunk_2", "content": "Fresh pasta dishes daily", "source_field": "menu"},
            {"id": "chunk_3", "content": "Business hours", "source_field": "hours"}
        ]
        
        relationships = mapper.create_semantic_relationships(chunks)
        
        assert isinstance(relationships, list)
        
        # Should find semantic relationships between cuisine and menu chunks
        semantic_rels = [rel for rel in relationships if rel["type"] == "semantically_related"]
        assert len(semantic_rels) > 0
        
        # Should have confidence scores
        for rel in semantic_rels:
            assert "confidence" in rel
            assert 0.0 <= rel["confidence"] <= 1.0
    
    def test_create_temporal_relationships(self):
        """Test creating temporal relationships for time-sensitive content."""
        if not RelationshipMapper:
            pytest.skip("RelationshipMapper not implemented yet")
        
        mapper = RelationshipMapper(config={'create_temporal': True})
        
        chunks = [
            {"id": "chunk_1", "content": "Open Monday-Friday 9-5", "source_field": "hours"},
            {"id": "chunk_2", "content": "Weekend brunch special", "source_field": "specials"},
            {"id": "chunk_3", "content": "Contact information", "source_field": "contact"}
        ]
        
        relationships = mapper.create_temporal_relationships(chunks)
        
        assert isinstance(relationships, list)
        
        # Should find temporal relationships
        temporal_rels = [rel for rel in relationships if rel["type"] == "temporally_related"]
        
        # At least hours and specials should be temporally related
        hour_special_rel = any(
            (rel["from"] == "chunk_1" and rel["to"] == "chunk_2") or
            (rel["from"] == "chunk_2" and rel["to"] == "chunk_1")
            for rel in temporal_rels
        )
        assert hour_special_rel
    
    def test_calculate_semantic_similarity(self):
        """Test calculating semantic similarity between chunks."""
        if not RelationshipMapper:
            pytest.skip("RelationshipMapper not implemented yet")
        
        mapper = RelationshipMapper()
        
        chunk1 = {"content": "Italian pasta restaurant", "id": "1"}
        chunk2 = {"content": "Fresh pasta dishes and Italian cuisine", "id": "2"}
        chunk3 = {"content": "Business contact phone number", "id": "3"}
        
        # Similar chunks should have high similarity
        sim_high = mapper.calculate_semantic_similarity(chunk1, chunk2)
        
        # Dissimilar chunks should have low similarity  
        sim_low = mapper.calculate_semantic_similarity(chunk1, chunk3)
        
        assert isinstance(sim_high, float)
        assert isinstance(sim_low, float)
        assert 0.0 <= sim_high <= 1.0
        assert 0.0 <= sim_low <= 1.0
        assert sim_high > sim_low  # Italian/pasta chunks more similar than pasta/phone
    
    def test_detect_bidirectional_relationships(self):
        """Test detecting bidirectional relationships."""
        if not RelationshipMapper:
            pytest.skip("RelationshipMapper not implemented yet")
        
        mapper = RelationshipMapper()
        
        chunks = [
            {"id": "restaurant_info", "content": "Bistro Romano", "source_field": "name"},
            {"id": "location_info", "content": "123 Main Street", "source_field": "location"}
        ]
        
        relationships = mapper.create_relationships(chunks, {})
        
        # Should detect that restaurant and location are bidirectionally related
        bidirectional_rels = [rel for rel in relationships if rel.get("bidirectional", False)]
        assert len(bidirectional_rels) > 0
    
    def test_filter_relationships_by_confidence(self):
        """Test filtering relationships by confidence threshold."""
        if not RelationshipMapper:
            pytest.skip("RelationshipMapper not implemented yet")
        
        mapper = RelationshipMapper(config={'confidence_threshold': 0.7})
        
        # Mock relationships with different confidence scores
        relationships = [
            {"from": "chunk_1", "to": "chunk_2", "type": "related", "confidence": 0.9},
            {"from": "chunk_2", "to": "chunk_3", "type": "related", "confidence": 0.5},
            {"from": "chunk_1", "to": "chunk_3", "type": "related", "confidence": 0.8}
        ]
        
        filtered = mapper.filter_relationships_by_confidence(relationships)
        
        # Should only keep relationships with confidence >= 0.7
        assert len(filtered) == 2
        for rel in filtered:
            assert rel["confidence"] >= 0.7
    
    def test_create_cross_reference_relationships(self):
        """Test creating cross-reference relationships between related fields."""
        if not RelationshipMapper:
            pytest.skip("RelationshipMapper not implemented yet")
        
        mapper = RelationshipMapper()
        
        chunks = [
            {"id": "menu_chunk", "content": "Pizza and pasta", "source_field": "menu"},
            {"id": "price_chunk", "content": "$15-25 per entree", "source_field": "price_range"},
            {"id": "cuisine_chunk", "content": "Italian", "source_field": "cuisine"}
        ]
        
        relationships = mapper.create_cross_reference_relationships(chunks)
        
        assert isinstance(relationships, list)
        
        # Should link menu with price and cuisine
        menu_refs = [rel for rel in relationships if rel["from"] == "menu_chunk"]
        assert len(menu_refs) >= 2  # Links to price and cuisine
    
    def test_detect_containment_relationships(self):
        """Test detecting containment/composition relationships."""
        if not RelationshipMapper:
            pytest.skip("RelationshipMapper not implemented yet")
        
        mapper = RelationshipMapper()
        
        chunks = [
            {"id": "restaurant", "content": "Bistro Romano restaurant", "source_field": "name"},
            {"id": "address", "content": "123 Main St, City", "source_field": "location.address"},
            {"id": "phone", "content": "555-1234", "source_field": "contact.phone"}
        ]
        
        relationships = mapper.detect_containment_relationships(chunks)
        
        # Should detect that restaurant contains address and phone
        containment_rels = [rel for rel in relationships if rel["type"] == "contains"]
        assert len(containment_rels) >= 2
    
    def test_create_dependency_relationships(self):
        """Test creating dependency relationships."""
        if not RelationshipMapper:
            pytest.skip("RelationshipMapper not implemented yet")
        
        mapper = RelationshipMapper()
        
        chunks = [
            {"id": "hours", "content": "Open 9-5", "source_field": "hours"},
            {"id": "location", "content": "Downtown area", "source_field": "location"},
            {"id": "contact", "content": "Call for reservations", "source_field": "contact"}
        ]
        
        relationships = mapper.create_dependency_relationships(chunks)
        
        # Hours and location might depend on each other for relevance
        dependency_rels = [rel for rel in relationships if rel["type"] == "depends_on"]
        assert isinstance(dependency_rels, list)
    
    def test_add_relationship_metadata(self):
        """Test adding metadata to relationships."""
        if not RelationshipMapper:
            pytest.skip("RelationshipMapper not implemented yet")
        
        mapper = RelationshipMapper()
        
        relationships = [
            {"from": "chunk_1", "to": "chunk_2", "type": "related"}
        ]
        
        enriched_rels = mapper.add_relationship_metadata(relationships)
        
        assert len(enriched_rels) == 1
        rel = enriched_rels[0]
        
        # Should add metadata
        assert "metadata" in rel
        metadata = rel["metadata"]
        assert "created_at" in metadata
        assert "confidence" in metadata
        assert "strength" in metadata
    
    def test_remove_duplicate_relationships(self):
        """Test removing duplicate relationships."""
        if not RelationshipMapper:
            pytest.skip("RelationshipMapper not implemented yet")
        
        mapper = RelationshipMapper()
        
        relationships = [
            {"from": "chunk_1", "to": "chunk_2", "type": "related"},
            {"from": "chunk_1", "to": "chunk_2", "type": "related"},  # Duplicate
            {"from": "chunk_2", "to": "chunk_1", "type": "related"},  # Reverse (should keep if bidirectional)
            {"from": "chunk_1", "to": "chunk_3", "type": "related"}
        ]
        
        deduplicated = mapper.remove_duplicate_relationships(relationships)
        
        # Should remove exact duplicates but keep unique relationships
        assert len(deduplicated) <= len(relationships)
        assert len(deduplicated) >= 2  # At least chunk_1->chunk_3 and one chunk_1<->chunk_2
    
    def test_handle_empty_chunks_gracefully(self):
        """Test handling empty or invalid chunk data gracefully."""
        if not RelationshipMapper:
            pytest.skip("RelationshipMapper not implemented yet")
        
        mapper = RelationshipMapper()
        
        # Empty chunks list
        relationships_empty = mapper.create_relationships([], {})
        assert relationships_empty == []
        
        # Chunks with missing fields
        invalid_chunks = [
            {"id": "chunk_1"},  # Missing content
            {"content": "Some content"}  # Missing id
        ]
        
        relationships_invalid = mapper.create_relationships(invalid_chunks, {})
        # Should not crash and return empty or minimal relationships
        assert isinstance(relationships_invalid, list)