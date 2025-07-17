"""Dynamic prompt adjustment system for optimizing LLM interactions."""

import logging
import re
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class DynamicPromptAdjuster:
    """Dynamically adjusts prompts based on content analysis and performance."""

    def __init__(self):
        """Initialize dynamic prompt adjuster."""
        self.complexity_thresholds = {
            "simple": 0.3,
            "moderate": 0.6,
            "complex": 0.8,
            "very_complex": 0.9,
        }

        self.prompt_strategies = {
            "simple": "Use direct, straightforward extraction instructions",
            "moderate": "Use structured extraction with clear examples",
            "complex": "Use multi-step extraction with verification",
            "creative_interpretation": "Use creative interpretation for artistic/poetic content",
            "technical": "Use technical terminology and precise extraction",
            "multilingual": "Handle multiple languages with translation context",
        }

        self.performance_history = {}

    def analyze_complexity(self, content: str) -> Dict[str, Any]:
        """Analyze content complexity and suggest prompt strategy.

        Args:
            content: Content to analyze

        Returns:
            Complexity analysis with prompt recommendations
        """
        try:
            complexity_factors = self._calculate_complexity_factors(content)
            overall_complexity = self._calculate_overall_complexity(
                complexity_factors
            )
            content_type = self._determine_content_type(
                content, complexity_factors
            )

            # Select appropriate strategy
            strategy = self._select_prompt_strategy(
                overall_complexity, content_type
            )

            return {
                "complexity_score": overall_complexity,
                "content_type": content_type,
                "complexity_factors": complexity_factors,
                "recommended_strategy": strategy,
                "prompt_adjustments": self._generate_prompt_adjustments(
                    strategy, content_type
                ),
                "reasoning": self._explain_selection_reasoning(
                    overall_complexity, content_type, strategy
                ),
            }

        except Exception as e:
            logger.error(f"Complexity analysis failed: {str(e)}")
            return self._default_complexity_result()

    def _calculate_complexity_factors(self, content: str) -> Dict[str, float]:
        """Calculate various complexity factors."""
        factors = {}

        # Language complexity
        factors["language_complexity"] = self._analyze_language_complexity(
            content
        )

        # Structure complexity
        factors["structure_complexity"] = self._analyze_structure_complexity(
            content
        )

        # Content density
        factors["content_density"] = self._analyze_content_density(content)

        # Artistic/poetic language
        factors["artistic_language"] = self._detect_artistic_language(content)

        # Technical terminology
        factors["technical_content"] = self._detect_technical_content(content)

        # Multilingual content
        factors["multilingual"] = self._detect_multilingual_content(content)

        return factors

    def _analyze_language_complexity(self, content: str) -> float:
        """Analyze language complexity (sentence length, vocabulary, etc.)."""
        sentences = re.split(r"[.!?]+", content)

        if not sentences:
            return 0.0

        # Average sentence length
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(
            sentences
        )

        # Vocabulary diversity (unique words / total words)
        words = re.findall(r"\b\w+\b", content.lower())
        vocab_diversity = len(set(words)) / len(words) if words else 0

        # Complex words (longer than 7 characters)
        complex_words = [w for w in words if len(w) > 7]
        complex_word_ratio = len(complex_words) / len(words) if words else 0

        # Combine factors
        complexity = (
            min(avg_sentence_length / 20, 1.0) * 0.4
            + vocab_diversity * 0.3
            + complex_word_ratio * 0.3
        )

        return min(complexity, 1.0)

    def _analyze_structure_complexity(self, content: str) -> float:
        """Analyze HTML structure complexity."""
        # Count nested elements
        nested_elements = len(re.findall(r"<[^>]+>", content))

        # Count different element types
        element_types = set(re.findall(r"<(\w+)", content))

        # Calculate complexity based on structure
        structure_score = (
            min(nested_elements / 100, 1.0) * 0.6
            + min(len(element_types) / 20, 1.0) * 0.4
        )

        return min(structure_score, 1.0)

    def _analyze_content_density(self, content: str) -> float:
        """Analyze content information density."""
        # Text to HTML ratio
        text_content = re.sub(r"<[^>]+>", "", content)
        text_ratio = len(text_content) / len(content) if content else 0

        # Information markers (prices, names, etc.)
        price_count = len(re.findall(r"\$\d+", content))
        name_count = len(re.findall(r"<h[1-6]", content))

        density_score = (
            text_ratio * 0.4
            + min(price_count / 10, 1.0) * 0.3
            + min(name_count / 15, 1.0) * 0.3
        )

        return min(density_score, 1.0)

    def _detect_artistic_language(self, content: str) -> float:
        """Detect artistic/poetic language patterns."""
        artistic_indicators = [
            r"\b(symphony|whisper|dance|embrace|journey|treasure)\b",
            r"\b(delicate|gentle|lovingly|artisan|crafted)\b",
            r"\b(sunset|moonbeam|starlight|grove|garden)\b",
            r"\b(secrets|mystery|awakening|harmony)\b",
        ]

        matches = 0
        text_content = re.sub(r"<[^>]+>", "", content).lower()

        for pattern in artistic_indicators:
            matches += len(re.findall(pattern, text_content, re.IGNORECASE))

        # Normalize by content length
        artistic_score = min(matches / (len(text_content.split()) / 10), 1.0)

        return artistic_score

    def _detect_technical_content(self, content: str) -> float:
        """Detect technical terminology."""
        technical_indicators = [
            r"\b(API|JSON|HTML|CSS|JavaScript)\b",
            r"\b(algorithm|database|protocol|interface)\b",
            r"\b(configuration|parameter|variable|function)\b",
        ]

        matches = 0
        for pattern in technical_indicators:
            matches += len(re.findall(pattern, content, re.IGNORECASE))

        technical_score = min(matches / 5, 1.0)
        return technical_score

    def _detect_multilingual_content(self, content: str) -> float:
        """Detect multilingual content."""
        # Simple detection of non-English characters/patterns
        multilingual_patterns = [
            r"[àáâãäåæçèéêëìíîïñòóôõöøùúûüý]",  # Accented characters
            r"[αβγδεζηθικλμνξοπρστυφχψω]",  # Greek
            r"[あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん]",  # Japanese hiragana
        ]

        matches = 0
        for pattern in multilingual_patterns:
            matches += len(re.findall(pattern, content, re.IGNORECASE))

        multilingual_score = min(matches / 10, 1.0)
        return multilingual_score

    def _calculate_overall_complexity(
        self, factors: Dict[str, float]
    ) -> float:
        """Calculate overall complexity score."""
        weights = {
            "language_complexity": 0.3,
            "structure_complexity": 0.2,
            "content_density": 0.2,
            "artistic_language": 0.15,
            "technical_content": 0.1,
            "multilingual": 0.05,
        }

        overall = sum(
            factors.get(factor, 0) * weight
            for factor, weight in weights.items()
        )
        return min(overall, 1.0)

    def _determine_content_type(
        self, content: str, factors: Dict[str, float]
    ) -> str:
        """Determine the primary content type."""
        if factors.get("artistic_language", 0) > 0.6:
            return "poetic"
        elif factors.get("technical_content", 0) > 0.7:
            return "technical"
        elif factors.get("multilingual", 0) > 0.5:
            return "multilingual"
        elif factors.get("structure_complexity", 0) > 0.8:
            return "complex_structured"
        else:
            return "standard"

    def _select_prompt_strategy(
        self, complexity: float, content_type: str
    ) -> str:
        """Select appropriate prompt strategy."""
        if content_type == "poetic":
            return "creative_interpretation"
        elif content_type == "technical":
            return "technical"
        elif content_type == "multilingual":
            return "multilingual"
        elif complexity > 0.8:
            return "complex"
        elif complexity > 0.6:
            return "moderate"
        else:
            return "simple"

    def _generate_prompt_adjustments(
        self, strategy: str, content_type: str
    ) -> List[str]:
        """Generate specific prompt adjustments."""
        adjustments = []

        if strategy == "creative_interpretation":
            adjustments.extend(
                [
                    "Use creative interpretation for poetic descriptions",
                    "Focus on extracting actual food items from metaphorical language",
                    "Identify cuisine style from artistic descriptions",
                    "Translate poetic language into practical menu information",
                ]
            )
        elif strategy == "technical":
            adjustments.extend(
                [
                    "Use precise technical terminology",
                    "Focus on structured data extraction",
                    "Maintain technical accuracy",
                ]
            )
        elif strategy == "multilingual":
            adjustments.extend(
                [
                    "Handle multiple languages appropriately",
                    "Provide translations where needed",
                    "Preserve original language context",
                ]
            )
        elif strategy == "complex":
            adjustments.extend(
                [
                    "Break down extraction into multiple steps",
                    "Verify extracted information",
                    "Handle complex nested structures",
                ]
            )
        else:
            adjustments.extend(
                [
                    "Use straightforward extraction instructions",
                    "Focus on clear, obvious information",
                ]
            )

        return adjustments

    def _explain_selection_reasoning(
        self, complexity: float, content_type: str, strategy: str
    ) -> str:
        """Explain why this strategy was selected."""
        reasons = []

        if complexity > 0.8:
            reasons.append("High complexity content detected")
        elif complexity > 0.6:
            reasons.append("Moderate complexity content detected")
        else:
            reasons.append("Simple content structure detected")

        if content_type != "standard":
            reasons.append(f"{content_type.title()} content type identified")

        reasoning = (
            ". ".join(reasons)
            + f". Selected {strategy} strategy for optimal extraction."
        )

        return reasoning

    def _default_complexity_result(self) -> Dict[str, Any]:
        """Return default complexity analysis result."""
        return {
            "complexity_score": 0.5,
            "content_type": "standard",
            "complexity_factors": {},
            "recommended_strategy": "moderate",
            "prompt_adjustments": ["Use standard extraction approach"],
            "reasoning": "Default analysis due to processing error",
        }

    def optimize_prompts_from_history(
        self, extraction_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Optimize prompts based on historical performance."""
        if not extraction_history:
            return {"optimization": "No history available"}

        # Analyze success patterns
        successful_extractions = [
            h for h in extraction_history if h.get("success_rate", 0) > 0.8
        ]

        if successful_extractions:
            # Find common patterns in successful extractions
            common_strategies = {}
            for extraction in successful_extractions:
                strategy = extraction.get("strategy", "unknown")
                common_strategies[strategy] = (
                    common_strategies.get(strategy, 0) + 1
                )

            best_strategy = max(common_strategies, key=common_strategies.get)

            return {
                "optimization": "Based on historical performance",
                "recommended_strategy": best_strategy,
                "success_count": common_strategies[best_strategy],
                "total_extractions": len(extraction_history),
            }

        return {
            "optimization": "Insufficient successful extractions for optimization"
        }
