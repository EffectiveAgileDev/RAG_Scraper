"""Confidence scoring system for AI-enhanced extraction results."""

import logging
import time
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import statistics
import math
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ScoringMethod(Enum):
    """Available confidence scoring methods."""

    WEIGHTED_AVERAGE = "weighted_average"
    MULTIPLICATIVE = "multiplicative"
    MIN_MAX_NORMALIZED = "min_max_normalized"


@dataclass
class ConfidenceFactors:
    """Data class for confidence factors."""

    source_reliability: float = 0.0
    extraction_method: float = 0.0
    content_quality: float = 0.0
    industry_relevance: float = 0.0
    llm_confidence: float = 0.0


class ConfidenceScorer:
    """Multi-factor confidence scoring system for extraction results."""

    def __init__(
        self,
        weights: Dict[str, float] = None,
        scoring_method: ScoringMethod = ScoringMethod.WEIGHTED_AVERAGE,
    ):
        """Initialize confidence scorer.

        Args:
            weights: Factor weights for scoring
            scoring_method: Method to use for combining factors
        """
        # Default weights that sum to 1.0
        self.weights = weights or {
            "source_reliability": 0.3,
            "extraction_method": 0.25,
            "content_quality": 0.2,
            "industry_relevance": 0.15,
            "llm_confidence": 0.1,
        }

        # Validate weights
        self._validate_weights(self.weights)

        self.scoring_method = scoring_method
        self.industry_weights = {}  # Industry-specific weight overrides
        self.custom_factors = {}  # Custom factor calculators

        # Performance tracking for weight adjustment
        self.performance_history = {}

    def _validate_weights(self, weights: Dict[str, float]):
        """Validate weight configuration.

        Args:
            weights: Weights dictionary to validate

        Raises:
            ValueError: If weights are invalid
        """
        total = sum(weights.values())
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total}")

        for factor, weight in weights.items():
            if weight < 0:
                raise ValueError(f"Negative weight for {factor}: {weight}")

    def calculate_confidence(self, extraction_data: Dict[str, Any]) -> float:
        """Calculate overall confidence score for extraction.

        Args:
            extraction_data: Data from extraction process

        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Get industry-specific weights if available
        industry = extraction_data.get("industry")
        weights = self.industry_weights.get(industry, self.weights)

        # Calculate individual factor scores
        factors = {}

        if "source_reliability" in weights:
            factors["source_reliability"] = self._calculate_source_reliability(
                extraction_data
            )

        if "extraction_method" in weights:
            factors[
                "extraction_method"
            ] = self._calculate_extraction_method_score(extraction_data)

        if "content_quality" in weights:
            factors["content_quality"] = self._calculate_content_quality(
                extraction_data
            )

        if "industry_relevance" in weights:
            factors["industry_relevance"] = self._calculate_industry_relevance(
                extraction_data
            )

        if "llm_confidence" in weights:
            factors["llm_confidence"] = self._calculate_llm_confidence(
                extraction_data
            )

        # Calculate custom factors
        for factor_name, calculator in self.custom_factors.items():
            if factor_name in weights:
                try:
                    factors[factor_name] = calculator(extraction_data)
                except Exception as e:
                    logger.warning(
                        f"Custom factor {factor_name} calculation failed: {e}"
                    )
                    factors[factor_name] = 0.0

        # Apply scoring method
        return self._apply_scoring_method(factors, weights)

    def _calculate_source_reliability(self, data: Dict[str, Any]) -> float:
        """Calculate source reliability score.

        Args:
            data: Extraction data

        Returns:
            Source reliability score (0.0 to 1.0)
        """
        score = 0.5  # Base score

        # URL analysis
        source_url = data.get("source_url", "")
        if source_url:
            parsed = urlparse(source_url)

            # HTTPS bonus
            if parsed.scheme == "https":
                score += 0.1

            # Domain quality (simplified check)
            domain = parsed.netloc.lower()
            if any(
                suspicious in domain
                for suspicious in ["temp", "test", "staging"]
            ):
                score -= 0.2

            # Top-level domain assessment
            if domain.endswith((".com", ".org", ".edu", ".gov")):
                score += 0.1

        # Domain authority (if provided)
        domain_authority = data.get("domain_authority", 0)
        if domain_authority > 0:
            score += (domain_authority / 100) * 0.3  # Up to 30% bonus

        # SSL certificate
        if data.get("ssl_certificate", False):
            score += 0.1

        # Content freshness
        last_updated = data.get("last_updated")
        if last_updated:
            try:
                if isinstance(last_updated, str):
                    update_date = datetime.fromisoformat(
                        last_updated.replace("Z", "+00:00")
                    )
                else:
                    update_date = last_updated

                days_old = (
                    datetime.now().replace(tzinfo=None)
                    - update_date.replace(tzinfo=None)
                ).days
                if days_old < 30:
                    score += 0.1
                elif days_old > 365:
                    score -= 0.1
            except Exception:
                pass  # Ignore date parsing errors

        return max(0.0, min(1.0, score))

    def _calculate_extraction_method_score(
        self, data: Dict[str, Any]
    ) -> float:
        """Calculate extraction method confidence score.

        Args:
            data: Extraction data

        Returns:
            Extraction method score (0.0 to 1.0)
        """
        extraction_methods = data.get("extraction_methods", [])
        if not extraction_methods:
            return 0.3  # Default for unknown method

        # Method quality scores
        method_scores = {
            "json_ld": 0.9,  # Structured data is most reliable
            "microdata": 0.8,  # Also structured
            "llm": 0.7,  # AI analysis is good but can hallucinate
            "heuristic": 0.5,  # Pattern matching is less reliable
            "generic": 0.3,  # Fallback methods
        }

        # Calculate base score from methods used
        method_score = 0.0
        for method in extraction_methods:
            method_score = max(method_score, method_scores.get(method, 0.3))

        # Bonus for multiple methods (consensus)
        if len(extraction_methods) > 1:
            method_score += 0.1

        # Agreement bonus (if provided)
        agreement = data.get("method_agreement", 1.0)
        method_score *= agreement

        return max(0.0, min(1.0, method_score))

    def _calculate_content_quality(self, data: Dict[str, Any]) -> float:
        """Calculate content quality score.

        Args:
            data: Extraction data

        Returns:
            Content quality score (0.0 to 1.0)
        """
        content = data.get("content", "")
        if not content:
            return 0.0

        score = 0.5  # Base score

        # Content length assessment
        content_length = len(content)
        if content_length > 100:
            score += 0.2
        elif content_length < 20:
            score -= 0.2

        # Structured data presence
        if data.get("structured_data_present", False):
            score += 0.2

        # Spelling and grammar (simplified check)
        spelling_errors = data.get("spelling_errors", 0)
        if spelling_errors == 0:
            score += 0.1
        elif spelling_errors > 3:
            score -= 0.2

        # Word count and sentence structure
        words = content.split()
        if len(words) > 10:
            score += 0.1

        # Check for complete sentences
        sentences = re.split(r"[.!?]+", content)
        complete_sentences = sum(
            1 for s in sentences if len(s.strip().split()) >= 3
        )
        if complete_sentences > 0:
            score += 0.1

        return max(0.0, min(1.0, score))

    def _calculate_industry_relevance(self, data: Dict[str, Any]) -> float:
        """Calculate industry relevance score.

        Args:
            data: Extraction data

        Returns:
            Industry relevance score (0.0 to 1.0)
        """
        content = data.get("content", "").lower()
        industry = data.get("industry", "")

        if not content or not industry:
            return 0.5  # Neutral score

        # Industry-specific keywords
        industry_keywords = {
            "restaurant": [
                "menu",
                "dining",
                "food",
                "restaurant",
                "cuisine",
                "chef",
                "table",
                "reservation",
            ],
            "medical": [
                "doctor",
                "medical",
                "health",
                "patient",
                "treatment",
                "clinic",
                "hospital",
                "appointment",
            ],
            "real estate": [
                "property",
                "house",
                "home",
                "real estate",
                "agent",
                "listing",
                "price",
                "bedroom",
            ],
            "dental": [
                "dental",
                "dentist",
                "teeth",
                "oral",
                "hygiene",
                "cleaning",
                "cavity",
                "braces",
            ],
        }

        keywords = industry_keywords.get(industry.lower(), [])
        if not keywords:
            return 0.5  # Neutral for unknown industries

        # Count keyword matches
        keyword_matches = sum(1 for keyword in keywords if keyword in content)
        keyword_density = keyword_matches / len(keywords) if keywords else 0

        # Use provided keyword density if available
        provided_density = data.get("keyword_density")
        if provided_density is not None:
            keyword_density = provided_density

        # Base score from keyword density
        score = (
            keyword_density * 0.8 + 0.2
        )  # 20% base + up to 80% from keywords

        return max(0.0, min(1.0, score))

    def _calculate_llm_confidence(self, data: Dict[str, Any]) -> float:
        """Calculate LLM confidence score.

        Args:
            data: Extraction data

        Returns:
            LLM confidence score (0.0 to 1.0)
        """
        llm_extractions = data.get("llm_extractions", [])
        if not llm_extractions:
            return 0.5  # Neutral score when no LLM data

        # Calculate average confidence from LLM extractions
        confidences = []
        for extraction in llm_extractions:
            if isinstance(extraction, dict) and "confidence" in extraction:
                confidences.append(extraction["confidence"])

        if not confidences:
            return 0.5

        return statistics.mean(confidences)

    def _apply_scoring_method(
        self, factors: Dict[str, float], weights: Dict[str, float] = None
    ) -> float:
        """Apply scoring method to combine factors.

        Args:
            factors: Calculated factor scores
            weights: Factor weights

        Returns:
            Combined confidence score
        """
        if not factors:
            return 0.0

        weights = weights or self.weights

        if self.scoring_method == ScoringMethod.WEIGHTED_AVERAGE:
            # Weighted average of factors
            total_score = 0.0
            total_weight = 0.0

            for factor, score in factors.items():
                if factor in weights:
                    total_score += score * weights[factor]
                    total_weight += weights[factor]

            return total_score / total_weight if total_weight > 0 else 0.0

        elif self.scoring_method == ScoringMethod.MULTIPLICATIVE:
            # Multiply factors together
            score = 1.0
            for factor_score in factors.values():
                score *= factor_score
            return score

        elif self.scoring_method == ScoringMethod.MIN_MAX_NORMALIZED:
            # Normalize and combine
            if not factors:
                return 0.0

            scores = list(factors.values())
            min_score = min(scores)
            max_score = max(scores)

            if max_score == min_score:
                return min_score

            # Normalize to 0-1 range
            normalized = [
                (s - min_score) / (max_score - min_score) for s in scores
            ]
            return statistics.mean(normalized)

        else:
            # Default to weighted average
            return self._apply_scoring_method(factors, weights)

    def set_scoring_method(self, method: ScoringMethod):
        """Set the scoring method.

        Args:
            method: Scoring method to use
        """
        self.scoring_method = method

    def set_industry_weights(self, industry: str, weights: Dict[str, float]):
        """Set industry-specific weights.

        Args:
            industry: Industry name
            weights: Industry-specific weights
        """
        self._validate_weights(weights)
        self.industry_weights[industry] = weights

    def add_custom_factor(
        self, name: str, calculator: Callable, weight: float
    ):
        """Add custom confidence factor.

        Args:
            name: Factor name
            calculator: Function to calculate factor score
            weight: Weight for this factor
        """
        self.custom_factors[name] = calculator

        # Update weights to include new factor
        self.weights[name] = weight

        # Renormalize weights to sum to 1.0
        total = sum(self.weights.values())
        for factor in self.weights:
            self.weights[factor] /= total

    def filter_by_confidence(
        self,
        extraction_data: Union[List[Dict[str, Any]], Dict[str, Any]],
        threshold: float,
    ) -> List[Dict[str, Any]]:
        """Filter extractions by confidence threshold.

        Args:
            extraction_data: List of extraction data or single extraction
            threshold: Minimum confidence threshold

        Returns:
            Filtered list of extractions
        """
        # Handle single extraction data case
        if isinstance(extraction_data, dict):
            extraction_data = [extraction_data]

        filtered = []
        for data in extraction_data:
            if isinstance(data, dict):
                confidence = self.calculate_confidence(data)
                if confidence >= threshold:
                    filtered.append(data)

        return filtered

    def explain_confidence(
        self, extraction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate explanation for confidence score.

        Args:
            extraction_data: Extraction data

        Returns:
            Explanation dictionary with factor breakdown
        """
        industry = extraction_data.get("industry")
        weights = self.industry_weights.get(industry, self.weights)

        explanation = {}

        # Calculate individual factors
        if "source_reliability" in weights:
            explanation[
                "source_reliability"
            ] = self._calculate_source_reliability(extraction_data)

        if "extraction_method" in weights:
            explanation[
                "extraction_method"
            ] = self._calculate_extraction_method_score(extraction_data)

        if "content_quality" in weights:
            explanation["content_quality"] = self._calculate_content_quality(
                extraction_data
            )

        if "industry_relevance" in weights:
            explanation[
                "industry_relevance"
            ] = self._calculate_industry_relevance(extraction_data)

        if "llm_confidence" in weights:
            explanation["llm_confidence"] = self._calculate_llm_confidence(
                extraction_data
            )

        # Overall confidence
        explanation["overall_confidence"] = self.calculate_confidence(
            extraction_data
        )
        explanation["weights_used"] = weights.copy()
        explanation["scoring_method"] = self.scoring_method.value

        return explanation

    def score_batch(
        self, extraction_batch: List[Dict[str, Any]]
    ) -> List[float]:
        """Score multiple extractions in batch.

        Args:
            extraction_batch: List of extraction data

        Returns:
            List of confidence scores
        """
        return [self.calculate_confidence(data) for data in extraction_batch]

    def adjust_weights_from_performance(
        self, performance_data: Dict[str, Dict[str, Any]]
    ):
        """Adjust weights based on performance feedback.

        Args:
            performance_data: Performance metrics for each factor
        """
        # Calculate performance-based adjustments
        adjustments = {}

        for factor, metrics in performance_data.items():
            if factor in self.weights:
                accuracy = metrics.get("accuracy", 0.5)
                samples = metrics.get("samples", 1)

                # Weight adjustment based on accuracy and sample size
                confidence_in_metric = min(
                    1.0, samples / 100
                )  # More samples = more confidence
                adjustment = (
                    (accuracy - 0.5) * confidence_in_metric * 0.1
                )  # Max 10% adjustment

                adjustments[factor] = adjustment

        # Apply adjustments
        for factor, adjustment in adjustments.items():
            self.weights[factor] += adjustment

        # Renormalize weights
        total = sum(self.weights.values())
        for factor in self.weights:
            self.weights[factor] /= total

    def calibrate(
        self, calibration_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calibrate confidence scores against ground truth.

        Args:
            calibration_data: List of predictions vs actual accuracy

        Returns:
            Calibration metrics
        """
        if not calibration_data:
            return {"calibration_error": 0.0, "reliability_diagram": []}

        # Calculate calibration error
        total_error = 0.0
        reliability_diagram = []

        # Group predictions into bins
        bin_size = 0.1
        bins = {}

        for data in calibration_data:
            predicted = data.get("predicted_confidence", 0.5)
            actual = data.get("actual_accuracy", 0.5)

            bin_idx = int(predicted / bin_size) * bin_size
            if bin_idx not in bins:
                bins[bin_idx] = {"predictions": [], "accuracies": []}

            bins[bin_idx]["predictions"].append(predicted)
            bins[bin_idx]["accuracies"].append(actual)

        # Calculate error for each bin
        for bin_center, bin_data in bins.items():
            if bin_data["predictions"]:
                avg_predicted = statistics.mean(bin_data["predictions"])
                avg_actual = statistics.mean(bin_data["accuracies"])
                bin_error = abs(avg_predicted - avg_actual)

                total_error += bin_error * len(bin_data["predictions"])
                reliability_diagram.append(
                    {
                        "bin_center": bin_center,
                        "avg_predicted": avg_predicted,
                        "avg_actual": avg_actual,
                        "count": len(bin_data["predictions"]),
                    }
                )

        total_samples = len(calibration_data)
        calibration_error = (
            total_error / total_samples if total_samples > 0 else 0.0
        )

        return {
            "calibration_error": calibration_error,
            "reliability_diagram": reliability_diagram,
        }

    def analyze_confidence_trends(
        self, time_series_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze confidence trends over time.

        Args:
            time_series_data: Time series of confidence scores

        Returns:
            Trend analysis results
        """
        if len(time_series_data) < 2:
            return {
                "trend_direction": "stable",
                "average_confidence": 0.0,
                "confidence_variance": 0.0,
            }

        confidences = [
            data.get("confidence", 0.0) for data in time_series_data
        ]

        # Calculate trend direction
        first_half = confidences[: len(confidences) // 2]
        second_half = confidences[len(confidences) // 2 :]

        avg_first = statistics.mean(first_half)
        avg_second = statistics.mean(second_half)

        if avg_second > avg_first + 0.05:
            trend_direction = "increasing"
        elif avg_second < avg_first - 0.05:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"

        return {
            "trend_direction": trend_direction,
            "average_confidence": statistics.mean(confidences),
            "confidence_variance": statistics.variance(confidences)
            if len(confidences) > 1
            else 0.0,
        }
