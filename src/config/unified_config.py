"""Unified configuration manager for all scraping configurations."""

import os
from typing import Dict, Any, List
from dataclasses import dataclass, asdict

from .core_config import CoreScrapingConfig, TimeoutConfig, FieldSelectionConfig
from .javascript_config import JavaScriptConfig
from .multipage_config import MultiPageConfig
from .schema_config import SchemaConfig, AIExtractionConfig


@dataclass
class UnifiedScrapingConfig:
    """Unified configuration combining all domain-specific configs."""
    
    core: CoreScrapingConfig
    timeouts: TimeoutConfig
    fields: FieldSelectionConfig
    javascript: JavaScriptConfig
    multipage: MultiPageConfig
    schema: SchemaConfig
    ai_extraction: AIExtractionConfig = None
    
    def __post_init__(self):
        """Initialize AI extraction config if not provided."""
        if self.ai_extraction is None:
            self.ai_extraction = AIExtractionConfig()
    
    @classmethod
    def from_legacy_config(cls, legacy_config: 'ScrapingConfig') -> 'UnifiedScrapingConfig':
        """Create unified config from legacy ScrapingConfig."""
        # Extract core configuration
        core = CoreScrapingConfig(
            urls=legacy_config.urls,
            output_directory=legacy_config.output_directory,
            file_mode=legacy_config.file_mode,
            output_format=legacy_config.output_format,
            session_id=legacy_config.session_id,
            timestamp=legacy_config.timestamp,
            user_agent=legacy_config.user_agent
        )
        
        # Extract timeout configuration
        timeouts = TimeoutConfig(
            timeout_per_page=legacy_config.timeout_per_page,
            timeout_per_site=legacy_config.timeout_per_site,
            rate_limit_delay=legacy_config.rate_limit_delay
        )
        
        # Extract field selection configuration
        fields = FieldSelectionConfig(
            selected_optional_fields=legacy_config.selected_optional_fields,
            default_fields=legacy_config.default_fields,
            optional_fields=legacy_config.optional_fields
        )
        
        # Extract JavaScript configuration
        javascript = JavaScriptConfig(
            enable_javascript_rendering=legacy_config.enable_javascript_rendering,
            javascript_timeout=legacy_config.javascript_timeout,
            enable_popup_detection=legacy_config.enable_popup_detection,
            popup_handling_strategy=legacy_config.popup_handling_strategy,
            enable_browser_automation=legacy_config.enable_browser_automation,
            browser_type=legacy_config.browser_type,
            headless_browser=legacy_config.headless_browser
        )
        
        # Extract multi-page configuration
        multipage = MultiPageConfig(
            enable_multi_page=legacy_config.enable_multi_page,
            max_pages_per_site=legacy_config.max_pages_per_site,
            max_crawl_depth=legacy_config.max_crawl_depth,
            follow_pagination=legacy_config.follow_pagination,
            max_total_pages=legacy_config.max_total_pages,
            crawl_timeout=legacy_config.crawl_timeout,
            concurrent_requests=legacy_config.concurrent_requests,
            respect_robots_txt=legacy_config.respect_robots_txt,
            page_timeout=legacy_config.page_timeout,
            page_discovery_enabled=legacy_config.page_discovery_enabled,
            link_patterns=legacy_config.link_patterns,
            crawl_settings=legacy_config.crawl_settings,
            per_domain_settings=legacy_config.per_domain_settings
        )
        
        # Extract schema configuration
        schema = SchemaConfig(
            enable_restw_schema=getattr(legacy_config, 'enable_restw_schema', False),
            force_batch_processing=getattr(legacy_config, 'force_batch_processing', False)
        )
        
        # Create AI extraction config (default for now)
        ai_extraction = AIExtractionConfig()
        
        return cls(
            core=core,
            timeouts=timeouts,
            fields=fields,
            javascript=javascript,
            multipage=multipage,
            schema=schema,
            ai_extraction=ai_extraction
        )
    
    def to_legacy_config(self) -> Dict[str, Any]:
        """Convert to legacy ScrapingConfig format for backward compatibility."""
        # Combine all configurations into a single dictionary
        config_dict = {}
        
        # Add core configuration
        config_dict.update(asdict(self.core))
        
        # Add timeout configuration
        config_dict.update(asdict(self.timeouts))
        
        # Add field selection configuration
        config_dict.update(asdict(self.fields))
        
        # Add JavaScript configuration
        config_dict.update(asdict(self.javascript))
        
        # Add multi-page configuration
        config_dict.update(asdict(self.multipage))
        
        # Add schema configuration
        config_dict.update(asdict(self.schema))
        
        return config_dict
    
    def get_output_filename(self, file_type: str = "txt") -> str:
        """Generate output filename based on configuration."""
        timestamp_str = self.core.timestamp.strftime("%Y%m%d-%H%M")
        return f"WebScrape_{timestamp_str}.{file_type}"
    
    def get_full_output_path(self, filename: str) -> str:
        """Get full path for output file."""
        return os.path.join(self.core.output_directory, filename)
    
    def validate_permissions(self) -> bool:
        """Validate that output directory is writable."""
        try:
            import tempfile
            test_file = tempfile.NamedTemporaryFile(
                dir=self.core.output_directory, delete=True
            )
            test_file.close()
            return True
        except (OSError, PermissionError):
            return False
    
    def get_estimated_file_size(self) -> int:
        """Estimate output file size in bytes."""
        base_size_per_restaurant = 500
        
        if self.core.output_format == "pdf":
            base_size_per_restaurant *= 3
        elif self.core.output_format == "both":
            base_size_per_restaurant *= 4
        
        # Add extra size for optional fields
        optional_field_multiplier = 1 + (len(self.fields.selected_optional_fields) * 0.2)
        
        estimated_size = (
            len(self.core.urls) * base_size_per_restaurant * optional_field_multiplier
        )
        
        return int(estimated_size)
    
    def get_estimated_duration(self) -> float:
        """Estimate scraping duration in seconds."""
        base_time_per_url = 5.0
        rate_limit_time = len(self.core.urls) * self.timeouts.rate_limit_delay
        optional_field_time = len(self.fields.selected_optional_fields) * 0.5
        
        multi_page_time = 0
        if self.multipage.page_discovery_enabled:
            multi_page_time = len(self.core.urls) * 2.0
        
        total_time = (
            len(self.core.urls) * base_time_per_url
            + rate_limit_time
            + len(self.core.urls) * optional_field_time
            + multi_page_time
        )
        
        return total_time
    
    def save_to_file(self, filepath: str) -> None:
        """Save configuration to JSON file."""
        import json
        
        config_dict = self.to_legacy_config()
        # Convert datetime to string for JSON serialization
        if 'timestamp' in config_dict:
            config_dict['timestamp'] = config_dict['timestamp'].isoformat()
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'UnifiedScrapingConfig':
        """Load configuration from JSON file."""
        import json
        from datetime import datetime
        from ..scraping_config import ScrapingConfig
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Convert timestamp string back to datetime
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        
        # Create legacy config first, then convert
        legacy_config = ScrapingConfig.from_dict(data)
        return cls.from_legacy_config(legacy_config)
    
    def is_ai_extraction_ready(self) -> bool:
        """Check if configuration is ready for AI-powered extraction."""
        return (
            self.ai_extraction.is_ai_enabled() and
            self.schema.extraction_strategies and
            "ai_extraction" in self.schema.extraction_strategies
        )
    
    def prepare_for_ai_extraction(self) -> None:
        """Prepare configuration for AI-powered extraction."""
        if "ai_extraction" not in self.schema.extraction_strategies:
            # Insert AI extraction as first priority
            self.schema.add_extraction_strategy("ai_extraction", 0)
        
        self.ai_extraction.enable_ai_extraction = True