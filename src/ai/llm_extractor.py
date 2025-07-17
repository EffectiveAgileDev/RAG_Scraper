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
        """Generate prompt for content extraction.

        Args:
            content: Website content to analyze

        Returns:
            Generated prompt string
        """
        categories_text = "\n".join([f"- {cat}" for cat in self.categories])

        prompt = f"""
You are an expert data extractor specializing in the {self.industry} industry.

Your task is to analyze the following website content and extract relevant business information.

CONTENT TO ANALYZE:
{content}

EXTRACT INFORMATION FOR THESE CATEGORIES:
{categories_text}

INSTRUCTIONS:
1. Look for both explicit and implied information
2. Extract business differentiators and unique features
3. Understand context beyond exact keyword matches
4. Assign confidence scores (0.0 to 1.0) for each extraction
5. Only include information with confidence >= 0.6

{self.custom_instructions}

REQUIRED OUTPUT FORMAT (JSON):
{{
    "extractions": [
        {{
            "category": "Category Name",
            "confidence": 0.85,
            "extracted_data": {{
                "key": ["value1", "value2"]
            }}
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
        """Validate and filter extractions.

        Args:
            extractions: Raw extractions from LLM

        Returns:
            Filtered valid extractions
        """
        valid_extractions = []

        for extraction in extractions:
            if not isinstance(extraction, dict):
                continue

            # Validate confidence score
            confidence = extraction.get("confidence", 0.0)
            if (
                not isinstance(confidence, (int, float))
                or confidence < 0.0
                or confidence > 1.0
            ):
                continue

            # Ensure required fields
            if (
                "category" not in extraction
                or "extracted_data" not in extraction
            ):
                continue

            valid_extractions.append(extraction)

        return valid_extractions

    def merge(self, other_response: "LLMResponse") -> "LLMResponse":
        """Merge with another LLM response.

        Args:
            other_response: Another LLM response to merge

        Returns:
            Merged response
        """
        merged_data = {
            "extractions": self.extractions + other_response.extractions,
            "source_attribution": f"{self.source_attribution}; {other_response.source_attribution}",
        }

        return LLMResponse(merged_data, validate=False)


class LLMExtractor:
    """LLM-powered content extractor with caching and statistics."""

    def __init__(
        self,
        api_key: str = None,
        model: str = "gpt-3.5-turbo",
        enable_cache: bool = True,
        track_stats: bool = False,
        rate_limit_calls_per_minute: int = 60,
    ):
        """Initialize LLM extractor.

        Args:
            api_key: OpenAI API key
            model: Model to use for extraction
            enable_cache: Whether to cache responses
            track_stats: Whether to track usage statistics
            rate_limit_calls_per_minute: Rate limiting for API calls
        """
        if not OpenAI:
            raise ImportError("OpenAI package required for LLM extraction")

        self.api_key = api_key
        self.model = model
        self.enable_cache = enable_cache
        self.track_stats = track_stats

        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key) if api_key else None

        # Initialize caching
        self._cache = {} if enable_cache else None
        self._cache_lock = threading.RLock()

        # Initialize statistics
        self._stats = (
            {
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
            }
            if track_stats
            else None
        )

        # Rate limiting
        self._rate_limit = rate_limit_calls_per_minute
        self._call_times = []
        self._rate_lock = threading.Lock()

        # Custom template
        self._custom_template = None

    def _generate_cache_key(
        self, content: str, industry: str, **kwargs
    ) -> str:
        """Generate cache key for content and parameters.

        Args:
            content: Content to extract from
            industry: Industry context
            **kwargs: Additional parameters

        Returns:
            Cache key string
        """
        key_data = f"{content}:{industry}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _enforce_rate_limiting(self):
        """Enforce rate limiting for API calls."""
        if not self._rate_limit:
            return

        with self._rate_lock:
            current_time = time.time()

            # Remove calls older than 1 minute
            self._call_times = [
                t for t in self._call_times if current_time - t < 60
            ]

            # Check if we need to wait
            if len(self._call_times) >= self._rate_limit:
                wait_time = 60 - (current_time - self._call_times[0])
                if wait_time > 0:
                    time.sleep(wait_time)

            self._call_times.append(current_time)

    def _generate_prompt(
        self, content: str, industry: str, industry_config: Dict[str, Any]
    ) -> str:
        """Generate prompt for LLM extraction.

        Args:
            content: Content to analyze
            industry: Industry context
            industry_config: Industry configuration with categories

        Returns:
            Generated prompt
        """
        if self._custom_template:
            return self._custom_template.format(
                content=content,
                industry=industry,
                categories=industry_config.get("categories", []),
            )

        # Extract category names from config
        categories = []
        if "categories" in industry_config:
            for cat in industry_config["categories"]:
                if isinstance(cat, dict) and "category" in cat:
                    categories.append(cat["category"])
                elif isinstance(cat, str):
                    categories.append(cat)

        template = PromptTemplate(industry, categories)
        return template.generate(content)

    def extract(
        self,
        content: str,
        industry: str,
        industry_config: Dict[str, Any] = None,
        confidence_threshold: float = 0.6,
        **kwargs,
    ) -> Dict[str, Any]:
        """Extract information from content using LLM.

        Args:
            content: Website content to analyze
            industry: Industry context
            industry_config: Industry configuration
            confidence_threshold: Minimum confidence for results
            **kwargs: Additional parameters

        Returns:
            Extraction results dictionary
        """
        if not content or not content.strip():
            return {
                "extractions": [],
                "source_attribution": "LLM extraction from webpage content",
            }

        # Check cache first
        cache_key = None
        if self.enable_cache:
            cache_key = self._generate_cache_key(content, industry, **kwargs)

            with self._cache_lock:
                if cache_key in self._cache:
                    if self.track_stats:
                        self._stats["cache_hits"] += 1
                    return self._cache[cache_key]

        if self.track_stats:
            self._stats["total_calls"] += 1
            if self.enable_cache:
                self._stats["cache_misses"] += 1

        try:
            # Enforce rate limiting
            self._enforce_rate_limiting()

            # Generate prompt
            industry_config = industry_config or {"categories": []}
            prompt = self._generate_prompt(content, industry, industry_config)

            # Call LLM API
            if not self.client:
                raise Exception("No OpenAI client configured")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert business data extractor.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=1000,
            )

            # Track token usage
            if (
                self.track_stats
                and hasattr(response, "usage")
                and response.usage
            ):
                usage = response.usage
                total_tokens = getattr(usage, "total_tokens", 0)
                prompt_tokens = getattr(usage, "prompt_tokens", 0)
                completion_tokens = getattr(usage, "completion_tokens", 0)

                # Handle mock objects that might not be integers
                if isinstance(total_tokens, int):
                    self._stats["token_usage"]["total_tokens"] += total_tokens
                if isinstance(prompt_tokens, int):
                    self._stats["token_usage"][
                        "prompt_tokens"
                    ] += prompt_tokens
                if isinstance(completion_tokens, int):
                    self._stats["token_usage"][
                        "completion_tokens"
                    ] += completion_tokens

            # Parse response
            try:
                response_text = response.choices[0].message.content
                response_data = json.loads(response_text)
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                logger.error(f"Failed to parse LLM response: {e}")
                raise Exception("Malformed API response")

            # Validate and create response object
            llm_response = LLMResponse(response_data, validate=True)

            # Apply confidence threshold
            filtered_extractions = []
            for extraction in llm_response.extractions:
                if extraction.get("confidence", 0.0) >= confidence_threshold:
                    filtered_extractions.append(extraction)

            result = {
                "extractions": filtered_extractions,
                "source_attribution": llm_response.source_attribution,
            }

            # Track statistics
            if self.track_stats:
                self._stats["successful_extractions"] += 1
                for extraction in filtered_extractions:
                    self._stats["confidence_scores"].append(
                        extraction.get("confidence", 0.0)
                    )

            # Cache result
            if self.enable_cache and cache_key:
                with self._cache_lock:
                    self._cache[cache_key] = result

            return result

        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")

            if self.track_stats:
                self._stats["failed_extractions"] += 1

            return {
                "extractions": [],
                "error": str(e),
                "fallback_message": "LLM extraction unavailable",
                "source_attribution": "LLM extraction from webpage content",
            }

    def extract_batch(
        self,
        contents: List[str],
        industry: str,
        industry_config: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """Extract information from multiple content pieces.

        Args:
            contents: List of content strings to analyze
            industry: Industry context
            industry_config: Industry configuration

        Returns:
            List of extraction results
        """
        results = []
        for content in contents:
            result = self.extract(content, industry, industry_config)
            results.append(result)
        return results

    def set_custom_template(self, template: str):
        """Set custom prompt template.

        Args:
            template: Custom template string with {content}, {industry}, {categories} placeholders
        """
        self._custom_template = template

    def configure_rate_limiting(self, calls_per_minute: int):
        """Configure rate limiting.

        Args:
            calls_per_minute: Maximum calls per minute
        """
        self._rate_limit = calls_per_minute

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics.

        Returns:
            Statistics dictionary
        """
        if not self.track_stats:
            return {"tracking_enabled": False}

        total_requests = (
            self._stats["cache_hits"] + self._stats["cache_misses"]
        )
        cache_hit_rate = (
            self._stats["cache_hits"] / total_requests
            if total_requests > 0
            else 0.0
        )

        confidence_scores = self._stats["confidence_scores"]
        avg_confidence = (
            sum(confidence_scores) / len(confidence_scores)
            if confidence_scores
            else 0.0
        )

        return {
            "total_calls": self._stats["total_calls"],
            "successful_extractions": self._stats["successful_extractions"],
            "failed_extractions": self._stats["failed_extractions"],
            "average_confidence": avg_confidence,
            "cache_hit_rate": cache_hit_rate,
        }

    def get_token_usage(self) -> Dict[str, int]:
        """Get token usage statistics.

        Returns:
            Token usage dictionary
        """
        if not self.track_stats:
            return {"tracking_enabled": False}

        return self._stats["token_usage"].copy()

    def clear_cache(self):
        """Clear the response cache."""
        if self.enable_cache:
            with self._cache_lock:
                self._cache.clear()
                if self.track_stats:
                    self._stats["cache_hits"] = 0
                    self._stats["cache_misses"] = 0
