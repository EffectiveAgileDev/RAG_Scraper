"""
Refactored LLM-powered content extraction with separated concerns.

This refactored version addresses the brittleness issues by:
- Separating API client, caching, statistics, and extraction logic
- Using dependency injection instead of complex initialization
- Enabling unit testing of individual concerns
- Eliminating threading issues in tests
"""

import json
import logging
import time
import hashlib
from typing import Dict, List, Optional, Any, Union, Protocol
from dataclasses import dataclass
from datetime import datetime
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
except ImportError:
    logger.warning("OpenAI package not installed. LLM extraction will not work.")
    OpenAI = None


@dataclass
class ExtractionResult:
    """Result of an LLM extraction operation."""
    success: bool
    extractions: List[Dict[str, Any]]
    confidence_score: Optional[float] = None
    error_message: Optional[str] = None
    source_attribution: str = "LLM extraction"
    processing_time: Optional[float] = None
    token_usage: Optional[Dict[str, int]] = None
    cache_hit: bool = False


class LLMServiceProtocol(Protocol):
    """Protocol for LLM services."""
    
    def extract_content(self, prompt: str) -> ExtractionResult:
        """Extract content using LLM."""
        ...


class SimplifiedLLMService:
    """
    Simplified LLM service that focuses only on API interaction.
    
    This eliminates the complex mocking issues by having a single responsibility.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """Initialize with minimal dependencies."""
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key) if api_key and OpenAI else None
    
    def extract_content(self, prompt: str) -> ExtractionResult:
        """Extract content using OpenAI API."""
        if not self.client:
            return ExtractionResult(
                success=False,
                extractions=[],
                error_message="OpenAI client not available"
            )
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data extraction assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            processing_time = time.time() - start_time
            
            # Parse response
            content = response.choices[0].message.content
            try:
                result_data = json.loads(content)
                extractions = result_data.get("extractions", [])
                
                return ExtractionResult(
                    success=True,
                    extractions=extractions,
                    confidence_score=0.8,  # Default confidence
                    processing_time=processing_time,
                    token_usage={
                        "total_tokens": response.usage.total_tokens,
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens
                    } if response.usage else None
                )
            except json.JSONDecodeError:
                return ExtractionResult(
                    success=False,
                    extractions=[],
                    error_message="Failed to parse JSON response",
                    processing_time=processing_time
                )
                
        except Exception as e:
            return ExtractionResult(
                success=False,
                extractions=[],
                error_message=str(e)
            )


class CachingLLMService:
    """
    LLM service decorator that adds caching functionality.
    
    This separates caching concerns from API interaction.
    """
    
    def __init__(self, llm_service: LLMServiceProtocol, enable_cache: bool = True):
        """Initialize with injectable LLM service."""
        self.llm_service = llm_service
        self.enable_cache = enable_cache
        self._cache = {} if enable_cache else None
        self._cache_lock = threading.RLock() if enable_cache else None
    
    def extract_content(self, prompt: str) -> ExtractionResult:
        """Extract content with caching support."""
        if not self.enable_cache:
            return self.llm_service.extract_content(prompt)
        
        # Generate cache key
        cache_key = hashlib.md5(prompt.encode('utf-8')).hexdigest()
        
        # Check cache
        with self._cache_lock:
            if cache_key in self._cache:
                cached_result = self._cache[cache_key]
                cached_result.cache_hit = True
                return cached_result
        
        # Not in cache, get from service
        result = self.llm_service.extract_content(prompt)
        
        # Store in cache if successful
        if result.success and self._cache is not None:
            with self._cache_lock:
                self._cache[cache_key] = result
        
        result.cache_hit = False
        return result
    
    def clear_cache(self):
        """Clear the cache."""
        if self._cache is not None:
            with self._cache_lock:
                self._cache.clear()


class StatisticsTracker:
    """
    Separate statistics tracking service.
    
    This eliminates the need to mock statistics in tests.
    """
    
    def __init__(self):
        """Initialize statistics tracking."""
        self.stats = {
            "total_calls": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "confidence_scores": [],
            "cache_hits": 0,
            "cache_misses": 0,
            "token_usage": {
                "total_tokens": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
            },
            "processing_times": []
        }
        self._stats_lock = threading.Lock()
    
    def record_extraction(self, result: ExtractionResult):
        """Record an extraction result."""
        with self._stats_lock:
            self.stats["total_calls"] += 1
            
            if result.success:
                self.stats["successful_extractions"] += 1
                if result.confidence_score is not None:
                    self.stats["confidence_scores"].append(result.confidence_score)
            else:
                self.stats["failed_extractions"] += 1
            
            if result.cache_hit:
                self.stats["cache_hits"] += 1
            else:
                self.stats["cache_misses"] += 1
            
            if result.token_usage:
                for key, value in result.token_usage.items():
                    self.stats["token_usage"][key] += value
            
            if result.processing_time is not None:
                self.stats["processing_times"].append(result.processing_time)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current statistics."""
        with self._stats_lock:
            return self.stats.copy()
    
    def reset_statistics(self):
        """Reset all statistics."""
        with self._stats_lock:
            self.stats = {
                "total_calls": 0,
                "successful_extractions": 0,
                "failed_extractions": 0,
                "confidence_scores": [],
                "cache_hits": 0,
                "cache_misses": 0,
                "token_usage": {
                    "total_tokens": 0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                },
                "processing_times": []
            }


