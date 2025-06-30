"""Unit tests for synonym expansion functionality."""
import pytest
from unittest.mock import Mock, patch


class TestSynonymExpander:
    """Test cases for the SynonymExpander class."""

    def test_synonym_expander_initialization(self):
        """Test SynonymExpander initializes correctly."""
        from src.knowledge.synonym_expander import SynonymExpander
        
        mock_db = Mock()
        expander = SynonymExpander(mock_db)
        
        assert expander.database == mock_db
        assert hasattr(expander, 'synonym_cache')
        assert hasattr(expander, 'bidirectional_mapping')

    def test_expand_term_with_synonyms(self):
        """Test expanding a term to include its synonyms."""
        from src.knowledge.synonym_expander import SynonymExpander
        
        mock_db = Mock()
        mock_db.get_synonyms.return_value = {
            "primary_term": "parking",
            "synonyms": ["parking lot", "valet", "garage"],
            "confidence": 0.9
        }
        
        expander = SynonymExpander(mock_db)
        result = expander.expand_term("parking", "Restaurant")
        
        assert result is not None
        assert result["primary_term"] == "parking"
        assert "parking lot" in result["synonyms"]
        assert "valet" in result["synonyms"]
        assert "garage" in result["synonyms"]
        assert result["confidence"] == 0.9

    def test_expand_term_no_synonyms_returns_original(self):
        """Test expanding term with no synonyms returns original term."""
        from src.knowledge.synonym_expander import SynonymExpander
        
        mock_db = Mock()
        mock_db.get_synonyms.return_value = None
        
        expander = SynonymExpander(mock_db)
        result = expander.expand_term("unique_term", "Restaurant")
        
        assert result is not None
        assert result["primary_term"] == "unique_term"
        assert result["synonyms"] == ["unique_term"]
        assert result["expansion_type"] == "none"

    def test_expand_multiple_terms_batch(self):
        """Test expanding multiple terms in batch."""
        from src.knowledge.synonym_expander import SynonymExpander
        
        mock_db = Mock()
        mock_db.get_synonyms_batch.return_value = {
            "parking": {
                "primary_term": "parking",
                "synonyms": ["parking lot", "valet", "garage"],
                "confidence": 0.9
            },
            "wifi": {
                "primary_term": "wifi",
                "synonyms": ["wi-fi", "internet", "wireless"],
                "confidence": 0.85
            }
        }
        
        expander = SynonymExpander(mock_db)
        terms = ["parking", "wifi"]
        results = expander.expand_terms_batch(terms, "Restaurant")
        
        assert len(results) == 2
        assert "parking" in results
        assert "wifi" in results
        assert len(results["parking"]["synonyms"]) == 3
        assert len(results["wifi"]["synonyms"]) == 3

    def test_bidirectional_synonym_mapping(self):
        """Test bidirectional synonym relationships work correctly."""
        from src.knowledge.synonym_expander import SynonymExpander
        
        mock_db = Mock()
        
        def mock_get_synonyms(term, industry):
            synonym_map = {
                "parking": ["parking lot", "valet", "garage"],
                "parking lot": ["parking", "valet", "garage"],
                "valet": ["parking", "parking lot", "garage"],
                "garage": ["parking", "parking lot", "valet"]
            }
            if term in synonym_map:
                return {
                    "primary_term": term,
                    "synonyms": synonym_map[term],
                    "confidence": 0.9
                }
            return None
        
        mock_db.get_synonyms.side_effect = mock_get_synonyms
        
        expander = SynonymExpander(mock_db)
        
        # Test forward mapping
        result1 = expander.expand_term("parking", "Restaurant")
        # Test reverse mapping  
        result2 = expander.expand_term("valet", "Restaurant")
        
        assert "valet" in result1["synonyms"]
        assert "parking" in result2["synonyms"]

    def test_synonym_expansion_with_confidence_filtering(self):
        """Test synonym expansion filters by confidence threshold."""
        from src.knowledge.synonym_expander import SynonymExpander
        
        mock_db = Mock()
        mock_db.get_synonyms.return_value = {
            "primary_term": "parking",
            "synonyms": [
                {"term": "parking lot", "confidence": 0.9},
                {"term": "valet", "confidence": 0.7},
                {"term": "garage", "confidence": 0.4}  # Below threshold
            ],
            "overall_confidence": 0.8
        }
        
        expander = SynonymExpander(mock_db, confidence_threshold=0.5)
        result = expander.expand_term("parking", "Restaurant")
        
        # Should filter out low confidence synonyms
        high_confidence_synonyms = [s for s in result["synonyms"] 
                                  if isinstance(s, dict) and s["confidence"] >= 0.5]
        assert len(high_confidence_synonyms) == 2

    def test_synonym_caching_for_performance(self):
        """Test synonym expansion uses caching for performance."""
        from src.knowledge.synonym_expander import SynonymExpander
        
        mock_db = Mock()
        mock_db.get_synonyms.return_value = {
            "primary_term": "parking",
            "synonyms": ["parking lot", "valet", "garage"],
            "confidence": 0.9
        }
        
        expander = SynonymExpander(mock_db, enable_cache=True)
        
        # First call should hit database
        result1 = expander.expand_term("parking", "Restaurant")
        assert mock_db.get_synonyms.call_count == 1
        
        # Second call should use cache
        result2 = expander.expand_term("parking", "Restaurant")
        assert mock_db.get_synonyms.call_count == 1  # No additional calls
        
        assert result1 == result2

    def test_clear_synonym_cache(self):
        """Test clearing the synonym cache."""
        from src.knowledge.synonym_expander import SynonymExpander
        
        mock_db = Mock()
        expander = SynonymExpander(mock_db, enable_cache=True)
        
        # Populate cache
        mock_db.get_synonyms.return_value = {"synonyms": ["test"]}
        expander.expand_term("test", "Restaurant")
        assert len(expander.synonym_cache) > 0
        
        # Clear cache
        expander.clear_cache()
        assert len(expander.synonym_cache) == 0

    def test_get_synonym_mapping_statistics(self):
        """Test getting synonym mapping statistics."""
        from src.knowledge.synonym_expander import SynonymExpander
        
        mock_db = Mock()
        mock_db.get_synonyms.return_value = {
            "primary_term": "test",
            "synonyms": ["test1", "test2"],
            "confidence": 0.8
        }
        
        expander = SynonymExpander(mock_db, track_usage=True)
        
        # Perform expansions
        expander.expand_term("test1", "Restaurant")
        expander.expand_term("test2", "Restaurant")
        expander.expand_term("test1", "Restaurant")  # Duplicate
        
        stats = expander.get_usage_stats()
        
        assert stats["total_expansions"] == 3
        assert stats["unique_terms"] == 2
        assert stats["cache_hit_rate"] >= 0.0

    def test_synonym_expansion_industry_isolation(self):
        """Test synonym expansion isolates industries correctly."""
        from src.knowledge.synonym_expander import SynonymExpander
        
        mock_db = Mock()
        
        def mock_industry_synonyms(term, industry):
            if industry == "Restaurant" and term == "menu":
                return {
                    "primary_term": "menu",
                    "synonyms": ["food items", "dishes", "offerings"],
                    "confidence": 0.9
                }
            elif industry == "Medical" and term == "menu":
                return None  # No synonyms in medical context
            return None
        
        mock_db.get_synonyms.side_effect = mock_industry_synonyms
        
        expander = SynonymExpander(mock_db)
        
        restaurant_result = expander.expand_term("menu", "Restaurant")
        medical_result = expander.expand_term("menu", "Medical")
        
        assert restaurant_result["synonyms"] == ["food items", "dishes", "offerings"]
        assert medical_result["synonyms"] == ["menu"]  # Original term only

    def test_add_custom_synonym_mapping(self):
        """Test adding custom synonym mappings."""
        from src.knowledge.synonym_expander import SynonymExpander
        
        mock_db = Mock()
        mock_db.add_custom_synonym.return_value = {"success": True, "mapping_id": "custom_123"}
        
        expander = SynonymExpander(mock_db)
        
        result = expander.add_custom_synonym(
            primary_term="dairy-free",
            synonyms=["lactose-free", "no-dairy", "milk-free"],
            industry="Restaurant",
            confidence=0.95
        )
        
        assert result["success"] is True
        assert result["mapping_id"] == "custom_123"
        mock_db.add_custom_synonym.assert_called_once()

    def test_remove_synonym_mapping(self):
        """Test removing synonym mappings."""
        from src.knowledge.synonym_expander import SynonymExpander
        
        mock_db = Mock()
        mock_db.remove_synonym.return_value = {"success": True, "removed_count": 1}
        
        expander = SynonymExpander(mock_db)
        
        result = expander.remove_synonym_mapping("outdated_term", "Restaurant")
        
        assert result["success"] is True
        assert result["removed_count"] == 1
        mock_db.remove_synonym.assert_called_once_with("outdated_term", "Restaurant")

    def test_synonym_expansion_with_context_awareness(self):
        """Test synonym expansion considers context for better accuracy."""
        from src.knowledge.synonym_expander import SynonymExpander
        
        mock_db = Mock()
        
        def mock_context_synonyms(term, industry, context=None):
            if term == "reservation" and industry == "Restaurant":
                if context == "booking":
                    return {
                        "synonyms": ["booking", "table booking", "dinner reservation"],
                        "confidence": 0.95
                    }
                else:
                    return {
                        "synonyms": ["booking", "appointment", "table"],
                        "confidence": 0.8
                    }
            return None
        
        mock_db.get_synonyms.side_effect = mock_context_synonyms
        
        expander = SynonymExpander(mock_db)
        
        # Test with specific context
        result_with_context = expander.expand_term(
            "reservation", "Restaurant", context="booking"
        )
        
        # Test without context
        result_without_context = expander.expand_term("reservation", "Restaurant")
        
        assert result_with_context["confidence"] > result_without_context["confidence"]
        assert "dinner reservation" in result_with_context["synonyms"]

    def test_synonym_expansion_performance_optimization(self):
        """Test synonym expansion performance with large datasets."""
        from src.knowledge.synonym_expander import SynonymExpander
        import time
        
        mock_db = Mock()
        mock_db.get_synonyms.return_value = {
            "primary_term": "test",
            "synonyms": [f"synonym_{i}" for i in range(100)],
            "confidence": 0.8
        }
        
        expander = SynonymExpander(mock_db, enable_cache=True)
        
        # Test expansion performance
        start_time = time.time()
        for i in range(50):
            expander.expand_term(f"test_term_{i}", "Restaurant")
        execution_time = time.time() - start_time
        
        # Should complete 50 expansions in reasonable time
        assert execution_time < 2.0  # Under 2 seconds
        avg_time = execution_time / 50
        assert avg_time < 0.04  # Under 40ms per expansion

    def test_export_synonym_mappings_for_analysis(self):
        """Test exporting synonym mappings for analysis."""
        from src.knowledge.synonym_expander import SynonymExpander
        
        mock_db = Mock()
        mock_db.export_synonyms.return_value = {
            "Restaurant": {
                "parking": ["parking lot", "valet", "garage"],
                "wifi": ["wi-fi", "internet", "wireless"]
            },
            "Medical": {
                "appointment": ["visit", "consultation", "meeting"]
            }
        }
        
        expander = SynonymExpander(mock_db)
        
        export_data = expander.export_all_synonyms()
        
        assert "Restaurant" in export_data
        assert "Medical" in export_data
        assert len(export_data["Restaurant"]["parking"]) == 3
        assert "consultation" in export_data["Medical"]["appointment"]

    def test_import_synonym_mappings_from_file(self):
        """Test importing synonym mappings from external file."""
        from src.knowledge.synonym_expander import SynonymExpander
        
        import_data = {
            "Restaurant": {
                "custom_term": {
                    "synonyms": ["synonym1", "synonym2"],
                    "confidence": 0.9,
                    "source": "imported"
                }
            }
        }
        
        mock_db = Mock()
        mock_db.import_synonyms.return_value = {
            "success": True,
            "imported_count": 1,
            "errors": []
        }
        
        expander = SynonymExpander(mock_db)
        
        result = expander.import_synonyms(import_data)
        
        assert result["success"] is True
        assert result["imported_count"] == 1
        assert len(result["errors"]) == 0

    def test_validate_synonym_mapping_integrity(self):
        """Test validating synonym mapping data integrity."""
        from src.knowledge.synonym_expander import SynonymExpander
        
        valid_mapping = {
            "primary_term": "parking",
            "synonyms": ["parking lot", "valet", "garage"],
            "confidence": 0.9,
            "bidirectional": True
        }
        
        invalid_mapping = {
            "primary_term": "",  # Invalid: empty
            "synonyms": [],  # Invalid: empty list
            "confidence": 1.5,  # Invalid: > 1.0
        }
        
        expander = SynonymExpander(Mock())
        
        valid_result = expander.validate_mapping(valid_mapping)
        invalid_result = expander.validate_mapping(invalid_mapping)
        
        assert valid_result["valid"] is True
        assert len(valid_result["errors"]) == 0
        
        assert invalid_result["valid"] is False
        assert len(invalid_result["errors"]) > 0