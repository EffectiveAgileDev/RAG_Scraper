"""Core configuration classes for domain-specific settings."""

import os
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class CoreScrapingConfig:
    """Core scraping configuration with basic settings."""
    
    urls: List[str]
    output_directory: str = field(
        default_factory=lambda: os.path.join(os.path.expanduser("~"), "Downloads")
    )
    file_mode: str = "single"  # 'single' or 'multiple'
    output_format: str = "text"  # 'text', 'pdf', or 'both'
    session_id: str = field(
        default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    timestamp: datetime = field(default_factory=datetime.now)
    user_agent: str = "RAG_Scraper/1.0 (Restaurant Data Collection)"
    
    def __post_init__(self):
        """Post-initialization validation."""
        if not self.urls:
            raise ValueError("At least one URL must be provided")
        
        if self.file_mode not in ["single", "multiple"]:
            raise ValueError("file_mode must be 'single' or 'multiple'")
        
        if self.output_format not in ["text", "pdf", "both"]:
            raise ValueError("output_format must be 'text', 'pdf', or 'both'")
        
        # Ensure output directory exists
        if not os.path.exists(self.output_directory):
            try:
                os.makedirs(self.output_directory, exist_ok=True)
            except OSError:
                import tempfile
                self.output_directory = tempfile.gettempdir()


@dataclass
class TimeoutConfig:
    """Timeout configuration for various operations."""
    
    timeout_per_page: int = 30
    timeout_per_site: int = 300  # 5 minutes
    rate_limit_delay: float = 2.0  # seconds between requests
    
    def __post_init__(self):
        """Validate timeout configuration."""
        if self.timeout_per_page <= 0:
            raise ValueError("timeout_per_page must be positive")
        
        if self.timeout_per_site <= 0:
            raise ValueError("timeout_per_site must be positive")
        
        if self.rate_limit_delay < 0:
            raise ValueError("rate_limit_delay cannot be negative")


@dataclass
class FieldSelectionConfig:
    """Configuration for field selection and extraction."""
    
    selected_optional_fields: List[str] = field(default_factory=list)
    
    # Default fields that are always extracted
    default_fields: List[str] = field(
        default_factory=lambda: [
            "name",
            "address", 
            "phone",
            "website",
            "price_range",
            "hours",
            "menu_items",
        ]
    )
    
    # Optional fields that can be selected
    optional_fields: List[str] = field(
        default_factory=lambda: [
            "cuisine_types",
            "special_features", 
            "parking_info",
            "reservation_info",
            "featured_items",
            "pricing_specials",
            "email",
            "social_media",
            "delivery_options",
            "dietary_accommodations",
            "ambiance",
        ]
    )
    
    def __post_init__(self):
        """Validate field selection."""
        invalid_fields = set(self.selected_optional_fields) - set(self.optional_fields)
        if invalid_fields:
            raise ValueError(f"Invalid optional fields: {invalid_fields}")
    
    def get_all_selected_fields(self) -> List[str]:
        """Get all fields to extract (default + selected optional)."""
        return self.default_fields + self.selected_optional_fields
    
    def is_field_selected(self, field_name: str) -> bool:
        """Check if a field is selected for extraction."""
        return (
            field_name in self.default_fields
            or field_name in self.selected_optional_fields
        )