class PromptBuilder:
    """
    Separate prompt building service.
    
    This makes prompt generation testable without LLM dependencies.
    """
    
    def __init__(self, industry: str = "restaurant", categories: Optional[List[str]] = None):
        """Initialize prompt builder."""
        self.industry = industry
        self.categories = categories or ["menu", "contact", "hours", "location"]
    
    def build_extraction_prompt(self, content: str, custom_instructions: str = "") -> str:
        """Build extraction prompt for given content."""
        categories_str = ", ".join(self.categories)
        
        prompt = f"""
Extract structured information from the following {self.industry} website content.

Focus on these categories: {categories_str}

{custom_instructions}

Content to analyze:
{content[:2000]}  # Limit content length

Return the results in this JSON format:
{{
    "extractions": [
        {{
            "category": "category_name",
            "items": ["item1", "item2"],
            "confidence": 0.8
        }}
    ],
    "source_attribution": "LLM extraction from webpage content"
}}

Respond only with valid JSON.
"""
        return prompt.strip()


class RefactoredLLMExtractor:
    """
    Refactored LLM extractor using dependency injection and separation of concerns.
    
    This version addresses the brittleness issues by:
    - Using composition instead of inheritance
    - Separating caching, statistics, and API concerns
    - Enabling easy unit testing
    - Eliminating complex mock setups
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 model: str = "gpt-3.5-turbo",
                 enable_caching: bool = True,  # Match original parameter name
                 enable_statistics: bool = True,  # Match original parameter name
                 llm_service: Optional[LLMServiceProtocol] = None,
                 enable_cache: Optional[bool] = None,  # Backward compatibility
                 track_stats: Optional[bool] = None):
        """
        Initialize with injectable dependencies.
        
        Args:
            api_key: OpenAI API key
            model: Model name
            enable_caching: Whether to enable caching (original parameter name)
            enable_statistics: Whether to track statistics (original parameter name)
            llm_service: Injectable LLM service (creates default if None)
            enable_cache: Backward compatibility parameter
            track_stats: Backward compatibility parameter
        """
        # Store original parameters for backward compatibility
        self.api_key = api_key
        self.model = model
        self.enable_caching = enable_caching if enable_cache is None else enable_cache
        self.enable_statistics = enable_statistics if track_stats is None else track_stats
        
        # Create default service if none provided
        if llm_service is None:
            llm_service = SimplifiedLLMService(api_key=api_key, model=model)
        
        # Add caching if enabled
        if self.enable_caching:
            llm_service = CachingLLMService(llm_service, enable_cache=True)
        
        self.llm_service = llm_service
        
        # Initialize statistics tracker
        self.stats_tracker = StatisticsTracker() if self.enable_statistics else None
        
        # Initialize prompt builder
        self.prompt_builder = PromptBuilder()
        
        # Add legacy attributes for backward compatibility
        self._cache = getattr(self.llm_service, '_cache', None)
        self._stats = self.stats_tracker.stats if self.stats_tracker else None
    
    def extract_from_content(self, 
                           content: str, 
                           industry: str = "restaurant",
                           categories: Optional[List[str]] = None,
                           custom_instructions: str = "") -> ExtractionResult:
        """
        Extract structured data from content.
        
        Args:
            content: HTML or text content to extract from
            industry: Industry type for extraction
            categories: Categories to extract
            custom_instructions: Additional instructions
            
        Returns:
            ExtractionResult with extraction data
        """
        # Build prompt
        prompt_builder = PromptBuilder(industry, categories)
        prompt = prompt_builder.build_extraction_prompt(content, custom_instructions)
        
        # Extract using LLM service
        result = self.llm_service.extract_content(prompt)
        
        # Record statistics
        if self.stats_tracker:
            self.stats_tracker.record_extraction(result)
        
        return result
    
    def get_statistics(self) -> Optional[Dict[str, Any]]:
        """Get extraction statistics."""
        return self.stats_tracker.get_statistics() if self.stats_tracker else None
    
    def clear_cache(self):
        """Clear the cache if caching is enabled."""
        if hasattr(self.llm_service, 'clear_cache'):
            self.llm_service.clear_cache()


# Backward compatibility alias
LLMExtractor = RefactoredLLMExtractor