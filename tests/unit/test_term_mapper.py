"""Unit tests for term mapping functionality."""
import pytest
from unittest.mock import Mock, patch


class TestTermMapper:
    """Test cases for the TermMapper class."""

    def test_mapper_initialization(self):
        """Test TermMapper initializes correctly with industry database."""
        from src.knowledge.term_mapper import TermMapper
        
        mock_db = Mock()
        mapper = TermMapper(mock_db)
        
        assert mapper.database == mock_db
        assert hasattr(mapper, 'confidence_threshold')
        assert hasattr(mapper, 'cache')

    def test_map_customer_term_to_website_terms_exact_match(self):
        """Test mapping customer term to website terms with exact match."""
        from src.knowledge.term_mapper import TermMapper
        
        mock_db = Mock()
        mock_db.get_term_mapping.return_value = {
            "customer_term": "vegetarian options",
            "website_terms": [
                {"term": "vegetarian", "confidence": 1.0},
                {"term": "vegan", "confidence": 0.9},
                {"term": "plant-based", "confidence": 0.8}
            ],
            "category": "Menu Items"
        }
        
        mapper = TermMapper(mock_db)
        result = mapper.map_term("vegetarian options", "Restaurant")
        
        assert result is not None
        assert result["customer_term"] == "vegetarian options"
        assert len(result["website_terms"]) == 3
        assert result["category"] == "Menu Items"
        assert result["match_type"] == "exact"

    def test_map_customer_term_no_match_returns_none(self):
        """Test mapping returns None for unknown customer terms."""
        from src.knowledge.term_mapper import TermMapper
        
        mock_db = Mock()
        mock_db.get_term_mapping.return_value = None
        
        mapper = TermMapper(mock_db)
        result = mapper.map_term("quantum dining", "Restaurant")
        
        assert result is None
        mock_db.get_term_mapping.assert_called_once_with("quantum dining", "Restaurant")

    def test_map_term_with_confidence_filtering(self):
        """Test mapping filters results by confidence threshold."""
        from src.knowledge.term_mapper import TermMapper
        
        mock_db = Mock()
        mock_db.get_term_mapping.return_value = {
            "customer_term": "parking",
            "website_terms": [
                {"term": "parking", "confidence": 0.9},
                {"term": "valet", "confidence": 0.7},
                {"term": "garage", "confidence": 0.4}  # Below threshold
            ],
            "category": "Amenities"
        }
        
        mapper = TermMapper(mock_db, confidence_threshold=0.5)
        result = mapper.map_term("parking", "Restaurant")
        
        # Should filter out terms below threshold
        filtered_terms = [t for t in result["website_terms"] if t["confidence"] >= 0.5]
        assert len(filtered_terms) == 2
        assert all(t["confidence"] >= 0.5 for t in filtered_terms)

    def test_map_multiple_terms_batch_processing(self):
        """Test mapping multiple terms in batch for efficiency."""
        from src.knowledge.term_mapper import TermMapper
        
        mock_db = Mock()
        mock_db.get_term_mappings_batch.return_value = {
            "vegetarian options": {
                "customer_term": "vegetarian options",
                "website_terms": [{"term": "vegetarian", "confidence": 1.0}],
                "category": "Menu Items"
            },
            "parking": {
                "customer_term": "parking",
                "website_terms": [{"term": "parking", "confidence": 0.9}],
                "category": "Amenities"
            }
        }
        
        mapper = TermMapper(mock_db)
        terms = ["vegetarian options", "parking"]
        results = mapper.map_terms_batch(terms, "Restaurant")
        
        assert len(results) == 2
        assert "vegetarian options" in results
        assert "parking" in results
        mock_db.get_term_mappings_batch.assert_called_once()

    def test_map_term_caching_functionality(self):
        """Test term mapping uses caching for performance."""
        from src.knowledge.term_mapper import TermMapper
        
        mock_db = Mock()
        mock_db.get_term_mapping.return_value = {
            "customer_term": "wifi",
            "website_terms": [{"term": "wifi", "confidence": 1.0}],
            "category": "Amenities"
        }
        
        mapper = TermMapper(mock_db, enable_cache=True)
        
        # First call should hit database
        result1 = mapper.map_term("wifi", "Restaurant")
        assert mock_db.get_term_mapping.call_count == 1
        
        # Second call should use cache
        result2 = mapper.map_term("wifi", "Restaurant")
        assert mock_db.get_term_mapping.call_count == 1  # No additional calls
        
        assert result1 == result2

    def test_map_term_cross_industry_isolation(self):
        """Test term mapping isolates industries correctly."""
        from src.knowledge.term_mapper import TermMapper
        
        mock_db = Mock()
        
        def mock_get_mapping(term, industry):
            if industry == "Restaurant" and term == "menu items":
                return {"customer_term": "menu items", "website_terms": []}
            elif industry == "Medical" and term == "menu items":
                return None
            return None
        
        mock_db.get_term_mapping.side_effect = mock_get_mapping
        
        mapper = TermMapper(mock_db)
        
        # Should find mapping in Restaurant industry
        restaurant_result = mapper.map_term("menu items", "Restaurant")
        assert restaurant_result is not None
        
        # Should not find mapping in Medical industry
        medical_result = mapper.map_term("menu items", "Medical")
        assert medical_result is None

    def test_get_mapping_confidence_score_calculation(self):
        """Test confidence score calculation for mappings."""
        from src.knowledge.term_mapper import TermMapper
        
        mapper = TermMapper(Mock())
        
        # Test confidence calculation with multiple factors
        factors = {
            "exact_match": True,
            "source_reliability": 0.9,
            "term_frequency": 0.8,
            "context_relevance": 0.7
        }
        
        confidence = mapper.calculate_confidence(factors)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.7  # Should be high for exact match

    def test_get_mapping_confidence_score_fuzzy_match(self):
        """Test confidence score calculation for fuzzy matches."""
        from src.knowledge.term_mapper import TermMapper
        
        mapper = TermMapper(Mock())
        
        # Test confidence calculation for fuzzy match
        factors = {
            "exact_match": False,
            "fuzzy_similarity": 0.85,
            "source_reliability": 0.9,
            "term_frequency": 0.6
        }
        
        confidence = mapper.calculate_confidence(factors)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence < 0.9  # Should be lower for fuzzy match

    def test_map_term_logs_unknown_terms(self):
        """Test mapper logs unknown terms for analysis."""
        from src.knowledge.term_mapper import TermMapper
        
        mock_db = Mock()
        mock_db.get_term_mapping.return_value = None
        
        with patch('src.knowledge.term_mapper.logger') as mock_logger:
            mapper = TermMapper(mock_db)
            result = mapper.map_term("unknown_term", "Restaurant")
            
            assert result is None
            mock_logger.info.assert_called_with(
                "Unknown term logged: unknown_term (Industry: Restaurant)"
            )

    def test_map_term_fallback_to_generic_extraction(self):
        """Test mapper suggests fallback to generic extraction."""
        from src.knowledge.term_mapper import TermMapper
        
        mock_db = Mock()
        mock_db.get_term_mapping.return_value = None
        
        mapper = TermMapper(mock_db, enable_fallback=True)
        result = mapper.map_term("unknown_term", "Restaurant")
        
        assert result is not None
        assert result["fallback"] is True
        assert result["extraction_type"] == "generic"
        assert "suggestion" in result

    def test_map_term_performance_measurement(self):
        """Test term mapping performance meets requirements."""
        from src.knowledge.term_mapper import TermMapper
        import time
        
        mock_db = Mock()
        mock_db.get_term_mapping.return_value = {
            "customer_term": "test_term",
            "website_terms": [{"term": "test", "confidence": 1.0}],
            "category": "Test"
        }
        
        mapper = TermMapper(mock_db)
        
        # Test 50 consecutive lookups
        start_time = time.time()
        for i in range(50):
            mapper.map_term(f"test_term_{i}", "Restaurant")
        total_time = time.time() - start_time
        
        # Each lookup should complete in under 100ms
        avg_time = total_time / 50
        assert avg_time < 0.1

    def test_map_term_with_industry_specific_context(self):
        """Test mapping considers industry-specific context."""
        from src.knowledge.term_mapper import TermMapper
        
        mock_db = Mock()
        
        def mock_context_mapping(term, industry):
            if industry == "Restaurant":
                return {
                    "customer_term": term,
                    "website_terms": [{"term": "menu", "confidence": 0.9}],
                    "category": "Menu Items",
                    "context": "restaurant"
                }
            elif industry == "Medical":
                return {
                    "customer_term": term,
                    "website_terms": [{"term": "services", "confidence": 0.9}],
                    "category": "Services",
                    "context": "medical"
                }
            return None
        
        mock_db.get_term_mapping.side_effect = mock_context_mapping
        
        mapper = TermMapper(mock_db)
        
        restaurant_result = mapper.map_term("offerings", "Restaurant")
        medical_result = mapper.map_term("offerings", "Medical")
        
        assert restaurant_result["context"] == "restaurant"
        assert medical_result["context"] == "medical"
        assert restaurant_result["category"] != medical_result["category"]

    def test_clear_mapping_cache(self):
        """Test clearing the mapping cache."""
        from src.knowledge.term_mapper import TermMapper
        
        mock_db = Mock()
        mock_db.get_term_mapping.return_value = {
            "customer_term": "test",
            "website_terms": [{"term": "test", "confidence": 1.0}],
            "category": "Test"
        }
        
        mapper = TermMapper(mock_db, enable_cache=True)
        
        # Populate cache
        mapper.map_term("test", "Restaurant")
        assert len(mapper.cache) > 0
        
        # Clear cache
        mapper.clear_cache()
        assert len(mapper.cache) == 0

    def test_get_cache_statistics(self):
        """Test getting cache hit/miss statistics."""
        from src.knowledge.term_mapper import TermMapper
        
        mock_db = Mock()
        mock_db.get_term_mapping.return_value = {
            "customer_term": "test",
            "website_terms": [{"term": "test", "confidence": 1.0}],
            "category": "Test"
        }
        
        mapper = TermMapper(mock_db, enable_cache=True)
        
        # Generate cache hits and misses
        mapper.map_term("test1", "Restaurant")  # Miss
        mapper.map_term("test1", "Restaurant")  # Hit
        mapper.map_term("test2", "Restaurant")  # Miss
        
        stats = mapper.get_cache_stats()
        
        assert stats["hits"] == 1
        assert stats["misses"] == 2
        assert stats["hit_rate"] == 1/3

    def test_export_mapping_statistics(self):
        """Test exporting mapping usage statistics."""
        from src.knowledge.term_mapper import TermMapper
        
        mock_db = Mock()
        mock_db.get_term_mapping.return_value = {
            "customer_term": "test",
            "website_terms": [{"term": "test", "confidence": 1.0}],
            "category": "Test"
        }
        
        mapper = TermMapper(mock_db, track_usage=True)
        
        # Perform mappings
        mapper.map_term("test1", "Restaurant")
        mapper.map_term("test2", "Restaurant")
        mapper.map_term("test1", "Restaurant")  # Duplicate
        
        stats = mapper.export_usage_stats()
        
        assert "total_lookups" in stats
        assert "unique_terms" in stats
        assert "most_frequent_terms" in stats
        assert stats["total_lookups"] == 3
        assert stats["unique_terms"] == 2