"""Schema and extraction configuration."""

from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class SchemaConfig:
    """Configuration for data extraction schemas."""
    
    enable_restw_schema: bool = False
    force_batch_processing: bool = False
    extraction_strategies: List[str] = None
    
    def __post_init__(self):
        """Initialize default extraction strategies if not provided."""
        if self.extraction_strategies is None:
            self.extraction_strategies = ["json_ld", "microdata", "heuristic"]
    
    def is_restw_enabled(self) -> bool:
        """Check if RestW schema is enabled."""
        return self.enable_restw_schema
    
    def should_force_batch_processing(self) -> bool:
        """Check if batch processing should be forced."""
        return self.force_batch_processing
    
    def get_extraction_strategies(self) -> List[str]:
        """Get list of extraction strategies in priority order."""
        return self.extraction_strategies.copy()
    
    def add_extraction_strategy(self, strategy: str, position: int = None) -> None:
        """Add a new extraction strategy at specified position."""
        if position is None:
            self.extraction_strategies.append(strategy)
        else:
            self.extraction_strategies.insert(position, strategy)
    
    def remove_extraction_strategy(self, strategy: str) -> bool:
        """Remove an extraction strategy. Returns True if removed."""
        try:
            self.extraction_strategies.remove(strategy)
            return True
        except ValueError:
            return False
    
    def set_strategy_priority(self, strategy: str, position: int) -> bool:
        """Move strategy to specific position. Returns True if successful."""
        if strategy not in self.extraction_strategies:
            return False
        
        # Remove and re-insert at new position
        self.extraction_strategies.remove(strategy)
        self.extraction_strategies.insert(position, strategy)
        return True


@dataclass
class AIExtractionConfig:
    """Configuration for AI-powered extraction (prepared for future use)."""
    
    enable_ai_extraction: bool = False
    ai_model: str = "gpt-3.5-turbo"
    ai_temperature: float = 0.1
    ai_max_tokens: int = 1000
    ai_fallback_enabled: bool = True
    ai_confidence_threshold: float = 0.7
    ai_retry_attempts: int = 2
    ai_timeout: int = 30
    
    # AI-specific field mappings
    ai_field_mappings: Dict[str, str] = None
    
    # Custom prompts for different extraction types
    ai_prompts: Dict[str, str] = None
    
    def __post_init__(self):
        """Initialize default AI configurations."""
        if self.ai_field_mappings is None:
            self.ai_field_mappings = {
                "restaurant_name": "name",
                "business_address": "address",
                "contact_phone": "phone",
                "operating_hours": "hours",
                "price_category": "price_range",
                "cuisine_type": "cuisine",
                "menu_offerings": "menu_items",
                "social_links": "social_media"
            }
        
        if self.ai_prompts is None:
            self.ai_prompts = {
                "restaurant_extraction": """
                Extract restaurant information from the following content.
                Focus on: name, address, phone, hours, price range, cuisine type, and menu items.
                Return structured data in JSON format.
                """,
                "menu_extraction": """
                Extract menu items and pricing information from the following content.
                Include item names, descriptions, prices, and categories.
                Return as structured JSON.
                """,
                "contact_extraction": """
                Extract contact information including address, phone, email, and website.
                Format addresses consistently and validate phone numbers.
                Return as structured JSON.
                """
            }
    
    def is_ai_enabled(self) -> bool:
        """Check if AI extraction is enabled."""
        return self.enable_ai_extraction
    
    def get_prompt_for_type(self, extraction_type: str) -> str:
        """Get AI prompt for specific extraction type."""
        return self.ai_prompts.get(extraction_type, self.ai_prompts["restaurant_extraction"])
    
    def should_use_fallback(self) -> bool:
        """Check if fallback to traditional extraction is enabled."""
        return self.ai_fallback_enabled
    
    def is_confidence_acceptable(self, confidence: float) -> bool:
        """Check if AI extraction confidence meets threshold."""
        return confidence >= self.ai_confidence_threshold