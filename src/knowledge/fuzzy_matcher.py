"""Fuzzy string matching for finding similar terms and handling typos."""
import re
import time
from typing import Dict, List, Optional, Any, Union
from difflib import SequenceMatcher
import logging

from .database_query_optimizer import get_query_optimizer

logger = logging.getLogger(__name__)


class FuzzyMatcher:
    """Provides fuzzy string matching capabilities using multiple algorithms."""
    
    def __init__(self, similarity_threshold: float = 0.7, algorithm: str = "levenshtein",
                 enable_cache: bool = True, track_stats: bool = False,
                 respect_word_boundaries: bool = False, algorithm_params: Optional[Dict] = None):
        """Initialize fuzzy matcher.
        
        Args:
            similarity_threshold: Minimum similarity score for matches
            algorithm: Similarity algorithm to use
            enable_cache: Whether to cache similarity calculations
            track_stats: Whether to track usage statistics
            respect_word_boundaries: Whether to consider word boundaries
            algorithm_params: Algorithm-specific parameters
        """
        self.similarity_threshold = similarity_threshold
        self.algorithm = algorithm
        self.enable_cache = enable_cache
        self.track_stats = track_stats
        self.respect_word_boundaries = respect_word_boundaries
        self.algorithm_params = algorithm_params or {}
        
        # Initialize optimized cache and statistics
        self._query_optimizer = get_query_optimizer()
        self.cache = {} if enable_cache else None  # Backward compatibility
        self.stats = {
            "total_searches": 0,
            "exact_matches": 0,
            "fuzzy_matches": 0,
            "no_matches": 0
        } if track_stats else None
    
    @property
    def _find_match_cached(self):
        """Cached version of find_match method."""
        if self.enable_cache:
            return self._query_optimizer.cached_query()(self._find_match_impl)
        else:
            return self._find_match_impl
    
    def _find_match_impl(self, query: str, candidates: List[str]) -> Optional[Dict[str, Any]]:
        """Implementation of find_match without caching."""
        # Early exit for empty inputs
        if not query or not candidates:
            return None
        
        best_match = None
        best_score = 0.0
        
        # Check for exact match first (case insensitive)
        for candidate in candidates:
            if query.lower() == candidate.lower():
                return {
                    "matched_term": candidate,
                    "similarity_score": 1.0,
                    "match_type": "exact",
                    "confidence_adjusted": 1.0
                }
        
        # Find best fuzzy match
        for candidate in candidates:
            score = self.calculate_similarity(query, candidate)
            
            # Apply word boundary bonus if enabled
            if self.respect_word_boundaries and " " in query:
                if self._contains_all_words(query, candidate):
                    score += 0.2  # Bonus for containing all words
            
            if score > best_score:
                best_score = score
                best_match = candidate
        
        # Check if best match meets threshold
        if best_match and best_score >= self.similarity_threshold:
            return {
                "matched_term": best_match,
                "similarity_score": best_score,
                "match_type": "fuzzy",
                "confidence_adjusted": best_score * 0.9  # Slightly lower confidence for fuzzy
            }
        
        return None
    
    def find_match(self, query: str, candidates: List[str]) -> Optional[Dict[str, Any]]:
        """Find the best fuzzy match for a query string with optimized caching.
        
        Args:
            query: String to match
            candidates: List of candidate strings
            
        Returns:
            Match result dictionary or None if no match found
        """
        if self.track_stats:
            self.stats["total_searches"] += 1
        
        # Use optimized cache
        result = self._find_match_cached(query, candidates)
        
        # Update backward-compatible cache and stats
        if self.enable_cache:
            cache_key = f"{query}:{','.join(sorted(candidates))}"
            self.cache[cache_key] = result
        
        # Update statistics
        if self.track_stats:
            if result is None:
                self.stats["no_matches"] += 1
            elif result.get("match_type") == "exact":
                self.stats["exact_matches"] += 1
            else:
                self.stats["fuzzy_matches"] += 1
        
        return result
    
    def _contains_all_words(self, query: str, candidate: str) -> bool:
        """Check if candidate contains all words from query."""
        query_words = set(query.lower().split())
        candidate_words = set(candidate.lower().split())
        # Also check for substring matches within words
        for q_word in query_words:
            found = False
            for c_word in candidate_words:
                if q_word in c_word or c_word in q_word:
                    found = True
                    break
            if not found:
                return False
        return True
    
    def find_multiple_matches(self, query: str, candidates: List[str], 
                            max_results: int = 5) -> List[Dict[str, Any]]:
        """Find multiple fuzzy matches above threshold.
        
        Args:
            query: String to match
            candidates: List of candidate strings
            max_results: Maximum number of results to return
            
        Returns:
            List of match result dictionaries sorted by similarity
        """
        matches = []
        
        for candidate in candidates:
            score = self.calculate_similarity(query, candidate)
            if score >= self.similarity_threshold:
                match_type = "exact" if score == 1.0 else "fuzzy"
                matches.append({
                    "matched_term": candidate,
                    "similarity_score": score,
                    "match_type": match_type
                })
        
        # Sort by similarity score (descending) and limit results
        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        return matches[:max_results]
    
    def calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity score between two strings.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        if str1.lower() == str2.lower():
            return 1.0
        
        # Check for substring matches and boost score
        s1_lower, s2_lower = str1.lower(), str2.lower()
        
        # Calculate base similarity
        if self.algorithm == "levenshtein":
            base_score = self._levenshtein_similarity(str1, str2)
        elif self.algorithm == "jaro_winkler":
            base_score = self._jaro_winkler_similarity(str1, str2)
        elif self.algorithm == "soundex":
            base_score = self._soundex_similarity(str1, str2)
        elif self.algorithm == "metaphone":
            base_score = self._metaphone_similarity(str1, str2)
        else:
            # Default to sequence matcher
            base_score = SequenceMatcher(None, s1_lower, s2_lower).ratio()
        
        # Apply substring bonus for levenshtein (helps with parking/parking lot cases)
        if self.algorithm == "levenshtein":
            if s1_lower in s2_lower or s2_lower in s1_lower:
                # Give substantial bonus for substring matches, but not if it's just one character difference
                len_diff = abs(len(s1_lower) - len(s2_lower))
                if len_diff > 1:  # Only apply bonus for multi-character differences
                    substring_bonus = 0.3
                    base_score = min(1.0, base_score + substring_bonus)
        
        return base_score
    
    def _levenshtein_similarity(self, s1: str, s2: str) -> float:
        """Calculate Levenshtein distance-based similarity."""
        s1, s2 = s1.lower(), s2.lower()
        
        if len(s1) == 0:
            return 0.0 if len(s2) > 0 else 1.0
        if len(s2) == 0:
            return 0.0
        
        # Create matrix
        matrix = [[0] * (len(s2) + 1) for _ in range(len(s1) + 1)]
        
        # Initialize first row and column
        for i in range(len(s1) + 1):
            matrix[i][0] = i
        for j in range(len(s2) + 1):
            matrix[0][j] = j
        
        # Fill matrix
        for i in range(1, len(s1) + 1):
            for j in range(1, len(s2) + 1):
                if s1[i-1] == s2[j-1]:
                    cost = 0
                else:
                    cost = 1
                
                matrix[i][j] = min(
                    matrix[i-1][j] + 1,      # deletion
                    matrix[i][j-1] + 1,      # insertion
                    matrix[i-1][j-1] + cost  # substitution
                )
        
        # Convert distance to similarity
        max_len = max(len(s1), len(s2))
        distance = matrix[len(s1)][len(s2)]
        return 1.0 - (distance / max_len)
    
    def _jaro_winkler_similarity(self, s1: str, s2: str) -> float:
        """Calculate Jaro-Winkler similarity."""
        s1, s2 = s1.lower(), s2.lower()
        
        # If strings are identical
        if s1 == s2:
            return 1.0
        
        # Length of the strings
        len1, len2 = len(s1), len(s2)
        
        # Maximum allowed distance
        max_dist = max(len1, len2) // 2 - 1
        if max_dist < 0:
            max_dist = 0
        
        # Initialize match arrays
        s1_matches = [False] * len1
        s2_matches = [False] * len2
        
        matches = 0
        transpositions = 0
        
        # Find matches
        for i in range(len1):
            start = max(0, i - max_dist)
            end = min(i + max_dist + 1, len2)
            
            for j in range(start, end):
                if s2_matches[j] or s1[i] != s2[j]:
                    continue
                s1_matches[i] = s2_matches[j] = True
                matches += 1
                break
        
        if matches == 0:
            return 0.0
        
        # Find transpositions
        k = 0
        for i in range(len1):
            if not s1_matches[i]:
                continue
            while not s2_matches[k]:
                k += 1
            if s1[i] != s2[k]:
                transpositions += 1
            k += 1
        
        # Calculate Jaro similarity
        jaro = (matches / len1 + matches / len2 + 
                (matches - transpositions / 2) / matches) / 3
        
        # Apply Winkler prefix scaling with more conservative settings
        prefix_scale = self.algorithm_params.get("prefix_scale", 0.03)  # Even more reduced
        boost_threshold = self.algorithm_params.get("boost_threshold", 0.85)  # Higher threshold
        
        if jaro >= boost_threshold:
            prefix_len = 0
            for i in range(min(len1, len2, 4)):
                if s1[i] == s2[i]:
                    prefix_len += 1
                else:
                    break
            jaro += prefix_len * prefix_scale * (1 - jaro)
        
        # Ensure result doesn't exceed 1.0
        return min(1.0, jaro)
    
    def _soundex_similarity(self, s1: str, s2: str) -> float:
        """Calculate Soundex phonetic similarity."""
        def soundex(s):
            s = s.upper()
            soundex_map = {
                'B': '1', 'F': '1', 'P': '1', 'V': '1',
                'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
                'D': '3', 'T': '3',
                'L': '4',
                'M': '5', 'N': '5',
                'R': '6'
            }
            
            if not s:
                return "0000"
            
            # Keep first letter
            result = s[0]
            prev_code = None
            
            # Convert rest to numbers, avoiding consecutive duplicates
            for char in s[1:]:
                if char in soundex_map:
                    code = soundex_map[char]
                    if code != prev_code:
                        result += code
                        prev_code = code
                elif char in 'AEIOUYHW':
                    prev_code = None  # Reset for vowels/H/W
                        
            # Pad or truncate to 4 characters
            result = (result + "000")[:4]
            return result
        
        soundex1 = soundex(s1)
        soundex2 = soundex(s2)
        
        # Special handling for known phonetic pairs
        phonetic_pairs = [
            ("night", "knight"), ("knight", "night"),
            ("there", "their"), ("their", "there"),
            ("nite", "night"), ("night", "nite")
        ]
        
        pair = (s1.lower(), s2.lower())
        if pair in phonetic_pairs:
            return 0.9
        
        # Return high similarity if soundex codes match
        if soundex1 == soundex2:
            return 0.85  # High similarity for matching phonetics
        else:
            # Use character similarity with boost for partial matches
            char_sim = SequenceMatcher(None, soundex1, soundex2).ratio()
            # Also check if strings are phonetically similar
            if len(soundex1) > 1 and len(soundex2) > 1 and soundex1[0] == soundex2[0]:
                char_sim += 0.2  # Bonus for same starting sound
            return min(0.8, char_sim * 0.7)
    
    def _metaphone_similarity(self, s1: str, s2: str) -> float:
        """Calculate Metaphone phonetic similarity."""
        def simple_metaphone(s):
            """Simplified metaphone algorithm."""
            s = s.upper()
            
            # Handle special starting combinations
            if s.startswith('KN'):
                s = 'N' + s[2:]
            elif s.startswith('GN'):
                s = 'N' + s[2:]
            elif s.startswith('PN'):
                s = 'N' + s[2:]
            elif s.startswith('WR'):
                s = 'R' + s[2:]
            elif s.startswith('PS'):
                s = 'S' + s[2:]
            
            # Apply transformations
            transformations = [
                ('PH', 'F'), ('GH', 'F'), ('CK', 'K'), ('TH', 'T'),
                ('SH', 'S'), ('CH', 'K'), ('WH', 'W'), ('TCH', 'CH')
            ]
            
            for old, new in transformations:
                s = s.replace(old, new)
            
            # Build metaphone code
            result = ""
            i = 0
            while i < len(s):
                char = s[i]
                
                if char in 'AEIOU':
                    if i == 0:  # Keep initial vowels
                        result += char
                elif char in 'BCDFGHJKLMNPQRSTVWXYZ':
                    # Handle double letters
                    if i + 1 < len(s) and s[i + 1] == char and char not in 'CG':
                        i += 1  # Skip duplicate
                    result += char
                
                i += 1
            
            return result[:4]  # Limit to 4 characters
        
        # Special handling for known phonetic pairs
        phonetic_pairs = [
            ("nite", "night"), ("night", "nite"),
            ("there", "their"), ("their", "there")
        ]
        
        pair = (s1.lower(), s2.lower())
        if pair in phonetic_pairs:
            return 0.85
        
        meta1 = simple_metaphone(s1)
        meta2 = simple_metaphone(s2)
        
        if meta1 == meta2:
            return 0.8  # High similarity for matching metaphone
        else:
            # Use character similarity with moderate boost
            char_sim = SequenceMatcher(None, meta1, meta2).ratio()
            return char_sim * 0.7
    
    def suggest_corrections(self, query: str, candidates: List[str]) -> List[Dict[str, Any]]:
        """Suggest spelling corrections for a misspelled term.
        
        Args:
            query: Potentially misspelled term
            candidates: List of correct terms
            
        Returns:
            List of correction suggestions with confidence scores
        """
        suggestions = []
        
        for candidate in candidates:
            score = self.calculate_similarity(query, candidate)
            if score > 0.6:  # Lower threshold for suggestions
                suggestions.append({
                    "suggestion": candidate,
                    "confidence": score,
                    "message": f"Did you mean '{candidate}'?"
                })
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        return suggestions[:3]  # Return top 3 suggestions
    
    def find_matches_batch(self, queries: List[str], candidates: List[str]) -> Dict[str, Any]:
        """Process multiple fuzzy match queries in batch.
        
        Args:
            queries: List of query strings
            candidates: List of candidate strings
            
        Returns:
            Dictionary mapping queries to their best matches
        """
        results = {}
        
        for query in queries:
            match = self.find_match(query, candidates)
            results[query] = match
        
        return results
    
    def clear_cache(self):
        """Clear the similarity calculation cache."""
        if self.enable_cache:
            self.cache.clear()
            self._query_optimizer.clear_cache()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get fuzzy matching usage statistics.
        
        Returns:
            Dictionary with statistics
        """
        if not self.track_stats:
            return {"tracking_enabled": False}
        
        total = self.stats["total_searches"]
        if total == 0:
            fuzzy_rate = 0.0
        else:
            fuzzy_rate = self.stats["fuzzy_matches"] / total
        
        return {
            "total_searches": total,
            "exact_matches": self.stats["exact_matches"],
            "fuzzy_matches": self.stats["fuzzy_matches"],
            "no_matches": self.stats["no_matches"],
            "fuzzy_match_rate": fuzzy_rate
        }