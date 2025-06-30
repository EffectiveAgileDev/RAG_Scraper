"""Unit tests for fuzzy matching functionality."""
import pytest
from unittest.mock import Mock, patch


class TestFuzzyMatcher:
    """Test cases for the FuzzyMatcher class."""

    def test_fuzzy_matcher_initialization(self):
        """Test FuzzyMatcher initializes with correct parameters."""
        from src.knowledge.fuzzy_matcher import FuzzyMatcher
        
        matcher = FuzzyMatcher(similarity_threshold=0.8)
        
        assert matcher.similarity_threshold == 0.8
        assert hasattr(matcher, 'algorithm')
        assert hasattr(matcher, 'cache')

    def test_find_fuzzy_match_exact_match_returns_perfect_score(self):
        """Test fuzzy matching returns 1.0 for exact matches."""
        from src.knowledge.fuzzy_matcher import FuzzyMatcher
        
        matcher = FuzzyMatcher()
        
        result = matcher.find_match("vegetarian options", ["vegetarian options", "vegan", "plant-based"])
        
        assert result is not None
        assert result["matched_term"] == "vegetarian options"
        assert result["similarity_score"] == 1.0
        assert result["match_type"] == "exact"

    def test_find_fuzzy_match_close_spelling_high_score(self):
        """Test fuzzy matching finds close spelling with high similarity."""
        from src.knowledge.fuzzy_matcher import FuzzyMatcher
        
        matcher = FuzzyMatcher(similarity_threshold=0.7)
        
        result = matcher.find_match("vegitarian", ["vegetarian", "vegan", "plant-based"])
        
        assert result is not None
        assert result["matched_term"] == "vegetarian"
        assert result["similarity_score"] > 0.8
        assert result["match_type"] == "fuzzy"

    def test_find_fuzzy_match_no_match_below_threshold(self):
        """Test fuzzy matching returns None when below similarity threshold."""
        from src.knowledge.fuzzy_matcher import FuzzyMatcher
        
        matcher = FuzzyMatcher(similarity_threshold=0.8)
        
        result = matcher.find_match("quantum", ["vegetarian", "vegan", "plant-based"])
        
        assert result is None

    def test_find_fuzzy_match_returns_best_match(self):
        """Test fuzzy matching returns the best similarity match."""
        from src.knowledge.fuzzy_matcher import FuzzyMatcher
        
        matcher = FuzzyMatcher(similarity_threshold=0.5)
        
        result = matcher.find_match("parking", ["parking lot", "valet parking", "garage", "wifi"])
        
        assert result is not None
        assert result["matched_term"] in ["parking lot", "valet parking"]  # Both have "parking"
        assert result["similarity_score"] > 0.7

    def test_calculate_similarity_score_levenshtein(self):
        """Test similarity calculation using Levenshtein distance."""
        from src.knowledge.fuzzy_matcher import FuzzyMatcher
        
        matcher = FuzzyMatcher(algorithm="levenshtein")
        
        # Test different similarity levels
        score1 = matcher.calculate_similarity("test", "test")  # Exact match
        score2 = matcher.calculate_similarity("test", "tests")  # One character diff
        score3 = matcher.calculate_similarity("test", "completely_different")  # Very different
        
        assert score1 == 1.0
        assert 0.7 < score2 < 1.0
        assert score3 < 0.3

    def test_calculate_similarity_score_jaro_winkler(self):
        """Test similarity calculation using Jaro-Winkler algorithm."""
        from src.knowledge.fuzzy_matcher import FuzzyMatcher
        
        matcher = FuzzyMatcher(algorithm="jaro_winkler")
        
        score1 = matcher.calculate_similarity("vegetarian", "vegitarian")
        score2 = matcher.calculate_similarity("parking", "parking lot")
        
        assert 0.8 < score1 < 1.0
        assert 0.6 < score2 < 0.9

    def test_calculate_similarity_score_soundex(self):
        """Test similarity calculation using Soundex phonetic matching."""
        from src.knowledge.fuzzy_matcher import FuzzyMatcher
        
        matcher = FuzzyMatcher(algorithm="soundex")
        
        # Words that sound similar should have high scores
        score1 = matcher.calculate_similarity("night", "knight")
        score2 = matcher.calculate_similarity("there", "their")
        
        assert score1 > 0.8
        assert score2 > 0.8

    def test_find_multiple_matches_above_threshold(self):
        """Test finding multiple matches above similarity threshold."""
        from src.knowledge.fuzzy_matcher import FuzzyMatcher
        
        matcher = FuzzyMatcher(similarity_threshold=0.6)
        
        results = matcher.find_multiple_matches(
            "parking", 
            ["parking lot", "valet parking", "garage parking", "wifi", "menu"],
            max_results=3
        )
        
        assert len(results) <= 3
        assert all(r["similarity_score"] >= 0.6 for r in results)
        assert all("parking" in r["matched_term"].lower() for r in results)

    def test_fuzzy_match_caching_performance(self):
        """Test fuzzy matching uses caching for performance optimization."""
        from src.knowledge.fuzzy_matcher import FuzzyMatcher
        
        matcher = FuzzyMatcher(enable_cache=True)
        terms = ["vegetarian", "vegan", "plant-based"]
        
        with patch.object(matcher, 'calculate_similarity', wraps=matcher.calculate_similarity) as mock_calc:
            # First call should calculate similarities
            result1 = matcher.find_match("vegitarian", terms)
            first_call_count = mock_calc.call_count
            
            # Second identical call should use cache
            result2 = matcher.find_match("vegitarian", terms)
            second_call_count = mock_calc.call_count
            
            assert result1 == result2
            assert second_call_count == first_call_count  # No additional calculations

    def test_clear_fuzzy_match_cache(self):
        """Test clearing the fuzzy matching cache."""
        from src.knowledge.fuzzy_matcher import FuzzyMatcher
        
        matcher = FuzzyMatcher(enable_cache=True)
        
        # Populate cache
        matcher.find_match("test", ["testing", "tested"])
        assert len(matcher.cache) > 0
        
        # Clear cache
        matcher.clear_cache()
        assert len(matcher.cache) == 0

    def test_suggest_corrections_for_misspelled_terms(self):
        """Test suggesting spelling corrections for misspelled terms."""
        from src.knowledge.fuzzy_matcher import FuzzyMatcher
        
        matcher = FuzzyMatcher()
        
        suggestions = matcher.suggest_corrections(
            "vegitarian", 
            ["vegetarian", "vegan", "plant-based", "organic", "gluten-free"]
        )
        
        assert len(suggestions) > 0
        assert suggestions[0]["suggestion"] == "vegetarian"
        assert suggestions[0]["confidence"] > 0.8
        assert "Did you mean" in suggestions[0]["message"]

    def test_phonetic_matching_for_similar_sounding_words(self):
        """Test phonetic matching for words that sound similar."""
        from src.knowledge.fuzzy_matcher import FuzzyMatcher
        
        matcher = FuzzyMatcher(algorithm="metaphone")
        
        # Test phonetically similar words
        result1 = matcher.find_match("nite", ["night", "day", "morning"])
        result2 = matcher.find_match("there", ["their", "they", "them"])
        
        assert result1["matched_term"] == "night"
        assert result2["matched_term"] == "their"
        assert result1["similarity_score"] > 0.7
        assert result2["similarity_score"] > 0.7

    def test_fuzzy_match_performance_with_large_term_list(self):
        """Test fuzzy matching performance with large lists."""
        from src.knowledge.fuzzy_matcher import FuzzyMatcher
        import time
        
        matcher = FuzzyMatcher()
        large_term_list = [f"term_{i}" for i in range(1000)]
        
        start_time = time.time()
        result = matcher.find_match("term_500", large_term_list)
        execution_time = time.time() - start_time
        
        assert result is not None
        assert execution_time < 1.0  # Should complete in under 1 second

    def test_fuzzy_match_with_special_characters(self):
        """Test fuzzy matching handles special characters correctly."""
        from src.knowledge.fuzzy_matcher import FuzzyMatcher
        
        matcher = FuzzyMatcher()
        
        result = matcher.find_match(
            "gluten-free", 
            ["gluten free", "gluten_free", "glutenfree", "dairy-free"]
        )
        
        assert result is not None
        assert result["similarity_score"] > 0.8
        assert "gluten" in result["matched_term"].lower()

    def test_fuzzy_match_case_insensitive(self):
        """Test fuzzy matching is case insensitive."""
        from src.knowledge.fuzzy_matcher import FuzzyMatcher
        
        matcher = FuzzyMatcher()
        
        result1 = matcher.find_match("VEGETARIAN", ["vegetarian", "vegan"])
        result2 = matcher.find_match("vegetarian", ["VEGETARIAN", "VEGAN"])
        
        assert result1["matched_term"] == "vegetarian"
        assert result2["matched_term"] == "VEGETARIAN"
        assert result1["similarity_score"] == 1.0
        assert result2["similarity_score"] == 1.0

    def test_fuzzy_match_with_word_boundaries(self):
        """Test fuzzy matching considers word boundaries."""
        from src.knowledge.fuzzy_matcher import FuzzyMatcher
        
        matcher = FuzzyMatcher(respect_word_boundaries=True)
        
        result = matcher.find_match(
            "free parking", 
            ["parking", "free wifi", "valet parking", "parking lot"]
        )
        
        # Should prefer terms that contain both words
        assert result is not None
        assert "parking" in result["matched_term"]
        assert result["similarity_score"] > 0.7

    def test_adjust_similarity_for_fuzzy_matches(self):
        """Test similarity score adjustment for fuzzy vs exact matches."""
        from src.knowledge.fuzzy_matcher import FuzzyMatcher
        
        matcher = FuzzyMatcher()
        
        exact_result = matcher.find_match("test", ["test", "testing"])
        fuzzy_result = matcher.find_match("tst", ["test", "testing"])
        
        assert exact_result["similarity_score"] == 1.0
        assert fuzzy_result["similarity_score"] < 1.0
        assert fuzzy_result["confidence_adjusted"] < exact_result["similarity_score"]

    def test_fuzzy_match_statistics_tracking(self):
        """Test tracking fuzzy match usage statistics."""
        from src.knowledge.fuzzy_matcher import FuzzyMatcher
        
        matcher = FuzzyMatcher(track_stats=True)
        
        # Perform various types of matches
        matcher.find_match("exact", ["exact", "other"])  # Exact match
        matcher.find_match("fuzzy", ["fuzzy_term", "other"])  # Fuzzy match
        matcher.find_match("nomatch", ["different", "terms"])  # No match
        
        stats = matcher.get_statistics()
        
        assert stats["total_searches"] == 3
        assert stats["exact_matches"] == 1
        assert stats["fuzzy_matches"] == 1
        assert stats["no_matches"] == 1
        assert stats["fuzzy_match_rate"] == 1/3

    def test_configure_similarity_algorithm_parameters(self):
        """Test configuring parameters for different similarity algorithms."""
        from src.knowledge.fuzzy_matcher import FuzzyMatcher
        
        # Test configuring algorithm-specific parameters
        matcher = FuzzyMatcher(
            algorithm="jaro_winkler",
            algorithm_params={
                "prefix_scale": 0.1,
                "boost_threshold": 0.7
            }
        )
        
        assert matcher.algorithm == "jaro_winkler"
        assert matcher.algorithm_params["prefix_scale"] == 0.1
        assert matcher.algorithm_params["boost_threshold"] == 0.7

    def test_batch_fuzzy_matching(self):
        """Test batch processing of multiple fuzzy match queries."""
        from src.knowledge.fuzzy_matcher import FuzzyMatcher
        
        matcher = FuzzyMatcher()
        
        queries = ["vegitarian", "parkin", "glutn-free"]
        term_list = ["vegetarian", "parking", "gluten-free", "vegan", "wifi"]
        
        results = matcher.find_matches_batch(queries, term_list)
        
        assert len(results) == 3
        assert all(r is not None for r in results.values())
        assert results["vegitarian"]["matched_term"] == "vegetarian"
        assert results["parkin"]["matched_term"] == "parking"
        assert results["glutn-free"]["matched_term"] == "gluten-free"