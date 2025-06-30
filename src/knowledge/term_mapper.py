"""Term mapping functionality for translating customer terms to website terms."""
import logging
import time
from typing import Dict, List, Optional, Any, Union
from collections import defaultdict

from .database_query_optimizer import get_query_optimizer

logger = logging.getLogger(__name__)


class TermMapper:
    """Maps customer search terms to website-specific terms using industry knowledge."""
    
    def __init__(self, database, confidence_threshold: float = 0.5, 
                 enable_cache: bool = True, enable_fallback: bool = False,
                 track_usage: bool = False):
        """Initialize term mapper.
        
        Args:
            database: Industry database instance
            confidence_threshold: Minimum confidence for results
            enable_cache: Whether to enable result caching
            enable_fallback: Whether to suggest fallback extraction
            track_usage: Whether to track usage statistics
        """
        self.database = database
        self.confidence_threshold = confidence_threshold
        self.enable_cache = enable_cache
        self.enable_fallback = enable_fallback
        self.track_usage = track_usage
        
        # Initialize optimized caching and stats
        self._query_optimizer = get_query_optimizer()
        self.enable_cache = enable_cache
        # Maintain backward compatibility with old cache interface
        self.cache = {} if enable_cache else None
        self.cache_stats = {"hits": 0, "misses": 0}
        self.usage_stats = defaultdict(int) if track_usage else None
    
    @property
    def _map_term_cached(self):
        """Cached version of map_term method."""
        if self.enable_cache:
            return self._query_optimizer.cached_query()(self._map_term_impl)
        else:
            return self._map_term_impl
    
    def _map_term_impl(self, customer_term: str, industry: str) -> Optional[Dict[str, Any]]:
        """Implementation of map_term without caching."""
        # Get mapping from database
        result = self.database.get_term_mapping(customer_term, industry)
        
        if result is None:
            return None
        
        # Apply confidence filtering to website terms
        if "website_terms" in result:
            filtered_terms = []
            for term in result["website_terms"]:
                if isinstance(term, dict) and "confidence" in term:
                    if term["confidence"] >= self.confidence_threshold:
                        filtered_terms.append(term)
                else:
                    # Simple string terms - assume they pass threshold
                    filtered_terms.append(term)
            result["website_terms"] = filtered_terms
        
        # Add match type
        result["match_type"] = "exact"
        
        return result
    
    def map_term(self, customer_term: str, industry: str) -> Optional[Dict[str, Any]]:
        """Map a customer term to website terms with optimized caching.
        
        Args:
            customer_term: Customer search term
            industry: Target industry
            
        Returns:
            Mapping result or None if no match found
        """
        # Track usage for all requests
        if self.track_usage:
            self.usage_stats["total_lookups"] += 1
            self.usage_stats[customer_term] += 1
        
        # Get result through optimized cache
        result = self._map_term_cached(customer_term, industry)
        
        # Update backward-compatible cache and stats
        if self.enable_cache:
            cache_key = f"{customer_term}:{industry}"
            self.cache[cache_key] = result
            cache_stats = self._query_optimizer.get_cache_stats()
            self.cache_stats["hits"] = cache_stats["hit_count"]
            self.cache_stats["misses"] = cache_stats["miss_count"]
        
        if result is None:
            # Log unknown term
            logger.info(f"Unknown term logged: {customer_term} (Industry: {industry})")
            
            # Handle fallback if enabled
            if self.enable_fallback:
                result = {
                    "fallback": True,
                    "extraction_type": "generic",
                    "suggestion": f"Consider using generic extraction for '{customer_term}'"
                }
        
        return result
    
    def map_terms_batch(self, terms: List[str], industry: str) -> Dict[str, Any]:
        """Map multiple terms in batch for efficiency.
        
        Args:
            terms: List of customer terms
            industry: Target industry
            
        Returns:
            Dictionary mapping terms to their results
        """
        results = {}
        
        # Use database batch method if available
        if hasattr(self.database, 'get_term_mappings_batch'):
            batch_results = self.database.get_term_mappings_batch(terms, industry)
            for term, result in batch_results.items():
                results[term] = result
        else:
            # Fall back to individual mapping
            for term in terms:
                results[term] = self.map_term(term, industry)
        
        return results
    
    def calculate_confidence(self, factors: Dict[str, Any]) -> float:
        """Calculate confidence score based on multiple factors.
        
        Args:
            factors: Dictionary of confidence factors
            
        Returns:
            Combined confidence score between 0.0 and 1.0
        """
        base_confidence = 0.5
        
        # Exact match bonus
        if factors.get("exact_match", False):
            base_confidence = 0.9  # Start high for exact match
            max_confidence = 1.0
        elif "fuzzy_similarity" in factors:
            base_confidence = factors["fuzzy_similarity"] * 0.8  # Cap fuzzy matches lower
            max_confidence = 0.85  # Ensure fuzzy matches can't exceed this
        else:
            max_confidence = 1.0
        
        # Apply multiplicative bonuses instead of penalties
        multiplier = 1.0
        
        # Source reliability bonus
        if "source_reliability" in factors:
            multiplier += (factors["source_reliability"] - 0.5) * 0.3
        
        # Term frequency bonus
        if "term_frequency" in factors:
            multiplier += (factors["term_frequency"] - 0.5) * 0.2
        
        # Context relevance bonus
        if "context_relevance" in factors:
            multiplier += (factors["context_relevance"] - 0.5) * 0.2
        
        final_confidence = base_confidence * multiplier
        
        # Ensure bounds
        return max(0.0, min(max_confidence, final_confidence))
    
    def clear_cache(self):
        """Clear the mapping cache."""
        if self.enable_cache:
            self.cache.clear()
            self._query_optimizer.clear_cache()
            self.cache_stats = {"hits": 0, "misses": 0}
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        if not self.enable_cache:
            return {"cache_enabled": False}
        
        total = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = self.cache_stats["hits"] / total if total > 0 else 0.0
        
        return {
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "hit_rate": hit_rate,
            "cache_size": len(self.cache)
        }
    
    def export_usage_stats(self) -> Dict[str, Any]:
        """Export usage statistics.
        
        Returns:
            Dictionary with usage statistics
        """
        if not self.track_usage:
            return {"tracking_enabled": False}
        
        # Count unique terms (exclude total_lookups)
        unique_terms = len([k for k in self.usage_stats.keys() if k != "total_lookups"])
        
        # Find most frequent terms
        term_counts = {k: v for k, v in self.usage_stats.items() if k != "total_lookups"}
        most_frequent = sorted(term_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_lookups": self.usage_stats["total_lookups"],
            "unique_terms": unique_terms,
            "most_frequent_terms": most_frequent
        }


# Mock database methods that tests expect
class MockDatabaseMethods:
    """Mock methods that the database should implement for term mapping."""
    
    def get_term_mapping(self, term: str, industry: str) -> Optional[Dict[str, Any]]:
        """Get term mapping from database."""
        # This would be implemented in the actual database
        return None
    
    def get_term_mappings_batch(self, terms: List[str], industry: str) -> Dict[str, Any]:
        """Get multiple term mappings in batch."""
        # This would be implemented in the actual database
        return {}