"""Relevance score data structure for content scoring."""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class RelevanceScore:
    """Data structure for content relevance scores."""
    
    content_id: str
    intent_type: str
    score: float
    confidence: float
    factors: Dict[str, float]
    
    def __post_init__(self):
        """Validate score and confidence ranges."""
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"Score must be between 0.0 and 1.0, got {self.score}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert RelevanceScore to dictionary."""
        return {
            "content_id": self.content_id,
            "intent_type": self.intent_type,
            "score": self.score,
            "confidence": self.confidence,
            "factors": self.factors
        }