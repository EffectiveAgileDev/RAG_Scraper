"""Scraping configuration management for RAG_Scraper."""
import os
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class ScrapingConfig:
    """Configuration for restaurant scraping operations."""

    urls: List[str]
    output_directory: str = field(
        default_factory=lambda: os.path.join(os.path.expanduser("~"), "Downloads")
    )
    file_mode: str = "single"  # 'single' or 'multiple'
    output_format: str = "text"  # 'text', 'pdf', or 'both'
    selected_optional_fields: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: str = field(
        default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    max_pages_per_site: int = 10
    page_discovery_enabled: bool = True
    timeout_per_page: int = 30
    timeout_per_site: int = 300  # 5 minutes
    rate_limit_delay: float = 2.0  # seconds between requests
    user_agent: str = "RAG_Scraper/1.0 (Restaurant Data Collection)"

    # Multi-page scraping configuration
    max_crawl_depth: int = 2
    follow_pagination: bool = False
    max_total_pages: Optional[int] = None
    crawl_timeout: Optional[int] = None
    concurrent_requests: int = 3
    respect_robots_txt: bool = True
    page_timeout: Optional[int] = None  # Override for timeout_per_page

    # Link patterns configuration
    link_patterns: Dict[str, List[str]] = field(
        default_factory=lambda: {"include": [], "exclude": []}
    )

    # Crawl settings
    crawl_settings: Dict[str, Any] = field(default_factory=dict)

    # Per-domain settings
    per_domain_settings: Dict[str, Dict[str, Any]] = field(default_factory=dict)

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
        """Post-initialization validation and setup."""
        # Validate URLs
        if not self.urls:
            raise ValueError("At least one URL must be provided")

        # Validate file mode
        if self.file_mode not in ["single", "multiple"]:
            raise ValueError("file_mode must be 'single' or 'multiple'")

        # Validate output format
        if self.output_format not in ["text", "pdf", "both"]:
            raise ValueError("output_format must be 'text', 'pdf', or 'both'")

        # Ensure output directory exists
        if not os.path.exists(self.output_directory):
            try:
                os.makedirs(self.output_directory, exist_ok=True)
            except OSError:
                # Fall back to temporary directory
                import tempfile

                self.output_directory = tempfile.gettempdir()

        # Validate optional fields
        invalid_fields = set(self.selected_optional_fields) - set(self.optional_fields)
        if invalid_fields:
            raise ValueError(f"Invalid optional fields: {invalid_fields}")

        # Validate timeouts
        if self.timeout_per_page <= 0:
            raise ValueError("timeout_per_page must be positive")

        if self.timeout_per_site <= 0:
            raise ValueError("timeout_per_site must be positive")

        # Validate rate limit
        if self.rate_limit_delay < 0:
            raise ValueError("rate_limit_delay cannot be negative")

        # Validate multi-page configuration
        if self.max_pages_per_site <= 0:
            raise ValueError("max_pages_per_site must be positive")

        if self.max_crawl_depth < 1:
            raise ValueError("max_crawl_depth must be at least 1")

        if self.concurrent_requests < 1:
            raise ValueError("concurrent_requests must be at least 1")

        if self.page_timeout is not None and self.page_timeout <= 0:
            raise ValueError("page_timeout must be positive")

        if self.max_total_pages is not None and self.max_total_pages <= 0:
            raise ValueError("max_total_pages must be positive")

        if self.crawl_timeout is not None and self.crawl_timeout <= 0:
            raise ValueError("crawl_timeout must be positive")

        # Validate link patterns
        self._validate_link_patterns()

        # Validate per-domain settings
        self._validate_per_domain_settings()

        # Process crawl_settings if provided
        if self.crawl_settings:
            self._process_crawl_settings()

        # Use page_timeout if specified, otherwise use timeout_per_page
        if self.page_timeout is not None:
            self.timeout_per_page = self.page_timeout

    def get_all_selected_fields(self) -> List[str]:
        """Get all fields to extract (default + selected optional)."""
        return self.default_fields + self.selected_optional_fields

    def is_field_selected(self, field_name: str) -> bool:
        """Check if a field is selected for extraction."""
        return (
            field_name in self.default_fields
            or field_name in self.selected_optional_fields
        )

    def get_output_filename(self, file_type: str = "txt") -> str:
        """Generate output filename based on configuration."""
        timestamp_str = self.timestamp.strftime("%Y%m%d-%H%M")
        return f"WebScrape_{timestamp_str}.{file_type}"

    def get_full_output_path(self, filename: str) -> str:
        """Get full path for output file."""
        return os.path.join(self.output_directory, filename)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        data = {
            "urls": self.urls,
            "output_directory": self.output_directory,
            "file_mode": self.file_mode,
            "output_format": self.output_format,
            "selected_optional_fields": self.selected_optional_fields,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
            "max_pages_per_site": self.max_pages_per_site,
            "page_discovery_enabled": self.page_discovery_enabled,
            "timeout_per_page": self.timeout_per_page,
            "timeout_per_site": self.timeout_per_site,
            "rate_limit_delay": self.rate_limit_delay,
            "user_agent": self.user_agent,
            "max_crawl_depth": self.max_crawl_depth,
            "follow_pagination": self.follow_pagination,
            "concurrent_requests": self.concurrent_requests,
            "respect_robots_txt": self.respect_robots_txt,
            "link_patterns": self.link_patterns,
        }

        # Add optional fields if set
        if self.max_total_pages is not None:
            data["max_total_pages"] = self.max_total_pages
        if self.crawl_timeout is not None:
            data["crawl_timeout"] = self.crawl_timeout
        if self.page_timeout is not None:
            data["page_timeout"] = self.page_timeout
        if self.crawl_settings:
            data["crawl_settings"] = self.crawl_settings
        if self.per_domain_settings:
            data["per_domain_settings"] = self.per_domain_settings

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScrapingConfig":
        """Create configuration from dictionary."""
        # Convert timestamp string back to datetime
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])

        return cls(**data)

    def save_to_file(self, filepath: str) -> None:
        """Save configuration to JSON file."""
        import json

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, filepath: str) -> "ScrapingConfig":
        """Load configuration from JSON file."""
        import json

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls.from_dict(data)

    def validate_permissions(self) -> bool:
        """Validate that output directory is writable."""
        try:
            # Try to create a temporary file
            import tempfile

            test_file = tempfile.NamedTemporaryFile(
                dir=self.output_directory, delete=True
            )
            test_file.close()
            return True
        except (OSError, PermissionError):
            return False

    def get_estimated_file_size(self) -> int:
        """Estimate output file size in bytes."""
        # Rough estimation: 500 bytes per restaurant for text output
        base_size_per_restaurant = 500

        if self.output_format == "pdf":
            base_size_per_restaurant *= 3  # PDFs are typically larger
        elif self.output_format == "both":
            base_size_per_restaurant *= 4  # Both formats

        # Add extra size for optional fields
        optional_field_multiplier = 1 + (len(self.selected_optional_fields) * 0.2)

        estimated_size = (
            len(self.urls) * base_size_per_restaurant * optional_field_multiplier
        )

        return int(estimated_size)

    def get_estimated_duration(self) -> float:
        """Estimate scraping duration in seconds."""
        # Base time per URL (including rate limiting)
        base_time_per_url = 5.0  # seconds

        # Add rate limiting time
        rate_limit_time = len(self.urls) * self.rate_limit_delay

        # Add extra time for optional fields
        optional_field_time = len(self.selected_optional_fields) * 0.5

        # Add multi-page processing time
        multi_page_time = 0
        if self.page_discovery_enabled:
            multi_page_time = len(self.urls) * 2.0  # average 2 extra pages per site

        total_time = (
            len(self.urls) * base_time_per_url
            + rate_limit_time
            + len(self.urls) * optional_field_time
            + multi_page_time
        )

        return total_time

    def _validate_link_patterns(self) -> None:
        """Validate link patterns are valid regex patterns."""
        for pattern_type, patterns in self.link_patterns.items():
            if pattern_type not in ["include", "exclude"]:
                raise ValueError(f"Invalid link pattern type: {pattern_type}")

            for pattern in patterns:
                try:
                    re.compile(pattern)
                except re.error as e:
                    raise ValueError(f"Invalid regex pattern '{pattern}': {e}")

    def _validate_per_domain_settings(self) -> None:
        """Validate per-domain settings."""
        for domain, settings in self.per_domain_settings.items():
            if "rate_limit" in settings:
                if settings["rate_limit"] <= 0:
                    raise ValueError(f"Rate limit must be positive for domain {domain}")

            if "max_pages" in settings:
                if settings["max_pages"] <= 0:
                    raise ValueError(f"Max pages must be positive for domain {domain}")

    def _process_crawl_settings(self) -> None:
        """Process crawl_settings and apply to instance attributes."""
        # Map crawl_settings to instance attributes
        if "max_crawl_depth" in self.crawl_settings:
            self.max_crawl_depth = self.crawl_settings["max_crawl_depth"]

        if "follow_pagination" in self.crawl_settings:
            self.follow_pagination = self.crawl_settings["follow_pagination"]

        if "respect_robots_txt" in self.crawl_settings:
            self.respect_robots_txt = self.crawl_settings["respect_robots_txt"]

    def should_follow_link(self, link: str) -> bool:
        """Check if a link should be followed based on link patterns.

        Args:
            link: URL or path to check

        Returns:
            bool: True if link should be followed, False otherwise
        """
        # First check if it matches any include patterns
        include_patterns = self.link_patterns.get("include", [])
        exclude_patterns = self.link_patterns.get("exclude", [])

        # If no include patterns, default to False unless no patterns at all
        if not include_patterns and not exclude_patterns:
            return True

        # Check exclude patterns first (they take precedence)
        for pattern in exclude_patterns:
            if re.search(pattern, link):
                return False

        # Check include patterns
        if include_patterns:
            for pattern in include_patterns:
                if re.search(pattern, link):
                    return True
            return False  # Didn't match any include pattern

        return True  # No include patterns, and didn't match exclude

    def get_domain_settings(self, domain: str) -> Dict[str, Any]:
        """Get settings for a specific domain, falling back to defaults.

        Args:
            domain: Domain name to get settings for

        Returns:
            Dict[str, Any]: Domain-specific settings or defaults
        """
        if domain in self.per_domain_settings:
            return self.per_domain_settings[domain]

        # Return default settings
        return self.per_domain_settings.get(
            "default",
            {
                "rate_limit": self.rate_limit_delay,
                "max_pages": self.max_pages_per_site,
                "user_agent": self.user_agent,
            },
        )
