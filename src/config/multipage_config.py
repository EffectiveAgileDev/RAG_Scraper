"""Multi-page scraping configuration."""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class MultiPageConfig:
    """Configuration for multi-page scraping operations."""
    
    enable_multi_page: bool = False
    max_pages_per_site: int = 10
    max_crawl_depth: int = 2
    follow_pagination: bool = False
    max_total_pages: Optional[int] = None
    crawl_timeout: Optional[int] = None
    concurrent_requests: int = 3
    respect_robots_txt: bool = True
    page_timeout: Optional[int] = None
    page_discovery_enabled: bool = True
    
    # Link patterns configuration
    link_patterns: Dict[str, List[str]] = field(
        default_factory=lambda: {"include": [], "exclude": []}
    )
    
    # Crawl settings
    crawl_settings: Dict[str, Any] = field(default_factory=dict)
    
    # Per-domain settings
    per_domain_settings: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate multi-page configuration."""
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
        if "max_crawl_depth" in self.crawl_settings:
            self.max_crawl_depth = self.crawl_settings["max_crawl_depth"]
        
        if "follow_pagination" in self.crawl_settings:
            self.follow_pagination = self.crawl_settings["follow_pagination"]
        
        if "respect_robots_txt" in self.crawl_settings:
            self.respect_robots_txt = self.crawl_settings["respect_robots_txt"]
    
    def should_follow_link(self, link: str) -> bool:
        """Check if a link should be followed based on link patterns."""
        include_patterns = self.link_patterns.get("include", [])
        exclude_patterns = self.link_patterns.get("exclude", [])
        
        # If no patterns at all, allow the link
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
        """Get settings for a specific domain, falling back to defaults."""
        if domain in self.per_domain_settings:
            return self.per_domain_settings[domain]
        
        # Return default settings
        return self.per_domain_settings.get(
            "default",
            {
                "max_pages": self.max_pages_per_site,
                "user_agent": "RAG_Scraper/1.0 (Restaurant Data Collection)",
            },
        )
    
    def is_enabled(self) -> bool:
        """Check if multi-page scraping is enabled."""
        return self.enable_multi_page
    
    def get_effective_page_timeout(self, default_timeout: int) -> int:
        """Get effective page timeout, using override if specified."""
        return self.page_timeout if self.page_timeout is not None else default_timeout