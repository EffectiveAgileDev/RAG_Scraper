"""Unit tests for ChunkOptimizer - optimizes chunk boundaries and sizes."""

import pytest
from unittest.mock import Mock, patch

# Import will fail until we implement - expected for RED phase
try:
    from src.semantic.chunk_optimizer import ChunkOptimizer, ChunkBoundary
except ImportError:
    ChunkOptimizer = None
    ChunkBoundary = None


class TestChunkOptimizer:
    """Test the ChunkOptimizer class."""
    
    def test_chunk_optimizer_initialization(self):
        """Test ChunkOptimizer can be initialized."""
        if not ChunkOptimizer:
            pytest.skip("ChunkOptimizer not implemented yet")
        
        optimizer = ChunkOptimizer()
        assert optimizer is not None
        assert hasattr(optimizer, 'max_chunk_size')
        assert hasattr(optimizer, 'overlap_size')
        assert optimizer.max_chunk_size == 512  # Default
    
    def test_chunk_optimizer_custom_config(self):
        """Test ChunkOptimizer with custom configuration."""
        if not ChunkOptimizer:
            pytest.skip("ChunkOptimizer not implemented yet")
        
        config = {
            'max_chunk_size': 256,
            'overlap_size': 25,
            'preserve_sentences': True
        }
        
        optimizer = ChunkOptimizer(config=config)
        assert optimizer.max_chunk_size == 256
        assert optimizer.overlap_size == 25
        assert optimizer.preserve_sentences is True
    
    def test_optimize_chunks_respects_size_limits(self):
        """Test chunk optimization respects size limits."""
        if not ChunkOptimizer:
            pytest.skip("ChunkOptimizer not implemented yet")
        
        optimizer = ChunkOptimizer(config={'max_chunk_size': 10})
        
        # Long text that needs chunking
        long_text = "This is a very long text " * 20  # 100 words
        
        optimized_chunks = optimizer.optimize_chunks([{
            "content": long_text,
            "id": "test_1"
        }])
        
        assert len(optimized_chunks) > 1  # Should be split
        
        for chunk in optimized_chunks:
            word_count = len(chunk["content"].split())
            assert word_count <= 10, f"Chunk exceeds size limit: {word_count}"
    
    def test_optimize_chunks_preserves_sentence_boundaries(self):
        """Test that chunk optimization preserves sentence boundaries."""
        if not ChunkOptimizer:
            pytest.skip("ChunkOptimizer not implemented yet")
        
        optimizer = ChunkOptimizer(config={
            'max_chunk_size': 15,
            'preserve_sentences': True
        })
        
        text = "First sentence here. Second sentence follows. Third sentence ends."
        
        optimized_chunks = optimizer.optimize_chunks([{
            "content": text,
            "id": "test_1"
        }])
        
        for chunk in optimized_chunks:
            content = chunk["content"].strip()
            if len(content) > 10:  # Only check longer chunks
                assert content.endswith(('.', '!', '?')), f"Chunk doesn't end at sentence: {content}"
    
    def test_optimize_chunks_adds_overlap(self):
        """Test that chunks include overlap for context."""
        if not ChunkOptimizer:
            pytest.skip("ChunkOptimizer not implemented yet")
        
        optimizer = ChunkOptimizer(config={
            'max_chunk_size': 10,
            'overlap_size': 3
        })
        
        long_text = " ".join([f"word{i}" for i in range(30)])  # 30 words
        
        optimized_chunks = optimizer.optimize_chunks([{
            "content": long_text,
            "id": "test_1"
        }])
        
        if len(optimized_chunks) > 1:
            # Check that subsequent chunks have overlap metadata
            for i in range(1, len(optimized_chunks)):
                chunk = optimized_chunks[i]
                assert "overlap_with_previous" in chunk.get("metadata", {}) or \
                       "overlap_info" in chunk.get("metadata", {})
    
    def test_find_optimal_boundaries_paragraph_breaks(self):
        """Test finding optimal boundaries at paragraph breaks."""
        if not ChunkOptimizer:
            pytest.skip("ChunkOptimizer not implemented yet")
        
        optimizer = ChunkOptimizer()
        
        text = "First paragraph.\n\nSecond paragraph here.\n\nThird paragraph content."
        
        boundaries = optimizer.find_optimal_boundaries(text, max_size=20)
        
        assert len(boundaries) > 0
        assert isinstance(boundaries[0], (dict, ChunkBoundary))
        
        # Should prefer paragraph boundaries
        for boundary in boundaries:
            boundary_info = boundary if isinstance(boundary, dict) else boundary.__dict__
            assert "boundary_type" in boundary_info
    
    def test_find_optimal_boundaries_sentence_breaks(self):
        """Test finding optimal boundaries at sentence breaks."""
        if not ChunkOptimizer:
            pytest.skip("ChunkOptimizer not implemented yet")
        
        optimizer = ChunkOptimizer()
        
        text = "First sentence. Second sentence here. Third sentence content. Fourth sentence."
        
        boundaries = optimizer.find_optimal_boundaries(text, max_size=15)
        
        assert len(boundaries) > 0
        
        # Check that boundaries respect sentence endings
        for boundary in boundaries:
            boundary_info = boundary if isinstance(boundary, dict) else boundary.__dict__
            assert boundary_info.get("boundary_type") in ["sentence", "paragraph", "word"]
    
    def test_calculate_semantic_coherence_score(self):
        """Test semantic coherence scoring."""
        if not ChunkOptimizer:
            pytest.skip("ChunkOptimizer not implemented yet")
        
        optimizer = ChunkOptimizer()
        
        # Coherent text
        coherent_text = "This restaurant serves Italian food. The pasta is excellent. Great wine selection."
        coherent_score = optimizer.calculate_semantic_coherence(coherent_text)
        
        # Less coherent text
        mixed_text = "Restaurant location. Pasta recipe ingredients. Weather forecast today."
        mixed_score = optimizer.calculate_semantic_coherence(mixed_text)
        
        assert isinstance(coherent_score, float)
        assert isinstance(mixed_score, float)
        assert 0.0 <= coherent_score <= 1.0
        assert 0.0 <= mixed_score <= 1.0
        # Coherent text should score higher
        assert coherent_score >= mixed_score
    
    def test_merge_small_chunks(self):
        """Test merging of chunks that are too small."""
        if not ChunkOptimizer:
            pytest.skip("ChunkOptimizer not implemented yet")
        
        optimizer = ChunkOptimizer(config={'min_chunk_size': 10})
        
        small_chunks = [
            {"content": "Short.", "id": "1"},
            {"content": "Also short.", "id": "2"}, 
            {"content": "This is a longer chunk that should not be merged with others.", "id": "3"},
            {"content": "Small.", "id": "4"}
        ]
        
        merged_chunks = optimizer.merge_small_chunks(small_chunks)
        
        # Should have fewer chunks after merging
        assert len(merged_chunks) < len(small_chunks)
        
        # No chunk should be too small (except possibly the last one)
        for i, chunk in enumerate(merged_chunks[:-1]):  # All but last
            word_count = len(chunk["content"].split())
            assert word_count >= 10 or i == len(merged_chunks) - 1
    
    def test_split_large_chunks(self):
        """Test splitting of chunks that are too large."""
        if not ChunkOptimizer:
            pytest.skip("ChunkOptimizer not implemented yet")
        
        optimizer = ChunkOptimizer(config={'max_chunk_size': 15})
        
        large_chunk = {
            "content": " ".join([f"word{i}" for i in range(30)]),  # 30 words
            "id": "large_1"
        }
        
        split_chunks = optimizer.split_large_chunks([large_chunk])
        
        # Should have more chunks after splitting
        assert len(split_chunks) > 1
        
        # Each chunk should be within size limit
        for chunk in split_chunks:
            word_count = len(chunk["content"].split())
            assert word_count <= 15
    
    def test_optimize_for_embeddings(self):
        """Test optimization specifically for embedding generation."""
        if not ChunkOptimizer:
            pytest.skip("ChunkOptimizer not implemented yet")
        
        optimizer = ChunkOptimizer()
        
        chunks = [
            {"content": "Restaurant serves Italian cuisine with authentic flavors.", "id": "1"},
            {"content": "The pasta dishes are handmade daily.", "id": "2"}
        ]
        
        optimized = optimizer.optimize_for_embeddings(chunks)
        
        assert len(optimized) > 0
        
        for chunk in optimized:
            assert "embedding_metadata" in chunk
            embedding_meta = chunk["embedding_metadata"]
            assert "optimal_for_embedding" in embedding_meta
            assert "keyword_density" in embedding_meta
            assert isinstance(embedding_meta["keyword_density"], (int, float))
    
    def test_add_contextual_overlap(self):
        """Test adding contextual overlap between chunks."""
        if not ChunkOptimizer:
            pytest.skip("ChunkOptimizer not implemented yet")
        
        optimizer = ChunkOptimizer(config={'overlap_size': 5})
        
        chunks = [
            {"content": "First chunk with some content here.", "id": "1"},
            {"content": "Second chunk with more information.", "id": "2"},
            {"content": "Third chunk concludes the text.", "id": "3"}
        ]
        
        chunks_with_overlap = optimizer.add_contextual_overlap(chunks)
        
        assert len(chunks_with_overlap) == len(chunks)
        
        # Check overlap metadata
        for i, chunk in enumerate(chunks_with_overlap):
            if i > 0:  # Not first chunk
                assert "overlap_with_previous" in chunk.get("metadata", {}) or \
                       "context_from_previous" in chunk.get("metadata", {})
            
            if i < len(chunks_with_overlap) - 1:  # Not last chunk
                assert "overlap_with_next" in chunk.get("metadata", {}) or \
                       "context_for_next" in chunk.get("metadata", {})


