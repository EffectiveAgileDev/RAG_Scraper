"""LLM-powered content extraction for business websites."""

import json
import logging
import time
import hashlib
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
except ImportError:
    logger.warning(
        "OpenAI package not installed. LLM extraction will not work."
    )
    OpenAI = None

# Import the refactored implementation
from .llm_extractor_refactored import (
    RefactoredLLMExtractor,
    ExtractionResult,
    SimplifiedLLMService,
    CachingLLMService,
    StatisticsTracker,
    PromptBuilder
)


@dataclass
class PromptTemplate:
    """Template for generating LLM prompts."""

    def __init__(
        self,
        industry: str,
        categories: List[str],
        custom_instructions: str = "",
    ):
        """Initialize prompt template.

        Args:
            industry: Target industry name
            categories: List of categories to extract
            custom_instructions: Additional instructions for extraction
        """
        if not industry.strip():
            raise ValueError("Industry cannot be empty")
        if not categories:
            raise ValueError("Categories list cannot be empty")

        self.industry = industry
        self.categories = categories
        self.custom_instructions = custom_instructions

    def generate(self, content: str) -> str:
        """Generate LLM prompt for content extraction.

        Args:
            content: HTML or text content to analyze

        Returns:
            Formatted prompt string for LLM
        """
        categories_str = ", ".join(self.categories)
        
        prompt = f"""
Extract structured information from the following {self.industry} website content.

Focus on these categories: {categories_str}

{self.custom_instructions}

Content to analyze:
{content[:2000]}

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


class LLMResponse:
    """Represents and validates LLM extraction response."""

    def __init__(self, response_data: Dict[str, Any], validate: bool = True):
        """Initialize LLM response.

        Args:
            response_data: Raw response data from LLM
            validate: Whether to validate and filter response
        """
        if not isinstance(response_data, dict):
            raise ValueError("Response data must be a dictionary")

        if "extractions" not in response_data:
            raise ValueError("Response must contain 'extractions' field")

        self.raw_data = response_data
        self.source_attribution = response_data.get(
            "source_attribution", "LLM extraction"
        )

        if validate:
            self.extractions = self._validate_extractions(
                response_data.get("extractions", [])
            )
        else:
            self.extractions = response_data.get("extractions", [])

    def _validate_extractions(
        self, extractions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate and filter extractions."""
        valid_extractions = []
        for extraction in extractions:
            if isinstance(extraction, dict) and "category" in extraction:
                valid_extractions.append(extraction)
        return valid_extractions

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "extractions": self.extractions,
            "source_attribution": self.source_attribution,
        }

    def merge_with(self, other: "LLMResponse") -> "LLMResponse":
        """Merge this response with another."""
        if not isinstance(other, LLMResponse):
            return self

        merged_extractions = self.extractions + other.extractions
        merged_data = {
            "extractions": merged_extractions,
            "source_attribution": f"{self.source_attribution}, {other.source_attribution}",
        }

        return LLMResponse(merged_data, validate=False)


class LLMExtractor:
    """
    LLM-powered content extractor with caching and statistics.
    
    This class now uses the refactored implementation internally while maintaining
    backward compatibility with existing code.
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = "gpt-3.5-turbo",
        enable_cache: bool = True,
        track_stats: bool = False,
        enable_caching: bool = None,  # Support original parameter name
        enable_statistics: bool = None,  # Support original parameter name
        rate_limit_calls_per_minute: int = 60,
    ):
        """Initialize LLM extractor.

        Args:
            api_key: OpenAI API key
            model: Model to use for extraction
            enable_cache: Whether to cache responses
            track_stats: Whether to track usage statistics
            enable_caching: Original parameter name for caching
            enable_statistics: Original parameter name for statistics
            rate_limit_calls_per_minute: Rate limiting for API calls (legacy)
        """
        # Handle parameter compatibility
        final_enable_cache = enable_caching if enable_caching is not None else enable_cache
        final_track_stats = enable_statistics if enable_statistics is not None else track_stats
        
        # Initialize the refactored implementation
        self._refactored_extractor = RefactoredLLMExtractor(
            api_key=api_key,
            model=model,
            enable_caching=final_enable_cache,
            enable_statistics=final_track_stats
        )
        
        # Store parameters for backward compatibility
        self.api_key = api_key
        self.model = model
        self.enable_cache = final_enable_cache
        self.track_stats = final_track_stats
        self.enable_caching = final_enable_cache  # Original parameter name
        self.enable_statistics = final_track_stats  # Original parameter name
        
        # Legacy attributes for backward compatibility
        self._cache = getattr(self._refactored_extractor.llm_service, '_cache', {})
        self._stats = self._refactored_extractor.stats_tracker.stats if self._refactored_extractor.stats_tracker else {}
        self.client = getattr(self._refactored_extractor.llm_service, 'client', None)
        
        # Rate limiting (simplified for backward compatibility)
        self._rate_limit = rate_limit_calls_per_minute
        self._call_times = []
        self._rate_lock = threading.Lock()
        
        # Custom template
        self._custom_template = None

    def extract_from_html(
        self, 
        html_content: str, 
        industry: str = "restaurant",
        categories: Optional[List[str]] = None,
        custom_instructions: str = ""
    ) -> LLMResponse:
        """Extract structured data from HTML content.

        Args:
            html_content: HTML content to extract from
            industry: Industry type for extraction
            categories: Categories to extract
            custom_instructions: Additional instructions

        Returns:
            LLMResponse with extraction results
        """
        # Delegate to the refactored implementation
        result = self._refactored_extractor.extract_from_content(
            html_content, industry, categories, custom_instructions
        )
        
        # Convert to legacy response format
        response_data = {
            "extractions": result.extractions,
            "source_attribution": result.source_attribution
        }
        
        return LLMResponse(response_data)

    def extract(
        self,
        content: str,
        industry: str = "restaurant",
        categories: Optional[List[str]] = None,
        custom_instructions: str = ""
    ) -> LLMResponse:
        """Extract structured data from content.
        
        This is the main extraction method used by the AI analysis system.
        
        Args:
            content: Content to extract from (HTML or text)
            industry: Industry type for extraction
            categories: Categories to extract
            custom_instructions: Additional instructions
            
        Returns:
            LLMResponse with extraction results
        """
        return self.extract_from_html(content, industry, categories, custom_instructions)

    def extract_from_content(
        self,
        content: str,
        industry: str = "restaurant",
        categories: Optional[List[str]] = None,
        custom_instructions: str = ""
    ) -> LLMResponse:
        """Extract structured data from content."""
        return self.extract_from_html(content, industry, categories, custom_instructions)

    def get_statistics(self) -> Optional[Dict[str, Any]]:
        """Get extraction statistics."""
        return self._refactored_extractor.get_statistics()

    def clear_cache(self):
        """Clear the extraction cache."""
        self._refactored_extractor.clear_cache()

    def set_custom_template(self, template: PromptTemplate):
        """Set a custom prompt template."""
        self._custom_template = template

    # Backward compatibility methods
    def _generate_cache_key(self, content: str, industry: str, **kwargs) -> str:
        """Generate cache key for backward compatibility."""
        return hashlib.md5(f"{content}{industry}".encode('utf-8')).hexdigest()

    def _track_statistics(self, *args, **kwargs):
        """Track statistics for backward compatibility."""
        pass  # Handled internally by refactored implementation

    def _apply_rate_limiting(self):
        """Apply rate limiting for backward compatibility."""
        pass  # Simplified for backward compatibility