"""Base classes for data extraction results."""
from dataclasses import dataclass
from typing import Dict, Any, Optional, List


@dataclass
class BaseExtractionResult:
    """Base class for all extraction results with common restaurant data fields."""

    name: str = ""
    address: str = ""
    phone: str = ""
    hours: str = ""
    price_range: str = ""
    cuisine: str = ""
    menu_items: Optional[Dict[str, List[str]]] = None
    social_media: Optional[List[str]] = None
    confidence: str = "medium"
    source: str = ""

    def __post_init__(self):
        """Initialize default values for optional fields."""
        if self.menu_items is None:
            self.menu_items = {}
        if self.social_media is None:
            self.social_media = []

    def is_valid(self) -> bool:
        """Check if extraction result has valid data."""
        return bool(self.name and self.name.strip())

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "hours": self.hours,
            "price_range": self.price_range,
            "cuisine": self.cuisine,
            "menu_items": self.menu_items,
            "social_media": self.social_media,
            "confidence": self.confidence,
            "source": self.source,
        }