class TestChunkBoundary:
    """Test the ChunkBoundary data structure."""
    
    def test_chunk_boundary_creation(self):
        """Test ChunkBoundary can be created."""
        if not ChunkBoundary:
            pytest.skip("ChunkBoundary not implemented yet")
        
        boundary = ChunkBoundary(
            position=100,
            boundary_type="sentence",
            confidence=0.9
        )
        
        assert boundary.position == 100
        assert boundary.boundary_type == "sentence"
        assert boundary.confidence == 0.9
    
    def test_chunk_boundary_validation(self):
        """Test ChunkBoundary validates its data."""
        if not ChunkBoundary:
            pytest.skip("ChunkBoundary not implemented yet")
        
        # Should validate position is non-negative
        with pytest.raises((ValueError, TypeError)):
            ChunkBoundary(
                position=-1,
                boundary_type="sentence", 
                confidence=0.9
            )
        
        # Should validate confidence is between 0 and 1
        with pytest.raises((ValueError, TypeError)):
            ChunkBoundary(
                position=100,
                boundary_type="sentence",
                confidence=1.5  # Should be <= 1.0
            )
    
    def test_chunk_boundary_comparison(self):
        """Test ChunkBoundary comparison for sorting."""
        if not ChunkBoundary:
            pytest.skip("ChunkBoundary not implemented yet")
        
        boundary1 = ChunkBoundary(position=50, boundary_type="word", confidence=0.5)
        boundary2 = ChunkBoundary(position=100, boundary_type="sentence", confidence=0.9)
        
        # Should be comparable by position or confidence
        assert boundary1 != boundary2
        
        # If comparable, should follow logical ordering
        if hasattr(boundary1, '__lt__'):
            boundaries = [boundary2, boundary1]
            sorted_boundaries = sorted(boundaries)
            assert sorted_boundaries[0].position <= sorted_boundaries[1].position